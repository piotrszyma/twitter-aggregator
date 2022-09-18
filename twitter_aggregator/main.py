import dataclasses
import logging
import re

import requests_cache
import toml
from dacite.core import from_dict

from twitter_aggregator.api import ApiConfig, TwitterApi
from twitter_aggregator.argparser import parse_args
from twitter_aggregator.cli import Cli, CliConfig
from twitter_aggregator.logger import configure_logger

logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class Config:
    api: ApiConfig
    cli: CliConfig


if __name__ == "__main__":
    cli_args = parse_args()
    raw_config = toml.load(cli_args.config_path)
    config = from_dict(data_class=Config, data=raw_config)

    configure_logger(config.cli.debug)

    RE_USER_TWEETS_URL = re.compile(r"/2\/users\/\d+\/tweets/s")

    def cache_controller(response: requests_cache.AnyResponse) -> bool:
        return not bool(RE_USER_TWEETS_URL.search(response.url))

    session = requests_cache.CachedSession(filter_fn=cache_controller)
    session.headers["Authorization"] = f"Bearer {config.api.bearer_token}"

    api = TwitterApi(
        base_path=config.api.base_path,
        session=session,
    )

    Cli(config.cli, api).run()
