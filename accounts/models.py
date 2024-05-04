from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from random import randint
from django.db.models.signals import post_save
from django.utils import timezone
from organization.models import Organization
from django.db import transaction
from django.core.validators import MinValueValidator


TOKEN_TYPE = (
    ('ACCOUNT_VERIFICATION', 'ACCOUNT_VERIFICATION'),
    ('PASSWORD_RESET', 'PASSWORD_RESET'),
)

GENDER = (
    ('MALE', 'MALE'),
    ('FEMALE', 'FEMALE'),
)


# Create a new user
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)

        user.set_password(password)

        user.save()

        return user

    # Use this to create a super user
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified",True)
        extra_fields.setdefault("role_id",1)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser has to have is_staff being True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser has to have is_superuser being True")

        return self.create_user(email=email, password=password, **extra_fields)


# Define the columns here and set their properties
class User(AbstractUser):
    email = models.EmailField(_('email address'), null=True, blank=True, unique=True)
    username = models.CharField(max_length=45, null=True)
    first_name = models.CharField(max_length=45, null=True)
    last_name = models.CharField(max_length=45, null=True)
    date_of_birth = models.DateField(null=True)
    role_id = models.IntegerField(null=True)
    first_group_id = models.IntegerField(null=True)
    organization_id = models.CharField(
        max_length=15,
        null=True,
    )
    organization_name = models.CharField(max_length=50, null=True)
    phone = models.CharField(max_length=17, null=True)
    gender = models.CharField(choices=GENDER, null=True, max_length=20)
    is_verified = models.BooleanField(default=False, null=True)
    image_url = models.CharField(max_length=255, null=True)
    cloud_id = models.CharField(max_length=255, null=True)
    online_count = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    objects = CustomUserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_active_for_chat(self):
        if self.online_count == 0 :
            return False
        return True

    def generate_organization_id(self):
        if self.is_superuser and self.role_id == 1:
            org_id = f"S-{randint(100000000, 999999999)}{timezone.now().strftime('%y%m')}"

        elif self.role_id == 2 and not self.is_superuser:
            prefix = self.organization_name[:3].upper()
            middle_part = f"{randint(1000000, 9999999):07d}{timezone.now().strftime('%y%m')}"
            org_id = f"{prefix}-{middle_part}"

        return org_id[:14] + str(randint(0, 9))

    def __str__(self):
        if self.username:
            return f"{self.username}"
        else:
            return self.organization_name

    class Meta:
        ordering = ("-created_at",)


@receiver(post_save, sender=User)
def generate_organization_id(sender, instance, created, **kwargs):
    if created and instance.role_id in [1, 2]:
        if not instance.organization_id:
            instance.organization_id = instance.generate_organization_id()
            instance.save()
            Organization.objects.create(
                name=instance.organization_name, organization_id=instance.organization_id
            )


class Token(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, null=True)
    token_type = models.CharField(
        max_length=100, choices=TOKEN_TYPE, default='ACCOUNT_VERIFICATION'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{str(self.user)} {self.token}"

    def generate_random_token(self):
        if not self.token:
            self.token = get_random_string(30)
            self.save()

    def reset_user_password(self, password):
        self.user.set_password(password)
        self.user.save()
