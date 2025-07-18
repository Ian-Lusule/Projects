import json
import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

class JobApplicationBot:
    def __init__(self, config_path="config.json", log_file="application_log.csv"):
        self.config = self.load_config(config_path)
        self.log_file = log_file
        self.applied_jobs = self.load_applied_jobs()
        self.driver = None

    def load_config(self, config_path):
        with open(config_path, "r") as f:
            return json.load(f)

    def load_applied_jobs(self):
        try:
            with open(self.log_file, "r", newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                return {row['job_url'] for row in reader}
        except FileNotFoundError:
            return set()

    def save_applied_job(self, job_title, company, job_url):
        with open(self.log_file, "a", newline='', encoding='utf-8') as csvfile:
            fieldnames = ['job_title', 'company', 'job_url']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if csvfile.tell() == 0:
                writer.writeheader()
            writer.writerow({'job_title': job_title, 'company': company, 'job_url': job_url})
        self.applied_jobs.add(job_url)

    def start_driver(self):
         service = Service(ChromeDriverManager().install())
         self.driver = webdriver.Chrome(service=service)
         self.driver.maximize_window()

    def login(self):
        platform = self.config['platform'].lower()
        if platform == "linkedin":
            self.login_linkedin()
        elif platform == "indeed":
            self.login_indeed()
        else:
            raise ValueError("Unsupported platform. Choose 'linkedin' or 'indeed'.")

    def login_linkedin(self):
        self.driver.get("https://www.linkedin.com/login")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        self.driver.find_element(By.ID, "username").send_keys(self.config["email"])
        self.driver.find_element(By.ID, "password").send_keys(self.config["password"])
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "global-nav-home"))
        )

    def login_indeed(self):
         self.driver.get("https://www.indeed.com/")
         WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "gnav-LoggedOut-signIn"))
         )

         sign_in_button = self.driver.find_element(By.CLASS_NAME, "gnav-LoggedOut-signIn")
         sign_in_button.click()

         WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "login-email-input"))
         )

         email_field = self.driver.find_element(By.ID, "login-email-input")
         email_field.send_keys(self.config["email"])

         continue_button = self.driver.find_element(By.ID, "login-submit-button")
         continue_button.click()

         WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "login-password-input"))
         )

         password_field = self.driver.find_element(By.ID, "login-password-input")
         password_field.send_keys(self.config["password"])

         sign_in_final_button = self.driver.find_element(By.ID, "login-submit-button")
         sign_in_final_button.click()

         WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "indeed-logo"))
         )



    def search_jobs(self):
        platform = self.config['platform'].lower()
        if platform == "linkedin":
            self.search_jobs_linkedin()
        elif platform == "indeed":
            self.search_jobs_indeed()
        else:
            raise ValueError("Unsupported platform. Choose 'linkedin' or 'indeed'.")

    def search_jobs_linkedin(self):
        self.driver.get("https://www.linkedin.com/jobs")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "jobs-search-box__inner"))
        )

        keywords_input = self.driver.find_element(By.ID, "jobs-search-box-keyword-id-ember132")
        keywords_input.send_keys(self.config["keywords"])

        location_input = self.driver.find_element(By.ID, "jobs-search-box-location-id-ember132")
        location_input.clear()
        location_input.send_keys(self.config["location"])
        location_input.send_keys(Keys.RETURN)
        time.sleep(2) # Wait for the search results to load
        # Apply Easy Apply filter
        try:
            all_filters_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='All filters']"))
            )
            all_filters_button.click()

            easy_apply_checkbox = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//label[@for='f_easyApply-0']"))
            )
            easy_apply_checkbox.click()

            show_results_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@data-control-name='filter_show_results']"))
            )
            show_results_button.click()

            time.sleep(2)
        except Exception as e:
            print(f"Error applying filters: {e}")

    def search_jobs_indeed(self):
         self.driver.get("https://www.indeed.com/jobs")

         WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "text-input-what"))
         )

         keyword_input = self.driver.find_element(By.ID, "text-input-what")
         keyword_input.send_keys(self.config["keywords"])

         location_input = self.driver.find_element(By.ID, "text-input-where")
         location_input.clear()
         location_input.send_keys(self.config["location"])

         search_button = self.driver.find_element(By.CLASS_NAME, "yosegi-InlineWhatWhere-primaryButton")
         search_button.click()

         time.sleep(2)


    def apply_to_jobs(self):
        platform = self.config['platform'].lower()
        if platform == "linkedin":
            self.apply_to_jobs_linkedin()
        elif platform == "indeed":
            self.apply_to_jobs_indeed()
        else:
            raise ValueError("Unsupported platform. Choose 'linkedin' or 'indeed'.")


    def apply_to_jobs_linkedin(self):
        job_listings = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "job-card-container__link"))
        )

        for job_element in job_listings:
            job_url = job_element.get_attribute("href")

            if job_url in self.applied_jobs:
                print(f"Skipping already applied job: {job_url}")
                continue

            try:
                self.driver.get(job_url)
                time.sleep(2)

                job_title = self.driver.find_element(By.CLASS_NAME, "top-card-layout__title").text
                company = self.driver.find_element(By.CLASS_NAME, "top-card-layout__company").text

                try:
                    apply_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'jobs-apply-button') or contains(@class, 'artdeco-button--primary')]"))
                    )
                    apply_button.click()

                    self.handle_application_flow()
                    self.save_applied_job(job_title, company, job_url)
                    print(f"Applied to: {job_title} at {company} - {job_url}")

                except Exception as e:
                    print(f"Could not apply to {job_title} at {company}: {e}")

            except Exception as e:
                print(f"Error processing job: {job_url} - {e}")


    def apply_to_jobs_indeed(self):
        job_listings = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "jobsearch-SerpJobCard"))
        )

        for job_element in job_listings:
            try:
                job_url = job_element.get_attribute("href")

                if job_url in self.applied_jobs:
                    print(f"Skipping already applied job: {job_url}")
                    continue


                job_title_element = job_element.find_element(By.CLASS_NAME, "jobtitle")
                job_title = job_title_element.text

                company_element = job_element.find_element(By.CLASS_NAME, "company")
                company = company_element.text

                job_element.click()
                time.sleep(2)


                try:
                    apply_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.ID, "indeedApplyButton"))
                    )
                    apply_button.click()

                    self.handle_indeed_application_flow()
                    self.save_applied_job(job_title, company, job_url)
                    print(f"Applied to: {job_title} at {company} - {job_url}")

                except Exception as e:
                    print(f"Could not find Easy Apply button for {job_title} at {company}: {e}")



            except Exception as e:
                print(f"Error processing job card: {e}")


    def handle_application_flow(self):
        platform = self.config['platform'].lower()
        if platform == "linkedin":
            self.handle_linkedin_application_flow()
        elif platform == "indeed":
            self.handle_indeed_application_flow()
        else:
            raise ValueError("Unsupported platform. Choose 'linkedin' or 'indeed'.")

    def handle_linkedin_application_flow(self):
        try:
            while True:
                time.sleep(1)
                next_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Continue to next step']"))
                )
                next_button.click()
        except:
            try:
                submit_application_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Submit application']"))
                )
                submit_application_button.click()

                close_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "artdeco-modal__dismiss"))
                )
                close_button.click()

            except:
                try:
                    close_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "artdeco-modal__dismiss"))
                    )
                    close_button.click()
                except:
                    pass


    def handle_indeed_application_flow(self):
        try:
             upload_resume_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "ia-file-upload"))
             )
             upload_resume_button.send_keys(self.config["resume_path"])

             WebDriverWait(self.driver, 10).until(
                 EC.presence_of_element_located((By.CLASS_NAME, "icl-Modal-header"))
             )


             continue_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "ia-continue-button"))
             )
             continue_button.click()

             submit_application_button = WebDriverWait(self.driver, 10).until(
                 EC.element_to_be_clickable((By.ID, "ia-SubmitButton"))
             )
             submit_application_button.click()

        except Exception as e:
            print(f"Error in Indeed application flow: {e}")

    def run(self):
        self.start_driver()
        self.login()
        self.search_jobs()
        self.apply_to_jobs()
        self.driver.quit()


if __name__ == "__main__":
    bot = JobApplicationBot()
    bot.run()