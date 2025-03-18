from decimal import Decimal
from market_data.market import Market

class Holding:
	"""
	Holding class to represent a single holding in a portfolio.
	"""

	def __init__(self, symbol: str, share: int | Decimal, market: Market, **kwargs):
		self.symbol = symbol
		self.share = share
		self.price = market.get_price(symbol)
		self.value = self.share * self.price

	def update_share(self, new_share: int | Decimal):
		"""Update the share of the holding."""
		self.share = new_share
		self.value = self.share * self.price
