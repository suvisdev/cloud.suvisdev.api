import pandas as pd

from gildle.adapter.outbound.repositories.csv_tree_segment_repository import (
    CsvTreeSegmentRepository,
)
from gildle.domain.entities.tree_segment import TreeSegment
from gildle.domain.value_objects.coordinate import Coordinate
from gildle.domain.value_objects.tree_species import TreeSpecies


def _write_csv(path, rows):
    pd.DataFrame(rows).to_csv(path, index=False, encoding="utf-8-sig")


def _row(**overrides):
    base = {
        "도로명": "여의대로",
        "시작위도": 37.50,
        "시작경도": 127.00,
        "종료위도": 37.52,
        "종료경도": 127.04,
        "수종": "벚나무",
        "수량": 120,
        "관리기관": "영등포구청",
    }
    base.update(overrides)
    return base


class TestFindAll:
    def test_each_row_becomes_tree_segment(self, tmp_path):
        csv = tmp_path / "trees.csv"
        _write_csv(csv, [_row(), _row(수종="느티나무", 도로명="국회대로")])
        repo = CsvTreeSegmentRepository(csv_path=csv)

        segments = repo.find_all()

        assert len(segments) == 2
        assert segments[0].species is TreeSpecies.CHERRY
        assert segments[0].start == Coordinate(latitude=37.50, longitude=127.00)
        assert segments[1].species is TreeSpecies.ZELKOVA

    def test_unrecognized_species_row_is_skipped(self, tmp_path):
        csv = tmp_path / "trees.csv"
        _write_csv(csv, [_row(), _row(수종="소나무")])
        repo = CsvTreeSegmentRepository(csv_path=csv)

        segments = repo.find_all()

        assert len(segments) == 1


class TestSaveMany:
    def test_save_many_writes_refined_csv(self, tmp_path):
        csv = tmp_path / "trees.csv"
        _write_csv(csv, [_row()])
        refined = tmp_path / "refined_tree_segments.csv"
        repo = CsvTreeSegmentRepository(csv_path=csv, refined_path=refined)

        repo.save_many(
            [
                TreeSegment(
                    id=1,
                    road_name="여의대로",
                    start=Coordinate(latitude=37.50, longitude=127.00),
                    end=Coordinate(latitude=37.52, longitude=127.04),
                    species=TreeSpecies.CHERRY,
                    quantity=120,
                    managing_agency="영등포구청",
                )
            ]
        )

        assert refined.exists()
        saved = pd.read_csv(refined)
        assert len(saved) == 1
        assert saved.iloc[0]["road_name"] == "여의대로"
        assert saved.iloc[0]["species"] == "벚나무"
