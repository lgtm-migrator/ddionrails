# Generated by Django 2.2.1 on 2019-05-28 09:22

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import config.validators


class Migration(migrations.Migration):

    dependencies = [("workspace", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="basket",
            name="description",
            field=models.TextField(
                blank=True,
                help_text="Description of the basket (Markdown)",
                verbose_name="Description (Markdown)",
            ),
        ),
        migrations.AlterField(
            model_name="basket",
            name="label",
            field=models.CharField(
                blank=True,
                help_text="Label of the basket",
                max_length=255,
                verbose_name="Label",
            ),
        ),
        migrations.AlterField(
            model_name="basket",
            name="name",
            field=models.CharField(
                help_text="Name of the basket (Lowercase)",
                max_length=255,
                validators=[config.validators.validate_lowercase],
            ),
        ),
        migrations.AlterField(
            model_name="basket",
            name="study",
            field=models.ForeignKey(
                help_text="Foreign key to studies.Study",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="baskets",
                to="studies.Study",
            ),
        ),
        migrations.AlterField(
            model_name="basket",
            name="user",
            field=models.ForeignKey(
                help_text="Foreign key to auth.User",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="baskets",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="basket",
            name="variables",
            field=models.ManyToManyField(
                help_text="ManyToMany relation to data.Variable",
                through="workspace.BasketVariable",
                to="data.Variable",
            ),
        ),
        migrations.AlterField(
            model_name="basketvariable",
            name="basket",
            field=models.ForeignKey(
                help_text="Foreign key to workspace.Basket",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="baskets_variables",
                to="workspace.Basket",
            ),
        ),
        migrations.AlterField(
            model_name="basketvariable",
            name="variable",
            field=models.ForeignKey(
                help_text="Foreign key to data.Variable",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="baskets_variables",
                to="data.Variable",
            ),
        ),
        migrations.AlterField(
            model_name="script",
            name="basket",
            field=models.ForeignKey(
                help_text="Foreign key to workspace.Basket",
                on_delete=django.db.models.deletion.CASCADE,
                to="workspace.Basket",
            ),
        ),
        migrations.AlterField(
            model_name="script",
            name="generator_name",
            field=models.CharField(
                default="soep-stata",
                help_text="Name of the selected Script generator (e.g. soep-stata)",
                max_length=255,
            ),
        ),
        migrations.AlterField(
            model_name="script",
            name="label",
            field=models.CharField(
                blank=True, help_text="Label of the script", max_length=255
            ),
        ),
        migrations.AlterField(
            model_name="script",
            name="name",
            field=models.CharField(help_text="Name of the script", max_length=255),
        ),
        migrations.AlterField(
            model_name="script",
            name="settings",
            field=models.TextField(help_text="Settings of the script"),
        ),
    ]
