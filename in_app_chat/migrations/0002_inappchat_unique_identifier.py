# Generated by Django 4.1.7 on 2024-02-21 20:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("in_app_chat", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="inappchat",
            name="unique_identifier",
            field=models.CharField(max_length=255, null=True),
        ),
    ]
