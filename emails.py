import os
import csv
import re
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# -------------------------
# SETTINGS
# -------------------------

INPUT_FOLDER = "datacold"
OUTPUT_FOLDER = "emailsout"

MAX_PAGES = 5
TIMEOUT = 10
MAX_WORKERS = 30

CONTACT_KEYWORDS = [
    "contact",
    "kontakt",
    "about",
    "om",
    "team",
    "staff",
    "support",
    "customer",
]

EMAIL_REGEX = re.compile(
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
)

# -------------------------
# SHARED SESSION
# -------------------------

session = requests.Session()

session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0 Safari/537.36"
    )
})

# -------------------------
# LOAD URLS
# -------------------------

urls = []

for filename in os.listdir(INPUT_FOLDER):
    if not filename.endswith(".csv"):
        continue

    file_path = os.path.join(INPUT_FOLDER, filename)

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)

        headers = next(reader, None)

        if not headers:
            continue

        website_columns = [
            idx
            for idx, col in enumerate(headers)
            if "website" in col.lower()
        ]

        if not website_columns:
            continue

        for row in reader:
            for idx in website_columns:
                if idx < len(row):
                    url = row[idx].strip()

                    if url:
                        urls.append(url)

urls = list(dict.fromkeys(urls))

print(f"✅ Loaded {len(urls)} unique URLs")

# -------------------------
# SCRAPER
# -------------------------

def scrape_site(base_url):
    found_emails = set()

    try:
        parsed = urlparse(base_url)

        if not parsed.scheme:
            base_url = "https://" + base_url

        domain = urlparse(base_url).netloc

    except Exception:
        return found_emails

    visited = set()
    to_visit = deque([base_url])

    while to_visit and len(visited) < MAX_PAGES:

        url = to_visit.popleft()

        if url in visited:
            continue

        visited.add(url)

        try:
            response = session.get(
                url,
                timeout=TIMEOUT,
                allow_redirects=True,
            )

            if response.status_code != 200:
                continue

            html = response.text

        except Exception:
            continue

        # ---------------------------------
        # FIND EMAILS IN RAW HTML
        # ---------------------------------

        emails = set(EMAIL_REGEX.findall(html))

        # Remove obvious junk emails
        emails = {
            e for e in emails
            if not e.lower().endswith(
                (
                    ".png",
                    ".jpg",
                    ".jpeg",
                    ".gif",
                    ".webp",
                    ".svg",
                )
            )
        }

        found_emails.update(emails)

        # mailto links
        if "mailto:" in html.lower():

            soup = BeautifulSoup(html, "html.parser")

            for a in soup.select('a[href^="mailto:"]'):
                email = (
                    a["href"]
                    .replace("mailto:", "")
                    .split("?")[0]
                    .strip()
                )

                if email:
                    found_emails.add(email)

        # If we found emails already, stop crawling
        if found_emails:
            break

        # ---------------------------------
        # FIND CONTACT PAGES
        # ---------------------------------

        soup = BeautifulSoup(html, "html.parser")

        for a in soup.find_all("a", href=True):

            href = a["href"]

            href_lower = href.lower()

            if not any(
                keyword in href_lower
                for keyword in CONTACT_KEYWORDS
            ):
                continue

            try:
                full_url = urljoin(url, href)

                parsed_link = urlparse(full_url)

                if parsed_link.netloc != domain:
                    continue

                if full_url not in visited:
                    to_visit.append(full_url)

            except Exception:
                pass

    return found_emails

# -------------------------
# RUN CONCURRENTLY
# -------------------------

results = {}

print(f"🚀 Starting scrape using {MAX_WORKERS} workers...")

with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:

    futures = {
        executor.submit(scrape_site, site): site
        for site in urls
    }

    completed = 0

    for future in as_completed(futures):

        site = futures[future]

        try:
            emails = future.result()

            results[site] = emails

            completed += 1

            print(
                f"[{completed}/{len(urls)}] "
                f"✅ {site} -> {len(emails)} emails"
            )

        except Exception as e:

            completed += 1

            print(
                f"[{completed}/{len(urls)}] "
                f"❌ {site} -> {e}"
            )

# -------------------------
# SAVE RESULTS
# -------------------------

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

output_file = os.path.join(
    OUTPUT_FOLDER,
    "scraped_emails.csv"
)

with open(
    output_file,
    "w",
    newline="",
    encoding="utf-8"
) as csvfile:

    writer = csv.writer(csvfile)

    writer.writerow([
        "site",
        "emails"
    ])

    for site, emails in results.items():

        writer.writerow([
            site,
            ", ".join(sorted(emails))
        ])

print(f"\n✅ Finished")
print(f"✅ Results saved to: {output_file}")
print(
    f"✅ Sites scraped: {len(results)}"
)