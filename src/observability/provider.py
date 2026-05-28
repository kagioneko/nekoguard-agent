"""
ObservabilityProvider 抽象基底クラス
"""

from abc import ABC, abstractmethod
from .schema import ObservabilitySnapshot


class ObservabilityProvider(ABC):
    """
    Mock と Dynatrace を透過的に切り替えるための抽象基底。
    agent / server は常にこのインターフェースだけを見る。
    """

    @abstractmethod
    def get_snapshot(self, time_window: str = "last_30m") -> ObservabilitySnapshot:
        """最新の観測スナップショットを返す"""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """接続可能かどうかを確認する"""
        ...
