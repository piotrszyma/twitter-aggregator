import collections
import dataclasses
import logging
import sys

from twitter_aggregator.api import TwitterApi
from twitter_aggregator.operators import get_hashtags, get_mentions

logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class CliConfig:
    debug: bool
    queried_profile_name: str
    cache_tweets_list: bool
    most_common_count: int
    max_results: int


class Cli:
    def __init__(
        self,
        config: CliConfig,
        twitter_api: TwitterApi,
        output=sys.stdout,
    ):
        self._twitter_api = twitter_api
        self._config = config
        self._output = output

    def run(self) -> None:
        logger.debug(
            "Fetching user data for user with profile name: %s",
            self._config.queried_profile_name,
        )
        users_data = self._twitter_api.get_users([self._config.queried_profile_name])
        assert (
            len(users_data) == 1
        ), f"Profile with name {self._config.queried_profile_name} does not exist."

        user_id = users_data[0].id

        logger.debug("Fetching tweets for user with id=%s", user_id)
        user_tweets = self._twitter_api.get_tweets(
            user_id=user_id, max_results=self._config.max_results
        )

        tweets = tuple(self._twitter_api.get_tweet(id=t.id) for t in user_tweets)

        logger.debug("Calculating statistics for tweets for user with id=%s", user_id)
        hashtags = tuple(get_hashtags(tweets))
        mentions = tuple(get_mentions(tweets))

        hashtags_counter = collections.Counter(hashtags)
        mentions_counter = collections.Counter(mentions)
        hashtags_count = len(hashtags)
        mentions_count = len(mentions)

        most_common_hashtags = hashtags_counter.most_common(
            self._config.most_common_count
        )
        most_common_mentions = mentions_counter.most_common(
            self._config.most_common_count
        )

        self._output.write(f"{hashtags_count=}\n")
        self._output.write(f"{mentions_count=}\n")
        self._output.write(f"{most_common_hashtags=}\n")
        self._output.write(f"{most_common_mentions=}\n")
