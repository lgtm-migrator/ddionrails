# Generated by Django 2.2.1 on 2019-05-22 09:01

import config.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("concepts", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="analysisunit",
            name="label_de",
            field=models.CharField(
                blank=True,
                help_text="Label of the analysis unit (German)",
                max_length=255,
                verbose_name="Label (German)",
            ),
        ),
        migrations.AddField(
            model_name="concept",
            name="label_de",
            field=models.CharField(
                blank=True,
                help_text="Label of the concept (German)",
                max_length=255,
                verbose_name="Label (German)",
            ),
        ),
        migrations.AddField(
            model_name="conceptualdataset",
            name="label_de",
            field=models.CharField(
                blank=True,
                help_text="Label of the conceptual dataset (German)",
                max_length=255,
                verbose_name="Label (German)",
            ),
        ),
        migrations.AddField(
            model_name="topic",
            name="label_de",
            field=models.CharField(
                blank=True,
                help_text="Label of the topic (German)",
                max_length=255,
                verbose_name="Label (German)",
            ),
        ),
        migrations.AlterField(
            model_name="analysisunit",
            name="description",
            field=models.TextField(
                blank=True,
                help_text="Description of the analysis unit (Markdown)",
                verbose_name="Description (Markdown)",
            ),
        ),
        migrations.AlterField(
            model_name="analysisunit",
            name="label",
            field=models.CharField(
                blank=True,
                help_text="Label of the analysis unit (English)",
                max_length=255,
                verbose_name="Label (English)",
            ),
        ),
        migrations.AlterField(
            model_name="analysisunit",
            name="name",
            field=models.CharField(
                help_text="Name of the analysis unit (Lowercase)",
                max_length=255,
                unique=True,
                validators=[config.validators.validate_lowercase],
            ),
        ),
        migrations.AlterField(
            model_name="concept",
            name="description",
            field=models.TextField(
                blank=True,
                help_text="Description of the concept (Markdown)",
                verbose_name="Description (Markdown)",
            ),
        ),
        migrations.AlterField(
            model_name="concept",
            name="label",
            field=models.CharField(
                blank=True,
                help_text="Label of the concept (English)",
                max_length=255,
                verbose_name="Label (English)",
            ),
        ),
        migrations.AlterField(
            model_name="concept",
            name="name",
            field=models.CharField(
                db_index=True,
                help_text="Name of the concept (Lowercase)",
                max_length=255,
                unique=True,
                validators=[config.validators.validate_lowercase],
                verbose_name="concept name",
            ),
        ),
        migrations.AlterField(
            model_name="concept",
            name="topics",
            field=models.ManyToManyField(
                help_text="ManyToMany relation to concepts.Topic",
                related_name="concepts",
                to="concepts.Topic",
            ),
        ),
        migrations.AlterField(
            model_name="conceptualdataset",
            name="description",
            field=models.TextField(
                blank=True,
                help_text="Description of the conceptual dataset (Markdown)",
                verbose_name="Description (Markdown)",
            ),
        ),
        migrations.AlterField(
            model_name="conceptualdataset",
            name="label",
            field=models.CharField(
                blank=True,
                help_text="Label of the conceptual dataset (English)",
                max_length=255,
                verbose_name="Label (English)",
            ),
        ),
        migrations.AlterField(
            model_name="conceptualdataset",
            name="name",
            field=models.CharField(
                help_text="Name of the conceptual dataset (Lowercase)",
                max_length=255,
                unique=True,
                validators=[config.validators.validate_lowercase],
            ),
        ),
        migrations.AlterField(
            model_name="period",
            name="definition",
            field=models.CharField(
                blank=True, help_text="Definition of the period", max_length=255
            ),
        ),
        migrations.AlterField(
            model_name="period",
            name="description",
            field=models.TextField(
                blank=True,
                help_text="Description of the period (Markdown)",
                verbose_name="Description (Markdown)",
            ),
        ),
        migrations.AlterField(
            model_name="period",
            name="label",
            field=models.CharField(
                blank=True,
                help_text="Label of the period (English)",
                max_length=255,
                verbose_name="Label (English)",
            ),
        ),
        migrations.AlterField(
            model_name="period",
            name="name",
            field=models.CharField(
                help_text="Name of the period (Lowercase)",
                max_length=255,
                validators=[config.validators.validate_lowercase],
            ),
        ),
        migrations.AlterField(
            model_name="period",
            name="study",
            field=models.ForeignKey(
                help_text="Foreign key to studies.Study",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="periods",
                to="studies.Study",
            ),
        ),
        migrations.AlterField(
            model_name="topic",
            name="description",
            field=models.TextField(
                blank=True,
                help_text="Description of the topic (Markdown)",
                verbose_name="Description (Markdown)",
            ),
        ),
        migrations.AlterField(
            model_name="topic",
            name="label",
            field=models.CharField(
                blank=True,
                help_text="Label of the topic (English)",
                max_length=255,
                verbose_name="Label (English)",
            ),
        ),
        migrations.AlterField(
            model_name="topic",
            name="name",
            field=models.CharField(
                help_text="Name of the topic (Lowercase)",
                max_length=255,
                unique=True,
                validators=[config.validators.validate_lowercase],
            ),
        ),
        migrations.AlterField(
            model_name="topic",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                help_text="Foreign key to concepts.Topic",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="children",
                to="concepts.Topic",
                verbose_name="Parent (concepts.Topic)",
            ),
        ),
        migrations.AlterField(
            model_name="topic",
            name="study",
            field=models.ForeignKey(
                help_text="Foreign key to studies.Study",
                on_delete=django.db.models.deletion.CASCADE,
                to="studies.Study",
            ),
        ),
    ]