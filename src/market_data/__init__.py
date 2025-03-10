import os
import importlib.util
import glob
from typing import Dict
from market_data.fetcher import Fetcher

# Initialize the market_fetcher dictionary
market_fetcher: Dict[str, Fetcher] = {}

# Get the directory where this __init__.py file is located
current_dir = os.path.dirname(os.path.abspath(__file__))

# Find all fetcher.*.py files in the current directory
fetcher_files = glob.glob(os.path.join(current_dir, 'fetcher.*.py'))

# Import each file
for fetcher_file in fetcher_files:
	# Get module name without .py extension
	module_name = os.path.basename(fetcher_file)[:-3]  # Remove ".py"
	
	try:
		# Use importlib.util for more direct file importing
		spec = importlib.util.spec_from_file_location(module_name, fetcher_file)
		module = importlib.util.module_from_spec(spec)
		spec.loader.exec_module(module)
	except Exception as e:
		print(f"Error importing {fetcher_file}: {e}")
