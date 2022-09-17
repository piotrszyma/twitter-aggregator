import dataclasses
import toml

from dacite.core import from_dict
from twitter_aggregator.api_client import TwitterClient


@dataclasses.dataclass(frozen=True)
class TwitterConfig:
    api_key: str
    api_key_secret: str
    bearer_token: str
    base_path: str


@dataclasses.dataclass
class Config:
    twitter: TwitterConfig


if __name__ == "__main__":
    raw_config = toml.load("config.toml")

    app_config = from_dict(data_class=Config, data=raw_config)
    config = app_config.twitter

    client = TwitterClient(base_path=config.base_path, bearer_token=config.bearer_token)

    users_data = client.get_users(["Google"])
    assert len(users_data) == 1

    user_tweets = client.get_tweets(user_id=users_data[0].id)

    first_tweet_id = user_tweets[0].id

    first_tweet = client.get_tweet(id=first_tweet_id)

    breakpoint()
    breakpoint()
