from abc import ABC, abstractmethod
from portfolio.portfolio import Portfolio
from decimal import Decimal
import importlib
from os import path

class Calculator(ABC):

	def __init__(self, portfolio: Portfolio):
		self.portfolio = portfolio

	@abstractmethod
	def calculate_adjustments(self, duration) -> dict[str, Decimal]:
		pass

def CreateCalculator(portfolio: Portfolio, method: str, *args, **kwargs):
	"""Factory function to create a calculator instance based on the specified method."""
	calculator_path = path.join(path.dirname(__file__), f'calculator.{method}.py')
	spec = importlib.util.spec_from_file_location(f"calculator.{method}", calculator_path)
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	StandardCalculator = module.StandardCalculator
	return StandardCalculator(portfolio, *args, **kwargs)
