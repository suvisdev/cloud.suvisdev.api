from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from gildle.app.ports.output.tree_segment_repository import TreeSegmentRepository
from gildle.domain.entities.tree_segment import TreeSegment
from gildle.domain.value_objects.coordinate import Coordinate
from gildle.domain.value_objects.tree_species import TreeSpecies

# data.go.kr "전국가로수길정보표준데이터"(서울 자치구) CSV 컬럼명 가정.
# 실제 다운로드 헤더와 다르면 이 상수만 맞추면 된다.
_COL_ROAD_NAME = "도로명"
_COL_START_LAT = "시작위도"
_COL_START_LNG = "시작경도"
_COL_END_LAT = "종료위도"
_COL_END_LNG = "종료경도"
_COL_SPECIES = "수종"
_COL_QUANTITY = "수량"
_COL_AGENCY = "관리기관"


class CsvTreeSegmentRepository(TreeSegmentRepository):
    """TreeSegmentRepository의 CSV 구현체(서울 한 자치구 가로수 데이터).

    좌표가 이미 포함된 표준데이터를 가정하므로 Geocoding이 필요 없다.
    수종을 인식하지 못하는 행은 Adapter 경계에서 걸러 Use Case에 깨끗한 엔티티만 전달한다.
    """

    def __init__(
        self,
        csv_path: str | Path,
        refined_path: str | Path = "refined_tree_segments.csv",
        encoding: str = "utf-8-sig",
    ) -> None:
        self._csv_path = Path(csv_path)
        self._refined_path = Path(refined_path)
        self._encoding = encoding

    def find_all(self) -> list[TreeSegment]:
        frame = pd.read_csv(self._csv_path, encoding=self._encoding)
        segments: list[TreeSegment] = []
        for position, row in enumerate(frame.to_dict("records"), start=1):
            segment = self._to_segment(position, row)
            if segment is not None:
                segments.append(segment)
        return segments

    def save_many(self, segments: list[TreeSegment]) -> None:
        records = [
            {
                "id": s.id,
                "road_name": s.road_name,
                "start_latitude": s.start.latitude,
                "start_longitude": s.start.longitude,
                "end_latitude": s.end.latitude,
                "end_longitude": s.end.longitude,
                "species": s.species.value,
                "quantity": s.quantity,
                "managing_agency": s.managing_agency,
            }
            for s in segments
        ]
        pd.DataFrame(records).to_csv(
            self._refined_path, index=False, encoding=self._encoding
        )

    def _to_segment(self, position: int, row: dict[str, Any]) -> TreeSegment | None:
        try:
            species = TreeSpecies.from_label(str(row[_COL_SPECIES]))
        except ValueError:
            return None  # 인식 불가 수종 → 제외(Adapter 경계 책임)

        return TreeSegment(
            id=position,
            road_name=row.get(_COL_ROAD_NAME),
            start=Coordinate(
                latitude=float(row[_COL_START_LAT]),
                longitude=float(row[_COL_START_LNG]),
            ),
            end=Coordinate(
                latitude=float(row[_COL_END_LAT]),
                longitude=float(row[_COL_END_LNG]),
            ),
            species=species,
            quantity=int(row[_COL_QUANTITY]),
            managing_agency=str(row[_COL_AGENCY]),
        )
