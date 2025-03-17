# Portfolio Rebalancer

A lightweight tool for managing investment portfolios by automatically calculating asset allocation adjustments to align with your target percentages.

> [!IMPORTANT]
> This project includes AI-generated code and is provided as-is with no warranties or guarantees.

## Getting Started

```bash
# Optional: Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install browser automation dependencies
playwright install --with-deps --no-shell

# Run the application
python src/main.py
```

## Required Configuration

### Calculators
The application requires a calculator implementation to function. Add a `calculator.*.py` file to the `src/rebalancer` directory. Extend the base class in `src/rebalancer/calculator.py` to implement your calculation algorithm for portfolio rebalancing.

## Optional Components

### Market Data Sources
You can optionally add your own market data fetchers by creating a `fetcher.*.py` file in the `src/market_data` directory. Implement the interface defined in `src/market_data/fetcher.py` to automatically retrieve current market values.
