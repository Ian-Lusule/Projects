import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def reverse_image_search(image_path):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get("https://images.google.com/")

    # Find the camera icon and click it
    camera_icon = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "div.ZaFQO a"))
    )
    camera_icon.click()

    # Find the "Upload an image" link and click it (if it exists)
    try:
        upload_link = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//div[text()='Upload a file']"))
        )
        upload_link.click()
    except:
        pass # If the upload button is already visible skip clicking the upload link

    # Find the hidden file input element and send the image path
    upload_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
    )
    upload_element.send_keys(image_path)

    # Wait for the results to load
    try:
        related_search_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a. related-search-title"))
        )
        related_search_text = related_search_element.text
    except:
        related_search_text = "No related search found."

    # Extract the URLs of the visually similar images
    similar_images_urls = []
    try:
        image_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.isv-r a:first-of-type"))
        )

        for i in range(min(5, len(image_elements))):
            try:
                image_elements[i].click()
                time.sleep(1) # Give time for URL to load
                actual_image = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "img.sFlh5c.pT0Scc.iPVvYb"))
                )
                similar_images_urls.append(actual_image.get_attribute("src"))
            except Exception as e:
                print(f"Error extracting URL for image {i+1}: {e}")

    except:
        similar_images_urls = ["No similar images found."]

    print("Possible related search:", related_search_text)
    print("Similar image URLs:", similar_images_urls)

    driver.quit()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        reverse_image_search(image_path)
    else:
        print("Please provide the image path as a command-line argument.")