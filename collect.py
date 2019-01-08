"""Fire the collectors and save the results."""

import os
import json
import argparse
from datetime import datetime

from goalposts import config, constants, goals
from goalposts.collectors import MyFitnessPalCollector, GarminCollector, GithubCollector


def collect(args):
    """Run the collection job."""
    collectors = [MyFitnessPalCollector, GarminCollector, GithubCollector]
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

    collected['weight']['current'] = collected['collections'][MyFitnessPalCollector.name]['weight']
    collected['weight']['loss'] = constants.WEIGHT_START - \
                                  collected['collections'][MyFitnessPalCollector.name]['weight']

    collected['goals'] = {
        'deficit': goals.LessThanGoal(collected['collections'][GarminCollector.name]['totalKilocalories'],
                                      collected['collections'][MyFitnessPalCollector.name]['calories']).report(),
        'steps': goals.GreaterThanGoal(constants.STEP_GOAL,
                                       collected['collections'][GarminCollector.name]['totalSteps']).report(),
        'sleep': goals.GreaterThanGoal(constants.SLEEP_GOAL,
                                       collected['collections'][GarminCollector.name]['sleepingSeconds']).report(),
        'protein': goals.GreaterThanGoal(constants.PROTEIN_GOAL,
                                         collected['collections'][MyFitnessPalCollector.name]['protein']).report(),
        'code': goals.GreaterThanGoal(constants.COMMIT_GOAL,
                                      len(collected['collections'][GithubCollector.name].keys())).report()
    }

    filename = f'{today_short}.json'
    filepath = os.path.join(config.REPORT_DIR, filename)
    with open(filepath, 'w') as outfile:
        json.dump(collected, outfile, indent=4)


def run_collection():
    """Parse the arguments for the collector."""
    parser = argparse.ArgumentParser(description='Collect data about yourself.')
    parser.add_argument('--date', help='Date to use for the report.')
    cli_args = parser.parse_args()
    collect(cli_args)


if __name__ == '__main__':
    run_collection()
