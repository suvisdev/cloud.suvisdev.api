import json
from pathlib import Path
import pandas as pd

_DATA_DIR = Path(__file__).resolve().parent.parent
_CSV_PATH = _DATA_DIR / "Titanic-Dataset.csv"


class WalterReader:
    """타이타닉 승객 데이터(CSV)에 접근하는 데이터 액세스 계층(Repository)."""

    def __init__(self) -> None:
        pass

    def get_dataframe(self) -> pd.DataFrame:
        """전체 타이타닉 데이터프레임을 반환합니다."""
        if not _CSV_PATH.is_file():
            raise FileNotFoundError(f"타이타닉 CSV 파일을 찾을 수 없습니다: {_CSV_PATH}")
        return pd.read_csv(_CSV_PATH)

    def get_data(self) -> pd.DataFrame:
        """인덱스 1번 행만 반환 (DataFrame 형태 유지 - 기존 호환용)."""
        df = self.get_dataframe()
        return df.iloc[[0]].astype(object).where(df.iloc[[0]].notna(), None)

    def get_count(self) -> int:
        """전체 승객 수(전체 행 개수)를 반환합니다."""
        df = self.get_dataframe()
        return len(df)

    def get_survived_count(self) -> int:
        """생존 승객 수를 반환합니다."""
        df = self.get_dataframe()
        return int((df["Survived"] == 1).sum())

    def get_dead_count(self) -> int:
        """사망 승객 수를 반환합니다."""
        df = self.get_dataframe()
        return int((df["Survived"] == 0).sum())
