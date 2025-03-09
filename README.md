# Portfolio Rebalancer

This project is a portfolio rebalancing tool that helps users manage their investment portfolios by adjusting asset allocations to meet target percentages.

## Project Structure

```
portfolio-rebalancer
├── src
│   ├── __init__.py
│   ├── main.py
│   ├── portfolio
│   │   ├── __init__.py
│   │   ├── asset.py
│   │   └── portfolio.py
│   ├── rebalancer
│   │   ├── __init__.py
│   │   ├── calculator.py
│   │   └── strategy.py
│   └── utils
│       ├── __init__.py
│       ├── config.py
│       └── logger.py
├── tests
│   ├── __init__.py
│   ├── test_asset.py
│   ├── test_portfolio.py
│   └── test_rebalancer.py
├── data
│   └── sample_portfolio.json
├── config.yaml
├── requirements.txt
└── README.md
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd portfolio-rebalancer
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the portfolio rebalancer, execute the following command:
```
python src/main.py
```

Follow the prompts to input your latest holding data and target asset percentages. The script will calculate the necessary adjustments to rebalance your portfolio.

## Features

- Load portfolio data from a JSON file.
- Calculate current asset allocations.
- Determine necessary adjustments to meet target percentages.
- Logging functionality to track events and errors.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.
