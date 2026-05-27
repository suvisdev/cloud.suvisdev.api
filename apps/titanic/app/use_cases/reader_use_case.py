import pandas as pd


class WalterReader:
    """내부 파일 접근이 제거된 타이타닉 데이터 리더."""

    def __init__(self) -> None:
        pass

    def get_dataframe(self) -> pd.DataFrame:
        raise RuntimeError(
            "프로젝트 내부 CSV 읽기 기능이 제거되었습니다. 외부 저장소/DB 경로를 사용하세요."
        )

    def get_data(self) -> pd.DataFrame:
        raise RuntimeError(
            "프로젝트 내부 CSV 읽기 기능이 제거되었습니다. 외부 저장소/DB 경로를 사용하세요."
        )

    def get_count(self) -> int:
        raise RuntimeError(
            "프로젝트 내부 CSV 읽기 기능이 제거되었습니다. 외부 저장소/DB 경로를 사용하세요."
        )

    def get_survived_count(self) -> int:
        raise RuntimeError(
            "프로젝트 내부 CSV 읽기 기능이 제거되었습니다. 외부 저장소/DB 경로를 사용하세요."
        )

    def get_dead_count(self) -> int:
        raise RuntimeError(
            "프로젝트 내부 CSV 읽기 기능이 제거되었습니다. 외부 저장소/DB 경로를 사용하세요."
        )
