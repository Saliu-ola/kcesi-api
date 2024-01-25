from django.db import models
from group.models import Group
from organization.models import Organization
from django.core.validators import MinValueValidator
from simpleblog.utils import (
    calculate_percentage,
    calculate_category_score,
)


class Socialization(models.Model):
    post_blog = models.DecimalField(
        default=0, decimal_places=5, max_digits=9, validators=[MinValueValidator(0)]
    )
    send_chat_message = models.DecimalField(
        default=0, decimal_places=5, max_digits=9, validators=[MinValueValidator(0)]
    )
    post_forum = models.DecimalField(
        default=0, decimal_places=5, max_digits=9, validators=[MinValueValidator(0)]
    )
    image_sharing = models.DecimalField(
        default=0, decimal_places=5, max_digits=9, validators=[MinValueValidator(0)]
    )
    video_sharing = models.DecimalField(
        default=0, decimal_places=5, max_digits=9, validators=[MinValueValidator(0)]
    )
    text_resource_sharing = models.DecimalField(
        default=0, decimal_places=5, max_digits=9, validators=[MinValueValidator(0)]
    )
    created_topic = models.DecimalField(
        default=0, decimal_places=5, max_digits=9, validators=[MinValueValidator(0)]
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="organization_socs",
    )

    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group_socs")

    class Meta:
        unique_together = ['organization', 'group']

    def __str__(self) -> str:
        return f"socialization for {self.organization} ,  group {self.group}"

    def calculate_socialization_score(self, tallies):
        constants = {
            'post_blog': self.post_blog,
            'send_chat_message': self.send_chat_message,
            'post_forum': self.post_forum,
            'image_sharing': self.image_sharing,
            'video_sharing': self.video_sharing,
            'text_resource_sharing': self.text_resource_sharing,
            'created_topic': self.created_topic,
        }
        return calculate_category_score(constants, tallies)

    def calculate_socialization_percentage(self, sec, tes):
        score = sec
        return calculate_percentage(score, tes)


class Externalization(models.Model):
    post_blog = models.DecimalField(
        default=0, decimal_places=5, max_digits=9, validators=[MinValueValidator(0)]
    )
    send_chat_message = models.DecimalField(
        default=0, decimal_places=5, max_digits=9, validators=[MinValueValidator(0)]
    )
    post_forum = models.DecimalField(
        default=0, decimal_places=5, max_digits=9, validators=[MinValueValidator(0)]
    )
    created_topic = models.DecimalField(
        default=0, decimal_places=5, max_digits=9, validators=[MinValueValidator(0)]
    )
    comment = models.DecimalField(
        default=0, decimal_places=5, max_digits=9, validators=[MinValueValidator(0)]
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="organization_exts",
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group_exts")

    class Meta:
        unique_together = ['organization', 'group']

    def __str__(self) -> str:
        return f"externalization for {self.organization} ,  group {self.group}"

    def calculate_externalization_score(self, tallies):
        constants = {
            'post_blog': self.post_blog,
            'send_chat_message': self.send_chat_message,
            'post_forum': self.post_forum,
            'created_topic': self.created_topic,
            'comment': self.comment,
        }
        return calculate_category_score(constants, tallies)

    def calculate_externalization_percentage(self, eec, tes):
        score = eec
        return calculate_percentage(score, tes)


class Combination(models.Model):
    created_topic = models.DecimalField(
        default=0, decimal_places=5, max_digits=9, validators=[MinValueValidator(0)]
    )
    post_blog = models.DecimalField(
        default=0, decimal_places=5, max_digits=9, validators=[MinValueValidator(0)]
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="organization_combs",
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group_combs")

    class Meta:
        unique_together = ['organization', 'group']

    def __str__(self) -> str:
        return f"combination for {self.organization} ,  group {self.group}"

    def calculate_combination_score(self, tallies):
        constants = {
            'created_topic': self.created_topic,
            'post_blog': self.post_blog,
        }
        return calculate_category_score(constants, tallies)

    def calculate_combination_percentage(self, cec, tes):
        score = cec
        return calculate_percentage(score, tes)


class Internalization(models.Model):
    used_in_app_browser = models.DecimalField(
        default=0, decimal_places=5, max_digits=9, validators=[MinValueValidator(0)]
    )
    read_blog = models.DecimalField(
        default=0, decimal_places=5, max_digits=9, validators=[MinValueValidator(0)]
    )
    read_forum = models.DecimalField(
        default=0, decimal_places=5, max_digits=9, validators=[MinValueValidator(0)]
    )
    recieve_chat_message = models.DecimalField(
        default=0, decimal_places=5, max_digits=9, validators=[MinValueValidator(0)]
    )
    download_resources = models.DecimalField(
        default=0, decimal_places=5, max_digits=9, validators=[MinValueValidator(0)]
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="organization_inters",
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group_inters")

    class Meta:
        unique_together = ['organization', 'group']

    def __str__(self) -> str:
        return f"internalization for {self.organization} ,  group {self.group}"

    def calculate_internalization_score(self, tallies):
        constants = {
            'used_in_app_browser': self.used_in_app_browser,
            'read_blog': self.read_blog,
            'read_forum': self.read_forum,
            'recieve_chat_message': self.recieve_chat_message,
            'download_resources': self.download_resources,
        }
        return calculate_category_score(constants, tallies)

    def calculate_internalization_percentage(self, iec, tes):
        score = iec
        return calculate_percentage(score, tes)
