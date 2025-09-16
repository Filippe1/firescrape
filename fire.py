from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException  # ✅ import added
import time
import os
import csv

# Folder containing the files
folder_path = "fireout"
output_file = "urls.csv"
# Function to scroll to bottom
def scroll_to_bottom(driver, pause_time=2):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause_time)  # wait for new content to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break  # no more content
        last_height = new_height



# Start Firefox
service = Service("/opt/homebrew/bin/geckodriver")  # path to geckodriver


driver = webdriver.Firefox(service=service)

driver.get("https://www.google.com/search?q=restaurant+sodermalm")

# Example: click a button
wait = WebDriverWait(driver, 30)
buttong = wait.until(EC.element_to_be_clickable((By.ID, "L2AGLb")))
buttong.click()

places = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Places']/..")))
places.click()

# Wait until results are loaded
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.MRe4xd")))

# Find all links with class 'MRe4xd'
#links = driver.find_elements(By.CSS_SELECTOR, "a.MRe4xd")

scroll_to_bottom(driver)

links = driver.find_elements(By.CSS_SELECTOR, "a.MRe4xd")
# Extract the 'href' attribute from each link
urls = []
for link in links:
    href = link.get_attribute("href")
    if href:
        urls.append(href)

# Print all URLs
print(urls)

time.sleep(1)


# Wait until the button is clickable
next_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, 'g-right-button[aria-label="Next"]'))
)

# Scroll into view and click
driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
ActionChains(driver).move_to_element(next_button).click().perform()

while True:
    try:
        time.sleep(1)

        scroll_to_bottom(driver)
        time.sleep(1)
        links = driver.find_elements(By.CSS_SELECTOR, "a.MRe4xd")
        # Extract the 'href' attribute from each link
        #urls = []
        for link in links:
            href = link.get_attribute("href")
            if href:
                urls.append(href)

        # Print all URLs
        print(urls)


        # Wait until the "Next" button is clickable
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'g-right-button[aria-label="Next"]'))
        )
        
        # Scroll into view and click
        driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
        ActionChains(driver).move_to_element(next_button).click().perform()
        
    except TimeoutException:
        # Exit loop when the button no longer exists or isn’t clickable
        print("No more 'Next' button found. Exiting loop.")
        break



# create csv: 
# Ensure folder exists
folder_path = "fireout"
os.makedirs(folder_path, exist_ok=True)

# Output file path inside 'fireout'
output_file = os.path.join(folder_path, "urls.csv")

# Write the CSV
with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["URL"])  # header
    for url in urls:
        writer.writerow([url])

print(f"✅ CSV file created at: {output_file}")
