from decimal import Decimal
from datetime import datetime, date, timedelta
import os
import json
import shutil
import time
import simplejson
from market_data import market_fetcher
from market_data.FX import ExchangeRate
from market_data.delay_update import DelayedUpdateError

class Market:
    def __init__(self, market_data_file_path, logger):
        self.logger = logger
        self.file_path = market_data_file_path
        self.FX = ExchangeRate(self.logger)
        self.update_delayed = set()

        if not os.path.exists(self.file_path):
            self.logger.error(f"Market data file not found: {self.file_path}")
            return {}

        with open(self.file_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f, parse_float=Decimal)
        self.init_data = {
            'update_at': '0001-01-01',
            'value': 0,
            'kind': 'unknown',
            'composition': {
                'update_at': '0001-01-01',
                'unknown': 1
            }
        }
        self.check()

    def update_market_data(self):
        self.check()
        data = self.data
        if not data:
            self.logger.error("Market data is not available.")
            return
        if not getattr(self, 'history_saved', False):
            # make sure .history folder is created
            # save self.file_path to .history with timestamp
            if not os.path.exists('.history'):
                os.makedirs('.history')
            history_file_path = os.path.join('.history', f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.path.basename(self.file_path)}")
            # copy self.file_path to history_file_path, not json dump
            shutil.copyfile(self.file_path, history_file_path)
            self.history_saved = True
        # store back to file_path
        with open(self.file_path, 'w', encoding='utf-8') as f:
            simplejson.dump(data, f, ensure_ascii=False, indent='\t')
        self.logger.info("Market data updated successfully.")
        time.sleep(1)

    def check(self):
        for symbol, info in {**{'unknown': self.init_data}, **self.data['holdings']}.items():
            if 'value' not in info or 'update_at' not in info or 'composition' not in info:
                self.logger.error(f"Missing property for symbol {symbol}.")
                raise ValueError(f"Missing property for symbol {symbol}.")
            composition = info['composition']
            if not isinstance(composition, dict):
                self.logger.error(f"Composition for symbol {symbol} is not a dictionary.")
                raise ValueError(f"Composition for symbol {symbol} is not a dictionary.")
            if 'update_at' not in composition:
                self.logger.error(f"Missing update_at in composition for symbol {symbol}.")
                raise ValueError(f"Missing update_at in composition for symbol {symbol}.")
            for asset, percentage in composition.items():
                if asset == 'update_at':
                    continue
                if not isinstance(percentage, (int, Decimal)):
                    self.logger.error(f"Percentage for asset {asset} in symbol {symbol} is not a number.")
                    raise ValueError(f"Percentage for asset {asset} in symbol {symbol} is not a number.")
            total_percentage = sum(percentage for asset, percentage in composition.items() if asset != 'update_at')
            if total_percentage != 1:
                self.logger.error(f"Total percentage for symbol {symbol} is not equal to 1.")
                raise ValueError(f"Total percentage for symbol {symbol} is not equal to 1.")

    def get_composition(self, symbol: str) -> dict[str, Decimal]:
        symbol_data = self.get_symbol(symbol)
        ret = symbol_data['composition'].copy()
        del ret['update_at']
        if symbol_data['kind'] == 'ETF联接':
            # change the 'ETF' composition to its corresponding 'ETF' symbol's composition
            etf_pct = ret['ETF']
            del ret['ETF']
            etf_composition = self.get_symbol(market_fetcher[symbol].ETF)['composition']
            for asset, percentage in etf_composition.items():
                if asset == 'update_at':
                    continue
                if asset not in ret:
                    ret[asset] = 0
                ret[asset] += percentage * etf_pct
        return ret

    def get_symbol(self, symbol: str):
        holdings = self.data['holdings']
        if symbol not in holdings:
            holdings[symbol] = self.init_data.copy()
        expired_time = datetime.strptime(holdings[symbol]['update_at'], '%Y-%m-%d') + timedelta(days=1, hours=9)
        if expired_time < datetime.now() and symbol in market_fetcher and symbol not in self.update_delayed:
            self.logger.info(f"Fetching new data for {symbol}.")
            try:
                holdings[symbol]['kind'] = market_fetcher[symbol].kind
                (value, value_date) = market_fetcher[symbol].fetch_current_value(self.logger)
                if value_date is not None and value_date < date.today():
                    raise DelayedUpdateError("latest data is not available.")
                holdings[symbol]['value'] = value
                if market_fetcher[symbol].fixed_composition() is not None:
                    holdings[symbol]['composition'] = market_fetcher[symbol].fixed_composition()
                    holdings[symbol]['composition']['update_at'] = '0001-01-01'
                else:
                    composition_update_time = market_fetcher[symbol].fetch_composition_update_time(self.logger)
                    prev_update_time = datetime.strptime(holdings[symbol]['composition']['update_at'], '%Y-%m-%d').date()
                    if composition_update_time > prev_update_time or prev_update_time < date.today() - timedelta(days=30):
                        if composition_update_time > prev_update_time:
                            prompt = 'The composition data has been updated. Please enter the new composition data: '
                        else:
                            prompt = 'The composition data is older than 30 days. Please enter the new composition data: '

                        composition_str = input(prompt)
                        composition = {}
                        if composition_str:
                            composition_str = composition_str.replace('=', ':')
                            for asset in composition_str.split(';'):
                                name, percentage = asset.split(':')
                                composition[name] = Decimal(percentage)
                            if sum(composition.values()) != 1:
                                composition['cash'] = 1 - sum(composition.values())
                        else:
                            # no update
                            composition = holdings[symbol]['composition'].copy()
                            del composition['update_at']
                            assert sum(composition.values()) == 1
                        holdings[symbol]['composition'] = composition
                        holdings[symbol]['composition']['update_at'] = date.today().strftime('%Y-%m-%d')
                holdings[symbol]['update_at'] = date.today().strftime('%Y-%m-%d')
                self.update_market_data()
            except DelayedUpdateError as e:
                self.logger.info(f"Delayed update for {symbol}: {e}")
                self.update_delayed.add(symbol)
            except Exception as e:
                self.logger.error(f"Failed to fetch data for {symbol}: {e}")
                raise
        if symbol not in market_fetcher:
            if not hasattr(self, 'warned'):
                self.warned = set()
            if symbol not in self.warned:
                self.warned.add(symbol)
                self.logger.warning(f"{symbol} has no fetcher defined.")
        return holdings[symbol]

    def iter_symbols(self):
        for symbol in self.data['holdings']:
            yield symbol, self.get_symbol(symbol)

    def get_price(self, symbol: str) -> Decimal:
        value = self.get_symbol(symbol)['value']
        if isinstance(value, Decimal) or isinstance(value, int):
            return value
        # split first character, and left
        currency_symbol = value[0]
        value = Decimal(value[1:])
        for currency, info in self.data['exchange_rate'].items():
            if info['symbol'] == currency_symbol:
                expired_time = datetime.strptime(info['update_at'], '%Y-%m-%d') + timedelta(days=1, hours=9)
                if expired_time < datetime.now():
                    info['rate'] = self.FX.get_exchange_rate(currency)
                    info['update_at'] = date.today().strftime('%Y-%m-%d')
                    self.update_market_data()
                return value * info['rate']
        raise ValueError(f"Unsupported currency: {currency}")
