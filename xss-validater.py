import requests
import concurrent.futures
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.alert import Alert
from webdriver_manager.chrome import ChromeDriverManager

# Global Selenium WebDriver (Reused)
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Thread-safe flag to stop execution
xss_found = threading.Event()

def load_payloads(files):
    """Load payloads from multiple files"""
    payloads = []
    for file in files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                payloads.extend([line.strip() for line in f if line.strip()])
        except FileNotFoundError:
            print(f"Warning: File '{file}' not found. Skipping.")
    return payloads

def send_get_request(session, url, payload):
    """Send GET request and check if payload is reflected"""
    if xss_found.is_set():  # Stop if XSS has already been found
        return False

    try:
        response = session.get(url, timeout=5)  # Reduced timeout for speed
        response.raise_for_status()

        if payload in response.text:
            print(f"[Potential XSS] Payload reflected: {payload}")
            return True
    except requests.exceptions.RequestException:
        pass
    return False

def check_xss_with_selenium(url):
    """Use Selenium to check if an alert appears (Confirms XSS)"""
    if xss_found.is_set():  # Stop if XSS has already been found
        return False

    try:
        driver.get(url)

        try:
            alert = Alert(driver)
            alert_text = alert.text
            print(f"[!!!] Confirmed XSS! Alert detected: {alert_text}")
            alert.accept()
            return True
        except:
            pass
    except Exception as e:
        print(f"Selenium Error: {e}")
    return False

def test_payload(base_url, payload):
    """Test a single payload using GET request & Selenium"""
    if xss_found.is_set():  # Stop if XSS has already been found
        return False

    full_url = f"{base_url}{payload}"
    session = requests.Session()

    if send_get_request(session, full_url, payload):  # Check for reflection
        if check_xss_with_selenium(full_url):  # Confirm with Selenium
            print(f"[✔] Confirmed XSS with payload: {payload}")
            xss_found.set()  # Set flag to stop execution
            return True
    return False

if __name__ == "__main__":
    base_url = input("Enter the target URL (e.g., https://example.com/search?q=): ").strip()

    if "?" not in base_url:
        print("Invalid URL format. Ensure the URL has a query parameter (e.g., ?q=).")
    else:
        payload_files = ["payload1.txt", "payload2.txt"]
        payloads = load_payloads(payload_files)

        if not payloads:
            print("No payloads found. Please check the payload files.")
        else:
            print(f"Loaded {len(payloads)} payloads. Starting tests...")

            # Run requests in parallel using ThreadPoolExecutor
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = {executor.submit(test_payload, base_url, payload): payload for payload in payloads}
                
                for future in concurrent.futures.as_completed(futures):
                    if future.result():
                        print("Stopping further tests as XSS is confirmed.")
                        break  # Stop after first confirmed XSS

            print("Scan completed.")

    # Close the Selenium driver
    driver.quit()
