import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import os
import csv

folder_path = "fireout"
urls = []

# Loop through all CSV files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".csv"):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)  # skip header if present
            for row in reader:
                if row:  # avoid empty rows
                    urls.append(row[0])  # first column = URL

print(f"✅ Loaded {len(urls)} URLs from {folder_path} , will now remove duplicates")

urls = list(dict.fromkeys(urls))

print(f"✅ Loaded {len(urls)} URLs from {folder_path}")


#urls = ['https://hermans.se/', 'http://www.mamawolf.nu/', 'https://www.kvarnen.com/?utm_source=google']

# exit()

# Regex for emails
email_pattern = re.compile(r"/\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b/g")

# Settings
MAX_PAGES = 30   # limit depth per site to avoid endless crawling
TIMEOUT = 20

def scrape_site(base_url):
    visited = set()
    to_visit = [base_url]
    found_emails = set()
    domain = urlparse(base_url).netloc

    while to_visit and len(visited) < MAX_PAGES:
        url = to_visit.pop(0)

        if url in visited:
            continue

        try:
            response = requests.get(url, timeout=TIMEOUT)
            response.raise_for_status()
        except requests.RequestException:
            continue

        visited.add(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract emails directly from the HTML
        html_content = str(soup)
        emails = set(re.findall(email_pattern, html_content))
        found_emails.update(emails)

        # Optional: Also check for mailto links
        for mailto in soup.select('a[href^=mailto]'):
            mail_email = mailto['href'].replace("mailto:", "").split('?')[0]
            found_emails.add(mail_email)

        # Extract internal links
        for a_tag in soup.find_all("a", href=True):
            link = urljoin(base_url, a_tag["href"])
            parsed_link = urlparse(link)

            # Stay inside the same domain
            if parsed_link.netloc == domain and link not in visited:
                to_visit.append(link)

    return found_emails

# Run scraper
results = {}
for site in urls:
    print(f"🔎 Scraping {site} ...")
    emails = scrape_site(site)
    results[site] = emails
    print(f"✅ Found {len(emails)} emails on {site}")

# Print results
for site, emails in results.items():
    print(f"\n{site}:")
    for email in emails:
        print("  -", email)


# Now store in csv file

# Ensure folder exists
folder_path = "emailsout"
os.makedirs(folder_path, exist_ok=True)

# Output file
output_file = os.path.join(folder_path, "scraped_emails.csv")

# Write results to CSV
with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["site", "emails"])  # header
    
    for site, emails in results.items():
        if emails:
            writer.writerow([site, ", ".join(emails)])
        else:
            writer.writerow([site, ""])  # empty if no emails found

print(f"✅ Emails saved to {output_file}")
