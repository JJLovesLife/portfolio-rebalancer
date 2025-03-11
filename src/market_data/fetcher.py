from abc import ABC, abstractmethod
from datetime import date

class Fetcher(ABC):
    def __init__(self, kind: str):
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0',
        }
        self.kind = kind

    @abstractmethod
    def fetch_current_value(self, logger) -> float:
        pass

    @abstractmethod
    def fetch_composition_update_time(self, logger) -> date:
        pass
