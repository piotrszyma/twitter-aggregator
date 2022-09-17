import http

import requests
import requests_cache
from dacite.core import from_dict

from twitter_aggregator.models import TweetData, TweetDetailsData, UserData


class TwitterClient:
    def __init__(
        self,
        *,
        base_path: str,
        bearer_token: str,
        cache_tweets_list=False,
        session_factory=requests_cache.CachedSession,
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

    def get_users(self, usernames: list[str]) -> list[UserData]:
        url = f"{self._base_path}/2/users/by?usernames={','.join(usernames)}"
        response = self._session_with_cache.get(url)
        self._assert_success(response)
        response_json = response.json().get("data")
        assert isinstance(response_json, list)
        return [from_dict(data_class=UserData, data=data) for data in response_json]

    def get_tweets(self, *, user_id: str, max_results=100) -> list[TweetData]:
        """Returns list of ids of latest tweets for given user."""
        url = (
            f"{self._base_path}/2/users/{user_id}/tweets?"
            f"max_results={max_results}&"  # Limit results.
            "tweet.fields=id"  # Fetch only IDs.
        )

        if self._cache_tweets_list:
            response = self._session_with_cache.get(url)
        else:
            with self._session_with_cache.cache_disabled():
                response = self._session_with_cache.get(url)

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
        response = self._session_with_cache.get(url)
        self._assert_success(response)
        response_json = response.json().get("data")
        assert isinstance(response_json, dict)
        return from_dict(data_class=TweetDetailsData, data=response_json)
