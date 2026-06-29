import pandas as pd

from gildle.adapter.outbound.repositories.traffic_authority_hazard_zone_repository import (
    TrafficAuthorityHazardZoneRepository,
)
from gildle.domain.value_objects.coordinate import Coordinate


def _write_csv(path, rows):
    pd.DataFrame(rows).to_csv(path, index=False, encoding="utf-8-sig")


def _row(**overrides):
    base = {
        "시도": "서울특별시",
        "지점명": "여의도 결빙 다발지역",
        "위도": 37.521,
        "경도": 126.924,
        "반경": 200.0,
        "사고건수": 8,
    }
    base.update(overrides)
    return base


class TestFindAll:
    def test_seoul_rows_become_hazard_zones(self, tmp_path):
        csv = tmp_path / "hazards.csv"
        _write_csv(csv, [_row()])
        repo = TrafficAuthorityHazardZoneRepository(csv_path=csv)

        zones = repo.find_all()

        assert len(zones) == 1
        assert zones[0].center == Coordinate(latitude=37.521, longitude=126.924)
        assert zones[0].radius_meters == 200.0
        assert zones[0].accident_count == 8
        assert zones[0].description == "여의도 결빙 다발지역"

    def test_non_seoul_rows_are_filtered_out(self, tmp_path):
        csv = tmp_path / "hazards.csv"
        _write_csv(csv, [_row(), _row(시도="부산광역시", 지점명="부산 지점")])
        repo = TrafficAuthorityHazardZoneRepository(csv_path=csv)

        zones = repo.find_all()

        assert len(zones) == 1
        assert zones[0].description == "여의도 결빙 다발지역"
