import tkinter as tk
from tkinter import ttk, messagebox
from portfolio.portfolio import Portfolio
from rebalancer.calculator import Calculator

class AdjustmentsTab:
    def __init__(self, parent, portfolio: Portfolio, calculator: Calculator):
        """Initialize the adjustments tab."""
        self.parent = parent
        self.portfolio = portfolio
        self.calculator = calculator
        self.create_tab()

    def create_tab(self):
        """Create the rebalancing adjustments tab."""
        # Create the treeview
        self.adjustments_tree = ttk.Treeview(self.parent, columns=("Asset", "Current", "Target", "Adjustment", "Action"), show="headings")
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

        scrollbar = ttk.Scrollbar(self.parent, orient=tk.VERTICAL, command=self.adjustments_tree.yview)
        self.adjustments_tree.configure(yscroll=scrollbar.set)

        # Button to generate report
        btn_frame = ttk.Frame(self.parent)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        export_btn = ttk.Button(btn_frame, text="Export Report", command=self.export_report)
        export_btn.pack(side=tk.RIGHT, padx=5)

        refresh_btn = ttk.Button(btn_frame, text="Refresh", command=self.refresh_view)
        refresh_btn.pack(side=tk.RIGHT, padx=5)

        # Pack the treeview and scrollbar
        self.adjustments_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Populate with data
        self.refresh_view()

    def refresh_view(self):
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
            target_pct = target_pcts.get(asset, 0) * 100  # Convert from decimal to percentage
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
            for asset, amount in adjustments.items():
                action = "Buy" if amount > 0 else "Sell" if amount < 0 else "No Change"
                amount_abs = abs(amount)
                report += f"  {asset}: {action} ${amount_abs:,.2f}\n"

            # Save to file
            with open("rebalancing_report.txt", "w") as f:
                f.write(report)

            messagebox.showinfo("Export Complete", "Report exported to rebalancing_report.txt")

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export report: {str(e)}")
