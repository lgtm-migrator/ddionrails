# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods,invalid-name

# We subscribe to the conventional ordering of (expected, result) in tests.
# Meaning, if possible, the expected value come first in a comparison.
# Pylint wants constants in a comparison to be at the end.
# To allow testing against contants we disable misplaced-comparison-constant.
# Another solution for this would be to use unittest assert functions, since they
# are not treated as comparisons(obviously, they are function calls) by pylint.
# pylint: disable=misplaced-comparison-constant

""" Test cases for ddionrails.publications.resources """

import unittest
from io import BytesIO

import pytest
import requests_mock
import tablib

from ddionrails.concepts.models import AnalysisUnit, Concept, Period
from ddionrails.data.models import Variable
from ddionrails.instruments.models import (
    ConceptQuestion,
    Instrument,
    Question,
    QuestionImage,
    QuestionVariable,
)
from ddionrails.instruments.resources import (
    ConceptQuestionResource,
    InstrumentResource,
    QuestionImageResource,
    QuestionResource,
    QuestionVariableResource,
)
from ddionrails.studies.models import Study

pytestmark = [pytest.mark.django_db, pytest.mark.resources]


@pytest.fixture(name="instrument_tablib_dataset")
def _instrument_tablib_dataset():
    """ A tablib.Dataset containing an instrument """

    headers = ("study", "name", "label", "label_de", "period", "analysis_unit")
    study = "some-study"
    instrument = "some-instrument"
    label = "some-instrument"
    label_de = "some-instrument"
    period = "some-period"
    analysis_unit = "some-analysis-unit"
    values = (study, instrument, label, label_de, period, analysis_unit)
    return tablib.Dataset(values, headers=headers)


@pytest.fixture(name="question_tablib_dataset")
def _question_tablib_dataset():
    """ A tablib.Dataset containing an question """

    headers = (
        "study",
        "instrument",
        "name",
        "label",
        "label_de",
        "description",
        "sort_id",
        "items",
    )
    study = "some-study"
    instrument = "some-instrument"
    name = "some-question"
    label = "some-question"
    label_de = "some-question"
    description = "some-question"
    sort_id = 1
    items = []
    values = (study, instrument, name, label, label_de, description, sort_id, items)
    return tablib.Dataset(values, headers=headers)


@pytest.fixture(name="concept_question_tablib_dataset")
def _concept_question_tablib_dataset():
    """ A tablib.Dataset containing a concept_question """

    headers = ("study_name", "instrument_name", "question_name", "concept_name")
    study_name = "some-study"
    instrument_name = "some-instrument"
    question_name = "some-question"
    concept_name = "some-concept"

    values = (study_name, instrument_name, question_name, concept_name)
    return tablib.Dataset(values, headers=headers)


@pytest.fixture(name="question_variable_tablib_dataset")
def _question_variable_tablib_dataset():
    """ A tablib.Dataset containing a question_variable """

    headers = (
        "study_name",
        "dataset_name",
        "variable_name",
        "instrument_name",
        "question_name",
    )
    study_name = "some-study"
    dataset_name = "some-dataset"
    variable_name = "some-variable"
    instrument_name = "some-instrument"
    question_name = "some-question"

    values = (study_name, dataset_name, variable_name, instrument_name, question_name)
    return tablib.Dataset(values, headers=headers)


class TestInstrumentResource:
    def test_resource_import_succeeds(
        self, study, period, analysis_unit, instrument_tablib_dataset
    ):
        assert 0 == Instrument.objects.count()
        assert 1 == Study.objects.count()
        assert 1 == Period.objects.count()
        assert 1 == AnalysisUnit.objects.count()
        result = InstrumentResource().import_data(instrument_tablib_dataset)
        assert False is result.has_errors()
        assert 1 == Instrument.objects.count()

        instrument = Instrument.objects.first()

        # test attributes
        name = instrument_tablib_dataset["name"][0]
        label = instrument_tablib_dataset["label"][0]

        assert name == instrument.name
        assert label == instrument.label

        # test relations
        assert study == instrument.study
        assert period == instrument.period
        assert analysis_unit == instrument.analysis_unit


class TestQuestionResource:
    def test_resource_import_succeeds(self, instrument, question_tablib_dataset):
        assert 0 == Question.objects.count()
        assert 1 == Study.objects.count()
        assert 1 == Instrument.objects.count()

        result = QuestionResource().import_data(question_tablib_dataset)
        assert False is result.has_errors()
        assert 1 == Question.objects.count()
        question = Question.objects.first()

        # test attributes
        name = question_tablib_dataset["name"][0]
        label = question_tablib_dataset["label"][0]
        label_de = question_tablib_dataset["label_de"][0]
        description = question_tablib_dataset["description"][0]
        sort_id = question_tablib_dataset["sort_id"][0]
        items = question_tablib_dataset["items"][0]

        assert name == question.name
        assert label == question.label
        assert label_de == question.label_de
        assert description == question.description
        assert sort_id == question.sort_id
        assert items == question.items

        # test relations
        assert instrument == question.instrument


class TestConceptQuestionResource:
    def test_resource_import_succeeds(
        self, concept, question, concept_question_tablib_dataset
    ):
        assert 0 == ConceptQuestion.objects.count()
        assert 1 == Concept.objects.count()
        assert 1 == Question.objects.count()
        result = ConceptQuestionResource().import_data(concept_question_tablib_dataset)
        assert False is result.has_errors()
        assert 1 == ConceptQuestion.objects.count()

        concept_question = ConceptQuestion.objects.first()
        # test relations
        assert concept == concept_question.concept
        assert question == concept_question.question


class TestQuestionVariableResource:
    def test_resource_import_succeeds(
        self, question, variable, question_variable_tablib_dataset
    ):
        assert 0 == QuestionVariable.objects.count()
        assert 1 == Variable.objects.count()
        assert 1 == Question.objects.count()
        result = QuestionVariableResource().import_data(question_variable_tablib_dataset)

        assert False is result.has_errors()
        assert 1 == QuestionVariable.objects.count()

        question_variable = QuestionVariable.objects.first()

        # test relations
        assert variable == question_variable.variable
        assert question == question_variable.question


@pytest.mark.django_db
@pytest.mark.usefixtures("variable_image_file", "question_image_dataset")
class TestQuestionImageResource(unittest.TestCase):

    variable_image_file = lambda file_type, size=1: BytesIO()
    question_image_dataset = tablib.Dataset()

    def test_import(self):
        url = {
            "en": self.question_image_dataset["url"][0],
            "de": self.question_image_dataset["url_de"][0],
        }
        image = {
            "en": self.variable_image_file("png", 1).getvalue(),
            "de": self.variable_image_file("png", 2).getvalue(),
        }
        _ressource = QuestionImageResource()
        with requests_mock.mock() as mocked_request:
            mocked_request.get(url["en"], content=image["en"])
            mocked_request.get(url["de"], content=image["de"])
            _ressource.import_data(self.question_image_dataset, raise_errors=True)

        result_image, image_created = QuestionImage.objects.get_or_create(
            label=self.question_image_dataset["label"][0]
        )
        self.assertFalse(image_created)
        self.assertEqual(
            image[result_image.language], result_image.image.file.open().read()
        )
        result_image.image.file.close()