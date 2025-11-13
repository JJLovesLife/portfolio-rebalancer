from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
from decimal import Decimal
from utils.trading_day import latest_china_trading_day, latest_us_trading_day

class Fetcher(ABC):
    def __init__(self, kind: str):
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0',
        }
        self.kind = kind
        match self.kind:
            case 'US_STOCK' | 'US_FUND':
                self.latest_value_date = latest_us_trading_day
            case 'BTC':
                self.latest_value_date = (datetime.now() + timedelta(hours=-15)).date()
            case _:
                self.latest_value_date = latest_china_trading_day

    @abstractmethod
    def fetch_current_value(self, logger) -> tuple[Decimal | str, date | None]:
        pass

    def fixed_composition(self) -> dict[str, Decimal] | None:
        return None

    @abstractmethod
    def fetch_composition_update_time(self, logger) -> date:
        pass

class MarketPriceFetcher(Fetcher):
    def __init__(self, kind: str):
        super().__init__(kind)

    def fetch_current_market_price(self, logger) -> Decimal | str:
        pass

class ETF联接Fetcher(Fetcher):
    def __init__(self, kind: str, source_ETF: str):
        super().__init__(kind)
        self.ETF = source_ETF
