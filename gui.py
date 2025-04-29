import tkinter as tk
from tkinter import ttk, messagebox
import bcrypt
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from database import get_employee_by_name, get_sales_by_employee, save_sale, add_employee, delete_employee, get_all_employees, get_sales_data_for_analysis
from commission import calculate_commission
from models import NeuralNetwork
import logging

# Logging setup
logging.basicConfig(filename='sales_app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class SalesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Commission Calculator")
        self.root.geometry("1200x800")
        self.current_employee_id = None
        self.selected_items = []
        
        self.products = {
            "Smartphones": {
                "iPhone 14": 799, "iPhone 15 Pro": 999, "Samsung Galaxy S23": 849, "Samsung Galaxy Z Fold 5": 1799,
                "Google Pixel 7": 599, "Google Pixel 8": 699, "OnePlus 11": 699, "Xiaomi 13 Pro": 799
            },
            "Tablets": {
                "iPad Air": 599, "iPad Pro 11\"": 799, "Galaxy Tab S8": 699, "Galaxy Tab S9": 899,
                "Microsoft Surface Go": 399, "Lenovo Tab P11 Pro": 499
            },
            "Laptops": {
                "MacBook Air M2": 999, "MacBook Pro 14\"": 1999, "Dell XPS 13": 1099, "HP Spectre x360": 1199,
                "Asus ROG Zephyrus G14": 1499, "Lenovo ThinkPad X1 Carbon": 1399
            },
            "Headphones": {
                "AirPods Pro": 249, "Sony WH-1000XM5": 399, "Bose QC45": 329, "Samsung Galaxy Buds 2": 149,
                "JBL Live 660NC": 199, "Sennheiser Momentum 4": 349
            },
            "Smart Watches": {
                "Apple Watch Series 8": 399, "Apple Watch Ultra": 799, "Samsung Galaxy Watch 5": 279,
                "Garmin Venu 2": 399, "Fitbit Versa 4": 229
            },
            "Televisions": {
                "Sony Bravia 55\" OLED": 1399, "LG C2 65\" OLED": 1899, "Samsung QN90B 55\" QLED": 1299,
                "TCL 6-Series 65\"": 899
            },
            "Gaming Consoles": {
                "PlayStation 5": 499, "Xbox Series X": 499, "Nintendo Switch OLED": 349, "Steam Deck 512GB": 649
            },
            "Cameras and Drones": {
                "GoPro HERO11": 399, "DJI Mavic 3 Drone": 2049, "Canon EOS R10": 979, "Sony Alpha 7 IV": 2499
            },
            "Audio and Smart Home": {
                "Sonos Arc Soundbar": 899, "Amazon Echo Show 15": 249, "Google Nest Hub": 99, "Bose SoundLink Revolve": 199
            },
            "Gaming Accessories": {
                "Razer Blade 14": 1999, "Logitech G Pro X Keyboard": 149, "SteelSeries Arctis 7": 149
            }
        }
        
        # Style setup
        self.setup_styles()
        
        self.notebook = ttk.Notebook(root)
        self.employee_frame = ttk.Frame(self.notebook)
        self.manager_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.employee_frame, text="Employee")
        self.notebook.add(self.manager_frame, text="Manager")
        self.notebook.pack(pady=10, fill="both", expand=True)
        
        self.notebook.bind("<<NotebookTabChanged>>", self.check_manager_access)
        self.manager_authenticated = False
        
        # Open Employee tab by default
        self.notebook.select(self.employee_frame)
        self.setup_employee_tab()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        print("Tkinter theme set: ", style.theme_use())
        
        # General styles
        style.configure("TFrame", background="#f5f6f5")
        style.configure("TLabel", background="#f5f6f5", font=("Arial", 12))
        style.configure("TEntry", font=("Arial", 12))
        style.configure("TButton", font=("Arial", 12), padding=8)
        style.configure("Treeview", font=("Arial", 9), rowheight=20, background="#ffffff", fieldbackground="#ffffff")
        style.configure("Treeview.Heading", font=("Arial", 9, "bold"), background="#e0e0e0")
        
        # Styles for Manager tab
        style.configure("Manager.TFrame", background="#f5f6f5")
        style.configure("Manager.TLabel", background="#f5f6f5", font=("Arial", 14))
        style.configure("Manager.TEntry", font=("Arial", 14))
        style.configure("Manager.TButton", font=("Arial", 12), padding=8, background="#0288d1", foreground="white")
        style.map("Manager.TButton", background=[("active", "#01579b")])
        style.configure("Manager.Title.TLabel", font=("Arial", 16, "bold"), background="#f5f6f5")
        style.configure("Manager.Stats.TLabel", font=("Arial", 12), background="#ffffff", padding=5)
        style.configure("Manager.Analytics.TFrame", background="#f5f6f5", relief="flat", padding=10)
        style.configure("Manager.Treeview", font=("Arial", 11), rowheight=30)
        style.configure("Manager.Treeview.Heading", font=("Arial", 12, "bold"), background="#0288d1", foreground="white")
        style.map("Manager.Treeview.Heading", background=[("active", "#01579b")])
        # Styles for analytics buttons
        style.configure("Analytics.TButton", font=("Arial", 12), padding=(8, 6), background="#ff9800", foreground="white")
        style.map("Analytics.TButton", background=[("active", "#e68900")])
        # Style for "Refresh List" button
        style.configure("Refresh.TButton", font=("Arial", 12), padding=(8, 6), background="#0288d1", foreground="white")
        style.map("Refresh.TButton", background=[("active", "#01579b")])
        
        # Styles for Employee tab
        style.configure("Large.TButton", font=("Arial", 11), padding=8, wraplength=120, background="#d3d3d3", foreground="black")
        style.map("Large.TButton", background=[("active", "#c0c0c0")])
        style.configure("Remove.TButton", font=("Arial", 12), padding=8, background="#ff4d4d", foreground="white")
        style.map("Remove.TButton", background=[("active", "#e63939")])
        style.configure("Action.TButton", font=("Arial", 12), padding=10, background="#007bff", foreground="white")
        style.map("Action.TButton", background=[("active", "#0056d2")])
        style.configure("Quantity.TButton", font=("Arial", 9), padding=3, background="#6c757d", foreground="white")
        style.map("Quantity.TButton", background=[("active", "#5a6268")])

    def setup_employee_tab(self):
        print("Setting up Employee tab")
        for widget in self.employee_frame.winfo_children():
            widget.destroy()
        
        # Frame for employee selection
        login_frame = ttk.Frame(self.employee_frame, style="TFrame")
        login_frame.pack(pady=20, fill="both", expand=True)
        
        # Employee dropdown
        ttk.Label(login_frame, text="Select Employee:", style="TLabel").pack(pady=5)
        self.employee_var = tk.StringVar()
        self.employee_dropdown = ttk.Combobox(login_frame, textvariable=self.employee_var, state="readonly", font=("Arial", 12))
        self.update_employee_dropdown()
        self.employee_dropdown.pack(pady=5)
        
        # Login button
        ttk.Button(login_frame, text="Login", command=self.authenticate_employee, style="Action.TButton").pack(pady=10)

    def update_employee_dropdown(self):
        """Updates the employee dropdown list."""
        employees = get_all_employees()
        employee_names = [emp[1] for emp in employees]
        self.employee_dropdown['values'] = employee_names
        self.employee_var.set("")  # Clear selection
        logging.debug(f"Employee list updated: {employee_names}")

    def authenticate_employee(self):
        name = self.employee_var.get()
        print(f"Login attempt: name={name}")
        
        if not name:
            messagebox.showerror("Error", "Select an employee")
            return
        
        employee = get_employee_by_name(name)
        if not employee:
            messagebox.showerror("Error", "Employee not found")
            print("Employee not found")
            return
        
        employee_id, _, is_manager, _ = employee
        print(f"Found employee: ID={employee_id}, is_manager={is_manager}")
        
        self.current_employee_id = employee_id
        if is_manager:
            self.manager_authenticated = False
            self.notebook.select(self.manager_frame)
            self.setup_manager_login()
        else:
            self.manager_authenticated = False
            self.load_employee_content()

    def check_manager_access(self, event):
        selected_tab = self.notebook.index(self.notebook.select())
        print(f"Tab switch: index={selected_tab}")
        if selected_tab == 1 and not self.manager_authenticated:
            self.setup_manager_login()
        elif selected_tab == 1 and self.manager_authenticated:
            self.setup_manager_tab()

    def setup_manager_login(self):
        print("Setting up manager password entry interface")
        for widget in self.manager_frame.winfo_children():
            widget.destroy()
        
        login_frame = ttk.Frame(self.manager_frame, style="Manager.TFrame")
        login_frame.pack(pady=20, fill="both", expand=True)
        
        ttk.Label(login_frame, text="Enter manager password:", style="Manager.TLabel").pack(pady=10)
        password_entry = ttk.Entry(login_frame, show="*", style="Manager.TEntry")
        password_entry.pack(pady=5)
        
        def verify_password():
            password = password_entry.get().encode('utf-8')
            employee = get_employee_by_name("Manager")
            if employee and bcrypt.checkpw(password, employee[3]):
                self.manager_authenticated = True
                print("Manager authentication successful")
                self.setup_manager_tab()
            else:
                messagebox.showerror("Error", "Invalid password")
                print("Invalid password")
                password_entry.delete(0, tk.END)
        
        ttk.Button(login_frame, text="Confirm", command=verify_password, style="Manager.TButton").pack(pady=10)

    def load_employee_content(self):
        print("Loading Employee tab content")
        for widget in self.employee_frame.winfo_children():
            widget.destroy()
        
        left_frame = ttk.Frame(self.employee_frame, style="TFrame")
        left_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        right_frame = ttk.Frame(self.employee_frame, style="TFrame")
        right_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        self.employee_frame.columnconfigure(0, weight=6)
        self.employee_frame.columnconfigure(1, weight=1)
        self.employee_frame.rowconfigure(0, weight=1)
        
        self.left_canvas = tk.Canvas(left_frame, bg="#f5f6f5")
        left_scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.left_canvas.yview)
        self.left_scrollable_frame = ttk.Frame(self.left_canvas, style="TFrame")
        
        self.left_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.left_canvas.configure(scrollregion=self.left_canvas.bbox("all"))
        )
        
        self.left_canvas.create_window((0, 0), window=self.left_scrollable_frame, anchor="nw")
        self.left_canvas.configure(yscrollcommand=left_scrollbar.set)
        
        self.left_canvas.pack(side="left", fill="both", expand=True)
        left_scrollbar.pack(side="right", fill="y")
        
        def _on_mousewheel_left(event):
            if self.left_canvas.winfo_ismapped():
                self.left_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.root.bind("<MouseWheel>", _on_mousewheel_left)
        
        ttk.Label(self.left_scrollable_frame, text="Select Products:", font=("Arial", 14, "bold")).pack(anchor="w", pady=10)
        for category, items in self.products.items():
            ttk.Label(self.left_scrollable_frame, text=category, font=("Arial", 13, "bold")).pack(anchor="w", pady=5)
            product_frame = ttk.Frame(self.left_scrollable_frame, style="TFrame")
            product_frame.pack(fill="both", expand=True, padx=10)
            num_columns = 4
            for i, (product, price) in enumerate(items.items()):
                row = i // num_columns
                col = i % num_columns
                btn = ttk.Button(product_frame, text=f"{product}\n${price}", width=20,
                                command=lambda p=product, c=category: self.add_item(p, c), style="Large.TButton")
                btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
                product_frame.rowconfigure(row, weight=1, uniform="row")
                product_frame.columnconfigure(col, weight=1, uniform="col")
        
        self.right_canvas = tk.Canvas(right_frame, bg="#f5f6f5")
        right_v_scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.right_canvas.yview)
        self.right_scrollable_frame = ttk.Frame(self.right_canvas, style="TFrame")
        
        self.right_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.right_canvas.configure(scrollregion=self.right_canvas.bbox("all"))
        )
        
        self.right_canvas.create_window((0, 0), window=self.right_scrollable_frame, anchor="nw")
        self.right_canvas.configure(yscrollcommand=right_v_scrollbar.set)
        
        self.right_canvas.pack(side="left", fill="both", expand=True)
        right_v_scrollbar.pack(side="right", fill="y")
        
        def _on_mousewheel_right(event):
            if self.right_canvas.winfo_ismapped():
                self.right_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.right_canvas.bind("<MouseWheel>", _on_mousewheel_right)
        
        self.setup_right_frame_content()

    def setup_right_frame_content(self):
        print("Setting up right side of Employee tab")
        for widget in self.right_scrollable_frame.winfo_children():
            widget.destroy()
        
        ttk.Label(self.right_scrollable_frame, text="Selected Products:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=8)
        self.items_frame = ttk.Frame(self.right_scrollable_frame, style="TFrame")
        self.items_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.total_label = ttk.Label(self.right_scrollable_frame, text="Total: $0.00", font=("Arial", 11, "bold"))
        self.total_label.pack(anchor="w", padx=10, pady=5)
        
        self.update_items_list()
        
        btn_frame = ttk.Frame(self.right_scrollable_frame, style="TFrame")
        btn_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(btn_frame, text="Clear All", command=self.clear_items, style="Remove.TButton").pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Save Sale", command=self.save_sale, style="Action.TButton").pack(side="left", padx=5)
        
        ttk.Label(self.right_scrollable_frame, text="Sales History:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=8)
        
        table_frame = ttk.Frame(self.right_scrollable_frame, style="TFrame")
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        
        self.sales_tree = ttk.Treeview(table_frame, columns=("Date", "Products", "Amount", "Commission"), show="headings", style="Treeview")
        self.sales_tree.heading("Date", text="Date")
        self.sales_tree.heading("Products", text="Products")
        self.sales_tree.heading("Amount", text="Amount")
        self.sales_tree.heading("Commission", text="Commission")
        self.sales_tree.column("Date", width=120)
        self.sales_tree.column("Products", width=120)
        self.sales_tree.column("Amount", width=80)
        self.sales_tree.column("Commission", width=80)
        self.sales_tree.pack(fill="both", expand=True)
        
        ttk.Button(self.right_scrollable_frame, text="Refresh History", command=self.load_sales, style="Action.TButton").pack(anchor="w", padx=10, pady=8)
        
        stats_frame = ttk.Frame(self.right_scrollable_frame, style="TFrame", padding=0)
        stats_frame.pack(fill="x", padx=10, pady=0)

        # Horizontal frame for "Total Sales" and "Logout"
        sales_logout_frame = ttk.Frame(stats_frame, style="TFrame", padding=0)
        sales_logout_frame.grid(row=0, column=0, sticky="ew")
        self.total_sales_label = ttk.Label(sales_logout_frame, text="Total Sales: $0.00", font=("Arial", 10))
        self.total_sales_label.pack(side="left")
        ttk.Button(sales_logout_frame, text="Logout", command=self.logout, style="Action.TButton").pack(side="right", padx=(0, 10))

        # "Total Commissions" on the next line
        self.total_commissions_label = ttk.Label(stats_frame, text="Total Commissions: $0.00", font=("Arial", 10))
        self.total_commissions_label.grid(row=1, column=0, sticky="w", pady=0)

        stats_frame.grid_columnconfigure(0, weight=1)

        self.root.update_idletasks()
        print(f"Total sales label: y={self.total_sales_label.winfo_y()}")
        print(f"Total commissions label: y={self.total_commissions_label.winfo_y()}")
        print(f"Distance: {self.total_commissions_label.winfo_y() - self.total_sales_label.winfo_y()}")
        
        self.load_sales()
        self.update_sales_stats()
        logging.debug("Updating right side in setup_right_frame_content")
        self.right_canvas.configure(scrollregion=self.right_canvas.bbox("all"))
        self.right_canvas.yview_moveto(0)

    def logout(self):
        """Log out the current employee."""
        print(f"Logging out employee: ID={self.current_employee_id}")
        self.current_employee_id = None
        self.selected_items = []
        self.setup_employee_tab()
        logging.debug("Employee logged out successfully")

    def add_item(self, product, category):
        for item in self.selected_items:
            if item["product"] == product and item["category"] == category:
                item["quantity"] += 1
                self.update_items_list()
                return
        self.selected_items.append({"product": product, "category": category, "quantity": 1})
        self.update_items_list()

    def remove_item(self, index):
        if 0 <= index < len(self.selected_items):
            self.selected_items.pop(index)
            self.update_items_list()

    def change_quantity(self, index, delta):
        if 0 <= index < len(self.selected_items):
            self.selected_items[index]["quantity"] += delta
            if self.selected_items[index]["quantity"] <= 0:
                self.selected_items.pop(index)
            self.update_items_list()

    def update_items_list(self):
        for widget in self.items_frame.winfo_children():
            widget.destroy()
        
        tree = ttk.Treeview(self.items_frame, columns=("Product", "Quantity", "Price", "Total Cost"), show="headings", style="Treeview")
        tree.heading("Product", text="Product")
        tree.heading("Quantity", text="Qty")
        tree.heading("Price", text="Price")
        tree.heading("Total Cost", text="Total")
        tree.column("Product", width=140)
        tree.column("Quantity", width=60)
        tree.column("Price", width=60)
        tree.column("Total Cost", width=80)
        tree.pack(fill="both", expand=True)
        
        total = 0
        for i, item in enumerate(self.selected_items):
            product = item["product"]
            category = item["category"]
            quantity = item["quantity"]
            price = self.products[category][product]
            subtotal = price * quantity
            total += subtotal
            tree.insert("", tk.END, values=(product, quantity, f"${price}", f"${subtotal:.2f}"))
            
            frame = ttk.Frame(self.items_frame, style="TFrame")
            frame.pack(fill="x", pady=3)
            ttk.Button(frame, text="-", command=lambda idx=i: self.change_quantity(idx, -1), style="Quantity.TButton").pack(side="left", padx=3)
            ttk.Label(frame, text=f"Qty: {quantity} pcs.", font=("Arial", 10)).pack(side="left", padx=5)
            ttk.Button(frame, text="+", command=lambda idx=i: self.change_quantity(idx, 1), style="Quantity.TButton").pack(side="left", padx=3)
        
        self.total_label.config(text=f"Total: ${total:.2f}")
        
        logging.debug("Updating cart in update_items_list")
        self.right_canvas.configure(scrollregion=self.right_canvas.bbox("all"))
        self.right_canvas.yview_moveto(0)

    def clear_items(self):
        self.selected_items = []
        self.update_items_list()

    def save_sale(self):
        if not self.selected_items:
            messagebox.showerror("Error", "Select at least one product")
            return
        
        total_amount = sum(self.products[item["category"]][item["product"]] * item["quantity"] for item in self.selected_items)
        items_json = json.dumps(self.selected_items)
        commission = calculate_commission(total_amount, self.current_employee_id)
        sale_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        save_sale(self.current_employee_id, total_amount, commission, sale_date, items_json)
        
        messagebox.showinfo("Success", f"Commission: ${commission:.2f}")
        self.clear_items()
        self.setup_right_frame_content()
        self.right_canvas.configure(scrollregion=self.right_canvas.bbox("all"))
        self.right_canvas.yview_moveto(0)
        self.left_canvas.configure(scrollregion=self.left_canvas.bbox("all"))
        self.left_canvas.yview_moveto(0)

    def load_sales(self):
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)
        sales = get_sales_by_employee(self.current_employee_id)
        for sale in sales:
            date, items_json, amount, commission = sale
            items = json.loads(items_json) if items_json else []
            items_str = ", ".join([f"{item['product']} ({item['quantity']} pcs.)" for item in items]) if items else "No data"
            self.sales_tree.insert("", tk.END, values=(date, items_str, amount, commission))
        self.update_sales_stats()

    def update_sales_stats(self):
        sales = get_sales_by_employee(self.current_employee_id)
        total_sales = sum(sale[2] for sale in sales)
        total_commissions = sum(sale[3] for sale in sales)
        self.total_sales_label.config(text=f"Total Sales: ${total_sales:.2f}")
        self.total_commissions_label.config(text=f"Total Commissions: ${total_commissions:.2f}")

    def setup_manager_tab(self):
        print("Starting setup of Manager tab")
        for widget in self.manager_frame.winfo_children():
            widget.destroy()
        
        self.manager_frame.configure(style="Manager.TFrame")
        
        # Top frame for General Statistics and Analytics
        top_frame = ttk.Frame(self.manager_frame, style="Manager.TFrame")
        top_frame.pack(side="top", fill="x", pady=10)
        print("Top frame created")
        
        # Configure grid for top_frame
        top_frame.columnconfigure(0, weight=1)
        top_frame.columnconfigure(1, weight=1)
        top_frame.rowconfigure(0, weight=1)
        
        # General Statistics (left)
        stats_frame = ttk.LabelFrame(top_frame, text="General Statistics", style="Manager.TFrame")
        stats_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        print("General Statistics frame created")
        
        df = get_sales_data_for_analysis()
        total_sales = df['amount'].sum() if not df.empty else 0
        total_commissions = df['commission'].sum() if not df.empty else 0
        employees = get_all_employees()
        avg_sales_per_employee = len(df) / len(employees) if employees and not df.empty else 0
        
        stats_inner_frame = ttk.Frame(stats_frame, style="Manager.TFrame")
        stats_inner_frame.pack(pady=10, padx=10, fill="x")
        
        ttk.Label(stats_inner_frame, text=f"Total Sales Amount: ${total_sales:.2f}", style="Manager.Stats.TLabel").pack(anchor="w", pady=5)
        ttk.Label(stats_inner_frame, text=f"Total Commissions: ${total_commissions:.2f}", style="Manager.Stats.TLabel").pack(anchor="w", pady=5)
        ttk.Label(stats_inner_frame, text=f"Average Sales per Employee: {avg_sales_per_employee:.2f}", style="Manager.Stats.TLabel").pack(anchor="w", pady=5)
        
        # Analytics (right)
        analytics_frame = ttk.Frame(top_frame, style="Manager.Analytics.TFrame")
        analytics_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        print("Analytics frame created")
        
        # Container for label and buttons
        analytics_content_frame = ttk.Frame(analytics_frame, style="Manager.Analytics.TFrame")
        analytics_content_frame.pack(pady=5, fill="x")
        
        # "Analytics" label centered above buttons
        analytics_label = ttk.Label(analytics_content_frame, text="Analytics", font=("Arial", 14, "bold"))
        analytics_label.pack(anchor="center", pady=4)
        analytics_label.pack_configure(padx=(0, 100))
                
        # Frame for buttons
        analytics_button_frame = ttk.Frame(analytics_content_frame, style="Manager.Analytics.TFrame")
        analytics_button_frame.pack(fill="x")
        print("Analytics buttons frame created")
        
        # Analytics buttons with uniform size
        button_width = 22
        ttk.Button(analytics_button_frame, text="Refresh List", command=self.load_employees, style="Refresh.TButton", width=button_width).pack(side="left", padx=5)
        print("Refresh List button created")
        ttk.Button(analytics_button_frame, text="Show Statistics", command=self.show_statistics, style="Analytics.TButton", width=button_width).pack(side="left", padx=5)
        print("Show Statistics button created")
        ttk.Button(analytics_button_frame, text="Employee Personal Progress", command=self.show_employee_progress, style="Analytics.TButton", width=25).pack(side="left", padx=5)
        print("Employee Personal Progress button created")
        
        # Logging button coordinates
        self.root.update_idletasks()
        try:
            buttons = analytics_button_frame.winfo_children()
            for i, btn in enumerate(buttons):
                logging.debug(f"Button {i+1}: x={btn.winfo_x()}, y={btn.winfo_y()}, width={btn.winfo_width()}, height={btn.winfo_height()}")
        except Exception as e:
            logging.error(f"Error logging button coordinates: {str(e)}")
        
        # Canvas for Employee Management
        canvas = tk.Canvas(self.manager_frame, bg="#f5f6f5")
        scrollbar = ttk.Scrollbar(self.manager_frame, orient="vertical", command=canvas.yview)
        main_frame = ttk.Frame(canvas, style="Manager.TFrame")
        
        main_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=main_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def _on_mousewheel(event):
            if canvas.winfo_ismapped():
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.manager_frame.bind("<MouseWheel>", _on_mousewheel)
        
        print("Main frame and canvas created")
        
        # Employee Management
        employee_frame = ttk.LabelFrame(main_frame, text="Employee Management", style="Manager.TFrame")
        employee_frame.pack(fill="both", pady=10, padx=10, expand=True)
        print("Employee Management frame created")
        
        # Horizontal frame for input, buttons, and table
        horizontal_frame = ttk.Frame(employee_frame, style="Manager.TFrame")
        horizontal_frame.pack(fill="both", pady=10, padx=10, expand=True)
        
        # Left frame for input and buttons
        input_frame = ttk.Frame(horizontal_frame, style="Manager.TFrame")
        input_frame.pack(side="left", fill="y", padx=10)
        
        # Frame for label and entry
        entry_frame = ttk.Frame(input_frame, style="Manager.TFrame")
        entry_frame.pack(anchor="w", pady=5)
        ttk.Label(entry_frame, text="Employee Name:", style="Manager.TLabel").pack(side="left", padx=(0, 5))
        self.employee_name = ttk.Entry(entry_frame, style="Manager.TEntry")
        self.employee_name.pack(side="left")
        
        # Frame for buttons
        button_frame = ttk.Frame(input_frame, style="Manager.TFrame")
        button_frame.pack(anchor="w", pady=5)
        ttk.Button(button_frame, text="Add Employee", command=self.add_employee, style="Manager.TButton").pack(side="left", padx=(0, 5))
        ttk.Button(button_frame, text="Delete Employee", command=self.delete_employee, style="Manager.TButton").pack(side="left")
        
        # Right frame for table
        tree_frame = ttk.Frame(horizontal_frame, style="Manager.TFrame")
        tree_frame.pack(side="left", fill="both", expand=True, padx=10)
        
        self.employee_tree = ttk.Treeview(tree_frame, columns=("ID", "Name"), show="headings", style="Manager.Treeview")
        self.employee_tree.heading("ID", text="ID")
        self.employee_tree.heading("Name", text="Name")
        self.employee_tree.column("ID", width=200)
        self.employee_tree.column("Name", width=200)
        
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.employee_tree.yview)
        self.employee_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.employee_tree.pack(side="left", fill="both", expand=True)
        tree_scrollbar.pack(side="right", fill="y")
        print("Employee table created")
        
        self.load_employees()
        print("Manager tab setup complete")

    def add_employee(self):
        name = self.employee_name.get()
        if not name:
            messagebox.showerror("Error", "Enter employee name")
            return
        success, message = add_employee(name, "", is_manager=False)
        messagebox.showinfo("Result", message)
        self.employee_name.delete(0, tk.END)
        self.load_employees()
        self.update_employee_dropdown()  # Update employee dropdown
        logging.debug(f"Employee added: {name}")

    def delete_employee(self):
        selected = self.employee_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select an employee")
            return
        employee_id = self.employee_tree.item(selected)["values"][0]
        if employee_id == self.current_employee_id:
            messagebox.showerror("Error", "Cannot delete the current user")
            return
        success, message = delete_employee(employee_id)
        messagebox.showinfo("Result", message)
        self.load_employees()
        self.update_employee_dropdown()  # Update dropdown after deletion
        logging.debug(f"Employee deleted: ID={employee_id}")

    def load_employees(self):
        for item in self.employee_tree.get_children():
            self.employee_tree.delete(item)
        employees = get_all_employees()
        print(f"Loaded employees: {len(employees)}")
        for employee in employees:
            self.employee_tree.insert("", tk.END, values=employee)

    def show_employee_progress(self):
        print("Opening Employee Personal Progress window")
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Employee Personal Progress")
        progress_window.geometry("1000x800")
        progress_window.configure(bg="#f5f6f5")
        
        # Employee dropdown
        employees = get_all_employees()
        employee_names = [emp[1] for emp in employees]
        employee_ids = {emp[1]: emp[0] for emp in employees}
        
        ttk.Label(progress_window, text="Select Employee:", font=("Arial", 14, "bold")).pack(pady=10)
        employee_var = tk.StringVar()
        employee_dropdown = ttk.Combobox(progress_window, textvariable=employee_var, values=employee_names, state="readonly", font=("Arial", 12))
        employee_dropdown.pack(pady=5)
        
        content_frame = ttk.Frame(progress_window, style="TFrame")
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        def update_progress():
            for widget in content_frame.winfo_children():
                widget.destroy()
            
            employee_name = employee_var.get()
            if not employee_name:
                return
            
            employee_id = employee_ids[employee_name]
            sales = get_sales_by_employee(employee_id)
            df = get_sales_data_for_analysis()
            employee_sales = df[df['employee_id'] == employee_id].copy()
            
            # Personal data
            sale_count = len(employee_sales)
            avg_sale_amount = employee_sales['amount'].mean() if not employee_sales.empty else 0
            total_commissions = employee_sales['commission'].sum() if not employee_sales.empty else 0
            
            ttk.Label(content_frame, text=f"Employee: {employee_name}", font=("Arial", 16, "bold")).pack(anchor="w", pady=5)
            ttk.Label(content_frame, text=f"Number of Sales: {sale_count}", style="Manager.Stats.TLabel").pack(anchor="w", pady=5)
            ttk.Label(content_frame, text=f"Average Sale Amount: ${avg_sale_amount:.2f}", style="Manager.Stats.TLabel").pack(anchor="w", pady=5)
            ttk.Label(content_frame, text=f"Total Commissions: ${total_commissions:.2f}", style="Manager.Stats.TLabel").pack(anchor="w", pady=5)
            
            # Last 10 sales
            ttk.Label(content_frame, text="Last 10 Sales:", font=("Arial", 14, "bold")).pack(anchor="w", pady=10)
            sales_tree = ttk.Treeview(content_frame, columns=("Date", "Products", "Amount", "Commission"), show="headings", style="Manager.Treeview")
            sales_tree.heading("Date", text="Date")
            sales_tree.heading("Products", text="Products")
            sales_tree.heading("Amount", text="Amount")
            sales_tree.heading("Commission", text="Commission")
            sales_tree.column("Date", width=150)
            sales_tree.column("Products", width=300)
            sales_tree.column("Amount", width=100)
            sales_tree.column("Commission", width=100)
            sales_tree.pack(fill="x", pady=5)
            
            for sale in sales[:10]:
                date, items_json, amount, commission = sale
                items = json.loads(items_json) if items_json else []
                items_str = ", ".join([f"{item['product']} ({item['quantity']} pcs.)" for item in items]) if items else "No data"
                sales_tree.insert("", tk.END, values=(date, items_str, f"${amount:.2f}", f"${commission:.2f}"))
            
            # Commission forecast (Deep Learning)
            try:
                if not employee_sales.empty:
                    employee_sales['sale_date'] = pd.to_datetime(employee_sales['sale_date'], errors='coerce')
                    employee_sales = employee_sales.dropna(subset=['sale_date'])
                    if not employee_sales.empty:
                        employee_sales['days'] = (employee_sales['sale_date'] - employee_sales['sale_date'].min()).dt.days
                        daily_data = employee_sales.groupby('days').agg({'amount': 'sum', 'commission': 'sum'}).reset_index()
                        
                        X = daily_data[['days', 'amount']].values
                        y = daily_data['commission'].values.reshape(-1, 1)
                        
                        if X.shape[0] > 1:
                            scaler_X = MinMaxScaler()
                            scaler_y = MinMaxScaler()
                            X_scaled = scaler_X.fit_transform(X)
                            y_scaled = scaler_y.fit_transform(y)
                            
                            nn = NeuralNetwork([2, 10, 1])
                            nn.train(X_scaled, y_scaled, epochs=1000, learning_rate=0.01)
                            
                            last_day = daily_data['days'].max()
                            future_days = np.array([[last_day + i, daily_data['amount'].mean()] for i in range(1, 31)])
                            future_X_scaled = scaler_X.transform(future_days)
                            predicted_commissions_scaled = nn.forward(future_X_scaled)
                            predicted_commissions = scaler_y.inverse_transform(predicted_commissions_scaled)
                            
                            ttk.Label(content_frame, text=f"30-Day Commission Forecast: ${predicted_commissions[-1][0]:.2f}", style="Manager.Stats.TLabel").pack(anchor="w", pady=5)
                            
                            fig, ax = plt.subplots(figsize=(8, 4))
                            ax.plot(daily_data['days'], daily_data['commission'], label="Actual Commissions")
                            ax.plot([last_day + i for i in range(1, 31)], predicted_commissions, color="green", label="Forecast")
                            ax.set_xlabel("Days")
                            ax.set_ylabel("Commissions")
                            ax.set_title(f"Commission Forecast for {employee_name}")
                            ax.legend()
                            ax.grid(True)
                            plt.tight_layout()
                            
                            canvas = FigureCanvasTkAgg(fig, master=content_frame)
                            canvas.draw()
                            canvas.get_tk_widget().pack(pady=10)
                        else:
                            # Fallback: Linear Regression
                            model = LinearRegression()
                            model.fit(X, y)
                            future_days = np.array([[last_day + i, daily_data['amount'].mean()] for i in range(1, 31)])
                            predicted_commissions = model.predict(future_days)
                            ttk.Label(content_frame, text=f"30-Day Commission Forecast (Linear Regression): ${predicted_commissions[-1][0]:.2f}", style="Manager.Stats.TLabel").pack(anchor="w", pady=5)
                    else:
                        ttk.Label(content_frame, text="Insufficient data for forecasting", style="Manager.Stats.TLabel").pack(anchor="w", pady=5)
                else:
                    ttk.Label(content_frame, text="No sales data for the employee", style="Manager.Stats.TLabel").pack(anchor="w", pady=5)
            except Exception as e:
                logging.error(f"Error forecasting for employee {employee_name}: {str(e)}")
                ttk.Label(content_frame, text=f"Forecasting error: {str(e)}", style="Manager.Stats.TLabel").pack(anchor="w", pady=5)
        
        employee_dropdown.bind("<<ComboboxSelected>>", lambda event: update_progress())

    def show_statistics(self):
        print("Opening General Statistics window")
        logging.debug("Starting show_statistics")
        df = get_sales_data_for_analysis()
        logging.debug(f"Data from get_sales_data_for_analysis: {df}")
        logging.debug(f"DataFrame columns: {list(df.columns)}")
        
        if df.empty or len(df) == 0:
            messagebox.showinfo("Statistics", "No data available for analysis")
            return

        # Expected columns and possible alternative names
        expected_columns = {
            'employee_id': ['employee_id', 'emp_id', 'id'],
            'sale_date': ['sale_date', 'date', 'transaction_date'],
            'amount': ['amount', 'sale_amount', 'total'],
            'commission': ['commission', 'sale_commission'],
            'items': ['items', 'sale_items', 'products']
        }

        # Check and rename columns
        rename_dict = {}
        missing_columns = []
        for expected, aliases in expected_columns.items():
            found = False
            for alias in aliases:
                if alias in df.columns:
                    rename_dict[alias] = expected
                    found = True
                    break
            if not found:
                missing_columns.append(expected)
        
        if missing_columns:
            logging.error(f"Missing columns: {missing_columns}")
            messagebox.showerror("Error", f"Missing required columns: {missing_columns}. Available columns: {list(df.columns)}")
            return

        try:
            df = df.rename(columns=rename_dict)
            logging.debug(f"Renamed columns: {list(df.columns)}")
        except Exception as e:
            logging.error(f"Error renaming columns: {str(e)}")
            messagebox.showerror("Error", f"Error renaming columns: {str(e)}")
            return

        # General statistics
        try:
            total_sales = df['amount'].sum()
            total_commissions = df['commission'].sum()
            avg_commission = df['commission'].mean() if not df['commission'].empty else 0
            logging.debug(f"Total sales: {total_sales}, Total commissions: {total_commissions}, Avg commission: {avg_commission}")
        except Exception as e:
            logging.error(f"Error calculating general statistics: {str(e)}")
            messagebox.showerror("Error", f"Error calculating statistics: {str(e)}")
            return

        # Date processing
        try:
            df['sale_date'] = pd.to_datetime(df['sale_date'], errors='coerce')
            if df['sale_date'].isna().any():
                logging.warning("Some dates could not be parsed")
                df = df.dropna(subset=['sale_date'])
                if df.empty:
                    messagebox.showinfo("Statistics", "No valid dates for analysis")
                    return
            df['days'] = (df['sale_date'] - df['sale_date'].min()).dt.days
            daily_data = df.groupby('days').agg({'amount': 'sum', 'commission': 'sum'}).reset_index()
            logging.debug(f"Daily data: {daily_data}")
        except Exception as e:
            logging.error(f"Error processing dates: {str(e)}")
            messagebox.showerror("Error", f"Error processing dates: {str(e)}")
            return

        # Data preparation for model
        try:
            X = daily_data[['days', 'amount']].values
            y = daily_data['commission'].values.reshape(-1, 1)
            logging.debug(f"X shape: {X.shape}, y shape: {y.shape}")
            
            if X.shape[0] == 0 or y.shape[0] == 0:
                messagebox.showinfo("Statistics", "Insufficient data for forecasting")
                return
        except Exception as e:
            logging.error(f"Error preparing data: {str(e)}")
            messagebox.showerror("Error", f"Error preparing data: {str(e)}")
            return

        # Normalization and training
        try:
            scaler_X = MinMaxScaler()
            scaler_y = MinMaxScaler()
            X_scaled = scaler_X.fit_transform(X)
            y_scaled = scaler_y.fit_transform(y)
            
            model = LinearRegression()
            model.fit(X_scaled, y_scaled)
            
            last_day = daily_data['days'].max()
            future_days = np.array([[last_day + i, daily_data['amount'].mean()] for i in range(1, 31)])
            future_X_scaled = scaler_X.transform(future_days)
            predicted_commissions_scaled = model.predict(future_X_scaled)
            predicted_commissions = scaler_y.inverse_transform(predicted_commissions_scaled)
            
            logging.debug(f"Predicted commissions: {predicted_commissions[:5]}")
        except Exception as e:
            logging.error(f"Error training model: {str(e)}")
            messagebox.showerror("Error", f"Error training model: {str(e)}")
            return

        # Employee clustering
        try:
            employee_stats = df.groupby('employee_id').agg({
                'amount': ['count', 'mean'],
                'commission': 'sum'
            }).reset_index()
            employee_stats.columns = ['employee_id', 'sale_count', 'avg_sale_amount', 'total_commission']
            
            if len(employee_stats) < 3:
                logging.warning("Not enough employees for clustering")
                employee_stats['cluster'] = 0
            else:
                kmeans = KMeans(n_clusters=min(3, len(employee_stats)), random_state=42)
                employee_stats['cluster'] = kmeans.fit_predict(employee_stats[['sale_count', 'avg_sale_amount']])
            
            employees = get_all_employees()
            employee_names = {emp[0]: emp[1] for emp in employees}
            employee_stats['name'] = employee_stats['employee_id'].map(employee_names)
            employee_stats['name'] = employee_stats['name'].fillna('Unknown')
            
            recommendations = []
            for _, row in employee_stats.iterrows():
                if row['cluster'] == employee_stats['cluster'].value_counts().idxmax():
                    recommendations.append(f"Employee {row['name']}: Continue maintaining high sales performance!")
                else:
                    recommendations.append(f"Employee {row['name']}: Increase the number of sales or average deal amount.")
            
            logging.debug(f"Employee stats: {employee_stats}")
        except Exception as e:
            logging.error(f"Error during clustering: {str(e)}")
            if self.root.winfo_exists():
                messagebox.showerror("Error", f"Error during clustering: {str(e)}")
            else:
                print(f"Clustering error (window unavailable): {str(e)}")
            return

        # Display statistics with scrolling
        try:
            stats_window = tk.Toplevel(self.root)
            stats_window.title("General Statistics")
            stats_window.geometry("1000x800")
            stats_window.configure(bg="#f5f6f5")
            
            # Canvas for scrolling
            canvas = tk.Canvas(stats_window, bg="#f5f6f5")
            scrollbar = ttk.Scrollbar(stats_window, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas, style="TFrame")
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="n")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            def _on_mousewheel(event):
                if canvas.winfo_ismapped():
                    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            stats_window.bind("<MouseWheel>", _on_mousewheel)
            
            # Centered container for content
            content_frame = ttk.Frame(scrollable_frame, style="TFrame")
            content_frame.pack(fill="x", padx=20, pady=20, expand=True)
            
            # Window content with centered text
            ttk.Label(content_frame, text="General Statistics for All Employees", font=("Arial", 16, "bold"), 
                     background="#f5f6f5", anchor="center").pack(fill="x", pady=10)
            ttk.Label(content_frame, text=f"Total Sales Amount: ${total_sales:.2f}", style="Manager.Stats.TLabel", 
                     anchor="center").pack(fill="x", pady=5)
            ttk.Label(content_frame, text=f"Total Commissions: ${total_commissions:.2f}", style="Manager.Stats.TLabel", 
                     anchor="center").pack(fill="x", pady=5)
            ttk.Label(content_frame, text=f"Average Commissions: ${avg_commission:.2f}", style="Manager.Stats.TLabel", 
                     anchor="center").pack(fill="x", pady=5)
            ttk.Label(content_frame, text=f"30-Day Commission Forecast: ${predicted_commissions[-1][0]:.2f}", 
                     style="Manager.Stats.TLabel", anchor="center").pack(fill="x", pady=5)
            
            ttk.Label(content_frame, text="Employee Clustering:", font=("Arial", 14, "bold"), 
                     background="#f5f6f5", anchor="center").pack(fill="x", pady=10)
            cluster_text = "\n".join([f"{row['name']}: Cluster {row['cluster']} (Sales: {row['sale_count']}, Avg Amount: {row['avg_sale_amount']:.2f})"
                                    for _, row in employee_stats.iterrows()])
            # Create frame for clustering to limit text width
            cluster_frame = ttk.Frame(content_frame, style="TFrame")
            cluster_frame.pack(fill="x", pady=5)
            ttk.Label(cluster_frame, text=cluster_text, style="Manager.Stats.TLabel", anchor="center", 
                     justify="center", wraplength=800).pack(fill="x")
            
            ttk.Label(content_frame, text="Recommendations:", font=("Arial", 14, "bold"), 
                     background="#f5f6f5", anchor="center").pack(fill="x", pady=10)
            rec_text = "\n".join(recommendations)
            # Create frame for recommendations
            rec_frame = ttk.Frame(content_frame, style="TFrame")
            rec_frame.pack(fill="x", pady=5)
            ttk.Label(rec_frame, text=rec_text, style="Manager.Stats.TLabel", anchor="center", 
                     justify="center", wraplength=800).pack(fill="x")
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))
            
            ax1.plot(daily_data['days'], daily_data['commission'], label="Actual Commissions")
            future_days_plot = [last_day + i for i in range(1, 31)]
            ax1.plot(future_days_plot, predicted_commissions, color="green", label="Forecast")
            ax1.set_xlabel("Days")
            ax1.set_ylabel("Commissions")
            ax1.set_title("Commission Forecast")
            ax1.legend()
            ax1.grid(True)
            
            scatter = ax2.scatter(employee_stats['sale_count'], employee_stats['avg_sale_amount'],
                                c=employee_stats['cluster'], cmap='viridis')
            for i, row in employee_stats.iterrows():
                ax2.annotate(row['name'], (row['sale_count'], row['avg_sale_amount']))
            ax2.set_xlabel("Number of Sales")
            ax2.set_ylabel("Average Sale Amount")
            ax2.set_title("Employee Clustering")
            plt.colorbar(scatter, ax=ax2, label='Cluster')
            
            plt.subplots_adjust(hspace=0.4)
            plt.tight_layout()
            
            canvas_fig = FigureCanvasTkAgg(fig, master=content_frame)
            canvas_fig.draw()
            canvas_fig.get_tk_widget().pack(fill="x", pady=10)
            
            logging.debug("Statistics displayed successfully")
        except Exception as e:
            logging.error(f"Error displaying statistics: {str(e)}")
            if self.root.winfo_exists():
                messagebox.showerror("Error", f"Error displaying statistics: {str(e)}")
            else:
                print(f"Error displaying statistics (window unavailable): {str(e)}")