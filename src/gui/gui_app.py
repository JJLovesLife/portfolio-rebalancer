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

        # Create configuration tab
        config_frame = ttk.Frame(notebook)
        notebook.add(config_frame, text="Configuration")
        self.create_config_tab(config_frame)

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

    def create_config_tab(self, parent):
        """Create the configuration tab for target percentages."""
        # Main container frame
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Top frame for treeview and chart
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Left and right frames inside top frame
        left_frame = ttk.Frame(top_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        right_frame = ttk.Frame(top_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Add a frame for the treeview and button
        tree_container = ttk.Frame(left_frame)
        tree_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Create table in left frame
        self.config_tree = ttk.Treeview(tree_container, columns=("Asset", "Target %"), show="headings")
        self.config_tree.heading("Asset", text="Asset")
        self.config_tree.heading("Target %", text="Target %")

        self.config_tree.column("Asset", width=120)
        self.config_tree.column("Target %", width=100)

        # Make tree editable
        self.config_tree.bind("<Double-1>", self.on_config_item_double_click)

        scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.config_tree.yview)
        self.config_tree.configure(yscroll=scrollbar.set)

        self.config_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Add "+" button below the treeview
        add_button = ttk.Button(left_frame, text="+", width=3, command=self.add_new_asset)
        add_button.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=2)

        # Create pie chart in right frame for target allocation preview
        self.config_fig = Figure(figsize=(5, 4), dpi=100)
        self.config_ax = self.config_fig.add_subplot(111)
        self.config_canvas = FigureCanvasTkAgg(self.config_fig, master=right_frame)
        self.config_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Bottom frame for buttons (will be below both treeview and chart)
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        # Total percentage indicator on the left
        self.total_percentage_var = tk.StringVar(value="Total: 0%")
        total_label = ttk.Label(btn_frame, textvariable=self.total_percentage_var)
        total_label.pack(side=tk.LEFT, padx=5)

        # Rebalance duration frame
        duration_frame = ttk.LabelFrame(btn_frame, text="Rebalance Over")
        duration_frame.pack(side=tk.LEFT, padx=10)

        # Duration input and dropdown
        self.duration_value = tk.StringVar(value="1")
        duration_entry = ttk.Entry(duration_frame, textvariable=self.duration_value, width=5)
        duration_entry.pack(side=tk.LEFT, padx=2, pady=2)

        self.duration_unit = tk.StringVar(value="day")
        duration_unit_combo = ttk.Combobox(duration_frame, 
                                          textvariable=self.duration_unit, 
                                          values=["day", "month"],
                                          width=7, 
                                          state="readonly")
        duration_unit_combo.pack(side=tk.LEFT, padx=2, pady=2)

        # Save button on the right
        save_btn = ttk.Button(btn_frame, text="Save Changes", command=self.save_target_allocations)
        save_btn.pack(side=tk.LEFT, padx=5)

        # Populate with data
        self.refresh_config_view()

    def on_config_item_double_click(self, event):
        """Handle double-click on configuration item."""
        # First check if the click is on a header
        region = self.config_tree.identify_region(event.x, event.y)
        if region != "cell":
            return  # Do nothing if clicking on heading

        selected_items = self.config_tree.selection()
        if not selected_items or getattr(self, 'editing', False):
            return
        item = selected_items[0]
        column = self.config_tree.identify_column(event.x)

        # Only allow editing the percentage column
        if column == "#2":  # Target % column
            self.editing = True
            asset = self.config_tree.item(item, "values")[0]
            current_value = self.config_tree.item(item, "values")[1]

            # Remove % sign for editing
            if current_value.endswith('%'):
                current_value = current_value[:-1]

            # Create a popup for editing
            popup = tk.Toplevel()
            popup.title(f"Edit target for {asset}")
            popup.geometry("250x120")
            popup.transient(self.root)

            # Center the popup
            popup.geometry("+%d+%d" % (
                self.root.winfo_rootx() + self.root.winfo_width() // 2 - 125,
                self.root.winfo_rooty() + self.root.winfo_height() // 2 - 50
            ))

            # Add label and entry
            label = ttk.Label(popup, text=f"Target percentage for {asset}:")
            label.pack(pady=(10, 5))

            entry = ttk.Entry(popup)
            entry.insert(0, current_value)
            entry.pack(padx=10, pady=5)
            entry.select_range(0, tk.END)
            entry.focus_set()

            def save_value():
                try:
                    new_value = float(entry.get())
                    if 0 <= new_value <= 100:
                        self.config_tree.item(item, values=(asset, f"{new_value:.2f}%"))
                        self.update_config_preview()
                        popup.destroy()
                        self.editing = False
                    else:
                        messagebox.showerror("Invalid Value", "Percentage must be between 0 and 100.")
                except ValueError:
                    messagebox.showerror("Invalid Value", "Please enter a valid number.")

            def cancel():
                popup.destroy()
                self.editing = False

            # Add buttons
            btn_frame = ttk.Frame(popup)
            btn_frame.pack(fill=tk.X, padx=10, pady=10)

            save_btn = ttk.Button(btn_frame, text="Save", command=save_value)
            save_btn.pack(side=tk.RIGHT, padx=5)

            cancel_btn = ttk.Button(btn_frame, text="Cancel", command=cancel)
            cancel_btn.pack(side=tk.RIGHT, padx=5)

            # Handle Enter key
            entry.bind("<Return>", lambda event: save_value())
            # Handle Escape key
            popup.bind("<Escape>", lambda event: cancel())

    def refresh_config_view(self):
        """Refresh the configuration view with current data."""
        # Clear existing data
        for i in self.config_tree.get_children():
            self.config_tree.delete(i)

        # Get target percentages
        target_pcts = self.portfolio.target_percentages()

        # Insert data into treeview
        for asset, percentage in target_pcts.items():
            self.config_tree.insert("", tk.END, values=(asset, f"{percentage:.2f}%"))

        self.update_config_preview()

    def update_config_preview(self):
        """Update the pie chart preview based on current settings."""
        # Get data from treeview
        labels = []
        sizes = []
        total = 0

        for item in self.config_tree.get_children():
            asset, percentage = self.config_tree.item(item, "values")
            if percentage.endswith('%'):
                percentage = float(percentage[:-1])
            else:
                percentage = float(percentage)

            labels.append(asset)
            sizes.append(percentage)
            total += percentage

        # Update total percentage display
        self.total_percentage_var.set(f"Total: {total:.2f}%")

        # Update pie chart
        self.config_ax.clear()
        self.config_ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        self.config_ax.axis('equal')
        self.config_ax.set_title('Target Allocation')
        self.config_canvas.draw()

    def save_target_allocations(self):
        """Save the target allocations to the portfolio."""
        try:
            new_targets = {}
            total = 0

            # Collect data from treeview
            for item in self.config_tree.get_children():
                asset, percentage = self.config_tree.item(item, "values")
                if percentage.endswith('%'):
                    percentage = float(percentage[:-1])
                else:
                    percentage = float(percentage)

                new_targets[asset] = percentage / 100  # Convert to decimal
                total += percentage

            # Validate total is close to 100%
            if total != 100: # if not 99.5 <= total <= 100.5:
                messagebox.showerror("Invalid Allocation", f"Total allocation must be 100%. Current total: {total:.2f}%")
                return

            # Get rebalance duration
            try:
                duration_value = int(self.duration_value.get())
                if duration_value <= 0:
                    messagebox.showerror("Invalid Duration", "Duration must be a positive number")
                    return
                duration_unit = self.duration_unit.get()
            except ValueError:
                messagebox.showerror("Invalid Duration", "Duration must be a valid number")
                return

            # Store duration information
            self.rebalance_duration = {
                'value': duration_value,
                'unit': duration_unit
            }

            # Update portfolio targets
            self.portfolio.update_target_percentages(new_targets)
            self.calculator = Calculator(self.portfolio, new_targets)

            messagebox.showinfo("Success", "Target allocations updated successfully.")

            # Refresh other views if they exist
            self.refresh_adjustments_view()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save target allocations: {str(e)}")

    def add_new_asset(self):
        """Open a dialog to add a new asset type to the portfolio."""
        popup = tk.Toplevel()
        popup.title("Add New Asset")
        popup.geometry("300x150")
        popup.transient(self.root)

        # Center the popup
        popup.geometry("+%d+%d" % (
            self.root.winfo_rootx() + self.root.winfo_width() // 2 - 150,
            self.root.winfo_rooty() + self.root.winfo_height() // 2 - 75
        ))

        # Asset name
        name_frame = ttk.Frame(popup)
        name_frame.pack(fill=tk.X, padx=10, pady=5)

        name_label = ttk.Label(name_frame, text="Asset Name:")
        name_label.pack(side=tk.LEFT, padx=5, pady=5)

        name_entry = ttk.Entry(name_frame, width=20)
        name_entry.pack(side=tk.LEFT, padx=5, pady=5)
        name_entry.focus_set()

        # Target percentage
        pct_frame = ttk.Frame(popup)
        pct_frame.pack(fill=tk.X, padx=10, pady=5)

        pct_label = ttk.Label(pct_frame, text="Target %:")
        pct_label.pack(side=tk.LEFT, padx=5, pady=5)

        pct_entry = ttk.Entry(pct_frame, width=10)
        pct_entry.pack(side=tk.LEFT, padx=5, pady=5)
        pct_entry.insert(0, "0.00")

        # Button frame
        btn_frame = ttk.Frame(popup)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        def save_asset():
            asset_name = name_entry.get().strip()

            if not asset_name:
                messagebox.showerror("Invalid Input", "Asset name cannot be empty.")
                return

            # Check if asset already exists
            for item in self.config_tree.get_children():
                if self.config_tree.item(item, "values")[0] == asset_name:
                    messagebox.showerror("Duplicate Asset", f"Asset '{asset_name}' already exists.")
                    return

            try:
                percentage = float(pct_entry.get())
                if percentage < 0 or percentage > 100:
                    messagebox.showerror("Invalid Percentage", "Percentage must be between 0 and 100.")
                    return

                # Add to treeview
                self.config_tree.insert("", tk.END, values=(asset_name, f"{percentage:.2f}%"))
                self.update_config_preview()
                popup.destroy()

            except ValueError:
                messagebox.showerror("Invalid Input", "Target percentage must be a valid number.")

        def cancel():
            popup.destroy()

        add_btn = ttk.Button(btn_frame, text="Add Asset", command=save_asset)
        add_btn.pack(side=tk.RIGHT, padx=5)

        cancel_btn = ttk.Button(btn_frame, text="Cancel", command=cancel)
        cancel_btn.pack(side=tk.RIGHT, padx=5)

        # Handle Enter key
        popup.bind("<Return>", lambda event: save_asset())
        # Handle Escape key
        popup.bind("<Escape>", lambda event: cancel())

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

    def refresh_adjustments_view(self):
        return # temporary disable this
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
