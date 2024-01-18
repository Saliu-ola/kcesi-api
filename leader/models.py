from django.db import models
from group.models import Group
from organization.models import Organization
from django.core.validators import MinValueValidator


class Socialization(models.Model):
    post_blog = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    send_chat_message = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    post_forum = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    image_sharing = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    video_sharing = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    text_resource_sharing = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    created_topic = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    organization = models.ForeignKey(
        Organization, on_delete=models.DO_NOTHING, related_name="organization_socs"
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group_socs")

    def __str__(self) -> str:
        return "socialization"

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
    post_blog = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    send_chat_message = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    post_forum = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    created_topic = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    comment = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    organization = models.ForeignKey(
        Organization, on_delete=models.DO_NOTHING, related_name="organization_exts"
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group_exts")

    def __str__(self) -> str:
        return "externalization"

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
    created_topic = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    post_blog = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    organization = models.ForeignKey(
        Organization, on_delete=models.DO_NOTHING, related_name="organization_combs"
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group_combs")

    def __str__(self) -> str:
        return "combination"

    def calculate_combination_score(self):
        attributes = ["created_topic", "post_blog"]
        return sum(getattr(self, attr) for attr in attributes)


class Internalization(models.Model):
    used_in_app_browser = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    read_blog = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    read_forum = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    recieve_chat_message = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    download_resources = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    organization = models.ForeignKey(
        Organization, on_delete=models.DO_NOTHING, related_name="organization_inters"
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group_inters")

    def __str__(self) -> str:
        return "internalization"

    def calculate_internalization_score(self):
        attributes = [
            "used_in_app_browser",
            "read_blog",
            "read_forum",
            "recieve_chat_message",
            "download_resources",
        ]
        return sum(getattr(self, attr) for attr in attributes)
