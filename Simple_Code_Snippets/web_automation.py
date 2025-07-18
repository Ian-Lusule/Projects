import time
import logging
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
from PIL import Image
import io
import requests
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SeleniumLibrary:
    """
    A reusable library of Selenium functions for common web automation tasks.
    """

    def __init__(self, browser="chrome", headless=True, grid_url=None):
        """
        Initializes the Selenium WebDriver.

        Args:
            browser (str): The browser to use (chrome or firefox). Defaults to chrome.
            headless (bool): Whether to run the browser in headless mode. Defaults to True.
            grid_url (str): URL of the Selenium Grid. Defaults to None (local execution).
        """
        self.browser = browser.lower()
        self.headless = headless
        self.grid_url = grid_url
        self.driver = self._create_driver()

    def _create_driver(self):
        """
        Creates the Selenium WebDriver instance based on the configured browser and settings.
        """
        if self.grid_url:
            try:
                if self.browser == "chrome":
                     chrome_options = ChromeOptions()
                     chrome_options.headless = self.headless
                     driver = webdriver.Remote(command_executor=self.grid_url, options=chrome_options)
                elif self.browser == "firefox":
                     firefox_options = FirefoxOptions()
                     firefox_options.headless = self.headless
                     driver = webdriver.Remote(command_executor=self.grid_url, options=firefox_options)
                else:
                    raise ValueError(f"Unsupported browser: {self.browser}")
                logging.info(f"Connected to Selenium Grid at {self.grid_url}")
                return driver
            except Exception as e:
                logging.error(f"Failed to connect to Selenium Grid: {e}")
                raise

        else:
            if self.browser == "chrome":
                chrome_options = ChromeOptions()
                chrome_options.headless = self.headless
                return webdriver.Chrome(options=chrome_options)
            elif self.browser == "firefox":
                firefox_options = FirefoxOptions()
                firefox_options.headless = self.headless
                return webdriver.Firefox(options=firefox_options)
            else:
                raise ValueError(f"Unsupported browser: {self.browser}")

    def go_to_url(self, url):
        """Navigates to the specified URL."""
        try:
            self.driver.get(url)
            logging.info(f"Navigated to URL: {url}")
        except Exception as e:
            logging.error(f"Failed to navigate to URL {url}: {e}")
            raise

    def find_element(self, by, value, timeout=10):
        """Finds an element using the specified locator."""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            logging.info(f"Found element using {by}: {value}")
            return element
        except TimeoutException:
            logging.warning(f"Timeout finding element using {by}: {value}")
            return None
        except Exception as e:
            logging.error(f"Error finding element using {by}: {value}: {e}")
            return None

    def find_elements(self, by, value, timeout=10):
        """Finds all elements matching the specified locator."""
        try:
            elements = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((by, value))
            )
            logging.info(f"Found {len(elements)} elements using {by}: {value}")
            return elements
        except TimeoutException:
            logging.warning(f"Timeout finding elements using {by}: {value}")
            return []
        except Exception as e:
            logging.error(f"Error finding elements using {by}: {value}: {e}")
            return []

    def click_element(self, by, value, timeout=10):
         """Clicks an element using the specified locator."""
         try:
             element = WebDriverWait(self.driver, timeout).until(
                 EC.element_to_be_clickable((by, value))
             )
             element.click()
             logging.info(f"Clicked element using {by}: {value}")
         except TimeoutException:
             logging.warning(f"Timeout waiting for element to be clickable using {by}: {value}")
             return False
         except ElementNotInteractableException:
             logging.warning(f"Element not interactable using {by}: {value}")
             return False
         except Exception as e:
             logging.error(f"Error clicking element using {by}: {value}: {e}")
             return False
         return True

    def fill_form(self, locator_value_pairs, timeout=10):
        """Fills out a form with the given locator-value pairs.

        Args:
            locator_value_pairs (list of tuples): A list of tuples, where each tuple contains the (by, locator, value) for a form field.
        """
        try:
            for by, locator, value in locator_value_pairs:
                element = self.find_element(by, locator, timeout)
                if element:
                    element.clear()
                    element.send_keys(value)
                    logging.info(f"Filled field {locator} with value {value}")
                else:
                    logging.warning(f"Could not find element {locator} to fill.")
                    return False
            return True
        except Exception as e:
            logging.error(f"Error filling form: {e}")
            return False

    def get_text(self, by, value, timeout=10):
        """Gets the text of an element."""
        element = self.find_element(by, value, timeout)
        if element:
            text = element.text
            logging.info(f"Got text from element {value}: {text}")
            return text
        else:
            logging.warning(f"Could not find element {value} to get text from.")
            return None

    def get_attribute(self, by, value, attribute, timeout=10):
        """Gets the value of an attribute of an element."""
        element = self.find_element(by, value, timeout)
        if element:
            attribute_value = element.get_attribute(attribute)
            logging.info(f"Got attribute {attribute} from element {value}: {attribute_value}")
            return attribute_value
        else:
            logging.warning(f"Could not find element {value} to get attribute {attribute} from.")
            return None

    def execute_javascript(self, script):
        """Executes JavaScript code."""
        try:
            self.driver.execute_script(script)
            logging.info(f"Executed JavaScript: {script}")
        except Exception as e:
            logging.error(f"Error executing JavaScript: {e}")
            return False
        return True

    def handle_alert(self, action="accept", timeout=10):
        """Handles JavaScript alerts (accept or dismiss)."""
        try:
            WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
            alert = Alert(self.driver)
            if action == "accept":
                alert.accept()
                logging.info("Accepted alert.")
            elif action == "dismiss":
                alert.dismiss()
                logging.info("Dismissed alert.")
            else:
                logging.warning(f"Invalid alert action: {action}. Accepting by default.")
                alert.accept()
            return True
        except TimeoutException:
            logging.warning("No alert present.")
            return False
        except Exception as e:
            logging.error(f"Error handling alert: {e}")
            return False

    def take_screenshot(self, filename="screenshot.png"):
        """Takes a screenshot of the current page."""
        try:
            self.driver.save_screenshot(filename)
            logging.info(f"Took screenshot and saved as {filename}")
        except Exception as e:
            logging.error(f"Error taking screenshot: {e}")

    def take_element_screenshot(self, by, value, filename="element_screenshot.png", timeout=10):
        """Takes a screenshot of a specific element."""
        element = self.find_element(by, value, timeout)
        if element:
            try:
                location = element.location
                size = element.size
                png = self.driver.get_screenshot_as_png()

                im = Image.open(io.BytesIO(png))

                left = location['x']
                top = location['y']
                right = location['x'] + size['width']
                bottom = location['y'] + size['height']

                im = im.crop((left, top, right, bottom))
                im.save(filename)
                logging.info(f"Took element screenshot and saved as {filename}")

            except Exception as e:
                logging.error(f"Error taking element screenshot: {e}")
        else:
            logging.warning(f"Could not find element {value} to take screenshot of.")

    def switch_to_frame(self, by, value, timeout=10):
        """Switches to an iframe."""
        try:
            frame = self.find_element(by, value, timeout)
            if frame:
                self.driver.switch_to.frame(frame)
                logging.info(f"Switched to frame using {by}: {value}")
                return True
            else:
                logging.warning(f"Could not find frame to switch to using {by}: {value}")
                return False
        except Exception as e:
            logging.error(f"Error switching to frame: {e}")
            return False

    def switch_to_default_content(self):
        """Switches back to the default content."""
        try:
            self.driver.switch_to.default_content()
            logging.info("Switched to default content.")
        except Exception as e:
            logging.error(f"Error switching to default content: {e}")

    def extract_data(self, by, value, attribute=None, timeout=10):
        """Extracts data from elements. If attribute is provided, extracts attribute value; otherwise, extracts text."""
        elements = self.find_elements(by, value, timeout)
        data = []
        if elements:
            for element in elements:
                if attribute:
                    data.append(element.get_attribute(attribute))
                else:
                    data.append(element.text)
            logging.info(f"Extracted data from {len(elements)} elements using {by}: {value}")
            return data
        else:
            logging.warning(f"No elements found using {by}: {value} to extract data from.")
            return []

    def solve_captcha(self, captcha_image_locator, api_key, captcha_solving_service="2captcha", timeout=30):
        """Solves CAPTCHA challenges using a CAPTCHA solving service like 2Captcha.
           Requires an API key for the chosen service.
        """
        try:
            # Find the CAPTCHA image element
            captcha_image_element = self.find_element(*captcha_image_locator, timeout=timeout)
            if not captcha_image_element:
                logging.error("CAPTCHA image element not found.")
                return None

            # Get the image URL or base64 data
            image_src = captcha_image_element.get_attribute("src")
            if not image_src:
                image_src = captcha_image_element.get_attribute("data:image/png;base64")  # Base64 encoded image
                if not image_src:
                    logging.error("CAPTCHA image source not found.")
                    return None

            # Download the image
            if image_src.startswith("http"):
                response = requests.get(image_src, stream=True)
                response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
                image_data = response.content
            else: #base64 encoded
                 image_data = BytesIO(base64.b64decode(image_src.split(',')[1])).read()


            # Send the CAPTCHA to the solving service
            if captcha_solving_service.lower() == "2captcha":
                url = "http://2captcha.com/in.php"
                files = {'file': ('captcha.png', io.BytesIO(image_data))}
                data = {'key': api_key, 'method': 'post'}
                response = requests.post(url, files=files, data=data)
                response.raise_for_status()

                captcha_id = response.text.split("|")[1]

                # Poll for the CAPTCHA solution
                url = f"http://2captcha.com/res.php?key={api_key}&action=get&id={captcha_id}"
                for _ in range(20):  # Poll for up to 60 seconds (adjust as needed)
                    time.sleep(3)
                    response = requests.get(url)
                    response.raise_for_status()

                    if "OK" in response.text:
                        captcha_solution = response.text.split("|")[1]
                        logging.info(f"CAPTCHA solved by 2Captcha: {captcha_solution}")
                        return captcha_solution
                    elif "CAPCHA_NOT_READY" not in response.text:
                        logging.error(f"Error solving CAPTCHA: {response.text}")
                        return None  # Error occurred

                logging.error("Timeout waiting for CAPTCHA solution from 2Captcha.")
                return None
            else:
                logging.error(f"Unsupported CAPTCHA solving service: {captcha_solving_service}")
                return None

        except requests.exceptions.RequestException as e:
            logging.error(f"Error communicating with CAPTCHA solving service: {e}")
            return None
        except Exception as e:
            logging.error(f"Error solving CAPTCHA: {e}")
            return None


    def close(self):
        """Closes the browser."""
        try:
            self.driver.quit()
            logging.info("Browser closed.")
        except Exception as e:
            logging.error(f"Error closing browser: {e}")

import base64
def validate_data(data, schema):
    """
    Validates data against a schema.  This is a placeholder.
    In a real implementation, you'd use a library like Cerberus or jsonschema.

    Args:
        data (dict): The data to validate.
        schema (dict): The schema to validate against.

    Returns:
        bool: True if the data is valid, False otherwise.
    """
    # Placeholder for data validation logic
    # In a real implementation, use a validation library
    logging.info("Data validation is a placeholder and not fully implemented.")
    return True  # Assume valid for now


def api_test(url, expected_status_code=200):
    """
    Performs a simple API test by checking the status code of a URL.

    Args:
        url (str): The URL to test.
        expected_status_code (int): The expected HTTP status code.

    Returns:
        bool: True if the status code matches the expected value, False otherwise.
    """
    try:
        response = requests.get(url)
        status_code = response.status_code
        if status_code == expected_status_code:
            logging.info(f"API test passed: URL {url} returned status code {status_code}")
            return True
        else:
            logging.error(
                f"API test failed: URL {url} returned status code {status_code}, expected {expected_status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logging.error(f"API test failed: {e}")
        return False


if __name__ == '__main__':
    # Example usage:
    try:
        # Initialize the Selenium library
        selenium_lib = SeleniumLibrary(browser="chrome", headless=True)  # or browser="firefox"

        # Navigate to a website
        selenium_lib.go_to_url("https://www.example.com")

        # Find an element and get its text
        heading_text = selenium_lib.get_text(By.TAG_NAME, "h1")
        if heading_text:
            print(f"Heading Text: {heading_text}")

        # Find an element and take a screenshot
        selenium_lib.take_element_screenshot(By.TAG_NAME, "h1", filename="example_heading.png")

        # Example of interacting with a form (this will fail on example.com as it has no form)
        #form_data = [
        #    (By.NAME, "firstName", "John"),
        #    (By.NAME, "lastName", "Doe"),
        #    (By.NAME, "email", "john.doe@example.com")
        #]
        #selenium_lib.fill_form(form_data)
        #selenium_lib.click_element(By.ID, "submitButton")

        # Example of API testing
        api_url = "https://www.example.com"
        api_test_result = api_test(api_url)
        print(f"API test result: {api_test_result}")

        # Example of Data Validation (Placeholder)
        sample_data = {"name": "Example", "value": 123}
        sample_schema = {"name": {"type": "string"}, "value": {"type": "integer"}}
        data_validation_result = validate_data(sample_data, sample_schema)
        print(f"Data validation result: {data_validation_result}")

        # Example of CAPTCHA solving (replace with actual values and website requiring CAPTCHA)
        # Replace with the actual locator for the CAPTCHA image.  This will likely require changes
        #captcha_image_locator = (By.ID, "captcha_image")  # Replace with the actual locator
        #captcha_api_key = "YOUR_2CAPTCHA_API_KEY"  # Replace with your 2Captcha API key
        #captcha_solution = selenium_lib.solve_captcha(captcha_image_locator, captcha_api_key)
        #if captcha_solution:
        #    print(f"CAPTCHA Solution: {captcha_solution}")
        #    # Find the CAPTCHA input field and fill it with the solution
        #    captcha_input_locator = (By.ID, "captcha_input")  # Replace with the actual locator
        #    captcha_input = selenium_lib.find_element(*captcha_input_locator)
        #    captcha_input.send_keys(captcha_solution)
        #    # Submit the form

        # Close the browser
        selenium_lib.close()

    except Exception as e:
        logging.error(f"An error occurred: {e}")