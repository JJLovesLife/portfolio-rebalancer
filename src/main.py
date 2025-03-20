import argparse
import tkinter as tk
from portfolio.portfolio import Portfolio
from utils.logger import setup_logger
from gui.gui_app import PortfolioRebalancerGUI

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Portfolio Rebalancer")
    parser.add_argument("--portfolio", type=str, help="Path to portfolio JSON file", default="data/portfolio.json")
    args = parser.parse_args()

    logger = setup_logger('portfolio_rebalancer')

    # Load configuration
    # config = Config('config.json')
    # logger.info("Configuration loaded successfully.")

    # Determine portfolio file path - CLI argument takes precedence over config
    portfolio_file = args.portfolio
    logger.info(f"Using portfolio file: {portfolio_file}")

    portfolio = Portfolio(portfolio_file, "data/market_data.json", logger)

    # GUI interface
    root = tk.Tk()

    app = PortfolioRebalancerGUI(root, portfolio)
    root.mainloop()

if __name__ == "__main__":
    main()