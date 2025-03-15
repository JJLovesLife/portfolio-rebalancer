import tkinter as tk
from tkinter import ttk
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

        # Track window state
        self.window_state = self.root.state()
        self.root.bind("<Configure>", self.on_window_configure)

        self.setup_ui()
        
    def on_window_configure(self, event):
        """Handle window configure events to detect window state changes."""
        # Get current window state
        current_state = self.root.state()

        # If state changed from normal to zoomed (maximized)
        if current_state == 'zoomed' and self.window_state != 'zoomed':
            self.refresh_current_tab()
            
        # If state changed from zoomed (maximized) to normal
        elif current_state != 'zoomed' and self.window_state == 'zoomed':
            self.refresh_current_tab()

        # Update the saved state
        self.window_state = current_state

    def refresh_current_tab(self, event=None):
        """Refresh only the currently active tab."""
        current_tab_index = self.notebook.index(self.notebook.select())

        if current_tab_index == 0 and hasattr(self, 'allocation_tab'):  # Allocation tab
            self.root.after(75, self.allocation_tab.refresh_view)
        elif current_tab_index == 1:  # Configuration tab
            self.root.after(75, self.config_tab.refresh_view)
        # Uncomment when adjustments tab is implemented
        # elif current_tab_index == 2:  # Adjustments tab
        #     self.adjustments_tab.refresh_view()

    def setup_ui(self):
        """Set up the user interface."""
        # Create a notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Bind tab change event
        self.notebook.bind("<<NotebookTabChanged>>", self.refresh_current_tab)

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
            self.calculator
        )

        # Uncomment when adjustments tab is implemented
        # Create adjustments tab
        # adjustments_frame = ttk.Frame(self.notebook)
        # self.notebook.add(adjustments_frame, text="Rebalancing Adjustments")
        # self.adjustments_tab = AdjustmentsTab(adjustments_frame, self.portfolio, self.calculator)
