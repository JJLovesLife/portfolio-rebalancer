import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from portfolio.portfolio import Portfolio
from rebalancer.calculator import Calculator
from gui.tabs.allocation_tab import AllocationTab
from gui.tabs.config_tab import ConfigurationTab
# Uncomment when implemented
# from gui.tabs.adjustments_tab import AdjustmentsTab

class PortfolioRebalancerGUI:
    def __init__(self, root, portfolio: Portfolio):
        """Initialize the GUI application."""
        self.root = root
        self.portfolio = portfolio
        self.calculator = Calculator(portfolio, portfolio.target_percentages())

        self.root.title("Portfolio Rebalancer")
        self.root.geometry("900x600")
        self.root.minsize(800, 500)

        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        # Create a notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create allocation tab
        allocation_frame = ttk.Frame(self.notebook)
        self.notebook.add(allocation_frame, text="Current Allocation")
        self.allocation_tab = AllocationTab(allocation_frame, self.portfolio)

        # Create configuration tab
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text="Configuration")
        self.config_tab = ConfigurationTab(
            config_frame, 
            self.portfolio, 
            self.calculator,
            refresh_callback=self.refresh_all_tabs
        )

        # Uncomment when adjustments tab is implemented
        # Create adjustments tab
        # adjustments_frame = ttk.Frame(self.notebook)
        # self.notebook.add(adjustments_frame, text="Rebalancing Adjustments")
        # self.adjustments_tab = AdjustmentsTab(adjustments_frame, self.portfolio, self.calculator)

    def refresh_all_tabs(self):
        """Refresh all tabs after portfolio changes."""
        self.allocation_tab.refresh_view()
        # Uncomment when adjustments tab is implemented
        # self.adjustments_tab.refresh_view()
