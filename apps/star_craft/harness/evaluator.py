"""
하네스 평가 엔진.
이벤트 흐름이 온톨로지 계약을 만족하는지 정적으로 검증한다.
"""
from star_craft.domain.events.base_event import BaseEvent


def assert_event_contract(event: BaseEvent) -> None:
    """이벤트가 최소 계약(source_spoke 비어있지 않음)을 만족하는지 검증."""
    if not event.source_spoke:
        raise ValueError(f"{type(event).__name__}: source_spoke must not be empty")
