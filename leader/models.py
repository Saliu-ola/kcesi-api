from django.db import models
from group.models import Group
from organization.models import Organization
from django.core.validators import MinValueValidator


class Socialization(models.Model):
    post_blog = models.DecimalField(
        default=0, decimal_places=2, max_digits=9, validators=[MinValueValidator(0)]
    )
    send_chat_message = models.DecimalField(
        default=0, decimal_places=2, max_digits=9, validators=[MinValueValidator(0)]
    )
    post_forum = models.DecimalField(
        default=0, decimal_places=2, max_digits=9, validators=[MinValueValidator(0)]
    )
    image_sharing = models.DecimalField(
        default=0, decimal_places=2, max_digits=9, validators=[MinValueValidator(0)]
    )
    video_sharing = models.DecimalField(
        default=0, decimal_places=2, max_digits=9, validators=[MinValueValidator(0)]
    )
    text_resource_sharing = models.DecimalField(
        default=0, decimal_places=2, max_digits=9, validators=[MinValueValidator(0)]
    )
    created_topic = models.DecimalField(
        default=0, decimal_places=2, max_digits=9, validators=[MinValueValidator(0)]
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.DO_NOTHING, related_name="organization_socs", 
    )

    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group_socs")

    class Meta:
        unique_together = ['organization', 'group']

    def __str__(self) -> str:
        return f"socialization for {self.organization}"

    def calculate_socialization_score(self):
        attributes = [
            "post_blog",
            "send_chat_message",
            "post_forum",
            "image_sharing",
            "video_sharing",
            "text_resource_sharing",
            "created_topic",
        ]
        return sum(getattr(self, attr) for attr in attributes)


class Externalization(models.Model):
    post_blog = models.DecimalField(
        default=0, decimal_places=2, max_digits=9, validators=[MinValueValidator(0)]
    )
    send_chat_message = models.DecimalField(
        default=0, decimal_places=2, max_digits=9, validators=[MinValueValidator(0)]
    )
    post_forum = models.DecimalField(
        default=0, decimal_places=2, max_digits=9, validators=[MinValueValidator(0)]
    )
    created_topic = models.DecimalField(
        default=0, decimal_places=2, max_digits=9, validators=[MinValueValidator(0)]
    )
    comment = models.DecimalField(
        default=0, decimal_places=2, max_digits=9, validators=[MinValueValidator(0)]
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.DO_NOTHING, related_name="organization_exts", 
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group_exts")

    class Meta:
        unique_together = ['organization', 'group']

    def __str__(self) -> str:
        return f"externalization for {self.organization}"

    def calculate_externalization_score(self):
        attributes = [
            "post_blog",
            "send_chat_message",
            "post_forum",
            "created_topic",
            "comment",
        ]
        return sum(getattr(self, attr) for attr in attributes)


class Combination(models.Model):
    created_topic = models.DecimalField(
        default=0, decimal_places=2, max_digits=9, validators=[MinValueValidator(0)]
    )
    post_blog = models.DecimalField(
        default=0, decimal_places=2, max_digits=9, validators=[MinValueValidator(0)]
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.DO_NOTHING, related_name="organization_combs", 
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group_combs")

    class Meta:
        unique_together = ['organization', 'group']

    def __str__(self) -> str:
        return f"combination for {self.organization}"

    def calculate_combination_score(self):
        attributes = ["created_topic", "post_blog"]
        return sum(getattr(self, attr) for attr in attributes)


class Internalization(models.Model):
    used_in_app_browser = models.DecimalField(
        default=0, decimal_places=2, max_digits=9, validators=[MinValueValidator(0)]
    )
    read_blog = models.DecimalField(
        default=0, decimal_places=2, max_digits=9, validators=[MinValueValidator(0)]
    )
    read_forum = models.DecimalField(
        default=0, decimal_places=2, max_digits=9, validators=[MinValueValidator(0)]
    )
    recieve_chat_message = models.DecimalField(
        default=0, decimal_places=2, max_digits=9, validators=[MinValueValidator(0)]
    )
    download_resources = models.DecimalField(
        default=0, decimal_places=2, max_digits=9, validators=[MinValueValidator(0)]
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.DO_NOTHING, related_name="organization_inters", 
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group_inters")

    class Meta:
        unique_together = ['organization', 'group']

    def __str__(self) -> str:
        return f"internalization for {self.organization}"

    def calculate_internalization_score(self):
        attributes = [
            "used_in_app_browser",
            "read_blog",
            "read_forum",
            "recieve_chat_message",
            "download_resources",
        ]
        return sum(getattr(self, attr) for attr in attributes)
