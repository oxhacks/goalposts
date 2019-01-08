"""Collectors that are used to retrieve stats."""

import logging
from abc import ABC
from datetime import datetime, timedelta
from typing import Dict

import myfitnesspal
from goodreads import client as goodreads_client
from github import Github, GithubException

from goalposts import config
from goalposts.clients import UserGarminClient


LOG = logging.getLogger(__name__)


class Collector(ABC):
    """Retrieve the stats from different endpoints."""
    name = __name__

    def collect(self, day: datetime) -> Dict:
        """The base collector method that fires the internal _collect method.

        This method should not be overridden.

        :param day: the datetime to collect
        :returns: the response from the API

        """
        LOG.info(f'Collecting stats for {self.name} on {day.isoformat()}')
        collected = self._collect(day)
        LOG.debug(f'Collection for {self.name} complete')
        return collected

    def _collect(self, day: datetime):
        """Collection method that should be overridden by Collectors.

        Should accept a datetime and return an API response.

        :param day: the day to collect

        """
        raise NotImplementedError("Do not use the Collector class directly.")


class MyFitnessPalCollector(Collector):
    """Collector to grab weight and nutrition information from MFP."""
    name = 'MyFitnessPal'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = myfitnesspal.Client(config.MFP_USER)

    def _collect(self, day: datetime) -> Dict:
        stats = self.client.get_date(day.year, day.month, day.day)
        def get_weight(weight_date: datetime = day.date()):
            measurements = self.client.get_measurements('Weight', weight_date)
            try:
                return measurements[weight_date]
            except KeyError:
                return get_weight(weight_date - timedelta(days=1))
        weight = get_weight()
        stats.totals.update({'weight': weight})
        return stats.totals


class GarminCollector(Collector):
    """Collector to get daily activity data from Garmin."""
    name = 'Garmin'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = UserGarminClient(config.GARMIN_USER, config.GARMIN_PASS)
        self.client.connect()

    def _collect(self, day: datetime) -> Dict:
        stats = self.client.get_daily_report(config.GARMIN_TOKEN, day)
        return stats


class GithubCollector(Collector):
    """Collector to retrieve recent commits from Github."""
    name = 'Github'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = Github(config.GITHUB_TOKEN)

    def _collect(self, day: datetime) -> Dict:
        response = {}

        for repo in self.client.get_user().get_repos():
            try:
                for commit in repo.get_commits(since=day, until=day + timedelta(days=1)):
                    commit_date = commit.commit.author.date.isoformat()
                    commit_slug = f'{commit.commit.sha[:7]}|{commit_date}'
                    try:
                        response[repo.full_name].append(commit_slug)
                    except KeyError:
                        response[repo.full_name] = [commit_slug]
            except GithubException:
                LOG.warning(f'Github: repo {repo.full_name} is bare')
                continue
        return response


class GoodreadsCollector(Collector):
    """Collector to retrieve user status information from Goodreads."""
    name = 'Goodreads'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = goodreads_client.GoodreadsClient(config.GOODREADS_KEY, config.GOODREADS_SECRET)
        self.client.authenticate()

    def _collect(self, day: datetime) -> Dict:
        return {'book': self.client.book(1)}
