from __future__ import annotations

from pathlib import Path

import pandas as pd

from gildle.app.ports.output.hazard_zone_repository import HazardZoneRepository
from gildle.domain.entities.hazard_zone import HazardZone
from gildle.domain.value_objects.coordinate import Coordinate

# 한국도로교통공단 "결빙 교통사고 다발지역" CSV 컬럼명 가정.
_COL_SIDO = "시도"
_COL_NAME = "지점명"
_COL_LAT = "위도"
_COL_LNG = "경도"
_COL_RADIUS = "반경"
_COL_ACCIDENT = "사고건수"
_SEOUL = "서울특별시"


class TrafficAuthorityHazardZoneRepository(HazardZoneRepository):
    """HazardZoneRepository의 결빙 사고 다발지역 CSV 구현체.

    시도='서울특별시' 행만 필터링해 중심좌표+반경으로 HazardZone을 만든다.
    """

    def __init__(self, csv_path: str | Path, encoding: str = "utf-8-sig") -> None:
        self._csv_path = Path(csv_path)
        self._encoding = encoding

    def find_all(self) -> list[HazardZone]:
        frame = pd.read_csv(self._csv_path, encoding=self._encoding)
        seoul = frame[frame[_COL_SIDO] == _SEOUL]
        zones: list[HazardZone] = []
        for position, row in enumerate(seoul.to_dict("records"), start=1):
            zones.append(
                HazardZone(
                    id=position,
                    center=Coordinate(
                        latitude=float(row[_COL_LAT]),
                        longitude=float(row[_COL_LNG]),
                    ),
                    radius_meters=float(row[_COL_RADIUS]),
                    accident_count=int(row[_COL_ACCIDENT]),
                    description=str(row[_COL_NAME]),
                )
            )
        return zones
