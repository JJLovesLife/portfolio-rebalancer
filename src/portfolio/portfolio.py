import os
import json
from portfolio.holding import Holding
from market_data.market import Market

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

        self.total_value = sum(holding.value for holding in self.holdings)

    def current_allocation(self):
        allocation = {}
        for holding in self.holdings:
            for asset, pct in self.market.get_composition(holding.symbol).items():
                if asset not in allocation:
                    allocation[asset] = 0
                allocation[asset] += holding.value * pct
        return allocation

    def target_percentages(self) -> dict[str, float]:
        return self.portfolio_data['target_percentages']

    def update_target_percentages(self, target_percentages: dict[str, float]):
        #todo
        return