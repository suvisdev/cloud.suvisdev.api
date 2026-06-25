from dataclasses import dataclass

from star_craft.domain.events.base_event import BaseEvent


@dataclass(frozen=True)
class UserSignedUpEvent(BaseEvent):
    """viewer Spoke → Hub → 관심 있는 Spoke로 전파"""
    user_id: int = 0
    username: str = ""


@dataclass(frozen=True)
class MovieWatchedEvent(BaseEvent):
    """mova Spoke → Hub → 관심 있는 Spoke로 전파"""
    user_id: int = 0
    movie_id: int = 0
    title: str = ""


@dataclass(frozen=True)
class PassengerUploadedEvent(BaseEvent):
    """titanic Spoke → Hub → 관심 있는 Spoke로 전파"""
    uploaded_by: str = ""
    row_count: int = 0