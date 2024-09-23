# Generated by Django 5.0.6 on 2024-09-19 14:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("forum", "0011_alter_commentreplies_score_alter_forum_score_and_more"),
        ("topics", "0003_alter_blogtopic_blog"),
    ]

    operations = [
        migrations.AlterField(
            model_name="forumtopic",
            name="forum",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="topics",
                to="forum.forum",
            ),
        ),
    ]
