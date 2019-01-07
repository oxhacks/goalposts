import os
import json
import argparse
from datetime import datetime, date

from goalposts import config, constants, goals
from goalposts.collectors import MyFitnessPalCollector, GarminCollector, GithubCollector, GoodreadsCollector


def main():
    parser = argparse.ArgumentParser(description='Collect data about yourself.')
    parser.add_argument('--date', help='Date to use for the report.')
    args = parser.parse_args()

    #collectors = [MyFitnessPalCollector, GarminCollector, GithubCollector]
    collectors = [GoodreadsCollector]
    today = datetime.strptime(args.date, '%Y-%m-%d') if args.date else datetime.today()
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
        collected['collections'][collector.name] = response

    collected['weight']['current'] = collected['collections']['MyFitnessPal']['weight']
    collected['weight']['loss'] = constants.WEIGHT_START - collected['collections'][MyFitnessPalCollector.name]['weight']

    collected['goals'] = {
        'deficit': goals.LessThanGoal(collected['collections']['Garmin']['totalKilocalories'],
                                      collected['collections']['MyFitnessPal']['nutrition']['calories']).report(),
        'steps': goals.GreaterThanGoal(constants.STEP_GOAL, collected['collections']['Garmin']['totalSteps']).report(),
        'sleep': goals.GreaterThanGoal(constants.SLEEP_GOAL, collected['collections']['Garmin']['sleepingSeconds']).report(),
        'protein': goals.GreaterThanGoal(constants.PROTEIN_GOAL, collected['collections']['MyFitnessPal']['nutrition']['protein']).report(),
        'code': goals.GreaterThanGoal(constants.COMMIT_GOAL, len(collected['collections'][GithubCollector.name].keys())).report()
    }

    filename = f'{today_short}.json'
    filepath = os.path.join(config.REPORT_DIR, filename)
    with open(filepath, 'w') as outfile:
        json.dump(collected, outfile, indent=4)


if __name__ == '__main__':
    main()
