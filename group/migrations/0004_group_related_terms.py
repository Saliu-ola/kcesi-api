# Generated by Django 4.1.7 on 2024-04-22 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("group", "0003_usergroup_unique_user_per_group"),
    ]

    operations = [
        migrations.AddField(
            model_name="group",
            name="related_terms",
            field=models.JSONField(blank=True, null=True),
        ),
    ]
