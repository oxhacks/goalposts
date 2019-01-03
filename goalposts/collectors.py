"""Collectors that are used to retrieve stats."""

import warnings
from abc import ABC
from datetime import datetime, timedelta
from typing import Dict

import myfitnesspal
from github import Github, GithubException

from goalposts import config
from goalposts.clients import UserGarminClient


class Collector(ABC):
    """Retrieve the stats from different endpoints."""
    def collect(self, day: datetime) -> Dict:
        return self._collect(day)

    def _collect(self):
        raise NotImplementedError("Do not use the Collector class directly.")


class MyFitnessPalCollector(Collector):
    name = 'MyFitnessPal'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = myfitnesspal.Client(config.MFP_USER)

    def _collect(self, day: datetime) -> Dict:
        stats = self.client.get_date(day.year, day.month, day.day)
        def get_weight(weight_date: datetime=day.date()):
            measurements = self.client.get_measurements('Weight', weight_date)
            try:
                return measurements[weight_date]
            except KeyError:
                return get_weight(day.date() - timedelta(days=1))
        weight = get_weight()
        print('weight', weight)
        return {'nutrition': stats.totals, 'weight': weight}


class GarminCollector(Collector):
    name = 'Garmin'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = UserGarminClient(config.GARMIN_USER, config.GARMIN_PASS)
        self.client.connect()

    def _collect(self, day: datetime) -> Dict:
        stats = self.client.get_daily_report(config.GARMIN_TOKEN, day)
        return stats


class GithubCollector(Collector):
    name = 'Github'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = Github(config.GITHUB_TOKEN)

    def _collect(self, day: datetime) -> Dict:
        response = []
        today = day.strftime('%Y-%m-%d')

        for repo in self.client.get_user().get_repos():
            try:
                for commit in repo.get_commits():
                    if today != commit.commit.committer.date.strftime('%Y-%m-%d'):
                        break
                    response.append(commit.commit.committer.date.isoformat())
            except GithubException:
                warnings.warn(f'Github: repo {repo.full_name} is bare')
                continue
        return response
