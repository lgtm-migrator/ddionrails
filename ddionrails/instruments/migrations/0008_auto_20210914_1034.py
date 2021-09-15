# pylint: disable=all
# Generated by Django 3.2.6 on 2021-09-14 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("instruments", "0007_auto_20210914_1028")]

    operations = [
        migrations.AddField(
            model_name="question",
            name="instruction_de",
            field=models.TextField(
                blank=True,
                help_text="Optional german question instruction.",
                verbose_name="Instruction German",
            ),
        ),
        migrations.AlterField(
            model_name="question",
            name="instruction",
            field=models.TextField(
                blank=True,
                help_text="Optional question instruction.",
                verbose_name="Instruction",
            ),
        ),
    ]