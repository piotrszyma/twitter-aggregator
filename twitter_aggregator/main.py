import toml
from dacite.core import from_dict

from twitter_aggregator.argparser import parse_args
from twitter_aggregator.cli import Cli, CliConfig

if __name__ == "__main__":
    cli_args = parse_args()
    raw_config = toml.load(cli_args.config_path)
    config = from_dict(data_class=CliConfig, data=raw_config)
    Cli().run(config)
