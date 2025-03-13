from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal

class Fetcher(ABC):
    def __init__(self, kind: str):
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0',
        }
        self.kind = kind

    @abstractmethod
    def fetch_current_value(self, logger) -> Decimal | str:
        pass

    def fixed_composition(self) -> dict[str, Decimal] | None:
        return None

    @abstractmethod
    def fetch_composition_update_time(self, logger) -> date:
        pass

class ETF联接Fetcher(Fetcher):
    def __init__(self, kind: str, source_ETF: str):
        super().__init__(kind)
        self.ETF = source_ETF
