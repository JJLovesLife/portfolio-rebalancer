from abc import ABC, abstractmethod

class Fetcher(ABC):
    def __init__(self):
        self.header = {
        }

    @abstractmethod
    def fetch_current_value(self) -> float:
        pass
