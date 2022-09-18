import http
import json
import pathlib
import re
from unittest import mock
import io
import requests
from twitter_aggregator.main import configure_cli, Config
from twitter_aggregator.api import ApiConfig
from twitter_aggregator.cli import CliConfig


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
        else:
            match = re.compile(r"/2/tweets/(\d+)").search(url)
            if match is None:
                raise ValueError("Unexpected url: %s" % url)

            id = match[1]
            raw_data = pathlib.Path(
                f"twitter_aggregator/testdata/get_tweet_{id}.json"
            ).read_text()
            data = json.loads(raw_data)
            response.json.return_value = data

        return response


def test_calculates_stats():
    # Arrange.
    output = io.StringIO()
    config = Config(
        api=ApiConfig(base_path="", bearer_token=""),
        cli=CliConfig(
            debug=False,
            queried_profile_name="Google",
            most_common_count=10,
            max_results=100,
        ),
    )
    cli = configure_cli(config, output, session=FakeSession())

    # Act.
    cli.run()

    # Assert.
    expected_output = """hashtags_count=3
mentions_count=55
most_common_hashtags=[('GABI', 1), ('NextBillionUsers', 1), ('Pixel6', 1)]
most_common_mentions=[('Google', 3), ('gmail', 2), ('SwaveDigest', 1), ('googlearts', 1), ('Lin_Manuel', 1), ('GoogleSmallBiz', 1), ('EricLeGrand52', 1), ('LeGrandCoffee', 1), ('akashsehwag', 1), ('iam_suraj_0718', 1)]
"""
    assert output.getvalue() == expected_output
