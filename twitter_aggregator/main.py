import logging
import toml
from dacite.core import from_dict

from twitter_aggregator.argparser import parse_args
from twitter_aggregator.cli import Cli, CliConfig
from twitter_aggregator.logger import configure_logger

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    cli_args = parse_args()
    raw_config = toml.load(cli_args.config_path)
    config = from_dict(data_class=CliConfig, data=raw_config)

    logger = configure_logger()

    if config.tool.debug:
        logger.setLevel(logging.DEBUG)

    Cli().run(config)
