from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from simpleblog.ai import get_cleaned_and_lematized_terms

# Create your models here.

"""
class Group:
    id int
    title str(50)
    content text
    created datetime
"""

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=50)
    content = models.TextField()
    organization_id = models.CharField(max_length=15, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    related_terms = models.JSONField(null=True, blank=True)
    related_terms_library_b = models.JSONField(null=True, blank=True)           #from files upload

    def __str__(self) -> str:
        return self.title or " "

    class Meta:
        ordering = ["-created_at"]


# Attach the signal to the Group model
@receiver(pre_save, sender=Group)
def regenerate_related_terms(sender, instance, **kwargs):
    """
    This signal regenerates related_terms whenever the content of a Group changes.
    """
    if instance.pk:  # If the Group already exists (not a new object)
        try:
            # Fetch the current version of the Group from the database
            old_instance = sender.objects.get(pk=instance.pk)

            # Compare the old content with the new one
            if old_instance.content != instance.content:
                # Content has changed, regenerate related_terms
                related_terms = get_cleaned_and_lematized_terms(instance.content)

                if not related_terms:
                    raise ValueError("No related terms found for the updated content")

                # Assign the new related_terms to the instance
                instance.related_terms = related_terms
        except sender.DoesNotExist:
            # If the Group doesn't exist in the database, it's being created
            pass


class UserGroup(models.Model):
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="user_groups",
        null=True,
    )
    groups = models.ManyToManyField("group.Group")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self) -> str:
        return f"{self.user}"

    class Meta:
        ordering = ["-created_at"]
        constraints = [models.UniqueConstraint(fields=['user'], name='unique_user_per_group')]
