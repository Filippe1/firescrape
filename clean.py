# will be used for cleaning emailsout and retrying scraping

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re

options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

driver.get("http://www.mamawolf.nu/")
html = driver.page_source
emails = set(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', html))
print('emails found: ' + str(emails))
driver.quit()


