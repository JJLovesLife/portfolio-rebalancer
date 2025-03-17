import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from portfolio.portfolio import Portfolio
from decimal import Decimal

class ConfigurationTab:
    def __init__(self, parent, portfolio: Portfolio):
        """Initialize the configuration tab."""
        self.parent = parent
        self.portfolio = portfolio
        self.editing = False
        self.current_target_name = self.portfolio.get_selected_target_percentage()
        self.create_tab()

    def create_tab(self):
        """Create the configuration tab for target percentages."""
        # Left and right frames inside top frame
        left_frame = ttk.Frame(self.parent)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        right_frame = ttk.Frame(self.parent)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Add selection combo for different target percentages
        target_frame = ttk.Frame(left_frame)
        target_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        ttk.Label(target_frame, text="Target Configuration:").pack(side=tk.LEFT, padx=5)

        # Get available target percentage configurations
        self.target_lists = self.portfolio.get_target_percentage_configurations()

        self.target_combo = ttk.Combobox(target_frame, values=list(self.target_lists), state="readonly", width=30)
        self.target_combo.pack(side=tk.LEFT, padx=5)
        self.target_combo.current(self.target_lists.index(self.current_target_name))
        self.target_combo.bind("<<ComboboxSelected>>", self.on_target_selected)

        # Add button to create new target configuration
        new_target_btn = ttk.Button(target_frame, text="New", width=5, command=self.create_new_target)
        new_target_btn.pack(side=tk.LEFT, padx=2)

        # Add frame for the treeview and button
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

        # Bottom frame for buttons
        btn_frame = ttk.Frame(left_frame)
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

        # Set as default button
        set_default_btn = ttk.Button(btn_frame, text="Set as Default", command=self.set_as_default)
        set_default_btn.pack(side=tk.LEFT, padx=5)

        # Populate with data
        self.populate_data()

    def on_target_selected(self, event):
        """Handle selection of a different target configuration."""
        self.current_target_name = self.target_combo.get()
        self.populate_data()

    def create_new_target(self):
        """Open a dialog to create a new target configuration."""
        popup = tk.Toplevel()
        popup.title("Create New Target Configuration")
        popup.geometry("300x120")
        popup.transient(self.parent.winfo_toplevel())

        # Center the popup
        popup.geometry("+%d+%d" % (
            self.parent.winfo_rootx() + self.parent.winfo_width() // 2 - 150,
            self.parent.winfo_rooty() + self.parent.winfo_height() // 2 - 60
        ))

        # Name entry
        ttk.Label(popup, text="Configuration Name:").pack(padx=10, pady=(10, 5))
        name_entry = ttk.Entry(popup, width=30)
        name_entry.pack(padx=10, pady=5)
        name_entry.focus_set()

        def save_new_config():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Name cannot be empty")
                return

            if name in self.target_lists:
                messagebox.showerror("Error", f"Configuration '{name}' already exists")
                return

            # Create a new configuration (initially empty)
            success = self.portfolio.create_new_target_percentage(name, self.current_target_name)
            if success:
                self.target_lists = self.portfolio.get_target_percentage_configurations()
                self.target_combo['values'] = self.target_lists
                self.target_combo.current(self.target_lists.index(name))
                self.current_target_name = name
                self.populate_data()
                popup.destroy()
            else:
                messagebox.showerror("Error", "Failed to create new configuration")

        # Buttons
        btn_frame = ttk.Frame(popup)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(btn_frame, text="Create", command=save_new_config).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=popup.destroy).pack(side=tk.RIGHT, padx=5)

        # Handle Enter key
        popup.bind("<Return>", lambda event: save_new_config())
        # Handle Escape key
        popup.bind("<Escape>", lambda event: popup.destroy())

    def set_as_default(self):
        """Set the current target configuration as default."""
        if self.portfolio.set_default_target_percentage(self.current_target_name):
            messagebox.showinfo("Success", f"'{self.current_target_name}' set as default configuration")
        else:
            messagebox.showerror("Error", "Failed to set as default")

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
            popup.transient(self.parent.winfo_toplevel())

            # Center the popup
            popup.geometry("+%d+%d" % (
                self.parent.winfo_rootx() + self.parent.winfo_width() // 2 - 125,
                self.parent.winfo_rooty() + self.parent.winfo_height() // 2 - 50
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
                    new_value = Decimal(entry.get())
                    if 0 <= new_value <= 100:
                        self.config_tree.item(item, values=(asset, f"{new_value:.2f}%"))
                        self.refresh_view()
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

    def populate_data(self):
        """Refresh the configuration view with current data."""
        # Clear existing data
        for i in self.config_tree.get_children():
            self.config_tree.delete(i)

        # Get target percentages for the currently selected configuration
        target_pcts = self.portfolio.target_percentages(self.current_target_name)

        # Insert data into treeview
        for asset, percentage in target_pcts.items():
            self.config_tree.insert("", tk.END, values=(asset, f"{percentage:.2f}%"))

        self.refresh_view()

    def refresh_view(self):
        """Update the pie chart preview based on current settings."""
        # Get data from treeview
        items_data = []
        total = 0

        for item in self.config_tree.get_children():
            asset, percentage = self.config_tree.item(item, "values")
            if percentage.endswith('%'):
                percentage = Decimal(percentage[:-1])
            else:
                percentage = Decimal(percentage)

            items_data.append((asset, percentage))
            self.config_tree.delete(item)
            total += percentage

        # Sort items alphabetically by asset name
        items_data.sort(key=lambda x: (x[1], x[0]))

        # Re-insert in sorted order
        for asset, percentage in items_data:
            self.config_tree.insert("", tk.END, values=(asset, f"{percentage:.2f}%"))

        # Extract sorted labels and sizes
        labels = [item[0] for item in items_data]
        sizes = [item[1] for item in items_data]

        # Update total percentage display
        self.total_percentage_var.set(f"Total: {total:.2f}%")

        # Update pie chart
        self.config_ax.clear()
        patches, texts, autotexts = self.config_ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)

        # Set font properties that support Chinese characters
        font_prop = {'family': 'Microsoft YaHei', 'size': 9}
        for text in texts:
            text.set_fontproperties(font_prop)
        for autotext in autotexts:
            autotext.set_fontproperties(font_prop)

        self.config_ax.axis('equal')
        self.config_ax.set_title('Target Allocation', fontproperties=font_prop)

        # Add legend to the right of the pie chart with Unicode support
        legend_labels = [f"{label} - {pct:.2f}%" for label, pct in zip(labels, sizes)]
        legend = self.config_ax.legend(patches, legend_labels, loc="center left", bbox_to_anchor=(1, 0.5), 
                                     prop=font_prop)

        # Adjust layout to make room for the legend
        self.config_fig.tight_layout()
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
                    percentage = Decimal(percentage[:-1])
                else:
                    percentage = Decimal(percentage)

                new_targets[asset] = percentage
                total += percentage

            # Validate total is close to 100%
            if total != 100: # if not 99.5 <= total <= 100.5:
                messagebox.showerror("Invalid Allocation", f"Total allocation must be 100%. Current total: {total:.2f}%")
                return

            # Update portfolio targets for the currently selected configuration
            self.portfolio.update_target_percentages(new_targets, self.current_target_name)

            messagebox.showinfo("Success", "Target allocations updated successfully.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save target allocations: {str(e)}")

    def add_new_asset(self):
        """Open a dialog to add a new asset type to the portfolio."""
        popup = tk.Toplevel()
        popup.title("Add New Asset")
        popup.geometry("300x150")
        popup.transient(self.parent.winfo_toplevel())

        # Center the popup
        popup.geometry("+%d+%d" % (
            self.parent.winfo_rootx() + self.parent.winfo_width() // 2 - 150,
            self.parent.winfo_rooty() + self.parent.winfo_height() // 2 - 75
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
                percentage = Decimal(pct_entry.get())
                if percentage < 0 or percentage > 100:
                    messagebox.showerror("Invalid Percentage", "Percentage must be between 0 and 100.")
                    return

                # Add to treeview
                self.config_tree.insert("", tk.END, values=(asset_name, f"{percentage:.2f}%"))
                self.refresh_view()
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

    def get_rebalance_duration(self):
        """Get the rebalance duration."""
        try:
            duration_value = Decimal(self.duration_value.get())
            if duration_value <= 0:
                messagebox.showerror("Invalid Duration", "Duration must be a positive number")
                return
            duration_unit = self.duration_unit.get()
            if duration_unit == 'day' and duration_value != duration_value.to_integral_value():
                messagebox.showerror("Invalid Duration", "Duration in days must be an integer")
        except ValueError:
            messagebox.showerror("Invalid Duration", "Duration must be a valid number")
            return

        return {
            'value': duration_value,
            'unit': duration_unit
        }

    def get_selected_target_percentage(self):
        """Get the currently selected target percentage configuration."""
        return self.current_target_name
