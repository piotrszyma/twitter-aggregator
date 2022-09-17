from dataclasses import dataclass
import requests_cache

import http

import requests
from dacite.core import from_dict


@dataclass
class UserData:
    id: str
    username: str


@dataclass
class TweetData:
    id: str


@dataclass
class TweetDetailsData:
    id: str
    text: str


class TwitterClient:
    def __init__(self, *, base_path: str, bearer_token: str):
        self._base_path = base_path
        self._bearer_token = bearer_token
        self._session_with_cache = requests_cache.CachedSession()
        self._session_with_cache.headers["Authorization"] = f"Bearer {bearer_token}"
        self._session_with_cache.headers["UserAgent"] = "test-client"

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

        # TODO(pszyma): After manual testing, reenable this.
        # with self._session_with_cache.cache_disabled():
        response = self._session_with_cache.get(url)

        self._assert_success(response)
        response_json = response.json().get("data")
        assert isinstance(response_json, list)
        return [from_dict(data_class=TweetData, data=data) for data in response_json]

    def get_tweet(self, *, id: str) -> TweetDetailsData:
        url = f"{self._base_path}/2/tweets/{id}?tweet.fields=entities&expansions=entities.hashtags"
        response = self._session_with_cache.get(url)
        self._assert_success(response)
        response_json = response.json().get("data")
        breakpoint()
        assert isinstance(response_json, dict)
        return from_dict(data_class=TweetDetailsData, data=response_json)
