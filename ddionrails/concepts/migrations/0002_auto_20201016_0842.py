# Generated by Django 3.1.2 on 2020-10-16 08:42
# pylint: disable=all

from django.db import migrations, models

import config.validators


class Migration(migrations.Migration):

    dependencies = [("concepts", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="topic",
            name="name",
            field=models.CharField(
                help_text="Name of the topic (Lowercase)",
                max_length=255,
                validators=[config.validators.validate_lowercase],
            ),
        )
    ]