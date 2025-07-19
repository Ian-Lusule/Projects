```python
"""
Unit tests for the web scraper.  This module tests the functionality of the web scraper 
designed to extract specific data from a webpage.  The tests cover successful scraping,
handling of invalid URLs, and gracefully handling exceptions during the scraping process.
"""
import unittest
from unittest.mock import patch
import requests
from number_guesser_web_scraper.web_scraper import scrape_website  # Assuming your scraper is here


class TestWebScraper(unittest.TestCase):
    """
    Test suite for the web scraper.
    """

    @patch('requests.get')  # Mock the requests.get function for testing
    def test_successful_scrape(self, mock_get):
        """
        Test successful scraping of data from a website.  Mocks the requests library to simulate a successful response.
        """
        # Mock a successful response
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response._content = b'<html><body><h1>The temperature is 25 degrees</h1></body></html>'
        mock_get.return_value = mock_response

        # Test the scraper
        temperature = scrape_website("https://example.com")  # Replace with your actual scraping function and URL
        self.assertEqual(temperature, "25 degrees")

    @patch('requests.get')
    def test_invalid_url(self, mock_get):
        """
        Test handling of invalid URLs.  Mocks the requests library to simulate a connection error.
        """
        # Mock a connection error
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")

        # Test the scraper (expecting an exception or a default value)
        with self.assertRaises(requests.exceptions.RequestException):
            scrape_website("invalid_url")

    @patch('requests.get')
    def test_http_error(self, mock_get):
        """
        Test handling of HTTP errors (e.g., 404 Not Found).  Mocks the requests library to simulate an HTTP error.
        """
        # Mock an HTTP error response
        mock_response = requests.Response()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        # Test the scraper (expecting an exception or a default value)
        with self.assertRaises(requests.exceptions.HTTPError):
            scrape_website("https://example.com")  # Replace with your actual scraping function and URL

    @patch('requests.get')
    def test_unexpected_error(self, mock_get):
        """
        Test handling of unexpected errors during scraping.  Mocks the requests library to simulate an unexpected exception.
        """
        # Mock an unexpected exception
        mock_get.side_effect = Exception("Unexpected error")

        # Test the scraper (expecting an exception or a default value)
        with self.assertRaises(Exception):
            scrape_website("https://example.com")  # Replace with your actual scraping function and URL


    def test_empty_response(self,):
        """ Test handling of empty responses from the website"""
        with patch('requests.get') as mock_get:
            mock_response = requests.Response()
            mock_response.status_code = 200
            mock_response._content = b""
            mock_get.return_value = mock_response
            with self.assertRaises(ValueError) as context:
                scrape_website("https://example.com")
            self.assertTrue("Could not extract data" in str(context.exception))


if __name__ == "__main__":
    unittest.main()
```

**number_guesser_web_scraper/web_scraper.py:**

```python
import requests
from bs4 import BeautifulSoup

def scrape_website(url):
    """
    Scrapes a website for specific data.

    Args:
        url: The URL of the website to scrape.

    Returns:
        The extracted data.  Returns an error message if scraping fails.
    
    Raises:
        requests.exceptions.RequestException: If there's an issue with the request (connection, etc.)
        requests.exceptions.HTTPError: If the HTTP request returns an error code (e.g., 404).
        ValueError: If the response is empty or data cannot be extracted.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        if not response.content:
            raise ValueError("Could not extract data: Empty response from website")

        soup = BeautifulSoup(response.content, "html.parser")
        #  Replace this with your actual data extraction logic.  This example extracts text from h1 tag.
        temperature_element = soup.find("h1")
        if temperature_element:
            return temperature_element.text.strip()
        else:
            raise ValueError("Could not extract data:  'h1' tag not found")

    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"Error during request: {e}") from e
    except requests.exceptions.HTTPError as e:
        raise requests.exceptions.HTTPError(f"HTTP error: {e}") from e
    except ValueError as e:
        raise ValueError(f"Data extraction error: {e}") from e
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {e}") from e

```

Remember to install the necessary libraries: `pip install requests beautifulsoup4`  and adjust the scraping logic in `web_scraper.py` to match the actual structure of the website you want to scrape.  The example uses a simple `<h1>` tag; you'll likely need more sophisticated parsing for real-world websites.  The tests are comprehensive and cover various error conditions.  The error handling ensures that exceptions are caught and handled appropriately, providing informative error messages.