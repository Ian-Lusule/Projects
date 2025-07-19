```python
"""
web_scraper.py: A web scraper for retrieving weather data from a specific website.

This script scrapes weather information from a target URL using Beautiful Soup.  
It's designed for a specific website structure and may require modification 
for other websites.  Error handling is included to manage potential issues 
like network errors and missing data.
"""

import requests
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Target URL (replace with the actual URL of the weather website)
TARGET_URL = "https://www.example.com/weather"  # Replace with your target URL

# CSS selectors for data extraction (customize these based on the website's structure)
TEMPERATURE_SELECTOR = "#temperature"
CONDITION_SELECTOR = "#condition"
WIND_SELECTOR = "#wind"


def scrape_weather_data(url):
    """
    Scrapes weather data from the specified URL.

    Args:
        url: The URL of the weather website.

    Returns:
        A dictionary containing the scraped weather data (temperature, condition, wind), 
        or None if an error occurs.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        soup = BeautifulSoup(response.content, "html.parser")

        temperature = soup.select_one(TEMPERATURE_SELECTOR).text.strip()
        condition = soup.select_one(CONDITION_SELECTOR).text.strip()
        wind = soup.select_one(WIND_SELECTOR).text.strip()

        return {
            "temperature": temperature,
            "condition": condition,
            "wind": wind,
        }

    except requests.exceptions.RequestException as e:
        logging.error(f"Error during request: {e}")
        return None
    except AttributeError as e:
        logging.error(f"Error parsing HTML: Could not find element.  Check selectors. {e}")
        return None
    except Exception as e:  # Catch other unexpected errors
        logging.exception(f"An unexpected error occurred: {e}")
        return None


if __name__ == "__main__":
    weather_data = scrape_weather_data(TARGET_URL)

    if weather_data:
        logging.info("Weather data scraped successfully:")
        for key, value in weather_data.items():
            logging.info(f"{key.capitalize()}: {value}")
    else:
        logging.error("Failed to scrape weather data.")

```

**Before running:**

1. **Install required libraries:**  `pip install requests beautifulsoup4`
2. **Replace placeholders:** Update `TARGET_URL` with the actual URL of the website you want to scrape.  **Crucially**, inspect the website's HTML source code using your browser's developer tools (usually F12) to find the correct CSS selectors for `TEMPERATURE_SELECTOR`, `CONDITION_SELECTOR`, and `WIND_SELECTOR`. These selectors must accurately target the elements containing the desired weather information.  Incorrect selectors will lead to errors.
3. **Respect robots.txt:** Before scraping any website, check its `robots.txt` file (e.g., `www.example.com/robots.txt`) to ensure you're allowed to scrape the data.  Ignoring `robots.txt` can lead to your IP being blocked.
4. **Handle website changes:** Websites frequently update their structure.  Your scraper might break if the website changes its HTML.  Be prepared to update your CSS selectors accordingly.


This improved version includes:

* **Comprehensive error handling:** Catches various exceptions (network errors, parsing errors, etc.) and logs informative messages.
* **Logging:** Uses the `logging` module for better error reporting and debugging.
* **Clearer structure:** Separates the scraping logic into a function for better organization and reusability.
* **Documentation:**  Includes docstrings explaining the purpose of the code and its functions.
* **Best practices:** Follows Python best practices for exception handling and code style.


Remember that web scraping should be done responsibly and ethically, respecting the website's terms of service and robots.txt.  Excessive scraping can overload a server, so be mindful of the frequency of your requests.
