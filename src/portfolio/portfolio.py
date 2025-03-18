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

	def update_holdings(self, new_shares: dict[str, Decimal | int]) -> bool:
		"""Update holdings based on the changes provided."""
		for i, holding in enumerate(self.holdings):
			if holding.symbol in new_shares:
				new_share = new_shares[holding.symbol]
				if isinstance(new_share, Decimal) or isinstance(new_share, float):
					assert self.portfolio_data['holdings'][i]['symbol'] == holding.symbol, f"Symbol mismatch for {i}th holding"
					assert self.portfolio_data['holdings'][i]['share'] == holding.share, f"Share mismatch for {holding.symbol}"
					if new_share < 0:
						self.logger.error(f"Invalid new share for {holding.symbol}: {new_share}")
						return False
					holding.update_share(new_share)
					self.portfolio_data['holdings'][i]['share'] = holding.share
				else:
					self.logger.error(f"Invalid change type for {holding.symbol}: {type(new_share)}")
					return False
				del new_shares[holding.symbol]
		if new_shares:
			self.logger.error(f"Invalid shares provided: {new_shares}")
			return False

		# Recalculate total value before saving
		self.total_value = sum(holding.value for holding in self.holdings)
		self.save_portfolio()
		return True

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

	def save_portfolio(self):
		"""Save portfolio data to the portfolio file."""
		with open(self.portfolio_file, 'w', encoding='utf-8') as f:
			simplejson.dump(self.portfolio_data, f, ensure_ascii=False, indent='\t')

	def get_target_percentage_configurations(self) -> list[str]:
		"""Get a list of all available target percentage configurations."""
		return list(self.portfolio_data['target_percentages'].keys())
	
	def get_selected_target_percentage(self) -> str:
		"""Get the name of the currently selected target percentage configuration."""
		return self.portfolio_data['selected_target_percentage']
	
	def set_default_target_percentage(self, config_name: str) -> bool:
		"""Set the specified configuration as the default."""
		if config_name in self.portfolio_data['target_percentages']:
			self.portfolio_data['selected_target_percentage'] = config_name
			self.save_portfolio()
			return True
		return False
	
	def create_new_target_percentage(self, name: str, create_from: str) -> bool:
		"""Create a new target percentage configuration."""
		if name in self.portfolio_data['target_percentages'] or create_from not in self.portfolio_data['target_percentages']:
			return False
		
		self.portfolio_data['target_percentages'][name] = self.portfolio_data['target_percentages'][create_from].copy()
		self.portfolio_data['target_percentages'][name]['update_at'] = datetime.now().strftime('%Y-%m-%d')
		self.save_portfolio()
		return True

	def target_percentages(self, selected: str = '') -> dict[str, float]:
		if selected == '':
			selected = self.portfolio_data['selected_target_percentage']
		ret = self.portfolio_data['target_percentages'][selected].copy()
		if 'update_at' in ret:
			del ret['update_at']
		return ret

	def update_target_percentages(self, target_percentages: dict[str, Decimal], selected: str = ''):
		target_percentages = {k: normalize_fraction(v) for k, v in target_percentages.items() if v != 0}
		self.portfolio_data['target_percentages'][selected] = target_percentages
		self.portfolio_data['target_percentages'][selected]['update_at'] = datetime.now().strftime('%Y-%m-%d')
		self.save_portfolio()
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
