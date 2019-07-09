# -*- coding: utf-8 -*-

""" URLConf for ddionrails.api app """

from django.urls import path

from ddionrails.data.views import variable_preview_id
from ddionrails.instruments.views import question_comparison_partial

from .views import (
    add_variable_by_id,
    add_variables_by_concept,
    add_variables_by_topic,
    baskets_by_study_and_user,
    concept_by_study,
    object_redirect,
    test_preview,
    topic_by_study,
    topic_list,
)

app_name = "api"

urlpatterns = [
    path(
        "test/preview/variable/<uuid:variable_id>",
        variable_preview_id,
        name="variable_preview",
    ),
    path(
        "test/preview/<str:object_type>/<uuid:object_id>",
        test_preview,
        name="test_preview",
    ),
    path(
        "questions/compare/<uuid:from_id>/<uuid:to_id>",
        question_comparison_partial,
        name="question_comparison_partial",
    ),
    path(
        "test/redirect/<str:object_type>/<uuid:object_id>",
        object_redirect,
        name="object_redirect",
    ),
    path("topics/<str:study_name>/<str:language>", topic_list, name="topic_list"),
    path(
        "topics/<str:study_name>/<str:language>/concept_<str:concept_name>",
        concept_by_study,
        name="concept_by_study",
    ),
    path(
        "topics/<str:study_name>/<str:language>/topic_<str:topic_name>",
        topic_by_study,
        name="topic_by_study",
    ),
    path(
        "topics/<str:study_name>/<str:language>/baskets",
        baskets_by_study_and_user,
        name="baskets_by_study_and_user",
    ),
    path(
        "topics/<str:study_name>/<str:language>/concept_<str:concept_name>/add_to_basket/<int:basket_id>",
        add_variables_by_concept,
        name="add_variables_by_concept",
    ),
    path(
        "topics/<str:study_name>/<str:language>/topic_<str:topic_name>/add_to_basket/<int:basket_id>",
        add_variables_by_topic,
        name="add_variables_by_topic",
    ),
    path(
        "topics/<str:study_name>/<str:language>/variable_<uuid:variable_id>/add_to_basket/<int:basket_id>",
        add_variable_by_id,
        name="add_variable_by_id",
    ),
]
