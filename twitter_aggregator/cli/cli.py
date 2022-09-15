
from twitter_aggregator.cli import argparser


def run_cli():
    args = argparser.parse_args()
    print(args)

