import http
import io
import json
import pathlib
import re
from unittest import mock

import requests

from twitter_aggregator.api import ApiConfig
from twitter_aggregator.cli import CliConfig
from twitter_aggregator.main import Config, configure_cli


class FakeSession(requests.Session):
    def get(self, url: str, **kwargs) -> requests.Response:
        response = mock.MagicMock(
            status_code=http.HTTPStatus.OK, spec=requests.Response
        )
        if "/2/users/by?usernames" in url:
            raw_data = pathlib.Path(
                "twitter_aggregator/testdata/get_users.json"
            ).read_text()
            data = json.loads(raw_data)
            response.json.return_value = data
        elif "/2/users/" in url:
            raw_data = pathlib.Path(
                "twitter_aggregator/testdata/get_tweets.json"
            ).read_text()
            data = json.loads(raw_data)
            response.json.return_value = data
        elif "/2/tweets/" in url:
            match = re.compile(r"/2/tweets/(\d+)").search(url)
            assert match is not None

            id = match[1]
            raw_data = pathlib.Path(
                f"twitter_aggregator/testdata/get_tweet_{id}.json"
            ).read_text()
            data = json.loads(raw_data)
            response.json.return_value = data
        else:
            raise ValueError("Unexpected url: %s" % url)

        return response


def test_calculates_stats():
    # Arrange.
    buffer = io.StringIO()
    config = Config(
        api=ApiConfig(base_path="", bearer_token=""),
        cli=CliConfig(
            debug=False,
            queried_profile_name="Google",
            most_common_count=10,
            max_results=100,
        ),
    )
    cli = configure_cli(config, buffer, session=FakeSession())

    # Act.
    cli.run()

    # Assert.
    output = buffer.getvalue()
    assert "hashtags_count=3" in output
    assert "mentions_count=55" in output
    assert (
        "most_common_hashtags=[('GABI', 1), ('NextBillionUsers', 1), ('Pixel6', 1)]"
        in output
    )
    assert (
        "most_common_mentions=[('Google', 3), ('gmail', 2), ('SwaveDigest', 1),"
        in output
    )
