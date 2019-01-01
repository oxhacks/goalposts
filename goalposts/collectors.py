"""Collectors that are used to retrieve stats."""

from abc import ABC
from datetime import datetime
from typing import Dict

import myfitnesspal

from goalposts import config
from goalposts.clients import UserGarminClient


class Collector(ABC):
    """Retrieve the stats from different endpoints."""
    def collect(self, day: datetime) -> Dict:
        return self._collect(day)

    def _collect(self):
        raise NotImplementedError("Do not use the Collector class directly.")


class MyFitnessPal(Collector):
    name = 'MyFitnessPal'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = myfitnesspal.Client(config.MFP_USER)

    def _collect(self, day: datetime) -> Dict:
        stats = self.client.get_date(day.year, day.month, day.day)
        weight = self.client.get_measurements('Weight', day.date())[day.date()]
        return {'nutrition': stats.totals, 'weight': weight}


class Garmin(Collector):
    name = 'Garmin'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = UserGarminClient(config.GARMIN_USER, config.GARMIN_PASS)
        self.client.connect()

    def _collect(self, day: datetime) -> Dict:
        stats = self.client.get_daily_report(config.GARMIN_TOKEN, day)
        return stats