import os
import json
from datetime import datetime

from goalposts import config, constants, goals
from goalposts.collectors import MyFitnessPal, Garmin


if __name__ == '__main__':
    collectors = [MyFitnessPal, Garmin]
    today = datetime.today()
    today_short = today.strftime('%Y%m%d')
    collected = {
        'date_long': today.isoformat(),
        'date': today_short,
        'weight': {
            'start': constants.WEIGHT_START,
            'goal': constants.WEIGHT_GOAL
        },
        'collections': {}
    }
    for collector in collectors:
        response = collector().collect(today)
        collected['collections'][collector.__name__] = response

    collected['weight']['current'] = collected['collections']['MyFitnessPal']['weight']
    collected['weight']['loss'] = constants.WEIGHT_START - collected['collections']['MyFitnessPal']['weight']

    collected['goals'] = {
        'deficit': goals.LessThanGoal(collected['collections']['Garmin']['totalKilocalories'],
                                      collected['collections']['MyFitnessPal']['nutrition']['calories']).report(),
        'steps': goals.GreaterThanGoal(constants.STEP_GOAL, collected['collections']['Garmin']['totalSteps']).report(),
        'sleep': goals.GreaterThanGoal(constants.SLEEP_GOAL, collected['collections']['Garmin']['sleepingSeconds']).report(),
        'protein': goals.GreaterThanGoal(constants.PROTEIN_GOAL, collected['collections']['MyFitnessPal']['nutrition']['protein']).report()
    }

    filename = f'{today_short}.json'
    filepath = os.path.join(config.REPORT_DIR, filename)
    with open(filepath, 'w') as outfile:
        json.dump(collected, outfile, indent=4)