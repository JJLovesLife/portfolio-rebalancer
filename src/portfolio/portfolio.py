import os
import json
from portfolio.holding import Holding
from market_data.market_data import Market

class Portfolio:
    def __init__(self, portfolio_file, market_data_path, logger):
        self.logger = logger
        if not os.path.exists(portfolio_file):
            self.logger.error(f"Portfolio file not found: {portfolio_file}")
            return

        self.market = Market(market_data_path, self.logger)

        with open(portfolio_file, 'r') as f:
            self.portfolio_data = json.load(f)
            self.holdings = [Holding(market=self.market, **holding) for holding in self.portfolio_data['holdings']]

    def current_allocation(self):
        total_value = self.total_value()
        allocation = {holding.symbol: { 'value': holding.value, 'percentage': (holding.value / total_value) * 100 } for holding in self.holdings}
        return allocation

    def total_value(self):
        if not hasattr(self, '_total_value'):
            self._total_value = sum(holding.value for holding in self.holdings)
        return self._total_value

    def target_percentages(self) -> dict[str, float]:
        return self.portfolio_data['target_percentages']
