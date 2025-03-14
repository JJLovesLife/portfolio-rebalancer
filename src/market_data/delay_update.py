class DelayedUpdateError(Exception):
	"""Custom exception for handling delayed market data updates."""
	def __init__(self, message):
		self.message = message
		super().__init__(self.message)
