# Generated by Django 4.1.7 on 2024-03-27 12:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0007_rename_platform_comment_platform"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="comment",
            name="platform",
        ),
    ]
