# Generated by Django 2.2 on 2019-04-09 07:58

import django.db.models.deletion
from django.db import migrations, models

import config.validators
import ddionrails.base.mixins
import ddionrails.elastic.mixins


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("data", "0001_initial"),
        ("concepts", "0001_initial"),
        ("studies", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Instrument",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        db_index=True,
                        max_length=255,
                        validators=[config.validators.validate_lowercase],
                    ),
                ),
                ("label", models.CharField(blank=True, max_length=255)),
                ("description", models.TextField(blank=True)),
                (
                    "analysis_unit",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="instruments",
                        to="concepts.AnalysisUnit",
                    ),
                ),
                (
                    "period",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="instruments",
                        to="concepts.Period",
                    ),
                ),
                (
                    "study",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="instruments",
                        to="studies.Study",
                    ),
                ),
            ],
            options={
                "ordering": ("study", "name"),
                "unique_together": {("study", "name")},
            },
            bases=(
                ddionrails.elastic.mixins.ModelMixin,
                ddionrails.base.mixins.ModelMixin,
                models.Model,
            ),
        ),
        migrations.CreateModel(
            name="Question",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        db_index=True,
                        max_length=255,
                        validators=[config.validators.validate_lowercase],
                    ),
                ),
                ("label", models.CharField(blank=True, max_length=255)),
                ("label_de", models.CharField(blank=True, max_length=255)),
                ("description", models.TextField(blank=True)),
                ("sort_id", models.IntegerField(blank=True, null=True)),
                (
                    "instrument",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="questions",
                        to="instruments.Instrument",
                    ),
                ),
            ],
            options={"unique_together": {("instrument", "name")}},
            bases=(
                ddionrails.elastic.mixins.ModelMixin,
                ddionrails.base.mixins.ModelMixin,
                models.Model,
            ),
        ),
        migrations.CreateModel(
            name="QuestionVariable",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="questions_variables",
                        to="instruments.Question",
                    ),
                ),
                (
                    "variable",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="questions_variables",
                        to="data.Variable",
                    ),
                ),
            ],
            options={"unique_together": {("question", "variable")}},
        ),
        migrations.CreateModel(
            name="ConceptQuestion",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "concept",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="concepts_questions",
                        to="concepts.Concept",
                    ),
                ),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="concepts_questions",
                        to="instruments.Question",
                    ),
                ),
            ],
            options={"unique_together": {("question", "concept")}},
        ),
    ]