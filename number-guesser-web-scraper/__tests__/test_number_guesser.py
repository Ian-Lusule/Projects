```python
"""
Unit tests for the number guessing game and web scraper.  This file demonstrates testing both
a simple game and a web scraping function, showcasing different testing strategies.
"""
import unittest
import requests
from unittest.mock import patch
from io import StringIO

# Simulate the number guessing game module
class NumberGuesser:
    def __init__(self, answer):
        self.answer = answer
        self.guesses_left = 7

    def guess(self, num):
        self.guesses_left -= 1
        if num == self.answer:
            return "Correct!"
        elif num < self.answer:
            return "Too low!"
        else:
            return "Too high!"

    def game_over(self):
        return self.guesses_left == 0


# Simulate a web scraper module
def scrape_weather(url):
    """
    Scrapes weather data from a given URL.  This is a simplified example and 
    would need adjustments for real-world websites.  Error handling is crucial here.
    """
    try:
        response = requests.get(url, timeout=5)  # Add a timeout for robustness
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        # In a real application, you would parse the HTML here using a library like Beautiful Soup
        # This is a placeholder
        return {"temperature": 25, "condition": "Sunny"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Error fetching weather data: {e}"}
    except Exception as e: #Catch any other unexpected errors.
        return {"error": f"An unexpected error occurred: {e}"}


class TestNumberGuesser(unittest.TestCase):
    """Tests for the number guessing game."""

    def test_correct_guess(self):
        guesser = NumberGuesser(5)
        result = guesser.guess(5)
        self.assertEqual(result, "Correct!")

    def test_too_low(self):
        guesser = NumberGuesser(8)
        result = guesser.guess(3)
        self.assertEqual(result, "Too low!")

    def test_too_high(self):
        guesser = NumberGuesser(2)
        result = guesser.guess(7)
        self.assertEqual(result, "Too high!")

    def test_game_over(self):
        guesser = NumberGuesser(5)
        for _ in range(7):
            guesser.guess(1)  # Incorrect guesses
        self.assertTrue(guesser.game_over())


class TestWebScraper(unittest.TestCase):
    """Tests for the web scraper."""

    @patch('requests.get')
    def test_successful_scrape(self, mock_get):
        # Mock a successful response
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        result = scrape_weather("http://example.com")
        self.assertEqual(result, {"temperature": 25, "condition": "Sunny"})

    @patch('requests.get')
    def test_failed_scrape(self, mock_get):
        # Mock a failed response
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        result = scrape_weather("http://example.com")
        self.assertTrue("Error fetching weather data" in result["error"])

    @patch('requests.get')
    def test_unexpected_error(self, mock_get):
        mock_get.side_effect = Exception("Something went wrong")
        result = scrape_weather("http://example.com")
        self.assertTrue("An unexpected error occurred" in result["error"])

if __name__ == "__main__":
    unittest.main()

```