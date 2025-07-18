import requests
from bs4 import BeautifulSoup

def scrape_website(url, tag, attribute=None, attribute_value=None):
    """
    Scrapes a website for specific data.

    Args:
        url: The URL of the website to scrape.
        tag: The HTML tag to search for.
        attribute: (Optional) The attribute to filter by.
        attribute_value: (Optional) The value of the attribute to filter by.

    Returns:
        A list of strings containing the extracted data, or None if an error occurs.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        soup = BeautifulSoup(response.content, 'html.parser')
        results = []

        if attribute and attribute_value:
            elements = soup.find_all(tag, {attribute: attribute_value})
        else:
            elements = soup.find_all(tag)

        for element in elements:
            results.append(element.text.strip())

        return results
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


if __name__ == "__main__":
    url = input("Enter the URL to scrape: ")
    tag = input("Enter the HTML tag to search for: ")
    attribute = input("Enter the attribute to filter by (optional, press Enter to skip): ")
    if attribute:
        attribute_value = input("Enter the attribute value: ")
    else:
        attribute_value = None

    data = scrape_website(url, tag, attribute, attribute_value)

    if data:
        print("\nScraped data:")
        for item in data:
            print(item)

