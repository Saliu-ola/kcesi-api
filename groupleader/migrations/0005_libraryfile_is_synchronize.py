# Generated by Django 5.0.6 on 2024-06-14 09:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("groupleader", "0004_alter_libraryfile_status_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="libraryfile",
            name="is_synchronize",
            field=models.BooleanField(default=False),
        ),
    ]
