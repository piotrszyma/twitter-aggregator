import http
import logging
from typing import Type

import requests
import requests_cache
from dacite.core import from_dict

from twitter_aggregator.models import TweetData, TweetDetailsData, UserData

logger = logging.getLogger(__name__)


class TwitterClient:
    def __init__(
        self,
        *,
        base_path: str,
        bearer_token: str,
        session_factory: Type[requests_cache.CachedSession],
        cache_tweets_list=False,
    ):
        self._base_path = base_path
        self._bearer_token = bearer_token
        self._session_with_cache = session_factory()
        self._session_with_cache.headers["Authorization"] = f"Bearer {bearer_token}"
        self._session_with_cache.headers["UserAgent"] = "test-client"
        self._cache_tweets_list = cache_tweets_list

    def _assert_success(self, response: requests.Response) -> None:
        assert response.status_code == http.HTTPStatus.OK, (
            f"unexpected {response.status_code=}, "
            f"{response.text=}, "
            f"{response.url=}"
        )

    def _request(self, url, *, cache_disabled=False) -> requests.Response:

        if cache_disabled:
            logger.debug("Requesting %s with cache disabled", url)
            with self._session_with_cache.cache_disabled():
                response = self._session_with_cache.get(url)
        else:
            logger.debug("Requesting %s with cache enabled", url)
            response = self._session_with_cache.get(url)

        logger.debug("Got response with status %s", response.status_code)
        return response

    def get_users(self, usernames: list[str]) -> list[UserData]:
        url = f"{self._base_path}/2/users/by?usernames={','.join(usernames)}"
        response = self._request(url)
        self._assert_success(response)
        response_json = response.json().get("data")
        assert isinstance(response_json, list)
        return [from_dict(data_class=UserData, data=data) for data in response_json]

    def get_tweets(self, *, user_id: str, max_results: int) -> list[TweetData]:
        """Returns list of ids of latest tweets for given user."""
        url = (
            f"{self._base_path}/2/users/{user_id}/tweets?"
            f"max_results={max_results}&"  # Limit results.
            "tweet.fields=id"  # Fetch only IDs.
        )

        response = self._request(url, cache_disabled=not self._cache_tweets_list)

        self._assert_success(response)
        response_json = response.json().get("data")
        assert isinstance(response_json, list)
        return [from_dict(data_class=TweetData, data=data) for data in response_json]

    def get_tweet(self, *, id: str) -> TweetDetailsData:
        url = (
            f"{self._base_path}/2/tweets/{id}?"
            f"tweet.fields=entities&"  # Enable entities.
            f"expansions=entities.mentions.username"  # Enable mentions.
        )
        response = self._request(url)
        self._assert_success(response)
        response_json = response.json().get("data")
        assert isinstance(response_json, dict)
        return from_dict(data_class=TweetDetailsData, data=response_json)
