from abc import ABC, abstractmethod
from datetime import date

class Fetcher(ABC):
    def __init__(self):
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0',
        }

    @abstractmethod
    def fetch_current_value(self) -> float:
        pass

    @abstractmethod
    def fetch_composition_update_time(self) -> date:
        pass
