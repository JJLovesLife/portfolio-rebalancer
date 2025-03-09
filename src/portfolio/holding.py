from market_data.market_data import Market

class Holding:
	"""
	Holding class to represent a single holding in a portfolio.
	"""

	def __init__(self, symbol: str, share: int, market: Market):
		self.symbol = symbol
		self.share = share
		self.price = market.get_price(symbol)
		self.value = self.share * self.price
