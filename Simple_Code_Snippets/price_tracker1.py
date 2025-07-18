import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import requests
from bs4 import BeautifulSoup
import schedule
import time
import threading
from plyer import notification
from fake_useragent import UserAgent
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PriceTrackerApp:
    def __init__(self, master):
        self.master = master
        master.title("E-commerce Price Tracker")

        self.db_conn = sqlite3.connect('tracked_products.db')
        self.cursor = self.db_conn.cursor()
        self.create_table()

        self.user_agent = UserAgent()

        self.product_url_label = ttk.Label(master, text="Product URL:")
        self.product_url_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.product_url_entry = ttk.Entry(master, width=50)
        self.product_url_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        self.add_button = ttk.Button(master, text="Add Product", command=self.add_product)
        self.add_button.grid(row=0, column=2, padx=5, pady=5)

        self.tree = ttk.Treeview(master, columns=('Name', 'Current Price', 'Last Checked'), show='headings')
        self.tree.heading('Name', text='Name')
        self.tree.heading('Current Price', text='Current Price')
        self.tree.heading('Last Checked', text='Last Checked')
        self.tree.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky='nsew')

        self.check_prices_button = ttk.Button(master, text="Check Prices", command=self.check_prices)
        self.check_prices_button.grid(row=2, column=0, columnspan=3, padx=5, pady=5)

        self.interval_label = ttk.Label(master, text="Check Interval (hours):")
        self.interval_label.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)

        self.interval_entry = ttk.Entry(master, width=5)
        self.interval_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        self.interval_entry.insert(0, "6")  # Default interval

        self.start_scheduler_button = ttk.Button(master, text="Start Auto-Check", command=self.start_scheduler)
        self.start_scheduler_button.grid(row=3, column=2, padx=5, pady=5)

        master.grid_columnconfigure(1, weight=1)
        master.grid_rowconfigure(1, weight=1)

        self.load_products()
        self.scheduler_running = False


    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                name TEXT,
                initial_price REAL,
                current_price REAL,
                last_checked TEXT
            )
        ''')
        self.db_conn.commit()

    def add_product(self):
        url = self.product_url_entry.get()
        try:
            name, price = self.scrape_product_details(url)
            self.cursor.execute("INSERT INTO products (url, name, initial_price, current_price, last_checked) VALUES (?, ?, ?, ?, datetime('now'))", (url, name, price, price))
            self.db_conn.commit()
            self.load_products()
            self.product_url_entry.delete(0, tk.END)
            messagebox.showinfo("Success", "Product added successfully.")
        except ValueError as e:
             messagebox.showerror("Error", str(e))
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Product URL already exists.")
        except Exception as e:
            logging.error(f"Error adding product: {e}")
            messagebox.showerror("Error", f"Failed to add product. Check URL and network connection.")

    def load_products(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.cursor.execute("SELECT name, current_price, last_checked FROM products")
        for row in self.cursor.fetchall():
            self.tree.insert('', 'end', values=row)

    def scrape_product_details(self, url):
        try:
            headers = {'User-Agent': self.user_agent.random}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            soup = BeautifulSoup(response.content, 'html.parser')

            if "amazon.com" in url:
                name = soup.find('span', {'id': 'productTitle'}).text.strip()
                price_element = soup.find('span', {'class': 'a-offscreen'})
                if not price_element:
                    price_element = soup.find('span', {'class': 'a-price'})
                    if price_element:
                        price_element = price_element.find('span', {'class': 'a-offscreen'})

                if price_element:
                    price = price_element.text.strip().replace('$', '').replace(',', '')
                    return name, float(price)
                else:
                    raise ValueError("Price element not found on Amazon.")

            elif "ebay.com" in url:
                name = soup.find('h1', {'class': 'item-title__mainTitle'}).text.strip()
                price_element = soup.find('span', {'class': 'ux-price-block__price__text'})
                if price_element:
                    price = price_element.text.strip().replace('$', '').replace(',', '')
                    return name, float(price)
                else:
                    raise ValueError("Price element not found on eBay.")

            elif "alibaba.com" in url:
                name = soup.find('h1', {'class': 'title'}).text.strip()
                price_element = soup.find('div', {'class': 'price'})
                if price_element:
                    price = price_element.text.strip().replace('US $', '').replace(',', '')
                    #Alibaba prices can be a range - take the lower value
                    if '-' in price:
                        price = price.split('-')[0].strip()
                    return name, float(price)
                else:
                    raise ValueError("Price element not found on Alibaba.")
            else:
                raise ValueError("Unsupported e-commerce site.")

        except requests.exceptions.RequestException as e:
            logging.error(f"Network error during scraping: {e}")
            raise ValueError(f"Network error: {e}")
        except AttributeError as e:
            logging.error(f"Element not found during scraping: {e}")
            raise ValueError("Could not find product name or price on the page. Website structure might have changed.")
        except Exception as e:
            logging.error(f"Error during scraping: {e}")
            raise ValueError(f"An unexpected error occurred during scraping: {e}")

    def check_prices(self):
        self.cursor.execute("SELECT id, url, current_price FROM products")
        products = self.cursor.fetchall()
        for product_id, url, old_price in products:
            try:
                name, new_price = self.scrape_product_details(url)
                if new_price < old_price:
                    self.send_notification(name, new_price)
                self.cursor.execute("UPDATE products SET current_price = ?, last_checked = datetime('now') WHERE id = ?", (new_price, product_id))
                self.db_conn.commit()
            except Exception as e:
                logging.error(f"Error checking price for product {url}: {e}")
                print(f"Error checking price for product {url}: {e}") # Print for debugging in console

        self.load_products()
        messagebox.showinfo("Update", "Prices checked and updated.")

    def send_notification(self, product_name, new_price):
        notification.notify(
            title="Price Drop Alert!",
            message=f"The price of {product_name} has dropped to ${new_price:.2f}!",
            app_name="E-commerce Price Tracker",
            timeout=10
        )

    def scheduled_check(self):
         self.check_prices()

    def start_scheduler(self):
        if self.scheduler_running:
            messagebox.showinfo("Info", "Scheduler is already running.")
            return

        try:
            interval = int(self.interval_entry.get())
            if interval <= 0:
                raise ValueError("Interval must be a positive integer.")
        except ValueError:
            messagebox.showerror("Error", "Invalid interval. Please enter a positive integer.")
            return

        schedule.every(interval).hours.do(self.scheduled_check)
        self.scheduler_running = True

        def run_scheduler():
            while self.scheduler_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        messagebox.showinfo("Info", f"Auto-check started. Prices will be checked every {interval} hours.")

    def on_closing(self):
        self.scheduler_running = False  # Stop the scheduler
        self.db_conn.close()
        self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = PriceTrackerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()