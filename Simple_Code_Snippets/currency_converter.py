import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import geocoder
import sqlite3
import os
from enum import Enum

# API Key (Replace with your actual API key)
API_KEY = "YOUR_API_KEY"  # Get a free API key from Open Exchange Rates or Fixer.io

# Database Configuration
DATABASE_NAME = "currency_converter.db"

class CurrencyAPI(Enum):
    OPEN_EXCHANGE_RATES = 1
    FIXER_IO = 2

SELECTED_API = CurrencyAPI.OPEN_EXCHANGE_RATES

def create_database():
    """Creates the database and tables if they don't exist."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS preferred_currencies (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            base_currency TEXT NOT NULL,
            target_currency TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversion_history (
            conversion_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            base_currency TEXT NOT NULL,
            target_currency TEXT NOT NULL,
            amount REAL NOT NULL,
            result REAL NOT NULL,
            rate REAL NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
            base_currency TEXT NOT NULL,
            target_currency TEXT NOT NULL,
            threshold REAL NOT NULL,
            direction TEXT NOT NULL,  -- 'above' or 'below'
            is_active INTEGER NOT NULL DEFAULT 1
        )
    """)

    conn.commit()
    conn.close()

def get_exchange_rate(base_currency, target_currency):
    """Fetches exchange rate from the API."""
    try:
        if SELECTED_API == CurrencyAPI.OPEN_EXCHANGE_RATES:
            url = f"https://openexchangerates.org/api/latest.json?app_id={API_KEY}"
            response = requests.get(url)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            data = response.json()
            rates = data['rates']
            if base_currency == "USD":
                rate = rates[target_currency]
            else:
                rate = rates[target_currency] / rates[base_currency]

        elif SELECTED_API == CurrencyAPI.FIXER_IO:
             url = f"http://data.fixer.io/api/latest?access_key={API_KEY}&base={base_currency}&symbols={target_currency}"
             response = requests.get(url)
             response.raise_for_status()
             data = response.json()
             if not data['success']:
                 raise Exception(data['error']['info'])
             rate = data['rates'][target_currency]
        return rate
    except requests.exceptions.RequestException as e:
        messagebox.showerror("API Error", f"Failed to connect to the API: {e}")
        return None
    except (KeyError, TypeError) as e:
        messagebox.showerror("API Error", f"Failed to parse API response: {e}")
        return None
    except Exception as e:
        messagebox.showerror("API Error", str(e))
        return None


def convert_currency():
    """Converts currency and updates the result label."""
    try:
        amount = float(amount_entry.get())
        base_currency = base_currency_combo.get()
        target_currency = target_currency_combo.get()

        if not all([amount, base_currency, target_currency]):
            raise ValueError("Please fill in all fields.")

        rate = get_exchange_rate(base_currency, target_currency)

        if rate is None:
            return  # Exit if API call failed

        result = amount * rate
        result_label.config(text=f"{amount:.2f} {base_currency} = {result:.2f} {target_currency}")

        # Store conversion history
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO conversion_history (base_currency, target_currency, amount, result, rate) VALUES (?, ?, ?, ?, ?)",
                       (base_currency, target_currency, amount, result, rate))
        conn.commit()
        conn.close()

    except ValueError as e:
        messagebox.showerror("Input Error", str(e))
    except Exception as e:
        messagebox.showerror("Error", str(e))


def get_historical_rates(base_currency, target_currency, days=7):
    """Fetches historical exchange rates from the API."""
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=days)

    historical_rates = {}
    current_date = start_date

    try:
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            if SELECTED_API == CurrencyAPI.OPEN_EXCHANGE_RATES:
               url = f"https://openexchangerates.org/api/historical/{date_str}.json?app_id={API_KEY}"
               response = requests.get(url)
               response.raise_for_status()
               data = response.json()
               rates = data['rates']
               if base_currency == "USD":
                   rate = rates[target_currency]
               else:
                   rate = rates[target_currency] / rates[base_currency]
            elif SELECTED_API == CurrencyAPI.FIXER_IO:
                url = f"http://data.fixer.io/api/{date_str}?access_key={API_KEY}&base={base_currency}&symbols={target_currency}"
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                if not data['success']:
                    continue  # Skip if data not available
                rate = data['rates'][target_currency]
            historical_rates[date_str] = rate
            current_date += datetime.timedelta(days=1)

        return historical_rates

    except requests.exceptions.RequestException as e:
        messagebox.showerror("API Error", f"Failed to connect to the API: {e}")
        return None
    except (KeyError, TypeError) as e:
        messagebox.showerror("API Error", f"Failed to parse API response: {e}")
        return None
    except Exception as e:
        messagebox.showerror("API Error", str(e))
        return None

def plot_historical_rates():
    """Plots historical exchange rates using Matplotlib."""
    base_currency = base_currency_combo.get()
    target_currency = target_currency_combo.get()

    historical_rates = get_historical_rates(base_currency, target_currency)

    if historical_rates is None:
        return

    dates = list(historical_rates.keys())
    rates = list(historical_rates.values())

    fig, ax = plt.subplots()
    ax.plot(dates, rates)
    ax.set_xlabel("Date")
    ax.set_ylabel("Exchange Rate")
    ax.set_title(f"Historical Exchange Rate: {base_currency} to {target_currency}")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Embed the plot in the Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid(row=5, column=0, columnspan=3, padx=10, pady=10)
    canvas.draw()

def detect_currency_by_location():
    """Detects currency based on user's location."""
    try:
        g = geocoder.ip('me')
        if g.country_code:
            # Basic mapping of country code to currency (can be expanded)
            country_code = g.country_code.upper()
            currency_map = {
                "US": "USD",
                "GB": "GBP",
                "EU": "EUR", #approximation
                "CA": "CAD",
                "AU": "AUD",
                "JP": "JPY",
                "IN": "INR",
                "CH": "CHF",
            }
            detected_currency = currency_map.get(country_code, "USD")  # Default to USD
            base_currency_combo.set(detected_currency)
        else:
            messagebox.showinfo("Location Detection", "Could not detect your location.  Using USD as default.")
            base_currency_combo.set("USD")
    except Exception as e:
        messagebox.showerror("Error", f"Error detecting location: {e}")


def save_preferred_currencies():
    """Saves preferred currencies to the database."""
    base_currency = base_currency_combo.get()
    target_currency = target_currency_combo.get()

    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO preferred_currencies (user_id, base_currency, target_currency) VALUES (1, ?, ?)",
                       (base_currency, target_currency))  # Assuming single user with ID 1
        conn.commit()
        conn.close()
        messagebox.showinfo("Preferences Saved", "Preferred currencies saved successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Error saving preferences: {e}")


def load_preferred_currencies():
    """Loads preferred currencies from the database."""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT base_currency, target_currency FROM preferred_currencies WHERE user_id = 1")
        data = cursor.fetchone()
        conn.close()

        if data:
            base_currency, target_currency = data
            base_currency_combo.set(base_currency)
            target_currency_combo.set(target_currency)
    except Exception as e:
        messagebox.showerror("Error", f"Error loading preferences: {e}")

def view_conversion_history():
    """Opens a new window to display conversion history."""
    history_window = tk.Toplevel(root)
    history_window.title("Conversion History")

    tree = ttk.Treeview(history_window, columns=("Timestamp", "Base Currency", "Target Currency", "Amount", "Result", "Rate"), show="headings")
    tree.heading("Timestamp", text="Timestamp")
    tree.heading("Base Currency", text="Base Currency")
    tree.heading("Target Currency", text="Target Currency")
    tree.heading("Amount", text="Amount")
    tree.heading("Result", text="Result")
    tree.heading("Rate", text="Rate")

    tree.column("Timestamp", width=150)
    tree.column("Base Currency", width=100)
    tree.column("Target Currency", width=100)
    tree.column("Amount", width=80)
    tree.column("Result", width=80)
    tree.column("Rate", width=80)

    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp, base_currency, target_currency, amount, result, rate FROM conversion_history ORDER BY timestamp DESC LIMIT 20") #Limit to 20 most recent
        history_data = cursor.fetchall()
        conn.close()

        for row in history_data:
            tree.insert("", tk.END, values=row)

    except Exception as e:
        messagebox.showerror("Error", f"Error fetching conversion history: {e}")

    tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

def set_alert():
    """Opens a dialog to set an exchange rate alert."""

    def save_alert():
        """Saves the alert to the database."""
        try:
            base_currency = base_currency_combo.get()
            target_currency = target_currency_combo.get()
            threshold = float(threshold_entry.get())
            direction = direction_var.get()

            if not all([base_currency, target_currency, threshold, direction]):
                raise ValueError("Please fill in all alert fields.")

            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO alerts (base_currency, target_currency, threshold, direction) VALUES (?, ?, ?, ?)",
                           (base_currency, target_currency, threshold, direction))
            conn.commit()
            conn.close()

            messagebox.showinfo("Alert Set", "Exchange rate alert set successfully.")
            alert_window.destroy()  # Close the alert window

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Error setting alert: {e}")


    alert_window = tk.Toplevel(root)
    alert_window.title("Set Exchange Rate Alert")

    # Threshold Label and Entry
    threshold_label = ttk.Label(alert_window, text="Threshold:")
    threshold_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
    threshold_entry = ttk.Entry(alert_window)
    threshold_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.E)

    # Direction Radio Buttons
    direction_var = tk.StringVar(value="above")
    above_radio = ttk.Radiobutton(alert_window, text="Above", variable=direction_var, value="above")
    below_radio = ttk.Radiobutton(alert_window, text="Below", variable=direction_var, value="below")
    above_radio.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
    below_radio.grid(row=1, column=1, padx=5, pady=5, sticky=tk.E)

    # Save Alert Button
    save_button = ttk.Button(alert_window, text="Save Alert", command=save_alert)
    save_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

def check_alerts():
    """Checks active alerts against current exchange rates and displays a message if triggered."""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT alert_id, base_currency, target_currency, threshold, direction FROM alerts WHERE is_active = 1")
        alerts = cursor.fetchall()
        conn.close()

        for alert_id, base_currency, target_currency, threshold, direction in alerts:
            rate = get_exchange_rate(base_currency, target_currency)

            if rate is None:
                continue # skip if API call failed

            if direction == "above" and rate > threshold:
                messagebox.showinfo("Alert Triggered", f"Exchange rate of {base_currency} to {target_currency} is now above {threshold:.2f} (Current rate: {rate:.2f})")
                deactivate_alert(alert_id) #Deactivate after trigger
            elif direction == "below" and rate < threshold:
                messagebox.showinfo("Alert Triggered", f"Exchange rate of {base_currency} to {target_currency} is now below {threshold:.2f} (Current rate: {rate:.2f})")
                deactivate_alert(alert_id)

    except Exception as e:
        print(f"Error checking alerts: {e}")  # Log the error, but don't necessarily show a message box

def deactivate_alert(alert_id):
     """Deactivates the alert with the given ID."""
     try:
         conn = sqlite3.connect(DATABASE_NAME)
         cursor = conn.cursor()
         cursor.execute("UPDATE alerts SET is_active = 0 WHERE alert_id = ?", (alert_id,))
         conn.commit()
         conn.close()
     except Exception as e:
         print(f"Error deactivating alert {alert_id}: {e}")

def populate_currency_list():
    """Populates currency lists based on API."""
    try:
        if SELECTED_API == CurrencyAPI.OPEN_EXCHANGE_RATES:
            url = f"https://openexchangerates.org/api/currencies.json?app_id={API_KEY}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            currencies = list(data.keys())
        elif SELECTED_API == CurrencyAPI.FIXER_IO:
            url = f"http://data.fixer.io/api/symbols?access_key={API_KEY}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if not data['success']:
                raise Exception(data['error']['info'])
            currencies = list(data['symbols'].keys())

        return currencies
    except requests.exceptions.RequestException as e:
        messagebox.showerror("API Error", f"Failed to connect to the API: {e}")
        return ["USD", "EUR", "GBP"]
    except (KeyError, TypeError) as e:
        messagebox.showerror("API Error", f"Failed to parse API response: {e}")
        return ["USD", "EUR", "GBP"]
    except Exception as e:
        messagebox.showerror("API Error", str(e))
        return ["USD", "EUR", "GBP"]

# Main application
if __name__ == "__main__":

    # Create database if it doesn't exist
    create_database()

    root = tk.Tk()
    root.title("Advanced Currency Converter")

    # Currency Options (Using a hardcoded list, can be fetched from API)
    currency_options = populate_currency_list()

    # Amount Label and Entry
    amount_label = ttk.Label(root, text="Amount:")
    amount_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
    amount_entry = ttk.Entry(root)
    amount_entry.grid(row=0, column=1, padx=10, pady=10, sticky=tk.E)

    # Base Currency Label and Combo
    base_currency_label = ttk.Label(root, text="Base Currency:")
    base_currency_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
    base_currency_combo = ttk.Combobox(root, values=currency_options)
    base_currency_combo.grid(row=1, column=1, padx=10, pady=10, sticky=tk.E)

    # Target Currency Label and Combo
    target_currency_label = ttk.Label(root, text="Target Currency:")
    target_currency_label.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
    target_currency_combo = ttk.Combobox(root, values=currency_options)
    target_currency_combo.grid(row=2, column=1, padx=10, pady=10, sticky=tk.E)

    # Convert Button
    convert_button = ttk.Button(root, text="Convert", command=convert_currency)
    convert_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    # Result Label
    result_label = ttk.Label(root, text="")
    result_label.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

    # Historical Data Button
    historical_data_button = ttk.Button(root, text="Show Historical Data", command=plot_historical_rates)
    historical_data_button.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

    # Detect Currency Button
    detect_currency_button = ttk.Button(root, text="Detect Currency", command=detect_currency_by_location)
    detect_currency_button.grid(row=1, column=2, padx=10, pady=10)

     # Save Preferences Button
    save_preferences_button = ttk.Button(root, text="Save Preferences", command=save_preferred_currencies)
    save_preferences_button.grid(row=7, column=0, padx=10, pady=10)

    # Load Preferences Button
    load_preferences_button = ttk.Button(root, text="Load Preferences", command=load_preferred_currencies)
    load_preferences_button.grid(row=7, column=1, padx=10, pady=10)

    # View History Button
    view_history_button = ttk.Button(root, text="View Conversion History", command=view_conversion_history)
    view_history_button.grid(row=8, column=0, columnspan=2, padx=10, pady=10)

    # Set Alert Button
    set_alert_button = ttk.Button(root, text="Set Exchange Rate Alert", command=set_alert)
    set_alert_button.grid(row=9, column=0, columnspan=2, padx=10, pady=10)

    # Load preferred currencies on startup
    load_preferred_currencies()

    # Periodic alert check (every 60 seconds)
    def periodic_check():
        check_alerts()
        root.after(60000, periodic_check)  # Check every 60 seconds (60000 milliseconds)

    root.after(5000, periodic_check) #Start alert check after 5 seconds

    root.mainloop()