from django.db import models
from group.models import Group
from organization.models import Organization
from django.core.validators import MinValueValidator
from simpleblog.utils import (
    calculate_percentage,
    calculate_category_score,
)
from decimal import Decimal, ROUND_DOWN, DivisionUndefined
import decimal

class Socialization(models.Model):
    post_blog = models.DecimalField(
        default=0.00000, decimal_places=5, max_digits=9, validators=[MinValueValidator(0.00000)]
    )
    send_chat_message = models.DecimalField(
        default=0.00000, decimal_places=5, max_digits=9, validators=[MinValueValidator(0.00000)]
    )
    post_forum = models.DecimalField(
        default=0.00000, decimal_places=5, max_digits=9, validators=[MinValueValidator(0.00000)]
    )
    image_sharing = models.DecimalField(
        default=0.00000, decimal_places=5, max_digits=9, validators=[MinValueValidator(0.00000)]
    )
    video_sharing = models.DecimalField(
        default=0.00000, decimal_places=5, max_digits=9, validators=[MinValueValidator(0.00000)]
    )
    text_resource_sharing = models.DecimalField(
        default=0.00000, decimal_places=5, max_digits=9, validators=[MinValueValidator(0.00000)]
    )
    created_topic = models.DecimalField(
        default=0.00000, decimal_places=5, max_digits=9, validators=[MinValueValidator(0.00000)]
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

        relevancy_fields = ['post_blog', 'post_forum', 'send_chat_message']
        score = Decimal('0')
        for key, constant in constants.items():
            tally = Decimal(tallies.get(key, 0))
            # print(f"Processing: {key}, Constant: {constant}, Tally: {tally}")

            if key in relevancy_fields:
                percentage = tally / Decimal('100')
                score += constant * percentage
                # print(f"Percentage for {key}: {percentage} (Tally: {tally})")
            else:
                score += constant * tally
                # print(f"Direct multiplication for {key}: {constant} * {tally} = {constant * tally}")
        # print(f"Final score: {score}")

        return score

        # return calculate_category_score(constants, tallies)

    def calculate_socialization_percentage(self, sec, tes):
        score = sec
        return calculate_percentage(score, tes)


class Externalization(models.Model):
    post_blog = models.DecimalField(
        default=0.00000, decimal_places=5, max_digits=9, validators=[MinValueValidator(0.00000)]
    )
    send_chat_message = models.DecimalField(
        default=0.00000, decimal_places=5, max_digits=9, validators=[MinValueValidator(0.00000)]
    )
    post_forum = models.DecimalField(
        default=0.00000, decimal_places=5, max_digits=9, validators=[MinValueValidator(0.00000)]
    )
    created_topic = models.DecimalField(
        default=0.00000, decimal_places=5, max_digits=9, validators=[MinValueValidator(0.00000)]
    )
    comment = models.DecimalField(
        default=0.00000, decimal_places=5, max_digits=9, validators=[MinValueValidator(0.00000)]
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

        relevancy_fields = ['post_blog', 'post_forum', 'send_chat_message', 'comment']
        score = Decimal('0')
        for key, constant in constants.items():
            tally = Decimal(tallies.get(key, 0))
            # print(f"constant {constant} {tally}" )
            if key in relevancy_fields:
                percentage = tally / Decimal('100')
                score += constant * percentage
            else:
                score += constant * tally

        return score
        # return calculate_category_score(constants, tallies)

    def calculate_externalization_percentage(self, eec, tes):
        score = eec
        return calculate_percentage(score, tes)


class Combination(models.Model):
    created_topic = models.DecimalField(
        default=0.00000, decimal_places=5, max_digits=9, validators=[MinValueValidator(0.00000)]
    )
    post_blog = models.DecimalField(
        default=0.00000, decimal_places=5, max_digits=9, validators=[MinValueValidator(0.00000)]
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
            # 'post_blog': self.post_blog,
        }
        return calculate_category_score(constants, tallies)

    def calculate_combination_percentage(self, cec, tes):
        score = cec
        return calculate_percentage(score, tes)


class Internalization(models.Model):
    used_in_app_browser = models.DecimalField(
        default=0.00000, decimal_places=5, max_digits=9, validators=[MinValueValidator(0.00000)]
    )
    read_blog = models.DecimalField(
        default=0.00000, decimal_places=5, max_digits=9, validators=[MinValueValidator(0.00000)]
    )
    read_forum = models.DecimalField(
        default=0.00000, decimal_places=5, max_digits=9, validators=[MinValueValidator(0.00000)]
    )
    recieve_chat_message = models.DecimalField(
        default=0.00000, decimal_places=5, max_digits=9, validators=[MinValueValidator(0.00000)]
    )
    download_resources = models.DecimalField(
        default=0.00000, decimal_places=5, max_digits=9, validators=[MinValueValidator(0.00000)]
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
