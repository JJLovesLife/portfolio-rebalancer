from datetime import datetime
from decimal import Decimal
import re
import tkinter as tk
from tkinter import ttk, messagebox
from portfolio.portfolio import Portfolio
from rebalancer.calculator import CreateCalculator
from itertools import chain

class AdjustmentsTab:
    def __init__(self, parent, portfolio: Portfolio, get_rebalance_duration, get_selected_target_percentage):
        """Initialize the adjustments tab."""
        self.parent = parent
        self.portfolio = portfolio
        self.get_rebalance_duration = get_rebalance_duration
        self.get_selected_target_percentage = get_selected_target_percentage
        self.create_tab()

    def create_tab(self):
        """Create the rebalancing adjustments tab."""
        # Create the treeview
        self.adjustments_tree = ttk.Treeview(self.parent, columns=("Asset", "Current", "Target", "End", "Adjustment", "AdjPct", "Action"), show="headings")
        self.adjustments_tree.heading("Asset", text="Asset")
        self.adjustments_tree.heading("Current", text="Current %")
        self.adjustments_tree.heading("Target", text="Target %")
        self.adjustments_tree.heading("End", text="End %")
        self.adjustments_tree.heading("Adjustment", text="Adjustment")
        self.adjustments_tree.heading("AdjPct", text="Adjustment %")
        self.adjustments_tree.heading("Action", text="Action")

        self.adjustments_tree.column("Asset", width=80)
        self.adjustments_tree.column("Current", width=60)
        self.adjustments_tree.column("Target", width=60)
        self.adjustments_tree.column("End", width=60)
        self.adjustments_tree.column("Adjustment", width=100)
        self.adjustments_tree.column("AdjPct", width=60)
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

    def refresh_view(self):
        """Refresh the adjustments view with current data."""
        # Clear existing data
        for i in self.adjustments_tree.get_children():
            self.adjustments_tree.delete(i)

        rebalance_duration = self.get_rebalance_duration()
        valid_rebalance_duration = True
        if not isinstance(rebalance_duration, dict):
            valid_rebalance_duration = False
        elif 'unit' not in rebalance_duration or rebalance_duration['unit'] not in ['day', 'month']:
            valid_rebalance_duration = False
        elif 'value' not in rebalance_duration or (not isinstance(rebalance_duration['value'], int) and not isinstance(rebalance_duration['value'], Decimal)):
            valid_rebalance_duration = False

        if not valid_rebalance_duration:
            self.adjustments_tree.insert("", tk.END, values=("Invalid Rebalance Duration", "", "", "", "", "", ""))
            return

        # Get adjustments data
        selected_target_percentage = self.get_selected_target_percentage()
        adjustments = CreateCalculator(self.portfolio, 'standard', selected_target_percentage).calculate_adjustments(rebalance_duration)

        current_pcts = self.portfolio.current_allocation(merge=True)
        target_pcts = self.portfolio.target_percentages(selected=selected_target_percentage)

        # Insert data into treeview
        for asset, [amount, end_pct] in adjustments.items():
            current_pct = current_pcts[asset] / self.portfolio.total_value * 100 if asset in current_pcts else 0
            target_pct = target_pcts.get(asset, 0)
            rebalance_granularity = 'day' if rebalance_duration['unit'] == 'day' else 'week'
            if rebalance_duration['unit'] == 'day':
                amount_per_granularity = amount / rebalance_duration['value']
            else:
                amount_per_granularity = amount / rebalance_duration['value'] / (Decimal(365) / 7 / 12)

            if asset == 'cash':
                action  = "save" if amount > 0 else "spend" if amount < 0 else "No Change"
            else:
                action = "Buy" if amount > 0 else "Sell" if amount < 0 else "No Change"

            self.adjustments_tree.insert("", tk.END, values=(
                asset,
                f"{current_pct:.2f}%",
                f"{target_pct:.2f}%",
                f"{end_pct * 100:.2f}%",
                f"{amount:,.2f}",
                f"{end_pct * 100 - current_pct:.2f}%",
                f"{action} {abs(amount_per_granularity):,.2f} per {rebalance_granularity}"
            ))

    def export_report(self):
        """Export the rebalancing report to a file."""
        try:
            rebalance_duration = self.get_rebalance_duration()
            valid_rebalance_duration = True
            if not isinstance(rebalance_duration, dict):
                valid_rebalance_duration = False
            elif 'unit' not in rebalance_duration or rebalance_duration['unit'] not in ['day', 'month']:
                valid_rebalance_duration = False
            elif 'value' not in rebalance_duration or (not isinstance(rebalance_duration['value'], int) and not isinstance(rebalance_duration['value'], Decimal)):
                valid_rebalance_duration = False
                
            if not valid_rebalance_duration:
                messagebox.showerror("Export Error", "Invalid rebalance duration")
                return
                
            # Get adjustments using CreateCalculator like in refresh_view
            selected_target_percentage = self.get_selected_target_percentage()
            adjustments = CreateCalculator(self.portfolio, 'standard', selected_target_percentage).calculate_adjustments(rebalance_duration)
            current_allocation = self.portfolio.current_allocation(merge=True)
            target_percentages = self.portfolio.target_percentages(selected=selected_target_percentage)
            total_value = self.portfolio.total_value

            # Create a simple report
            report = "Portfolio Rebalancing Report\n"
            report += "============================\n"

            report += f"Total Assets: {self.portfolio.total_value:>12.2f}\n"

            # Get all unique assets from both current and target allocations
            all_assets = set(list(current_allocation.keys()) + list(target_percentages.keys()))

            for asset in chain(['alphabetical order'], sorted(all_assets), ['adjustment order'], adjustments.keys()):
                if asset.endswith('order'):
                    order = asset
                    # Create formatted allocation comparison table
                    report += f"\nCurrent vs Target Allocation ({order}):\n"
                    report += f"--------------------------------{'-' * len(order)}\n"
                    report += f"{'Asset':<15} {'Current Value':<15} {'Current %':<10} {'Target %':<10} {'End %':<10} {'Adjustment %':<12}\n"
                    continue

                current_value = current_allocation.get(asset, 0)
                current_pct = current_value / total_value * 100 if total_value > 0 else 0
                target_pct = target_percentages.get(asset, 0)

                _, end_pct_decimal = adjustments[asset]
                end_pct = end_pct_decimal * 100

                adjustment_pct = end_pct - current_pct

                def is_cjk(text):
                    cjk_pattern = re.compile(r'[\u4E00-\u9FFF\u3400-\u4DBF\u3040-\u30FF\uAC00-\uD7AF]')
                    return bool(cjk_pattern.search(text))

                cjk_cnt = sum(is_cjk(char) for char in asset)
                asset_padded = asset + ' ' * max(0, 15 - len(asset) - cjk_cnt)

                report += f"{asset_padded} {current_value:,.2f}".ljust(31 - cjk_cnt)
                report += f"{current_pct:.2f}%".ljust(11)
                report += f"{target_pct:.2f}%".ljust(11)
                report += f"{end_pct:.2f}%".ljust(11)
                report += f"{adjustment_pct:+.2f}%\n"

            report += "\nAdjustments Needed:\n"
            report += "------------------\n"
            for asset, [amount, _] in adjustments.items():
                if asset == 'cash':
                    action = "Save" if amount > 0 else "Spend" if amount < 0 else "No Change"
                else:
                    action = "Buy" if amount > 0 else "Sell" if amount < 0 else "No Change"
                amount_abs = abs(amount)
                report += f"  {asset}: {action} {amount_abs:,.2f}\n"
                
            # Add rebalance duration information
            rebalance_granularity = 'day' if rebalance_duration['unit'] == 'day' else 'week'
            report += f"\nRebalancing Plan ({rebalance_duration['value']} {rebalance_duration['unit']}s):\n"
            report += f"---------------------------------------------\n"
            for asset, [amount, _] in adjustments.items():
                if amount == 0:
                    continue
                    
                if rebalance_duration['unit'] == 'day':
                    amount_per_granularity = amount / rebalance_duration['value']
                else:
                    amount_per_granularity = amount / rebalance_duration['value'] / (Decimal(365) / 7 / 12)
                    
                if asset == 'cash':
                    action = "Save" if amount > 0 else "Spend" if amount < 0 else "No Change"
                else:
                    action = "Buy" if amount > 0 else "Sell" if amount < 0 else "No Change"
                    
                report += f"  {asset}: {action} {abs(amount_per_granularity):,.2f} per {rebalance_granularity}\n"

            # Ask user for file location
            from tkinter import filedialog
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=datetime.now().strftime("%Y-%m-%d.txt"),
                title="Save Rebalancing Report"
            )
            
            if not file_path:  # User canceled the dialog
                return
                
            # Save to file
            with open(file_path, "w", encoding='utf-8') as f:
                f.write(report)

            messagebox.showinfo("Export Complete", f"Report exported to {file_path}")

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export report: {str(e)}")
