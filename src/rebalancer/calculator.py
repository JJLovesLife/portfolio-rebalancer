class Calculator:
    """
    Calculator class for determining portfolio adjustments needed to reach target allocations.
    """
    
    def __init__(self, portfolio, target_percentages: dict[str, float]):
        """
        Initialize the calculator with portfolio and target percentages.
        
        Args:
            portfolio: Portfolio object containing current holdings
            target_percentages: Dict mapping asset classes to target percentage allocations
        """
        self.portfolio = portfolio
        self.target_percentages = target_percentages

    def calculate_adjustments(self) -> dict[str, float]:
        """
        Calculate the adjustments needed to rebalance the portfolio.
        
        Returns:
            Dict mapping asset classes to adjustment amounts (positive for buy, negative for sell)
        """
        current_allocation = self.portfolio.current_allocation()
        adjustments = {}
        
        # Calculate target values for each asset class
        for asset_class, target_pct in self.target_percentages.items():
            target_value = self.portfolio.total_value * (target_pct / 100)
            current_value = current_allocation[asset_class]['value'] if asset_class in current_allocation else 0
            adjustment = target_value - current_value
            adjustments[asset_class] = round(adjustment, 2)
            
        return adjustments
        
    def get_rebalance_summary(self):
        """
        Generate a summary of the rebalancing adjustments.
        
        Returns:
            Dict containing current allocation, target allocation, and adjustments
        """
        current_allocation = self.portfolio.current_allocation()
        total_value = self.portfolio.total_value
        adjustments = self.calculate_adjustments()
        
        summary = {
            "total_value": total_value,
            "current_allocation": {},
            "target_allocation": {},
            "adjustments": adjustments
        }
        
        # Calculate current allocation percentages
        for asset_class, value in current_allocation.items():
            summary["current_allocation"][asset_class] = {
                "value": value,
                "percentage": (value / total_value) * 100 if total_value > 0 else 0
            }
            
        # Add target allocation details
        for asset_class, target_pct in self.target_percentages.items():
            target_value = total_value * (target_pct / 100)
            summary["target_allocation"][asset_class] = {
                "value": target_value,
                "percentage": target_pct
            }
            
        return summary