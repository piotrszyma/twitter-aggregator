import dataclasses
import logging

import requests_cache
import toml
from dacite.core import from_dict

from twitter_aggregator.api import ApiConfig, TwitterApi
from twitter_aggregator.argparser import parse_args
from twitter_aggregator.cli import Cli, CliConfig
from twitter_aggregator.logger import configure_logger
from twitter_aggregator.cache import should_cache_url

logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class Config:
    api: ApiConfig
    cli: CliConfig


def cache_filter_fn(response: requests_cache.AnyResponse) -> bool:
    should_cache = should_cache_url(response.url)

    if should_cache:
        logger.debug("Should cache response.url=%s", response.url)
    else:
        logger.debug("Should not cache response.url=%s", response.url)

    return should_cache


def configure_cli(config: Config) -> Cli:
    session = requests_cache.CachedSession(filter_fn=cache_filter_fn)
    session.headers["Authorization"] = f"Bearer {config.api.bearer_token}"

    api = TwitterApi(
        base_path=config.api.base_path,
        session=session,
    )

    return Cli(config.cli, api)


if __name__ == "__main__":
    cli_args = parse_args()
    logger.debug("running cli from config path=%s", cli_args.config_path)
    raw_config = toml.load(cli_args.config_path)
    config = from_dict(data_class=Config, data=raw_config)

    configure_logger(config.cli.debug)
    cli = configure_cli(config)
    cli.run()
