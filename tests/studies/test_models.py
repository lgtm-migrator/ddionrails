# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods

""" Test cases for ddionrails.studies.models """

import pathlib

import pytest

from ddionrails.studies.models import TopicList

pytestmark = [pytest.mark.studies, pytest.mark.models]  # pylint: disable=invalid-name


class TestStudyModel:
    def test_string_method(self, study):
        expected = "/" + study.name
        assert expected == str(study)

    def test_get_absolute_url_method(self, study):
        expected = "/" + study.name
        assert expected == study.get_absolute_url()

    def test_repo_url_method_https(self, study, settings):
        settings.GIT_PROTOCOL = "https"
        repo_url = study.repo_url()
        assert repo_url.startswith("https")
        assert study.repo in repo_url

    def test_repo_url_method_ssh(self, study, settings):
        settings.GIT_PROTOCOL = "ssh"
        repo_url = study.repo_url()
        assert repo_url.startswith("git")
        assert study.repo in repo_url

    def test_repo_url_method_exception(self, study, settings):
        settings.GIT_PROTOCOL = None
        with pytest.raises(Exception) as excinfo:
            study.repo_url()
            assert excinfo.value == "Specify a protocol for Git in your settings."

    def test_has_topics_method(self, study):
        expected = False
        assert expected is study.has_topics()

    def test_has_topics_method_returns_true(self, study):
        study.topic_languages = ["en"]
        study.save()
        expected = True
        assert expected is study.has_topics()

    def test_set_topiclist_method(self, study):
        assert 0 == TopicList.objects.count()
        body = [{"topics": []}]
        study.set_topiclist(body)
        assert 1 == TopicList.objects.count()
        topiclist = TopicList.objects.first()
        assert study == topiclist.study
        assert topiclist.topiclist == body

    def test_get_topiclist_method(
        self, study, topiclist
    ):  # pylint: disable=unused-argument
        result = study.get_topiclist()
        expected = [{"title": "some-topic"}]
        assert expected == result

    def test_get_topiclist_method_without_topic_list(
        self, study
    ):  # pylint: disable=unused-argument
        result = study.get_topiclist()
        expected = None
        assert expected is result
