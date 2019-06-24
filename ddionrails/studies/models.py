# -*- coding: utf-8 -*-
""" Model definitions for ddionrails.studies app """

import os
from typing import List, Optional

from django.conf import settings
from django.contrib.postgres.fields import ArrayField, JSONField
from django.contrib.postgres.fields.jsonb import JSONField as JSONBField
from django.db import models
from django.urls import reverse
from model_utils.models import TimeStampedModel

from ddionrails.base.mixins import ModelMixin


class TopicList(models.Model):

    # attributes
    topiclist = JSONBField(
        default=list,
        null=True,
        blank=True,
        help_text="Topics of the related study (JSON)",
    )

    # relations
    study = models.OneToOneField(
        "Study",
        blank=True,
        null=True,
        related_name="topiclist",
        on_delete=models.CASCADE,
        help_text="OneToOneField to studies.Study",
    )


class Study(ModelMixin, TimeStampedModel):
    """
    Stores a single study,
    related to :model:`data.Dataset`, :model:`instruments.Instrument`,
    :model:`concepts.Period` and :model:`workspace.Basket`.
    """

    # attributes
    name = models.CharField(
        max_length=255, unique=True, db_index=True, help_text="Name of the study"
    )
    label = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Label (English)",
        help_text="Label of the study (English)",
    )
    label_de = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Label (German)",
        help_text="Label of the study (German)",
    )
    description = models.TextField(
        blank=True, help_text="Description of the study (Markdown)"
    )
    repo = models.CharField(
        max_length=255,
        blank=True,
        help_text="Reference to the Git repository without definition of the protocol (e.g. https)",
    )
    current_commit = models.CharField(
        max_length=255,
        blank=True,
        help_text="Commit hash of the last metadata import. This field is automatically filled by DDI on Rails",
    )
    config = JSONField(
        default=dict, blank=True, null=True, help_text="Configuration of the study (JSON)"
    )

    topic_languages = ArrayField(
        models.CharField(max_length=200),
        blank=True,
        default=list,
        help_text="Topic languages of the study (Array)",
    )

    class Meta:  # pylint: disable=too-few-public-methods
        """ Django's metadata options """

        verbose_name_plural = "Studies"

    class DOR:  # pylint: disable=too-few-public-methods
        """ ddionrails' metadata options """

        io_fields = ["name", "label", "description"]
        id_fields = ["name"]

    def __str__(self) -> str:
        """ Returns a string representation using the "name" field """
        return f"/{self.name}"

    def get_absolute_url(self) -> str:
        """ Returns a canonical URL for the model using the "name" field """
        return reverse("study_detail", kwargs={"study_name": self.name})

    def import_path(self):
        path = os.path.join(
            settings.IMPORT_REPO_PATH, self.name, settings.IMPORT_SUB_DIRECTORY
        )
        return path

    def repo_url(self) -> str:
        if settings.GIT_PROTOCOL == "https":
            return f"https://{self.repo}.git"
        elif settings.GIT_PROTOCOL == "ssh":
            return f"git@{self.repo}.git"
        else:
            raise Exception("Specify a protocol for Git in your settings.")

    def set_topiclist(self, body: List) -> None:
        _topiclist, _ = TopicList.objects.get_or_create(study=self)
        _topiclist.topiclist = body
        _topiclist.save()

    def has_topics(self) -> bool:
        """ Returns True if the study has topics False otherwise (evaluates the length of self.topic_languages) """
        return len(self.topic_languages) > 0

    def get_topiclist(self, language: str = "en") -> Optional[List]:
        """ Returns the list of topics for a given language or None """
        try:
            for topiclist in self.topiclist.topiclist:
                if topiclist.get("language", "") == language:
                    return topiclist.get("topics")
        except TopicList.DoesNotExist:
            return None


def context(request):
    return dict(all_studies=Study.objects.all().only("name", "label", "description"))
