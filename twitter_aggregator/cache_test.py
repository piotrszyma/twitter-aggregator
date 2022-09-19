import pytest

from twitter_aggregator.cache import should_cache_url


@pytest.mark.parametrize(
    "url,expected_should_cache",
    [
        ("https://api.twitter.com/2/users/by?usernames=Google", True),
        (
            (
                "https://api.twitter.com/2/users/20536157/tweets"
                "?max_results=5&tweet.fields=id"
            ),
            False,
        ),
        (
            (
                "https://api.twitter.com/2/tweets/1570903551312011264"
                "?tweet.fields=entities&expansions=entities.mentions.username"
            ),
            True,
        ),
    ],
)
def test_should_cache_url(url, expected_should_cache):
    assert should_cache_url(url) == expected_should_cache
