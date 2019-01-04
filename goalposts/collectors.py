"""Collectors that are used to retrieve stats."""

import logging
from abc import ABC
from datetime import datetime, timedelta
from typing import Dict

import myfitnesspal
from github import Github, GithubException

from goalposts import config
from goalposts.clients import UserGarminClient


LOG = logging.getLogger(__name__)


class Collector(ABC):
    """Retrieve the stats from different endpoints."""
    name = __name__

    def collect(self, day: datetime) -> Dict:
        LOG.info(f'Collecting stats for {self.name} on {day.isoformat()}')
        collected = self._collect(day)
        LOG.debug(f'Collection for {self.name} complete')
        return collected

    def _collect(self, day: datetime):
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
                return get_weight(weight_date - timedelta(days=1))
        weight = get_weight()
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
        response = {}

        for repo in self.client.get_user().get_repos():
            try:
                for commit in repo.get_commits(since=day, until=day + timedelta(days=1)):
                    commit_date = commit.commit.committer.date.isoformat()
                    commit_slug = f'{commit.commit.sha[:7]}-{commit_date}'
                    try:
                        response[repo.full_name].append(commit_slug)
                    except KeyError:
                        response[repo.full_name] = [commit_slug]
            except GithubException:
                LOG.warn(f'Github: repo {repo.full_name} is bare')
                continue
        return response
