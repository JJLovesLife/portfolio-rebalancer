import logging

def setup_logger(name):
	logger = logging.getLogger(name)
	logger.setLevel(logging.DEBUG)

	# Create file handler which logs even debug messages
	fh = logging.FileHandler('portfolio_rebalancer.log', encoding='utf-8')
	fh.setLevel(logging.DEBUG)

	# Create console handler with a higher log level
	ch = logging.StreamHandler()
	ch.setLevel(logging.INFO)

	# Create formatter and add it to the handlers
	formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
	fh.setFormatter(formatter)
	ch.setFormatter(formatter)

	# Add the handlers to the logger
	logger.addHandler(fh)
	logger.addHandler(ch)

	return logger

# logger = setup_logger('PortfolioRebalancer')