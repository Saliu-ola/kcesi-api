from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _

TOKEN_TYPE = (
    ('ACCOUNT_VERIFICATION', 'ACCOUNT_VERIFICATION'),
    ('PASSWORD_RESET', 'PASSWORD_RESET'),
)


# Create a new user
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        # if extra_fields.get("role_id") == 1:
        #     newValue = True
        #     extra_fields.setdefault("is_superuser", True)
        #     extra_fields.setdefault("is_staff", True)

        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)

        user.set_password(password)

        user.save()

        return user

    # Use this to create a super user
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser has to have is_staff being True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser has to have is_superuser being True")

        return self.create_user(email=email, password=password, **extra_fields)


# Define the columns here and set their properties
class User(AbstractUser):
    email = models.EmailField(_('email address'), null=True, blank=True, unique=True)
    username = models.CharField(max_length=45)
    date_of_birth = models.DateField(null=True)
    role_id = models.IntegerField()
    group_id = models.IntegerField()
    organization_id = models.CharField(max_length=15, null=True)
    organization_name = models.CharField(max_length=50, null=True)
    phone = models.CharField(max_length=17, blank=True, null=True)
    is_verified = models.BooleanField(default=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    objects = CustomUserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.username

    class Meta:
        ordering = ("-created_at",)


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
