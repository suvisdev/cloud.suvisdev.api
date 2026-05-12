from pathlib import Path

import pandas as pd

_DATA_DIR = Path(__file__).resolve().parent
_CSV_PATH = _DATA_DIR / "한국도로공사_교통사고통계_20241231.csv"

class DoroReader:

    def __init__(self):
        pass

    def get_data(self):
        # 한글 CSV 인코딩(utf-8/cp949) 차이를 흡수해서 읽는다.
        try:
            df = pd.read_csv(_CSV_PATH, encoding="utf-8-sig")
        except UnicodeDecodeError:
            df = pd.read_csv(_CSV_PATH, encoding="cp949")
        # 인덱스 1번 행만 반환 (DataFrame 형태 유지)
        return df.iloc[[1]].astype(object).where(df.iloc[[1]].notna(), None)
