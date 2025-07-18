import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import random
import smtplib
from email.mime.text import MIMEText
import os
import logging
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration
CONFIG_FILE = 'config.json'

def load_config():
    """Loads configuration from a JSON file."""
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        logging.error(f"Config file '{CONFIG_FILE}' not found.")
        return None
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON in '{CONFIG_FILE}'.")
        return None

config = load_config()

if not config:
    exit()

USER_AGENTS = config.get('user_agents', [])
PROXIES = config.get('proxies', [])
EMAIL_CONFIG = config.get('email_config', {})
PRODUCTS = config.get('products', [])
DATA_STORAGE = config.get('data_storage', 'data.json')
SCRAPE_DELAY = config.get('scrape_delay', 5)
PRICE_DROP_THRESHOLD = config.get('price_drop_threshold', 0.1)


def get_random_user_agent():
    """Returns a random User-Agent from the list."""
    return random.choice(USER_AGENTS) if USER_AGENTS else None

def get_random_proxy():
    """Returns a random proxy from the list."""
    return random.choice(PROXIES) if PROXIES else None

def fetch_page(url, use_proxy=True):
    """Fetches a webpage using Requests with error handling, User-Agent rotation, and proxy support."""
    headers = {'User-Agent': get_random_user_agent()} if get_random_user_agent() else {}
    proxy = get_random_proxy() if use_proxy else None
    proxies = {'http': proxy, 'https': proxy} if proxy else None

    try:
        response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching {url}: {e}")
        return None

def extract_amazon_price(soup):
    """Extracts the price from an Amazon product page."""
    try:
        price_whole = soup.find("span", class_="a-price-whole").text.strip()
        price_fraction = soup.find("span", class_="a-price-fraction").text.strip()
        return float(price_whole + price_fraction)
    except AttributeError:
        logging.warning("Amazon price not found.")
        return None

def extract_ebay_price(soup):
    """Extracts the price from an eBay product page."""
    try:
        price = soup.find("span", class_="ebay-bin-price").text.replace('US $', '').strip()
        return float(price)
    except AttributeError:
        logging.warning("eBay price not found.")
        return None

def extract_bestbuy_price(soup):
    """Extracts the price from a Best Buy product page."""
    try:
        price = soup.find("div", class_="priceView-customer-price").find("span").text.replace('$', '').replace(',', '').strip()
        return float(price)
    except AttributeError:
        logging.warning("Best Buy price not found.")
        return None

def validate_data(data):
    """Validates that the extracted data contains necessary fields and correct data types."""
    if not isinstance(data, dict):
        logging.error("Data is not a dictionary.")
        return False
    if 'product_name' not in data or not isinstance(data['product_name'], str):
        logging.error("Invalid or missing product_name.")
        return False
    if 'price' not in data or not isinstance(data['price'], (int, float)):
        logging.error("Invalid or missing price.")
        return False
    if 'url' not in data or not isinstance(data['url'], str):
        logging.error("Invalid or missing URL.")
        return False
    if 'website' not in data or not isinstance(data['website'], str):
        logging.error("Invalid or missing website.")
        return False
    return True

def scrape_product(product_url):
    """Scrapes product information from a given URL based on the website."""
    logging.info(f"Scraping {product_url}")
    response = fetch_page(product_url)
    if not response:
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    
    if "amazon.com" in product_url:
        product_name = soup.find("span", id="productTitle").text.strip() if soup.find("span", id="productTitle") else "N/A"
        price = extract_amazon_price(soup)
        website = "Amazon"
    elif "ebay.com" in product_url:
        product_name = soup.find("h1", class_="x-item-title__mainTitle").text.strip() if soup.find("h1", class_="x-item-title__mainTitle") else "N/A"
        price = extract_ebay_price(soup)
        website = "eBay"
    elif "bestbuy.com" in product_url:
        product_name = soup.find("h4", class_="sku-title").text.strip() if soup.find("h4", class_="sku-title") else "N/A"
        price = extract_bestbuy_price(soup)
        website = "Best Buy"
    else:
        logging.warning(f"Unsupported website: {product_url}")
        return None

    if price is None:
        return None

    data = {
        'product_name': product_name,
        'price': price,
        'url': product_url,
        'website': website,
        'timestamp': time.time()
    }

    if not validate_data(data):
        return None

    return data

def load_data(filename=DATA_STORAGE):
    """Loads existing data from a JSON file or CSV file."""
    try:
        if filename.endswith('.json'):
            with open(filename, 'r') as f:
                data = json.load(f)
        elif filename.endswith('.csv'):
            data = []
            with open(filename, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        row['price'] = float(row['price'])
                        row['timestamp'] = float(row['timestamp'])
                        data.append(row)
                    except ValueError as e:
                         logging.error(f"Error converting data types in CSV: {e}")
                         continue
        else:
             logging.error("Unsupported file format. Use .json or .csv")
             return []
        return data
    except FileNotFoundError:
        logging.info(f"Data file '{filename}' not found. Creating a new one.")
        return []
    except (json.JSONDecodeError, csv.Error) as e:
        logging.error(f"Error loading data from '{filename}': {e}")
        return []

def save_data(data, filename=DATA_STORAGE):
    """Saves data to a JSON or CSV file."""
    try:
        if filename.endswith('.json'):
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)
        elif filename.endswith('.csv'):
            with open(filename, 'w', newline='') as f:
                if data:
                    fieldnames = data[0].keys()
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data)
        else:
            logging.error("Unsupported file format. Use .json or .csv")
    except IOError as e:
        logging.error(f"Error saving data to '{filename}': {e}")


def check_price_drops(new_data, existing_data):
    """Compares current prices with historical data and sends notifications if a price drops below a threshold."""
    for new_item in new_data:
        for existing_item in existing_data:
            if new_item['product_name'] == existing_item['product_name'] and new_item['website'] == existing_item['website']:
                price_change = (existing_item['price'] - new_item['price']) / existing_item['price']
                if price_change > PRICE_DROP_THRESHOLD:
                    logging.info(f"Price drop detected for {new_item['product_name']} on {new_item['website']}")
                    send_notification(new_item, existing_item, price_change)
                    break  # Only send one notification per product per run


def send_notification(new_item, existing_item, price_change):
    """Sends an email notification about a price drop."""
    if not EMAIL_CONFIG:
        logging.warning("Email configuration is missing.  Cannot send notifications.")
        return

    sender_email = EMAIL_CONFIG.get('sender_email')
    sender_password = EMAIL_CONFIG.get('sender_password')
    receiver_email = EMAIL_CONFIG.get('receiver_email')
    smtp_server = EMAIL_CONFIG.get('smtp_server', 'smtp.gmail.com')
    smtp_port = EMAIL_CONFIG.get('smtp_port', 587)

    if not all([sender_email, sender_password, receiver_email]):
        logging.error("Missing email configuration parameters.")
        return

    subject = f"Price Drop Alert: {new_item['product_name']} on {new_item['website']}"
    body = f"The price of {new_item['product_name']} on {new_item['website']} has dropped from ${existing_item['price']:.2f} to ${new_item['price']:.2f} (Price Change: {price_change:.2%}).\n\nCheck it out here: {new_item['url']}"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        logging.info("Email notification sent successfully.")
    except Exception as e:
        logging.error(f"Error sending email: {e}")

def main():
    """Main function to orchestrate the web scraping, data storage, and price drop alerts."""
    existing_data = load_data()
    new_data = []

    for product in PRODUCTS:
        product_data = scrape_product(product)
        if product_data:
            new_data.append(product_data)
            time.sleep(SCRAPE_DELAY) # Respectful scraping delay

    if new_data:
        check_price_drops(new_data, existing_data)
        all_data = existing_data + new_data
        save_data(all_data)
        logging.info("Data scraping and price check complete.")
    else:
        logging.info("No new data to save.")

if __name__ == "__main__":
    main()