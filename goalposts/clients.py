from random import randint
from datetime import datetime

from garminexport.garminclient import GarminClient, require_session


class UserGarminClient(GarminClient):
    @require_session
    def get_daily_report(self, token: str, day: datetime):
        day_string = day.isoformat().split('T')[0]
        cache_buster = randint(100000, 1000000)
        url = f'https://connect.garmin.com/modern/proxy/usersummary-service/usersummary/daily/{token}?calendarDate={day_string}&_={cache_buster}'
        response = self.session.get(url)
        return response.json()