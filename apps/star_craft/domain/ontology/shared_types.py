"""
Spoke 간 직접 의존 없이 공유할 공통 타입 온톨로지.
Spoke는 이 파일만 import해서 타입 계약을 맞춘다.
"""
from typing import TypeAlias

UserId: TypeAlias = int
MovieId: TypeAlias = int
SpokeId: TypeAlias = str
