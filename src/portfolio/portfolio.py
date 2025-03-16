from datetime import datetime
import os
import json
import simplejson
from portfolio.holding import Holding
from market_data.market import Market
from decimal import Decimal

class Portfolio:
	def __init__(self, portfolio_file, market_data_path, logger):
		self.logger = logger
		self.portfolio_file = portfolio_file
		if not os.path.exists(portfolio_file):
			self.logger.error(f"Portfolio file not found: {portfolio_file}")
			return

		self.market = Market(market_data_path, self.logger)

		with open(portfolio_file, 'r', encoding='utf-8') as f:
			self.portfolio_data = json.load(f, parse_float=Decimal)
			self.holdings = [Holding(market=self.market, **holding) for holding in self.portfolio_data['holdings']]
		self.holdings_map = {holding.symbol: holding for holding in self.holdings}

		self.total_value = sum(holding.value for holding in self.holdings)

	def get_holding(self, symbol: str) -> Holding | None:
		return self.holdings_map.get(symbol, None)

	def current_allocation(self, merge: bool = False) -> dict[str, Decimal]:
		allocation = {}
		for holding in self.holdings:
			for asset, pct in self.market.get_composition(holding.symbol).items():
				if asset not in allocation:
					allocation[asset] = 0
				allocation[asset] += holding.value * pct
		if merge:
			for merge_from, merge_to in self.portfolio_data['merge'].items():
				if merge_from in allocation:
					if merge_to not in allocation:
						allocation[merge_to] = 0
					allocation[merge_to] += allocation[merge_from]
					del allocation[merge_from]
		return allocation

	def target_percentages(self) -> dict[str, float]:
		ret = self.portfolio_data['target_percentages']
		if 'update_at' in ret:
			del ret['update_at']
		return ret

	def update_target_percentages(self, target_percentages: dict[str, Decimal]):
		target_percentages = {k: normalize_fraction(v) for k, v in target_percentages.items() if v != 0}
		self.portfolio_data['target_percentages'] = target_percentages
		self.portfolio_data['target_percentages']['update_at'] = datetime.now().strftime('%Y-%m-%d')
		with open(self.portfolio_file, 'w', encoding='utf-8') as f:
			simplejson.dump(self.portfolio_data, f, ensure_ascii=False, indent='\t')
		return

	def rebalance_parameters(self) -> dict[str, float]:
		return {
			'monthly_salary': self.portfolio_data['monthly_salary'],
			'yearly_spending': self.portfolio_data['yearly_spending'],
			'target_cash': self.portfolio_data['target_cash'],
		}

def normalize_fraction(d: Decimal) -> Decimal:
	normalized = d.normalize()
	sign, digit, exponent = normalized.as_tuple()
	return normalized if exponent <= 0 else normalized.quantize(1)
