# Generated by Django 5.0.6 on 2024-09-19 14:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0010_alter_blog_score_alter_blogcommentreplies_score_and_more"),
        ("topics", "0002_blogtopic_forumtopic"),
    ]

    operations = [
        migrations.AlterField(
            model_name="blogtopic",
            name="blog",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="topics",
                to="blog.blog",
            ),
        ),
    ]
