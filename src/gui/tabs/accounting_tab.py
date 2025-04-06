import tkinter as tk
from tkinter import ttk, messagebox
from decimal import Decimal
from portfolio.portfolio import Portfolio

class AccountingTab:
    def __init__(self, parent, portfolio: Portfolio):
        """Initialize the Accounting tab."""
        self.parent = parent
        self.portfolio = portfolio
        self.pending_changes = {}  # Track pending share changes {symbol: new_share}

        # Define colors for modified entries
        self.modified_color = "#CC0000"  # Red color for modified values

        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface for the Accounting tab."""
        # Create a frame for the holdings table
        table_frame = ttk.LabelFrame(self.parent, text="Holdings")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create a scrollable frame for holdings
        self.canvas = tk.Canvas(table_frame)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Add mouse wheel scrolling support
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Create table headers
        headers = ["Symbol", "Current Share", "New Share", "Add/Subtract", "Apply"]
        for col, header in enumerate(headers):
            ttk.Label(self.scrollable_frame, text=header, font=('Arial', 10, 'bold')).grid(
                row=0, column=col, padx=5, pady=5, sticky="w"
            )

        # Button frame for actions
        button_frame = ttk.Frame(self.parent)
        button_frame.pack(fill=tk.X, pady=10)

        # Save button
        self.save_button = ttk.Button(button_frame, text="Save Changes", command=self.save_changes)
        self.save_button.pack(side=tk.RIGHT, padx=5)

        # Reset button
        self.reset_button = ttk.Button(button_frame, text="Reset Changes", command=self.reset_changes)
        self.reset_button.pack(side=tk.RIGHT, padx=5)

        # Populate holdings
        self.refresh_view()

    def refresh_view(self):
        """Refresh the view with current portfolio data."""
        # Clear existing entries
        for widget in self.scrollable_frame.winfo_children():
            if int(widget.grid_info()["row"]) > 0:  # Skip headers
                widget.destroy()

        # Dictionary to store entry widgets
        self.share_entries = {}
        self.delta_entries = {}
        self.share_labels = {}  # Track the labels showing current share values

        # Add holdings data
        for i, holding in enumerate(self.portfolio.holdings, start=1):
            symbol = holding.symbol
            current_share = self.pending_changes.get(symbol, holding.share)
            
            # Symbol
            ttk.Label(self.scrollable_frame, text=symbol).grid(
                row=i, column=0, padx=5, pady=3, sticky="w"
            )

            # Current Share - using a normal Label instead of ttk.Label for color and font support
            share_label = tk.Label(
                self.scrollable_frame, 
                text=f"{Decimal(current_share)}",
                anchor="e"
            )

            # Apply color and bold if this symbol has pending changes
            if symbol in self.pending_changes:
                share_label.config(fg=self.modified_color, font=('Arial', 10, 'bold'))

            share_label.grid(row=i, column=1, padx=5, pady=3, sticky="e")
            self.share_labels[symbol] = share_label

            # New Share Entry
            share_entry = ttk.Entry(self.scrollable_frame, width=15)
            share_entry.grid(row=i, column=2, padx=5, pady=3)
            self.share_entries[symbol] = share_entry

            # Add/Subtract Entry
            delta_entry = ttk.Entry(self.scrollable_frame, width=15)
            delta_entry.grid(row=i, column=3, padx=5, pady=3)
            self.delta_entries[symbol] = delta_entry

            # Apply Button
            apply_button = ttk.Button(
                self.scrollable_frame, 
                text="Apply", 
                command=lambda sym=symbol: self.apply_change(sym)
            )
            apply_button.grid(row=i, column=4, padx=5, pady=3)

            # Add Enter key binding for the Apply button
            apply_button.bind("<Return>", lambda event, sym=symbol: self.apply_change(sym))

    def apply_change(self, symbol):
        """Apply the change for a specific holding but only store it temporarily."""
        holding = self.portfolio.get_holding(symbol)
        if not holding:
            return

        share_entry = self.share_entries[symbol]
        delta_entry = self.delta_entries[symbol]

        new_share = share_entry.get().strip()
        delta_share = delta_entry.get().strip()

        try:
            current_share = self.pending_changes.get(symbol, holding.share)

            if new_share:
                # Set absolute share
                new_share_val = Decimal(new_share.replace(',', ''))
                if new_share_val < 0:
                    messagebox.showerror("Error", "Share cannot be negative")
                    return
                self.pending_changes[symbol] = new_share_val
                share_entry.delete(0, tk.END)
            elif delta_share:
                # Apply delta
                delta_share_val = Decimal(delta_share.replace(',', ''))
                new_total = current_share + delta_share_val
                if new_total < 0:
                    messagebox.showerror("Error", "Resulting share would be negative")
                    return
                self.pending_changes[symbol] = new_total
                delta_entry.delete(0, tk.END)
            else:
                return  # No changes to apply

            # Update the displayed current share with modified color and bold font
            self.share_labels[symbol].configure(
                text=f"{Decimal(self.pending_changes[symbol])}",
                fg=self.modified_color,
                font=('Arial', 10, 'bold')
            )

        except ValueError:
            messagebox.showerror("Error", "Invalid number format")

    def save_changes(self):
        """Save all pending changes to the portfolio."""
        try:
            pending_changes = self.pending_changes
            if not pending_changes:
                messagebox.showinfo("Info", "No changes to save")
                return

            if self.portfolio.update_holdings(pending_changes):
                messagebox.showinfo("Success", "Portfolio changes saved successfully")
                self.pending_changes = {}
                self.refresh_view()
            else:
                messagebox.showerror("Error", "Failed to update holdings")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save changes: {str(e)}")

    def reset_changes(self):
        """Reset all pending changes."""
        if not self.pending_changes:
            messagebox.showinfo("Info", "No changes to reset")
            return

        self.pending_changes.clear()
        self.refresh_view()
        messagebox.showinfo("Info", "All pending changes have been reset")

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
