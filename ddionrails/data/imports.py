# -*- coding: utf-8 -*-

""" Importer classes for ddionrails.data app """

import json
from collections import OrderedDict
from csv import DictReader
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Tuple, Union

from django.db.transaction import atomic

from ddionrails.concepts.models import AnalysisUnit, Concept, ConceptualDataset, Period
from ddionrails.imports import imports
from ddionrails.studies.models import Study

from .forms import DatasetForm, VariableForm
from .models import Dataset, Transformation, Variable


class DatasetJsonImport(imports.Import):
    """Import Variable data from JSON files."""

    def execute_import(self):
        self.content = json.JSONDecoder(object_pairs_hook=OrderedDict).decode(
            self.content
        )
        self._import_dataset(self.name, self.content)

    def _import_dataset(self, name, content: Union[Dict, List]):
        dataset, _ = Dataset.objects.get_or_create(study=self.study, name=name)
        sort_id = 0
        if isinstance(content, dict):
            content = list(content.values())
        for var in content:
            self._import_variable(var, dataset, sort_id)
            sort_id += 1

    @staticmethod
    def _import_variable(var, dataset, sort_id):
        name = var.get("name", var.get("variable"))
        variable, _ = Variable.objects.get_or_create(name=name, dataset=dataset)
        variable.sort_id = sort_id
        variable.label = var.get("label", name)
        variable.label_de = var.get("label_de", name)
        if "statistics" in var:
            if "names" in var["statistics"]:
                statistics = dict(
                    zip(var["statistics"]["names"], var["statistics"]["values"])
                )
            else:
                statistics = var["statistics"]
            variable.statistics = statistics
        if "categories" in var:
            values = var["categories"].get("values")
            if values and len(values) > 0:
                variable.categories = var["categories"]
        variable.scale = var.get("scale", "")
        variable.save()


class DatasetImport(imports.CSVImport):
    """Import Dataset data"""

    class DOR:  # pylint: disable=missing-docstring,too-few-public-methods
        form = DatasetForm

    def import_element(self, element: OrderedDict):
        if "name" not in element.keys():
            element["name"] = element.get("dataset_name")

        self._import_dataset_links(element)

    def _import_dataset_links(self, element: OrderedDict):
        dataset, _ = Dataset.objects.get_or_create(
            study=self.study, name=element.get("name")
        )
        period_name = element.get("period", element.get("period_name", "none"))
        dataset.period = Period.objects.get_or_create(study=self.study, name=period_name)[
            0
        ]
        analysis_unit_name = element.get(
            "analysis_unit", element.get("analysis_unit_name", "none")
        )
        dataset.analysis_unit = AnalysisUnit.objects.get_or_create(
            study=self.study, name=analysis_unit_name
        )[0]
        conceptual_dataset = element.get(
            "conceptual_dataset", element.get("conceptual_dataset_name", "none")
        )
        dataset.conceptual_dataset = ConceptualDataset.objects.get_or_create(
            study=self.study, name=conceptual_dataset
        )[0]
        dataset.folder = element.get("folder", "")
        primary_key = element.get("primary_key", "").strip().split(" ")
        if "" in primary_key:
            primary_key.remove("")
        dataset.primary_key = primary_key
        dataset.label = element.get("label", "")
        dataset.description = element.get("description", "")
        dataset.save()


class VariableImport(imports.CSVImport):
    """Import Variable data from csv file."""

    class DOR:  # pylint: disable=missing-docstring,too-few-public-methods
        form = VariableForm

    def import_element(self, element):
        variable_metadata = element
        if "name" not in variable_metadata.keys():
            variable_metadata["name"] = variable_metadata.get("variable_name")

        # This basically dropped variables in "silence" when there was a problem.
        # Incomplete imports are highly undesirable.
        # The exceptions handling should remain here for a while till it is clear
        # what exceptions were actually meant to be handled here.
        try:
            self._import_variable(variable_metadata)
        except BaseException as error:
            variable = variable_metadata.get("name")
            dataset = variable_metadata.get("dataset", element.get("dataset_name"))
            raise type(error)(
                f'Failed to import variable "{variable}" from dataset "{dataset}"'
            )

    def execute_import(self):
        for row in self.content:
            self.import_element(row)

    def _import_variable(self, element):
        dataset = Dataset.objects.get(
            study=self.study, name=element.get("dataset", element.get("dataset_name"))
        )
        variable, _ = Variable.objects.get_or_create(
            dataset=dataset, dataset__study=self.study, name=element["name"]
        )
        concept_name = element.get("concept", element.get("concept_name", ""))
        if concept_name != "":
            concept = Concept.objects.get(name=concept_name)
            variable.concept = concept
        variable.description = element.get("description", "")
        variable.description_de = element.get("description_de", "")
        variable.description_long = element.get("description_long", "")
        variable.image_url = element.get("image_url", "")
        variable.statistics_type = element.get("type", "")
        variable.statistics_flag = element.get("statistics", "False") == "True"
        if not variable.label:
            variable.label = element.get("label", "")
        if not variable.label_de:
            variable.label_de = element.get("label_de", "")
        variable.save()


class TransformationImport(imports.CSVImport):
    """Import Object relations from the transformations.csv file."""

    class DOR:  # pylint: disable=missing-docstring,too-few-public-methods
        form = VariableForm

    @atomic
    def execute_import(self):
        return super().execute_import()

    def import_element(self, element):

        origin, target = self._get_origin_and_target(element)
        Transformation.objects.get_or_create(origin=origin, target=target)

    @classmethod
    def _get_origin_and_target(
        cls, metadata: Dict[str, str]
    ) -> Tuple[Variable, Variable]:
        origin, target = ({}, {})
        origin["study"] = metadata.get("origin_study", metadata.get("origin_study_name"))

        origin["dataset"] = metadata.get(
            "origin_dataset", metadata.get("origin_dataset_name")
        )
        origin["variable"] = metadata.get(
            "origin_variable", metadata.get("origin_variable_name")
        )

        target["study"] = metadata.get("target_study", metadata.get("target_study_name"))
        target["dataset"] = metadata.get(
            "target_dataset", metadata.get("target_dataset_name")
        )
        target["variable"] = metadata.get(
            "target_variable", metadata.get("target_variable_name")
        )

        origin_variable = cls._get_variable(
            origin["study"], origin["dataset"], origin["variable"], "Origin"
        )
        target_variable = cls._get_variable(
            target["study"], target["dataset"], target["variable"], "Target"
        )
        return (origin_variable, target_variable)

    @staticmethod
    @lru_cache(maxsize=100)
    def _get_variable(study, dataset, name, _type):
        try:
            _variable = (
                Variable.objects.filter(dataset__study__name=study)
                .filter(dataset__name=dataset)
                .get(name=name)
            )
        except BaseException as error:
            raise type(error)(
                (f"{_type} variable " f"{study}/{dataset}/{name} does not exist.")
            )
        return _variable


def variables_images_import(file: Path, study: Study) -> None:
    "Initiate imports of all question images"
    if not file.exists():
        return
    with open(file, "r", encoding="utf8") as csv:
        reader = DictReader(csv)
        variables: List[Variable] = []
        for index, row in enumerate(reader):
            variable = Variable.objects.get(
                dataset__study=study,
                dataset__name=row["dataset"],
                name=row["variable"],
            )
            variable.images = {
                "de": row["url_de"],
                "en": row["url"],
            }
            variables.append(variable)
            if index % 1000:
                Variable.objects.bulk_update(variables, ["images"])
                variables = []
        if variables:
            Variable.objects.bulk_update(variables, ["images"])
