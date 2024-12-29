import os
import time
import pickle
import requests
import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType
from pymongo import MongoClient
from dotenv import load_dotenv
from webdriver_manager.chrome import ChromeDriverManager

# Load environment variables
load_dotenv(".env")

proxymesh_user = os.getenv('proxymesh_user')
proxymesh_pass = os.getenv('proxymesh_pass')
twitter_user = os.getenv('twitter_user')
twitter_pass = os.getenv('twitter_pass')
twitter_email = os.getenv('twitter_email')

# MongoDB Configuration
mongo_client = MongoClient(os.getenv('mongodb_uri'))
db = mongo_client.twitter_data
trends_collection = db.trending_topics

# Configure proxy
def configure_proxy():
    return f"http://{proxymesh_user}:{proxymesh_pass}@us-ca.proxymesh.com:31280"

# Initialize the Selenium driver
def initialize_driver(proxy=None):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--start-maximized")
    options.binary_location = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

    if proxy:
        prox = Proxy()
        prox.proxy_type = ProxyType.MANUAL
        prox.http_proxy = proxy
        prox.ssl_proxy = proxy
        capabilities = webdriver.DesiredCapabilities.CHROME.copy()
        capabilities['proxy'] = prox.to_capabilities()
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    else:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    return driver

# Save cookies to a file
def save_cookies(driver, filename):
    with open(filename, "wb") as file:
        pickle.dump(driver.get_cookies(), file)

# Load cookies from a file
def load_cookies(driver, filename):
    with open(filename, "rb") as file:
        cookies = pickle.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)

def login_to_twitter(driver):
    try:
        driver.get('https://x.com/login')
        wait = WebDriverWait(driver, 10)

        # Wait for the first input field (username/email)
        first_input_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='text']")))

        # Enter username or email
        first_input_field.send_keys(twitter_user)
        first_input_field.send_keys(Keys.ENTER)
        time.sleep(4)

        # Wait for the password input field and enter password
        password_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='password']")))
        password_field.send_keys(twitter_pass)
        password_field.send_keys(Keys.ENTER)
        time.sleep(4)

        # Save cookies for future use
        save_cookies(driver, "twitter_cookies.pkl")
        print("Login successful!")
    except Exception as e:
        print(f"Login failed: {e}")


# Scrape trending topics
def scrape_trending_topics(driver):
    driver.get('https://x.com/home')
    time.sleep(6)
    trends = []
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    trend_elements = soup.find_all('div', {'data-testid': 'trend'})
    for element in trend_elements:
        trend_text = element.find('span').text
        if trend_text:
            trends.append(trend_text)
    return trends

# Get the current IP address
def fetch_current_ip():
    proxy_url = configure_proxy()
    response = requests.get('http://httpbin.org/ip', proxies={'http': proxy_url, 'https': proxy_url}, auth=(proxymesh_user, proxymesh_pass))
    ip_address = response.json()['origin']
    return ip_address

# Add data to MongoDB
def add_to_database(trends):
    try:
    # Ensure trends list has at least 5 elements
        trending_data = {
            'trend_1': trends[0] if len(trends) > 0 else None,
            'trend_2': trends[1] if len(trends) > 1 else None,
            'trend_3': trends[2] if len(trends) > 2 else None,
            'trend_4': trends[3] if len(trends) > 3 else None,
            'trend_5': trends[4] if len(trends) > 4 else None,
            'date': str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            'ip_address': fetch_current_ip()
        }
        # Insert data into MongoDB

        result = trends_collection.insert_one(trending_data)
        if result.acknowledged:
            print("Trending data successfully added to MongoDB.")
        else:
            print("Failed to add trending data to MongoDB.")
    except Exception as e:
        print(f"Error while inserting data into MongoDB: {e}")

# Check MongoDB connection
def check_mongo_connection():
    try:
        # Ping MongoDB server to check connection
        mongo_client.admin.command('ping')
        print("MongoDB connection successful.")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")

def main():
    check_mongo_connection()
    proxy = configure_proxy()
    driver = initialize_driver(proxy)
    try:
        try:
            load_cookies(driver, "twitter_cookies.pkl")
            driver.get("https://x.com/home")
            time.sleep(5)
        except Exception as e:
            print("No valid cookies found, logging in again...")
            login_to_twitter(driver)
        
        trends = scrape_trending_topics(driver)
        if trends:
            print(f"Trending Topics: {trends}")
            add_to_database(trends)
        else:
            print("No trending topics found.")
    except Exception as exc:
        print(f"An error occurred: {exc}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
