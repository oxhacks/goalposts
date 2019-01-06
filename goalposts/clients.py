"""Clients to help interface with various APIs used for collection."""

from random import randint
from datetime import datetime

from garminexport.garminclient import GarminClient, require_session


class UserGarminClient(GarminClient):
    """Add the ability to get a daily activity report from the GarminExport project."""
    @require_session
    def get_daily_report(self, token: str, day: datetime) -> dict:
        """Download the daily activity report from Garmin using the built-in session capability.

        :param token: the Garmin API token
        :param day: the datetime to collect
        :returns: the response from Garmin

        """
        day_string = day.isoformat().split('T')[0]
        cache_buster = randint(100000, 1000000)
        url = f'https://connect.garmin.com/modern/proxy/usersummary-service/usersummary/daily/\
                {token}?calendarDate={day_string}&_={cache_buster}'
        response = self.session.get(url)
        return response.json()
