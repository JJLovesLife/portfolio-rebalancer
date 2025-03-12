import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from portfolio.portfolio import Portfolio

class AllocationTab:
    def __init__(self, parent, portfolio: Portfolio):
        """Initialize the allocation tab."""
        self.parent = parent
        self.portfolio = portfolio
        self.create_tab()

    def create_tab(self):
        """Create the current allocation tab with table and chart."""
        # Create left and right frames
        left_frame = ttk.Frame(self.parent)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        right_frame = ttk.Frame(self.parent)
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
        self.refresh_view()

    def refresh_view(self):
        """Refresh the allocation view with current data."""
        # Clear existing data
        for i in self.allocation_tree.get_children():
            self.allocation_tree.delete(i)

        # Get current allocation
        allocation = self.portfolio.current_allocation()

        # Insert data into treeview
        labels = []
        sizes = []
        items = []
        for asset, value in allocation.items():
            percentage = value / self.portfolio.total_value * 100
            items.append((asset, f"{value:,.2f}", f"{percentage:.2f}%"))

            labels.append(asset)
            sizes.append(percentage)

        # sort labels and sizes by sizes desc
        sorted_indices = sorted(range(len(sizes)), key=lambda i: sizes[i])
        labels = [labels[i] for i in sorted_indices]
        sizes = [sizes[i] for i in sorted_indices]

        for i in sorted_indices:
            self.allocation_tree.insert("", tk.END, values=items[i])

        # Update pie chart
        self.ax.clear()
        patches, texts, autotexts = self.ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        self.ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        self.ax.set_title('Portfolio Allocation')

        # Add legend to the right of the pie chart
        self.ax.legend(patches, labels, loc="center left", bbox_to_anchor=(1, 0.5))

        # Adjust layout to make room for the legend
        self.fig.tight_layout()
        self.canvas.draw()
