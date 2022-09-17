import collections
import dataclasses

import toml
from dacite.core import from_dict

from twitter_aggregator.api_client import TwitterClient
from twitter_aggregator.operators import hashtags, mentions
from twitter_aggregator.argparser import parse_args


@dataclasses.dataclass(frozen=True)
class TwitterConfig:
    api_key: str
    api_key_secret: str
    bearer_token: str
    base_path: str


@dataclasses.dataclass(frozen=True)
class ToolConfig:
    queried_profile_name: str
    cache_tweets_list: bool


@dataclasses.dataclass(frozen=True)
class CliConfig:
    twitter: TwitterConfig
    tool: ToolConfig


def run_cli(config: CliConfig) -> None:
    twitter_config = config.twitter
    tool_config = config.tool

    client = TwitterClient(
        base_path=twitter_config.base_path,
        bearer_token=twitter_config.bearer_token,
        cache_tweets_list=tool_config.cache_tweets_list,
    )

    users_data = client.get_users([tool_config.queried_profile_name])
    assert (
        len(users_data) == 1
    ), f"Profile with name {tool_config.queried_profile_name} does not exist."

    user_tweets = client.get_tweets(user_id=users_data[0].id)

    tweets = tuple(client.get_tweet(id=t.id) for t in user_tweets)

    hashtags_counter = collections.Counter(hashtags(tweets))
    mentions_counter = collections.Counter(mentions(tweets))

    print(f"{hashtags_counter.most_common(5)=}")
    print(f"{mentions_counter.most_common(5)=}")


if __name__ == "__main__":
    cli_args = parse_args()
    raw_config = toml.load(cli_args.config_path)
    config = from_dict(data_class=CliConfig, data=raw_config)
    run_cli(config)
