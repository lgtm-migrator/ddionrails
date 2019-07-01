# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use

import json
import time
from pathlib import Path

import pytest
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

from ddionrails.concepts.models import (
    AnalysisUnit,
    Concept,
    ConceptualDataset,
    Period,
    Topic,
)
from ddionrails.data.models import Dataset, Transformation, Variable
from ddionrails.imports.manager import StudyImportManager
from ddionrails.instruments.models import (
    ConceptQuestion,
    Instrument,
    Question,
    QuestionVariable,
)
from ddionrails.publications.models import Attachment, Publication
from ddionrails.studies.models import Study, TopicList
from tests.data.factories import VariableFactory

pytestmark = [pytest.mark.functional]  # pylint: disable=invalid-name


@pytest.fixture()
def elasticsearch_client(settings):
    mapping_file = "ddionrails/elastic/mapping.json"
    with open(mapping_file, "r") as infile:
        mapping = json.loads(infile.read())
    elasticsearch_client = Elasticsearch(hosts=[settings.INDEX_HOST])
    # workaround to delete existing index

    # settings.INDEX_NAME = "testing"

    elasticsearch_client.indices.delete(index=settings.INDEX_NAME, ignore=[400, 404])
    elasticsearch_client.indices.create(
        index=settings.INDEX_NAME, ignore=400, body=mapping
    )

    # wait for elastic search index to be created
    time.sleep(0.1)
    yield elasticsearch_client
    elasticsearch_client.indices.delete(index=settings.INDEX_NAME, ignore=[400, 404])


@pytest.fixture
def study_import_manager(study, settings):
    settings.IMPORT_REPO_PATH = Path("tests/functional/test_data/")
    manager = StudyImportManager(study)
    return manager


class TestStudyImportManager:
    def test_import_study(
        self, study_import_manager, elasticsearch_client
    ):  # pylint: disable=unused-argument
        study_import_manager.import_single_entity("study")
        # wait for indexing to complete
        time.sleep(1)
        assert 1 == Study.objects.count()
        # refresh
        study = Study.objects.first()
        assert "Some Study" == study.label
        assert {"variables": {"label-table": True}} == study.config

    def test_import_csv_topics(self, study_import_manager):
        assert 0 == Topic.objects.count()
        study_import_manager.import_single_entity("topics.csv")
        assert 2 == Topic.objects.count()
        topic = Topic.objects.get(name="some-topic")
        parent_topic = Topic.objects.get(name="some-other-topic")
        assert "some-topic" == topic.label
        assert parent_topic == topic.parent
        assert "some-other-topic" == parent_topic.label

    def test_import_json_topics(
        self, study_import_manager, elasticsearch_client
    ):  # pylint: disable=unused-argument
        assert 1 == Study.objects.count()
        assert 0 == Topic.objects.count()
        assert 0 == TopicList.objects.count()
        study_import_manager.import_single_entity("study")
        time.sleep(1)
        study_import_manager.import_single_entity("topics.json")
        assert 1 == Study.objects.count()
        assert 1 == TopicList.objects.count()
        study = Study.objects.first()
        topiclist = TopicList.objects.first()
        assert study == topiclist.study
        english_topics = topiclist.topiclist[0]
        assert "en" == english_topics["language"]
        german_topics = topiclist.topiclist[1]
        assert "de" == german_topics["language"]

    def test_import_concepts(self, study_import_manager, elasticsearch_client, topic):
        assert 0 == Concept.objects.count()
        study_import_manager.import_single_entity("concepts")
        assert 1 == Concept.objects.count()
        concept = Concept.objects.first()
        assert "some-concept" == concept.name
        assert "Some concept" == concept.label
        assert topic == concept.topics.first()

        concept.index()
        # wait for indexing to complete
        time.sleep(1)
        search = Search(using=elasticsearch_client).doc_type("concept")
        assert 1 == search.count()
        response = search.execute()
        hit = response.hits[0]
        assert "some-concept" == hit.name

    def test_import_analysis_units(self, study_import_manager):
        assert 0 == AnalysisUnit.objects.count()
        study_import_manager.import_single_entity("analysis_units")
        assert 1 == AnalysisUnit.objects.count()
        analysis_unit = AnalysisUnit.objects.first()
        assert "some-analysis-unit" == analysis_unit.name
        assert "some-analysis-unit" == analysis_unit.label
        assert "some-analysis-unit" == analysis_unit.description

    def test_import_periods(self, study_import_manager, study):
        assert 0 == Period.objects.count()
        study_import_manager.import_single_entity("periods")
        assert 1 == Period.objects.count()
        period = Period.objects.first()
        assert "some-period" == period.name
        assert "some-period" == period.label
        assert study == period.study

    def test_import_conceptual_datasets(self, study_import_manager):
        assert 0 == ConceptualDataset.objects.count()
        study_import_manager.import_single_entity("conceptual_datasets")
        assert 1 == ConceptualDataset.objects.count()
        conceptual_dataset = ConceptualDataset.objects.first()
        assert "some-conceptual-dataset" == conceptual_dataset.name
        assert "some-conceptual-dataset" == conceptual_dataset.label
        assert "some-conceptual-dataset" == conceptual_dataset.description

    def test_import_instruments(
        self, study_import_manager, elasticsearch_client, study, period
    ):
        assert 0 == Instrument.objects.count()
        assert 0 == Question.objects.count()
        study_import_manager.import_single_entity("instruments")
        # wait for indexing to complete
        time.sleep(1)
        assert 1 == Instrument.objects.count()
        assert 1 == Question.objects.count()
        instrument = Instrument.objects.first()
        assert "some-instrument" == instrument.name
        assert study == instrument.study
        assert period == instrument.period

        search = Search(using=elasticsearch_client).doc_type("question")
        assert 1 == search.count()
        response = search.execute()
        hit = response.hits[0]
        assert study.name == hit.study
        assert "some-question" == hit.name
        assert "some-instrument" == hit.instrument

    def test_import_json_datasets(
        self, study_import_manager, elasticsearch_client, study
    ):
        assert 0 == Dataset.objects.count()
        assert 0 == Variable.objects.count()
        study_import_manager.import_single_entity("datasets.json")
        # wait for indexing to complete
        time.sleep(1)
        assert 1 == Dataset.objects.count()
        assert 2 == Variable.objects.count()
        dataset = Dataset.objects.first()
        variable = Variable.objects.first()
        assert "some-dataset" == dataset.name
        assert study == dataset.study
        assert "some-variable" == variable.name

        search = Search(using=elasticsearch_client).doc_type("variable")
        assert 2 == search.count()

    def test_import_csv_datasets(
        self, study_import_manager, dataset, period, analysis_unit, conceptual_dataset
    ):
        study_import_manager.import_single_entity("datasets.csv")
        assert 1 == Dataset.objects.count()
        dataset = Dataset.objects.first()
        assert "some-dataset" == dataset.label
        assert "some-dataset" == dataset.description
        assert analysis_unit == dataset.analysis_unit
        assert period == dataset.period
        assert conceptual_dataset == dataset.conceptual_dataset

    def test_import_variables(self, study_import_manager, variable, concept):
        assert 1 == Variable.objects.count()
        study_import_manager.import_single_entity("variables")
        assert 1 == Variable.objects.count()
        variable = Variable.objects.first()
        assert "https://variable-image.de" == variable.image_url
        assert concept == variable.concept

    def test_import_questions_variables(self, study_import_manager, variable, question):
        assert 0 == QuestionVariable.objects.count()
        study_import_manager.import_single_entity("questions_variables")
        assert 1 == QuestionVariable.objects.count()
        relation = QuestionVariable.objects.first()
        assert variable == relation.variable
        assert question == relation.question

    def test_import_concepts_questions(self, study_import_manager, concept, question):
        assert 0 == ConceptQuestion.objects.count()
        study_import_manager.import_single_entity("concepts_questions")
        assert 1 == ConceptQuestion.objects.count()
        relation = ConceptQuestion.objects.first()
        assert concept == relation.concept
        assert question == relation.question

    def test_import_transformations(self, study_import_manager, variable):
        assert 0 == Transformation.objects.count()
        other_variable = VariableFactory(name="some-other-variable")
        study_import_manager.import_single_entity("transformations")
        assert 1 == Transformation.objects.count()
        relation = Transformation.objects.first()
        assert variable == relation.origin
        assert other_variable == relation.target

    def test_import_attachments(self, study_import_manager, study):
        assert 0 == Attachment.objects.count()
        study_import_manager.import_single_entity("attachments")
        assert 1 == Attachment.objects.count()
        attachment = Attachment.objects.first()
        assert study == attachment.context_study
        assert "https://some-study.de" == attachment.url
        assert "some-study" == attachment.url_text

    def test_import_publications(self, study_import_manager, elasticsearch_client, study):
        assert 0 == Publication.objects.count()
        study_import_manager.import_single_entity("publications")
        # wait for indexing to complete
        time.sleep(1)

        assert 1 == Publication.objects.count()
        publication = Publication.objects.first()
        assert "Some Publication" == publication.title
        assert "some-doi" == publication.doi
        assert study == publication.study
        search = Search(using=elasticsearch_client).doc_type("publication")
        assert 1 == search.count()
        response = search.execute()
        hit = response.hits[0]
        assert study.name == hit.study
        assert "some-doi" == hit.doi
        assert "2018" == hit.year

    def test_import_all(self, study_import_manager, elasticsearch_client):
        assert 1 == Study.objects.count()

        assert 0 == Concept.objects.count()
        assert 0 == ConceptualDataset.objects.count()
        assert 0 == Dataset.objects.count()
        assert 0 == Variable.objects.count()
        assert 0 == Period.objects.count()
        assert 0 == Publication.objects.count()
        assert 0 == Question.objects.count()
        assert 0 == Transformation.objects.count()
        assert 0 == Instrument.objects.count()
        assert 0 == QuestionVariable.objects.count()
        assert 0 == ConceptQuestion.objects.count()

        study_import_manager.import_all_entities()
        time.sleep(1)

        assert 1 == Concept.objects.count()
        assert 1 == ConceptualDataset.objects.count()
        assert 1 == Dataset.objects.count()
        assert 2 == Variable.objects.count()
        assert 1 == Period.objects.count()
        assert 1 == Publication.objects.count()
        assert 1 == Question.objects.count()
        assert 1 == Transformation.objects.count()
        assert 1 == Instrument.objects.count()
        assert 1 == QuestionVariable.objects.count()
        assert 1 == ConceptQuestion.objects.count()

        # Concepts will be indexed when mgmt command "upgrade" is called
        # s = Search(using=elasticsearch_client).doc_type("concept")
        # assert 1 == s.count()
        assert Search(using=elasticsearch_client).doc_type("variable").count() == 2
        assert Search(using=elasticsearch_client).doc_type("publication").count() == 1
