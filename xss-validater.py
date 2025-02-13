import requests
import concurrent.futures
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.alert import Alert
from webdriver_manager.chrome import ChromeDriverManager

# Global flag to stop execution when XSS is found
xss_found = threading.Event()

# Thread-local storage for WebDriver instances
thread_local = threading.local()

def get_webdriver():
    """Create and return a thread-local Selenium WebDriver instance."""
    if not hasattr(thread_local, "driver"):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--log-level=3")  # Suppress warnings/errors

        # 🚀 Suppress "DevTools listening on ws://..." messages
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-blink-features"])
        chrome_options.add_argument("--remote-debugging-port=0")  # Disable DevTools debugging

        service = Service(ChromeDriverManager().install())

        # 🚀 Redirect Selenium logs to null to suppress unwanted messages
        service.service_log_path = "/dev/null"

        thread_local.driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return thread_local.driver
def load_payloads(files):
    """Load payloads from multiple files."""
    payloads = []
    for file in files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                payloads.extend([line.strip() for line in f if line.strip()])
        except FileNotFoundError:
            print(f"[!] Warning: File '{file}' not found. Skipping.")
    return payloads

def send_get_request(session, url, payload):
    """Send GET request and check if payload is reflected in response."""
    if xss_found.is_set():  # Stop execution if XSS is already found
        return False

    try:
        response = session.get(url, timeout=3)  # Reduced timeout for speed
        response.raise_for_status()
        
        if payload in response.text:
            print(f"[!] Potential XSS Detected (Payload Reflected): {payload}")
            return True
    except requests.exceptions.RequestException:
        pass  # Suppress request errors for cleaner output
    return False

def check_xss_with_selenium(url):
    """Use Selenium to check if an alert appears, confirming XSS."""
    if xss_found.is_set():  # Stop execution if XSS is already found
        return False

    try:
        driver = get_webdriver()
        driver.get(url)

        try:
            alert = Alert(driver)
            alert_text = alert.text
            if alert_text:  # Ensure alert has content before confirming
                print(f"[✔] Confirmed XSS! Alert detected: {alert_text}")
                alert.accept()
                return True
        except:
            pass  # Suppress unnecessary alert exceptions
    except Exception:
        pass  # Suppress unexpected Selenium errors
    return False

def test_payload(base_url, payload):
    """Test a single payload using GET request & Selenium."""
    if xss_found.is_set():  # Stop execution if XSS is already found
        return False

    full_url = f"{base_url}{payload}"
    session = requests.Session()

    if send_get_request(session, full_url, payload):  # Check for reflection
        if check_xss_with_selenium(full_url):  # Confirm with Selenium
            print(f"[✔] Confirmed XSS with payload: {payload}")
            xss_found.set()  # Stop further testing
            return True
    return False

def main():
    base_url = input("Enter the target URL (e.g., https://example.com/search?q=): ").strip()

    if "?" not in base_url:
        print("[X] Invalid URL format. Ensure the URL has a query parameter (e.g., ?q=).")
        return

    payload_files = ["payload1.txt", "payload2.txt"]
    payloads = load_payloads(payload_files)

    if not payloads:
        print("[X] No payloads found. Please check the payload files.")
        return

    print(f"[+] Loaded {len(payloads)} payloads. Starting tests...")

    # Run tests in parallel using ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(test_payload, base_url, payload): payload for payload in payloads}
        
        for future in concurrent.futures.as_completed(futures):
            if future.result():  # If XSS is confirmed, stop testing
                print("[!] Stopping further tests as XSS is confirmed.")
                break

    print("[✔] Scan completed.")

    # Close Selenium driver after all threads are done
    if hasattr(thread_local, "driver"):
        thread_local.driver.quit()

if __name__ == "__main__":
    main()
