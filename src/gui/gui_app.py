import tkinter as tk
from tkinter import ttk
from portfolio.portfolio import Portfolio
from gui.tabs.allocation_tab import AllocationTab
from gui.tabs.config_tab import ConfigurationTab
from gui.tabs.adjustments_tab import AdjustmentsTab

class PortfolioRebalancerGUI:
    def __init__(self, root, portfolio: Portfolio):
        """Initialize the GUI application."""
        self.root = root
        self.portfolio = portfolio

        self.root.title("Portfolio Rebalancer")
        self.root.geometry("900x600")
        self.root.minsize(800, 500)

        # Track window state
        self.window_state = self.root.state()
        self.root.bind("<Configure>", self.on_window_configure)
        
        # Add keyboard bindings for tab navigation
        self.root.bind("<Control-Tab>", self.next_tab)
        self.root.bind("<Control-Shift-Tab>", self.previous_tab)

        self.setup_ui()

    def on_window_configure(self, event):
        """Handle window configure events to detect window state changes."""
        # Get current window state
        current_state = self.root.state()

        # If state changed from normal to zoomed (maximized)
        if current_state == 'zoomed' and self.window_state != 'zoomed':
            self.refresh_current_tab(resize=True)

        # If state changed from zoomed (maximized) to normal
        elif current_state != 'zoomed' and self.window_state == 'zoomed':
            self.refresh_current_tab(resize=True)

        # Update the saved state
        self.window_state = current_state
    
    def next_tab(self, event=None):
        """Switch to the next tab."""
        current_tab = self.notebook.index(self.notebook.select())
        next_tab = (current_tab + 1) % self.notebook.index("end")
        self.notebook.select(next_tab)
        return "break"  # Prevent default behavior
        
    def previous_tab(self, event=None):
        """Switch to the previous tab."""
        current_tab = self.notebook.index(self.notebook.select())
        prev_tab = (current_tab - 1) % self.notebook.index("end")
        self.notebook.select(prev_tab)
        return "break"  # Prevent default behavior

    def refresh_current_tab(self, event=None, resize=False):
        """Refresh only the currently active tab."""
        current_tab_index = self.notebook.index(self.notebook.select())

        if current_tab_index == 0 and hasattr(self, 'allocation_tab'):  # Allocation tab
            self.root.after(75, self.allocation_tab.refresh_view)
        elif current_tab_index == 1:  # Configuration tab
            self.root.after(75, self.config_tab.refresh_view)
        elif not resize and current_tab_index == 2:  # no need to refresh when size for Adjustments tab
            self.adjustments_tab.refresh_view()

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
            self.portfolio
        )

        # Create adjustments tab
        adjustments_frame = ttk.Frame(self.notebook)
        self.notebook.add(adjustments_frame, text="Rebalancing Adjustments")
        self.adjustments_tab = AdjustmentsTab(adjustments_frame, self.portfolio, self.config_tab.get_rebalance_duration)
