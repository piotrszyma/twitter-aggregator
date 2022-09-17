"""Operators that can be applied over iterable of tweet details.

Useful to extract specific attributes from list of tweet details for
further statistics.

"""
from typing import Iterable

from api_client import TweetDetailsData


def hashtags(tweets: Iterable[TweetDetailsData]) -> Iterable[str]:
    """Yields hashtags from iterable of tweets."""
    for tweet in tweets:
        if tweet.entities is None:
            continue

        if tweet.entities.hashtags is None:
            continue

        yield from (h.tag for h in tweet.entities.hashtags)


def mentions(tweets: Iterable[TweetDetailsData]) -> Iterable[str]:
    """Yields mentioned usernames from iterable of tweets."""
    for tweet in tweets:
        if tweet.entities is None:
            continue

        if tweet.entities.mentions is None:
            continue

        yield from (m.username for m in tweet.entities.mentions)