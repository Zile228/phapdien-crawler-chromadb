import os
import re
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# Define the base directory for storing HTML files
BASE_DIR = "BoPhapDienDienTu"
FOLDER_PATH = os.path.join(BASE_DIR, "demuc")

# Initialize Selenium WebDriver
service = Service(r"chromedriver.exe")  # Path to chromedriver executable
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run in headless mode (no GUI)
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(service=service, options=options)

def save_html(url, folder, filename):
    """Save the HTML content of a webpage to a file"""
    os.makedirs(os.path.join(BASE_DIR, folder), exist_ok=True)
    filepath = os.path.join(BASE_DIR, folder, filename)
    if os.path.exists(filepath):
        print(f"File already exists: {filepath}")
        return
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(fetch_page(url))
    print(f"Saved: {filepath}")

def fetch_page(url):
    """Fetch the HTML content of a page using Selenium"""
    driver.get(url)
    try:
        # Wait up to 5 seconds for the main content to load
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
    except Exception as e:
        print(f"Warning: {url} might not have fully loaded.")
    return driver.page_source

def getfullitem(item_id):
    """Retrieve the full document for a given ItemID"""
    url = f"https://vbpl.vn/TW/Pages/vbpq-toanvan.aspx?ItemID={item_id}&Keyword="
    save_html(url, "vbpl", f"full_{item_id}.html")

def getproperty(item_id):
    """Retrieve document properties for a given ItemID"""
    url = f"https://vbpl.vn/tw/Pages/vbpq-thuoctinh.aspx?dvid=13&ItemID={item_id}&Keyword="
    save_html(url, "property", f"p_{item_id}.html")

def gethistory(item_id):
    """Retrieve document history for a given ItemID"""
    url = f"https://vbpl.vn/tw/Pages/vbpq-lichsu.aspx?dvid=13&ItemID={item_id}&Keyword="
    save_html(url, "history", f"h_{item_id}.html")

def getrelated(item_id):
    """Retrieve related documents for a given ItemID"""
    url = f"https://vbpl.vn/TW/Pages/vbpq-vanbanlienquan.aspx?ItemID={item_id}&Keyword="
    save_html(url, "related", f"r_{item_id}.html")

def save_pdf(url, folder, filename):
    """Download and save a PDF file"""
    os.makedirs(os.path.join(BASE_DIR, folder), exist_ok=True)
    filepath = os.path.join(BASE_DIR, folder, filename)
    if os.path.exists(filepath):
        print(f"File already exists: {filepath}")
        return
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(filepath, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
        print(f"PDF Saved: {filepath}")
    else:
        print(f"Failed to download PDF: {url}")

def getpdf(item_id):
    """Retrieve and save the original document PDF for a given ItemID"""
    url = f"https://vbpl.vn/TW/Pages/vbpq-van-ban-goc.aspx?dvid=13&ItemID={item_id}"
    html = fetch_page(url)
    embed_match = re.search(r'<embed\s+[^>]*src="([^"]+)"', html)
    if embed_match:
        url_match = re.search(r'url=([^"\s]+)', embed_match.group(1))
        if url_match:
            save_pdf(url_match.group(1), "pdf", f"pdf_{item_id}.pdf")
        else:
            print(f"No valid PDF URL for ItemID {item_id}")
    else:
        print(f"No <embed> tag found for ItemID {item_id}")

# Extract URLs containing ItemID from stored HTML files
href_dict = {}
href_pattern = r'href=["\'](.*?ItemID=(\d+).*?)["\']'

for file_name in os.listdir(FOLDER_PATH):
    file_path = os.path.join(FOLDER_PATH, file_name)
    if os.path.isfile(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            soup = BeautifulSoup(content, "html.parser")
            for a_tag in soup.find_all("a", href=True):
                link = a_tag["href"].split("#")[0]
                if "ItemID=" in link:
                    item_id = link.split("ItemID=")[-1].split("&")[0]
                    if item_id and item_id not in href_dict:
                        href_dict[item_id] = link

# Iterate through each ItemID and download relevant data
for item_id in href_dict.keys():
    print(f"Processing ItemID: {item_id}")
    getfullitem(item_id)
    getproperty(item_id)
    gethistory(item_id)
    getrelated(item_id)
    getpdf(item_id)

# Close the Selenium WebDriver
driver.quit()
