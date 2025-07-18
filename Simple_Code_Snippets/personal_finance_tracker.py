```python
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import os
import hashlib
import json
import yfinance as yf
import bcrypt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

nltk.download('stopwords', quiet=True)

class FinanceTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Finance Tracker")

        self.db_name = "finance_data.db"
        self.conn = None
        self.cursor = None
        self.current_user = None
        self.encryption_key = b'YourSecretEncryptionKey'  # Replace with a strong, randomly generated key

        self.setup_database()
        self.setup_ui()
        self.load_categories()
        self.train_categorization_model()

    def setup_database(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date DATE NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS investments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                ticker TEXT NOT NULL,
                quantity REAL NOT NULL,
                purchase_price REAL NOT NULL,
                purchase_date DATE NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS debts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT NOT NULL,
                principal REAL NOT NULL,
                interest_rate REAL NOT NULL,
                minimum_payment REAL NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        self.conn.commit()

    def setup_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.login_tab = ttk.Frame(self.notebook)
        self.transactions_tab = ttk.Frame(self.notebook)
        self.budget_tab = ttk.Frame(self.notebook)
        self.reports_tab = ttk.Frame(self.notebook)
        self.investments_tab = ttk.Frame(self.notebook)
        self.debts_tab = ttk.Frame(self.notebook)
        self.settings_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.login_tab, text="Login/Register")
        self.notebook.add(self.transactions_tab, text="Transactions")
        self.notebook.add(self.budget_tab, text="Budget")
        self.notebook.add(self.reports_tab, text="Reports")
        self.notebook.add(self.investments_tab, text="Investments")
        self.notebook.add(self.debts_tab, text="Debts")
        self.notebook.add(self.settings_tab, text="Settings")

        self.setup_login_tab()
        self.setup_transactions_tab()
        self.setup_budget_tab()
        self.setup_reports_tab()
        self.setup_investments_tab()
        self.setup_debts_tab()
        self.setup_settings_tab()

    def setup_login_tab(self):
        # Login widgets
        ttk.Label(self.login_tab, text="Username:").grid(row=0, column=0, padx=5, pady=5)
        self.login_username_entry = ttk.Entry(self.login_tab)
        self.login_username_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.login_tab, text="Password:").grid(row=1, column=0, padx=5, pady=5)
        self.login_password_entry = tk.Entry(self.login_tab, show="*")
        self.login_password_entry.grid(row=1, column=1, padx=5, pady=5)

        login_button = ttk.Button(self.login_tab, text="Login", command=self.login)
        login_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        # Registration widgets
        ttk.Label(self.login_tab, text="New Username:").grid(row=3, column=0, padx=5, pady=5)
        self.register_username_entry = ttk.Entry(self.login_tab)
        self.register_username_entry.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(self.login_tab, text="New Password:").grid(row=4, column=0, padx=5, pady=5)
        self.register_password_entry = tk.Entry(self.login_tab, show="*")
        self.register_password_entry.grid(row=4, column=1, padx=5, pady=5)

        ttk.Label(self.login_tab, text="Email (optional):").grid(row=5, column=0, padx=5, pady=5)
        self.register_email_entry = ttk.Entry(self.login_tab)
        self.register_email_entry.grid(row=5, column=1, padx=5, pady=5)

        register_button = ttk.Button(self.login_tab, text="Register", command=self.register)
        register_button.grid(row=6, column=0, columnspan=2, padx=5, pady=5)


    def setup_transactions_tab(self):
        # Date
        ttk.Label(self.transactions_tab, text="Date (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=5)
        self.date_entry = ttk.Entry(self.transactions_tab)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)

        # Description
        ttk.Label(self.transactions_tab, text="Description:").grid(row=1, column=0, padx=5, pady=5)
        self.description_entry = ttk.Entry(self.transactions_tab)
        self.description_entry.grid(row=1, column=1, padx=5, pady=5)

        # Category
        ttk.Label(self.transactions_tab, text="Category:").grid(row=2, column=0, padx=5, pady=5)
        self.category_combo = ttk.Combobox(self.transactions_tab, values=[])  # Categories will be loaded dynamically
        self.category_combo.grid(row=2, column=1, padx=5, pady=5)

        # Amount
        ttk.Label(self.transactions_tab, text="Amount:").grid(row=3, column=0, padx=5, pady=5)
        self.amount_entry = ttk.Entry(self.transactions_tab)
        self.amount_entry.grid(row=3, column=1, padx=5, pady=5)

        # Add Transaction Button
        add_button = ttk.Button(self.transactions_tab, text="Add Transaction", command=self.add_transaction)
        add_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

         # Import CSV Button
        import_button = ttk.Button(self.transactions_tab, text="Import CSV", command=self.import_csv)
        import_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

        # Transaction Treeview
        self.transaction_tree = ttk.Treeview(self.transactions_tab, columns=("ID", "Date", "Description", "Category", "Amount"), show="headings")
        self.transaction_tree.heading("ID", text="ID")
        self.transaction_tree.heading("Date", text="Date")
        self.transaction_tree.heading("Description", text="Description")
        self.transaction_tree.heading("Category", text="Category")
        self.transaction_tree.heading("Amount", text="Amount")

        self.transaction_tree.column("ID", width=30)
        self.transaction_tree.column("Date", width=100)
        self.transaction_tree.column("Description", width=200)
        self.transaction_tree.column("Category", width=100)
        self.transaction_tree.column("Amount", width=80)

        self.transaction_tree.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        # Delete Transaction Button
        delete_button = ttk.Button(self.transactions_tab, text="Delete Transaction", command=self.delete_transaction)
        delete_button.grid(row=7, column=0, columnspan=2, padx=5, pady=5)

        # Configure grid weights for resizing
        self.transactions_tab.grid_columnconfigure(0, weight=1)
        self.transactions_tab.grid_columnconfigure(1, weight=1)
        self.transactions_tab.grid_rowconfigure(6, weight=1)  # Make the treeview expand vertically


    def setup_budget_tab(self):
         # Category
        ttk.Label(self.budget_tab, text="Category:").grid(row=0, column=0, padx=5, pady=5)
        self.budget_category_combo = ttk.Combobox(self.budget_tab, values=[])  # Categories will be loaded dynamically
        self.budget_category_combo.grid(row=0, column=1, padx=5, pady=5)

        # Amount
        ttk.Label(self.budget_tab, text="Budgeted Amount:").grid(row=1, column=0, padx=5, pady=5)
        self.budget_amount_entry = ttk.Entry(self.budget_tab)
        self.budget_amount_entry.grid(row=1, column=1, padx=5, pady=5)

        # Add Budget Button
        add_budget_button = ttk.Button(self.budget_tab, text="Set Budget", command=self.set_budget)
        add_budget_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        # Budget Treeview
        self.budget_tree = ttk.Treeview(self.budget_tab, columns=("ID", "Category", "Amount"), show="headings")
        self.budget_tree.heading("ID", text="ID")
        self.budget_tree.heading("Category", text="Category")
        self.budget_tree.heading("Amount", text="Amount")

        self.budget_tree.column("ID", width=30)
        self.budget_tree.column("Category", width=150)
        self.budget_tree.column("Amount", width=100)

        self.budget_tree.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        # Delete Budget Button
        delete_budget_button = ttk.Button(self.budget_tab, text="Delete Budget", command=self.delete_budget)
        delete_budget_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        # Configure grid weights for resizing
        self.budget_tab.grid_columnconfigure(0, weight=1)
        self.budget_tab.grid_columnconfigure(1, weight=1)
        self.budget_tab.grid_rowconfigure(3, weight=1)  # Make the treeview expand vertically

    def setup_reports_tab(self):
        # Report Type
        ttk.Label(self.reports_tab, text="Report Type:").grid(row=0, column=0, padx=5, pady=5)
        self.report_type_combo = ttk.Combobox(self.reports_tab, values=["Spending by Category", "Monthly Summary"])
        self.report_type_combo.grid(row=0, column=1, padx=5, pady=5)
        self.report_type_combo.set("Spending by Category")  # Default value

        # Start Date
        ttk.Label(self.reports_tab, text="Start Date (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5)
        self.report_start_date_entry = ttk.Entry(self.reports_tab)
        self.report_start_date_entry.grid(row=1, column=1, padx=5, pady=5)

        # End Date
        ttk.Label(self.reports_tab, text="End Date (YYYY-MM-DD):").grid(row=2, column=0, padx=5, pady=5)
        self.report_end_date_entry = ttk.Entry(self.reports_tab)
        self.report_end_date_entry.grid(row=2, column=1, padx=5, pady=5)

        # Generate Report Button
        generate_report_button = ttk.Button(self.reports_tab, text="Generate Report", command=self.generate_report)
        generate_report_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        # Report Display (Text Area)
        self.report_text = tk.Text(self.reports_tab, height=15, width=60)
        self.report_text.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        # Export to PDF Button
        self.export_pdf_button = ttk.Button(self.reports_tab, text="Export to PDF", command=self.export_to_pdf)
        self.export_pdf_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

        # Visualization Frame (for plots)
        self.visualization_frame = tk.Frame(self.reports_tab)
        self.visualization_frame.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        # Configure grid weights for resizing
        self.reports_tab.grid_columnconfigure(0, weight=1)
        self.reports_tab.grid_columnconfigure(1, weight=1)
        self.reports_tab.grid_rowconfigure(4, weight=1) # Report Text area expands

    def setup_investments_tab(self):
        # Ticker Symbol
        ttk.Label(self.investments_tab, text="Ticker Symbol:").grid(row=0, column=0, padx=5, pady=5)
        self.ticker_entry = ttk.Entry(self.investments_tab)
        self.ticker_entry.grid(row=0, column=1, padx=5, pady=5)

        # Quantity
        ttk.Label(self.investments_tab, text="Quantity:").grid(row=1, column=0, padx=5, pady=5)
        self.quantity_entry = ttk.Entry(self.investments_tab)
        self.quantity_entry.grid(row=1, column=1, padx=5, pady=5)

        # Purchase Price
        ttk.Label(self.investments_tab, text="Purchase Price:").grid(row=2, column=0, padx=5, pady=5)
        self.purchase_price_entry = ttk.Entry(self.investments_tab)
        self.purchase_price_entry.grid(row=2, column=1, padx=5, pady=5)

        # Purchase Date
        ttk.Label(self.investments_tab, text="Purchase Date (YYYY-MM-DD):").grid(row=3, column=0, padx=5, pady=5)
        self.purchase_date_entry = ttk.Entry(self.investments_tab)
        self.purchase_date_entry.grid(row=3, column=1, padx=5, pady=5)

        # Add Investment Button
        add_investment_button = ttk.Button(self.investments_tab, text="Add Investment", command=self.add_investment)
        add_investment_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        # Investment Treeview
        self.investment_tree = ttk.Treeview(self.investments_tab, columns=("ID", "Ticker", "Quantity", "Purchase Price", "Purchase Date", "Current Value", "Profit/Loss"), show="headings")
        self.investment_tree.heading("ID", text="ID")
        self.investment_tree.heading("Ticker", text="Ticker")
        self.investment_tree.heading("Quantity", text="Quantity")
        self.investment_tree.heading("Purchase Price", text="Purchase Price")
        self.investment_tree.heading("Purchase Date", text="Purchase Date")
        self.investment_tree.heading("Current Value", text="Current Value")
        self.investment_tree.heading("Profit/Loss", text="Profit/Loss")

        self.investment_tree.column("ID", width=30)
        self.investment_tree.column("Ticker", width=80)
        self.investment_tree.column("Quantity", width=60)
        self.investment_tree.column("Purchase Price", width=80)
        self.investment_tree.column("Purchase Date", width=100)
        self.investment_tree.column("Current Value", width=80)
        self.investment_tree.column("Profit/Loss", width=80)

        self.investment_tree.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        # Delete Investment Button
        delete_investment_button = ttk.Button(self.investments_tab, text="Delete Investment", command=self.delete_investment)
        delete_investment_button.grid(row=6, column=0, columnspan=2, padx=5, pady=5)

        # Update Prices Button
        update_prices_button = ttk.Button(self.investments_tab, text="Update Prices", command=self.update_investment_prices)
        update_prices_button.grid(row=7, column=0, columnspan=2, padx=5, pady=5)

        # Configure grid weights for resizing
        self.investments_tab.grid_columnconfigure(0, weight=1)
        self.investments_tab.grid_columnconfigure(1, weight=1)
        self.investments_tab.grid_rowconfigure(5, weight=1)  # Make the treeview expand vertically

    def setup_debts_tab(self):
        # Loan Name
        ttk.Label(self.debts_tab, text="Loan Name:").grid(row=0, column=0, padx=5, pady=5)
        self.debt_name_entry = ttk.Entry(self.debts_tab)
        self.debt_name_entry.grid(row=0, column=1, padx=5, pady=5)

        # Principal
        ttk.Label(self.debts_tab, text="Principal Amount:").grid(row=1, column=0, padx=5, pady=5)
        self.debt_principal_entry = ttk.Entry(self.debts_tab)
        self.debt_principal_entry.grid(row=1, column=1, padx=5, pady=5)

        # Interest Rate
        ttk.Label(self.debts_tab, text="Interest Rate (%):").grid(row=2, column=0, padx=5, pady=5)
        self.debt_interest_rate_entry = ttk.Entry(self.debts_tab)
        self.debt_interest_rate_entry.grid(row=2, column=1, padx=5, pady=5)

        # Minimum Payment
        ttk.Label(self.debts_tab, text="Minimum Payment:").grid(row=3, column=0, padx=5, pady=5)
        self.debt_minimum_payment_entry = ttk.Entry(self.debts_tab)
        self.debt_minimum_payment_entry.grid(row=3, column=1, padx=5, pady=5)

        # Add Debt Button
        add_debt_button = ttk.Button(self.debts_tab, text="Add Debt", command=self.add_debt)
        add_debt_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        # Debt Treeview
        self.debt_tree = ttk.Treeview(self.debts_tab, columns=("ID", "Name", "Principal", "Interest Rate", "Minimum Payment"), show="headings")
        self.debt_tree.heading("ID", text="ID")
        self.debt_tree.heading("Name", text="Name")
        self.debt_tree.heading("Principal", text="Principal")
        self.debt_tree.heading("Interest Rate", text="Interest Rate")
        self.debt_tree.heading("Minimum Payment", text="Minimum Payment")

        self.debt_tree.column("ID", width=30)
        self.debt_tree.column("Name", width=120)
        self.debt_tree.column("Principal", width=100)
        self.debt_tree.column("Interest Rate", width=80)
        self.debt_tree.column("Minimum Payment", width=80)

        self.debt_tree.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        # Delete Debt Button
        delete_debt_button = ttk.Button(self.debts_tab, text="Delete Debt", command=self.delete_debt)
        delete_debt_button.grid(row=6, column=0, columnspan=2, padx=5, pady=5)

        # Calculate Repayment Schedule Button
        calculate_schedule_button = ttk.Button(self.debts_tab, text="Calculate Repayment Schedule", command=self.calculate_repayment_schedule)
        calculate_schedule_button.grid(row=7, column=0, columnspan=2, padx=5, pady=5)

        # Configure grid weights for resizing
        self.debts_tab.grid_columnconfigure(0, weight=1)
        self.debts_tab.grid_columnconfigure(1, weight=1)
        self.debts_tab.grid_rowconfigure(5, weight=1)  # Make the treeview expand vertically

    def setup_settings_tab(self):
        # Anomaly Detection Settings
        ttk.Label(self.settings_tab, text="Anomaly Detection Threshold:").grid(row=0, column=0, padx=5, pady=5)
        self.anomaly_threshold_entry = ttk.Entry(self.settings_tab)
        self.anomaly_threshold_entry.grid(row=0, column=1, padx=5, pady=5)
        self.anomaly_threshold_entry.insert(0, "3.0")  # Default threshold (e.g., 3 standard deviations)

        # Category Management
        ttk.Label(self.settings_tab, text="Add New Category:").grid(row=1, column=0, padx=5, pady=5)
        self.new_category_entry = ttk.Entry(self.settings_tab)
        self.new_category_entry.grid(row=1, column=1, padx=5, pady=5)
        add_category_button = ttk.Button(self.settings_tab, text="Add Category", command=self.add_category)
        add_category_button.grid(row=1, column=2, padx=5, pady=5)

        # Email Notifications
        ttk.Label(self.settings_tab, text="Email for Notifications:").grid(row=2, column=0, padx=5, pady=5)
        self.notification_email_entry = ttk.Entry(self.settings_tab)
        self.notification_email_entry.grid(row=2, column=1, padx=5, pady=5)
        enable_notifications_button = ttk.Button(self.settings_tab, text="Enable Notifications", command=self.enable_notifications)
        enable_notifications_button.grid(row=2, column=2, padx=5, pady=5)

        # SMTP Settings (for email)
        ttk.Label(self.settings_tab, text="SMTP Server:").grid(row=3, column=0, padx=5, pady=5)
        self.smtp_server_entry = ttk.Entry(self.settings_tab)
        self.smtp_server_entry.grid(row=3, column=1, padx=5, pady=5)
        self.smtp_server_entry.insert(0, "smtp.gmail.com")  # Default: Gmail SMTP

        ttk.Label(self.settings_tab, text="SMTP Port:").grid(row=4, column=0, padx=5, pady=5)
        self.smtp_port_entry = ttk.Entry(self.settings_tab)
        self.smtp_port_entry.grid(row=4, column=1, padx=5, pady=5)
        self.smtp_port_entry.insert(0, "587")  # Default: Gmail SMTP Port

        ttk.Label(self.settings_tab, text="SMTP Username:").grid(row=5, column=0, padx=5, pady=5)
        self.smtp_username_entry = ttk.Entry(self.settings_tab)
        self.smtp_username_entry.grid(row=5, column=1, padx=5, pady=5)

        ttk.Label(self.settings_tab, text="SMTP Password:").grid(row=6, column=0, padx=5, pady=5)
        self.smtp_password_entry = tk.Entry(self.settings_tab, show="*")
        self.smtp_password_entry.grid(row=6, column=1, padx=5, pady=5)

    def login(self):
        username = self.login_username_entry.get()
        password = self.login_password_entry.get()

        self.cursor.execute("SELECT id, password FROM users WHERE username=?", (username,))
        result = self.cursor.fetchone()

        if result:
            user_id, hashed_password = result
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                self.current_user = user_id
                messagebox.showinfo("Login Successful", "You have successfully logged in.")
                self.load_transactions()
                self.load_budgets()
                self.load_investments()
                self.load_debts()
                self.detect_anomalies()
                return
        messagebox.showerror("Login Failed", "Invalid username or password.")

    def register(self):
        username = self.register_username_entry.get()
        password = self.register_password_entry.get()
        email = self.register_email_entry.get()

        if not username or not password:
            messagebox.showerror("Registration Failed", "Username and password are required.")
            return

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        try:
            self.cursor.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", (username, hashed_password, email))
            self.conn.commit()
            messagebox.showinfo("Registration Successful", "You have successfully registered.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Registration Failed", "Username already exists.")

    def add_transaction(self):
        if not self.current_user:
            messagebox.showerror("Error", "Please log in first.")
            return

        date = self.date_entry.get()
        description = self.description_entry.get()
        category = self.category_combo.get()
        amount = self.amount_entry.get()

        try:
            amount = float(amount)
            datetime.datetime.strptime(date, '%Y-%m-%d')  # Validate date format
        except ValueError:
            messagebox.showerror("Error", "Invalid date or amount format.")
            return

        self.cursor.execute("INSERT INTO transactions (user_id, date, description, category, amount) VALUES (?, ?, ?, ?, ?)",
                            (self.current_user, date, description, category, amount))
        self.conn.commit()
        self.load_transactions()
        self.detect_anomalies()
        self.clear_transaction_fields()

    def import_csv(self):
        if not self.current_user:
            messagebox.showerror("Error", "Please log in first.")
            return

        filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not filepath:
            return

        try:
            with open(filepath, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        date = row['Date']
                        description = row['Description']
                        amount = float(row['Amount'])

                        # Attempt to categorize the transaction
                        category = self.predict_category(description)

                        self.cursor.execute("INSERT INTO transactions (user_id, date, description, category, amount) VALUES (?, ?, ?, ?, ?)",
                                            (self.current_user, date, description, category, amount))
                    except (KeyError, ValueError) as e:
                        print(f"Skipping row due to error: {e}")  # Log the error
                        continue # Skip the row if there's an error parsing it

                self.conn.commit()
                self.load_transactions()
                self.detect_anomalies()
                messagebox.showinfo("Import Successful", "CSV file imported successfully.")

        except Exception as e:
            messagebox.showerror("Import Failed", f"Error importing CSV file: {e}")

    def delete_transaction(self):
        if not self.current_user:
            messagebox.showerror("Error", "Please log in first.")
            return

        selected_item = self.transaction_tree.selection()
        if not selected_item:
            messagebox.showinfo("Info", "Please select a transaction to delete.")
            return

        transaction_id = self.transaction_tree.item(selected_item[0])['values'][0]

        confirmation = messagebox.askyesno("Confirmation", "Are you sure you want to delete this transaction?")
        if confirmation:
            self.cursor.execute("DELETE FROM transactions WHERE id=?", (transaction_id,))
            self.conn.commit()
            self.load_transactions()
            self.detect_anomalies()

    def load_transactions(self):
        if not self.current_user:
            return

        for item in self.transaction_tree.get_children():
            self.transaction_tree.delete(item)

        self.cursor.execute("SELECT id, date, description, category, amount FROM transactions WHERE user_id=?", (self.current_user,))
        transactions = self.cursor.fetchall()

        for transaction in transactions:
            self.transaction_tree.insert("", "end", values=transaction)

    def set_budget(self):
        if not self.current_user:
            messagebox.showerror("Error", "Please log in first.")
            return

        category = self.budget_category_combo.get()
        amount = self.budget_amount_entry.get()

        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Error", "Invalid amount format.")
            return

        # Check if a budget already exists for this category
        self.cursor.execute("SELECT id FROM budgets WHERE user_id=? AND category=?", (self.current_user, category))
        existing_budget = self.cursor.fetchone()

        if existing_budget:
            # Update the existing budget
            budget_id = existing_budget[0]
            self.cursor.execute("UPDATE budgets SET amount=? WHERE id=?", (amount, budget_id))
        else:
            # Insert a new budget
            self.cursor.execute("INSERT INTO budgets (user_id, category, amount) VALUES (?, ?, ?)", (self.current_user, category, amount))

        self.conn.commit()
        self.load_budgets()
        self.clear_budget_fields()

    def delete_budget(self):
        if not self.current_user:
            messagebox.showerror("Error", "Please log in first.")
            return

        selected_item = self.budget_tree.selection()
        if not selected_item:
            messagebox.showinfo("Info", "Please select a budget to delete.")
            return

        budget_id = self.budget_tree.item(selected_item[0])['values'][0]

        confirmation = messagebox.askyesno("Confirmation", "Are you sure