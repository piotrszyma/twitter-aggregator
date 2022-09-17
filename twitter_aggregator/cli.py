import collections
import dataclasses
from typing import Type

import requests_cache

from twitter_aggregator.api_client import TwitterClient
from twitter_aggregator.operators import get_hashtags, get_mentions


@dataclasses.dataclass(frozen=True)
class TwitterConfig:
    bearer_token: str
    base_path: str


@dataclasses.dataclass(frozen=True)
class ToolConfig:
    queried_profile_name: str
    cache_tweets_list: bool
    most_common_count: int


@dataclasses.dataclass(frozen=True)
class CliConfig:
    twitter: TwitterConfig
    tool: ToolConfig


class Cli:
    def __init__(
        self,
        session_factory: Type[
            requests_cache.CachedSession
        ] = requests_cache.CachedSession,
    ):
        self._session_factory = session_factory

    def run(self, config: CliConfig) -> None:
        twitter_config = config.twitter
        tool_config = config.tool

        client = TwitterClient(
            base_path=twitter_config.base_path,
            bearer_token=twitter_config.bearer_token,
            cache_tweets_list=tool_config.cache_tweets_list,
            session_factory=self._session_factory,
        )

        users_data = client.get_users([tool_config.queried_profile_name])
        assert (
            len(users_data) == 1
        ), f"Profile with name {tool_config.queried_profile_name} does not exist."

        user_tweets = client.get_tweets(user_id=users_data[0].id)

        tweets = tuple(client.get_tweet(id=t.id) for t in user_tweets)

        hashtags = tuple(get_hashtags(tweets))
        mentions = tuple(get_mentions(tweets))

        hashtags_counter = collections.Counter(hashtags)
        mentions_counter = collections.Counter(mentions)
        hashtags_count = len(hashtags)
        mentions_count = len(mentions)

        most_common_hashtags = hashtags_counter.most_common(
            tool_config.most_common_count
        )
        most_common_mentions = mentions_counter.most_common(
            tool_config.most_common_count
        )

        print(f"{hashtags_count=}")
        print(f"{mentions_count=}")
        print(f"{most_common_hashtags=}")
        print(f"{most_common_mentions=}")
