import dataclasses
import http
import logging

import requests
from dacite.core import from_dict

from twitter_aggregator.models import TweetData, TweetDetailsData, UserData

logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class ApiConfig:
    base_path: str
    bearer_token: str


class TwitterApi:
    def __init__(
        self,
        *,
        base_path: str,
        session: requests.Session,
    ):
        self._base_path = base_path
        self._session = session

    def _assert_success(self, response: requests.Response) -> None:
        assert response.status_code == http.HTTPStatus.OK, (
            f"unexpected {response.status_code=}, "
            f"{response.text=}, "
            f"{response.url=}"
        )

    def _request(self, url) -> requests.Response:
        logger.debug("Requesting %s", url)
        response = self._session.get(url)
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

        response = self._request(url)

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
