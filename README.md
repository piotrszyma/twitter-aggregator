# twitter aggregator

## How to run - step by step

1. make sure you have [poetry](https://python-poetry.org/) and proper version of `python3` installed (specified in `pyproject.toml`)
2. install dependencies via `poetry install`
3. copy sample config `cp config.example.toml config.toml`
4. fill twitter API credentials in `config.toml` (bearer token)
5. run cli `poetry run python3 twitter_aggregator/main.py --config-file ./config.toml`

## Cache

The cli assumes that:
1. once user ID was obtained, it will never change
2. once tweet is fetched by ID, it will never change
that is why requests to fetch user/tweet details are cached.

## Config file

To run the cli, you need to have a config file. Check `config.example.toml`
to see example config. You need to fill the `bearer_token` config attribute
before the first run. Check [twitter API Docs](https://developer.twitter.com/en/docs/twitter-api)
for info how to obtain `bearer_token`.
