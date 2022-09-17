import dataclasses
from typing import Optional


@dataclasses.dataclass(frozen=True)
class UserData:
    id: str
    username: str


@dataclasses.dataclass(frozen=True)
class TweetData:
    id: str


@dataclasses.dataclass(frozen=True)
class TweetHashtag:
    tag: str


@dataclasses.dataclass(frozen=True)
class TweetMention:
    id: str
    username: str


@dataclasses.dataclass(frozen=True)
class TweetEntities:
    hashtags: Optional[list[TweetHashtag]]
    mentions: Optional[list[TweetMention]]


@dataclasses.dataclass(frozen=True)
class TweetDetailsData:
    id: str
    text: str
    entities: Optional[TweetEntities]
