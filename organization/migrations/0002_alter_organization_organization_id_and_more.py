# Generated by Django 4.1.7 on 2024-01-25 07:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("organization", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="organization",
            name="organization_id",
            field=models.CharField(max_length=15, null=True, unique=True),
        ),
        migrations.AddConstraint(
            model_name="organization",
            constraint=models.UniqueConstraint(
                fields=("organization_id",),
                name="unique_organization_id_per_organization",
            ),
        ),
    ]