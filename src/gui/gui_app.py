import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd
from portfolio.portfolio import Portfolio
from rebalancer.calculator import Calculator

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
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create allocation tab
        allocation_frame = ttk.Frame(notebook)
        notebook.add(allocation_frame, text="Current Allocation")
        self.create_allocation_tab(allocation_frame)

        # temporary disable this before composition logic is implemented
        # Create adjustments tab
        # adjustments_frame = ttk.Frame(notebook)
        # notebook.add(adjustments_frame, text="Rebalancing Adjustments")
        # self.create_adjustments_tab(adjustments_frame)

    def create_allocation_tab(self, parent):
        """Create the current allocation tab with table and chart."""
        # Create left and right frames
        left_frame = ttk.Frame(parent)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        right_frame = ttk.Frame(parent)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create table in left frame
        self.allocation_tree = ttk.Treeview(left_frame, columns=("Asset", "Value", "Percentage"), show="headings")
        self.allocation_tree.heading("Asset", text="Asset")
        self.allocation_tree.heading("Value", text="Value")
        self.allocation_tree.heading("Percentage", text="Percentage")

        self.allocation_tree.column("Asset", width=120)
        self.allocation_tree.column("Value", width=100)
        self.allocation_tree.column("Percentage", width=100)

        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.allocation_tree.yview)
        self.allocation_tree.configure(yscroll=scrollbar.set)

        self.allocation_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create pie chart in right frame
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Populate with data
        self.refresh_allocation_view()

    def create_adjustments_tab(self, parent):
        """Create the rebalancing adjustments tab."""
        # Create the treeview
        self.adjustments_tree = ttk.Treeview(parent, columns=("Asset", "Current", "Target", "Adjustment", "Action"), show="headings")
        self.adjustments_tree.heading("Asset", text="Asset")
        self.adjustments_tree.heading("Current", text="Current %")
        self.adjustments_tree.heading("Target", text="Target %")
        self.adjustments_tree.heading("Adjustment", text="Adjustment")
        self.adjustments_tree.heading("Action", text="Action")
        
        self.adjustments_tree.column("Asset", width=120)
        self.adjustments_tree.column("Current", width=80)
        self.adjustments_tree.column("Target", width=80)
        self.adjustments_tree.column("Adjustment", width=100)
        self.adjustments_tree.column("Action", width=150)
        
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.adjustments_tree.yview)
        self.adjustments_tree.configure(yscroll=scrollbar.set)
        
        # Button to generate report
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        
        export_btn = ttk.Button(btn_frame, text="Export Report", command=self.export_report)
        export_btn.pack(side=tk.RIGHT, padx=5)
        
        refresh_btn = ttk.Button(btn_frame, text="Refresh", command=self.refresh_adjustments_view)
        refresh_btn.pack(side=tk.RIGHT, padx=5)
        
        # Pack the treeview and scrollbar
        self.adjustments_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate with data
        self.refresh_adjustments_view()

    def refresh_allocation_view(self):
        """Refresh the allocation view with current data."""
        # Clear existing data
        for i in self.allocation_tree.get_children():
            self.allocation_tree.delete(i)

        # Get current allocation
        allocation = self.portfolio.current_allocation()

        # Insert data into treeview
        labels = []
        sizes = []
        for asset, value in allocation.items():
            percentage = value / self.portfolio.total_value * 100
            self.allocation_tree.insert("", tk.END, values=(asset, f"${value:,.2f}", f"{percentage:.2f}%"))

            labels.append(asset)
            sizes.append(percentage)

        # Update pie chart
        self.ax.clear()
        self.ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        self.ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        self.ax.set_title('Portfolio Allocation')
        self.canvas.draw()

    def refresh_adjustments_view(self):
        """Refresh the adjustments view with current data."""
        # Clear existing data
        for i in self.adjustments_tree.get_children():
            self.adjustments_tree.delete(i)

        # Get adjustments data
        adjustments = self.calculator.calculate_adjustments()

        current_pcts = self.portfolio.current_allocation()
        target_pcts = self.portfolio.target_percentages()

        # Insert data into treeview
        for asset, amount in adjustments.items():
            current_pct = current_pcts[asset] / self.portfolio.total_value * 100 if asset in current_pcts else 0
            target_pct = target_pcts.get(asset, 0)
            action = "Buy" if amount > 0 else "Sell" if amount < 0 else "No Change"
            
            self.adjustments_tree.insert("", tk.END, values=(
                asset, 
                f"{current_pct:.2f}%", 
                f"{target_pct:.2f}%", 
                f"${abs(amount):,.2f}", 
                f"{action} ${abs(amount):,.2f}"
            ))

    def export_report(self):
        """Export the rebalancing report to a file."""
        try:
            # Get adjustments
            adjustments = self.calculator.calculate_adjustments()
            
            # Create a simple report
            report = "Portfolio Rebalancing Report\n"
            report += "============================\n\n"
            
            report += "Current Allocation:\n"
            allocation = self.portfolio.current_allocation()
            for asset, value in allocation.items():
                report += f"  {asset}: ${value:,.2f} ({value / self.portfolio.total_value * 100:.2f}%)\n"

            report += "\nAdjustments Needed:\n"
            for asset, details in adjustments.items():
                action = "Buy" if details.get('amount', 0) > 0 else "Sell" if details.get('amount', 0) < 0 else "No Change"
                amount = abs(details.get('amount', 0))
                report += f"  {asset}: {action} ${amount:,.2f}\n"

            # Save to file
            with open("rebalancing_report.txt", "w") as f:
                f.write(report)
                
            messagebox.showinfo("Export Complete", "Report exported to rebalancing_report.txt")

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export report: {str(e)}")
