# Generated by Django 4.1.7 on 2024-01-03 11:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("group", "0001_initial"),
        ("resource", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="resources",
            name="group",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="group_resources",
                to="group.group",
            ),
        ),
    ]
