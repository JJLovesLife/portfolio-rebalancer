import os
import json

class Market:
    def __init__(self, market_data_file_path, logger):
        self.logger = logger
        self.file_path = market_data_file_path

        if not os.path.exists(self.file_path):
            self.logger.error(f"Market data file not found: {self.file_path}")
            return {}

        with open(self.file_path, 'r') as f:
            self.data = json.load(f)

        self.check()

    def update_market_data(self):
        data = self.data
        if not data:
            self.logger.error("Market data is not available.")
            return
        # store back to file_path
        with open(self.file_path, 'w') as f:
            json.dump(data, f)
        self.logger.info(f"Market data updated successfully.")

    def check(self):
        for symbol, info in self.data.items():
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
                if not isinstance(percentage, (int, float)):
                    self.logger.error(f"Percentage for asset {asset} in symbol {symbol} is not a number.")
                    raise ValueError(f"Percentage for asset {asset} in symbol {symbol} is not a number.")
                if percentage < 0 or percentage > 1:
                    self.logger.error(f"Percentage for asset {asset} in symbol {symbol} is out of range [0, 1].")
                    raise ValueError(f"Percentage for asset {asset} in symbol {symbol} is out of range [0, 1].")
            total_percentage = sum(percentage for asset, percentage in composition.items() if asset != 'update_at')
            if total_percentage != 1:
                self.logger.error(f"Total percentage for symbol {symbol} is not equal to 1.")
                raise ValueError(f"Total percentage for symbol {symbol} is not equal to 1.")

    def get_price(self, symbol: str) -> float:
        if symbol not in self.data:
            self.logger.error(f"Symbol {symbol} not found in market data.")
            raise ValueError(f"Symbol {symbol} not found in market data.")
        return self.data[symbol]['value']

    def get_composition(self, symbol: str) -> dict[str, float]:
        if symbol not in self.data:
            self.logger.error(f"Symbol {symbol} not found in market data.")
            raise ValueError(f"Symbol {symbol} not found in market data.")
        #todo: check update_at
        ret = self.data[symbol]['composition'].copy()
        del ret['update_at']
        return ret
