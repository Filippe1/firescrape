#!/usr/bin/env python3
"""
Scrape emails and clickable links (anchors, areas, onclick handlers, buttons/inputs)
from a start URL using Selenium.
"""
#import re
#import time
import os
import pandas as pd
#from urllib.parse import urljoin, urlparse
import re
import time
from urllib.parse import urljoin, urlparse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ============================
# CONFIGURATION
# ============================
OUTPUT_CSV  = "crawlout/urls_updated.csv"
#START_URL   = "http://www.mamawolf.nu/"  # starting page
DEPTH       = 1                          # 0 = only start page
MAX_PAGES   = 20                        # maximum pages to visit
DOMAIN_ONLY = True                       # stay on same domain as START_URL
HEADLESS    = True                       # run Chrome headless
PAUSE       = 1.0                        # seconds to wait after page load
folder_path = "emailsout"
urls = []
# ============================



# Loop through all CSV files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".csv"):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            df = pd.read_csv(f)
            #header = next(df, None)  # skip header if present
            for row in df:
                if row:  # avoid empty rows
                    urls.append(row[0])  # first column = URL

updated_emails = []





EMAIL_RE = re.compile(
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
)

JS_URL_RE = re.compile(r"""(?:"|')(?P<url>https?://[^"']+)(?:"|')|(?P<rel>/[^\s'"]+)""", re.IGNORECASE)


def wait_for_ready(driver, timeout=10):
    """Wait until document.readyState == 'complete'."""
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
    except Exception:
        pass


def get_emails_from_html(html):
    return set(m.group(0) for m in EMAIL_RE.finditer(html))


def normalize_url(base, link):
    if not link:
        return None
    link = link.strip()
    if link.startswith(("mailto:", "javascript:", "#")):
        return None
    return urljoin(base, link)


def extract_urls_from_onclick(onclick_value, base_url):
    urls = set()
    if not onclick_value:
        return urls
    for m in JS_URL_RE.finditer(onclick_value):
        url = m.group('url') or m.group(0)
        if url:
            urls.add(urljoin(base_url, url))
    return urls


def get_clickable_links(driver, base_url):
    links = set()

    # anchors
    for a in driver.find_elements(By.XPATH, "//a[@href]"):
        href = a.get_attribute("href")
        final = normalize_url(base_url, href)
        if final:
            links.add(final)

    # area
    for area in driver.find_elements(By.XPATH, "//area[@href]"):
        href = area.get_attribute("href")
        final = normalize_url(base_url, href)
        if final:
            links.add(final)

    # buttons/inputs with action-like attrs
    buttons = driver.find_elements(By.XPATH, "//button|//input[@type='button']|//input[@type='submit']")
    for b in buttons:
        fa = b.get_attribute("formaction") or b.get_attribute("data-href") or b.get_attribute("href")
        if fa:
            final = normalize_url(base_url, fa)
            if final:
                links.add(final)

    # onclick with URL
    for e in driver.find_elements(By.XPATH, "//*[@onclick]"):
        onclick_val = e.get_attribute("onclick") or ""
        for url in extract_urls_from_onclick(onclick_val, base_url):
            links.add(url)

    # filter http(s)
    return set(u for u in links if urlparse(u).scheme in ("http", "https"))


def same_domain(url1, url2):
    return urlparse(url1).netloc == urlparse(url2).netloc


def crawl(START_URL):
    options = Options()
    if HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    to_visit = [(START_URL, 0)]
    visited = set()
    collected_emails = set()
    discovered_links = set()

    try:
        while to_visit and len(visited) < MAX_PAGES:
            url, d = to_visit.pop(0)
            if url in visited:
                continue
            if DOMAIN_ONLY and not same_domain(START_URL, url):
                continue

            try:
                driver.get(url)
            except Exception as e:
                print(f"[WARN] error loading {url}: {e}")
                visited.add(url)
                continue

            wait_for_ready(driver, timeout=8)
            time.sleep(PAUSE)

            html = driver.page_source or ""

            # extract emails
            emails = get_emails_from_html(html)
            new_emails = emails - collected_emails
            if new_emails:
                print(f"[+] found {len(new_emails)} new emails on {url}")
            collected_emails.update(emails)

            # extract links
            urls = get_clickable_links(driver, url)
            new_links = urls - discovered_links
            discovered_links.update(urls)

            if d < DEPTH:
                for u in sorted(new_links):
                    if u not in visited:
                        if DOMAIN_ONLY and not same_domain(START_URL, u):
                            continue
                        to_visit.append((u, d + 1))

            visited.add(url)
            print(f"[INFO] visited {len(visited)}/{MAX_PAGES}: {url} (links: {len(discovered_links)}, emails: {len(collected_emails)})")
            return collected_emails, discovered_links
    finally:
        driver.quit()

    print("\n=== SUMMARY ===")
    print(f"Pages visited: {len(visited)}")
    print(f"Discovered clickable links: {len(discovered_links)}")
    print(f"Emails found: {len(collected_emails)}")
    for e in sorted(collected_emails):
        print("  ", e)
    print("\nSample links (up to 50):")
    for u in list(sorted(discovered_links))[:50]:
        print("  ", u)

for i, row in df.iterrows():
        print(i)
        #print(row[0])
        url = str(row["site"]).strip()
        existing = str(row.get("emails", "")).strip()

        if not url or (existing and existing != "nan"):
            updated_emails.append(existing)
            continue

        print(f"\n[CRAWL] {url}")
        try:
                emails, links = crawl(url)
                # ensure returned values are iterable sets
                if emails is None:
                    emails = set()
                if links is None:
                    links = set()
        except Exception as e:
                print(f"[ERROR] crawl() raised an exception for {url}: {e}")
                #traceback.print_exc()
                emails, links = set(), set()

        #emails, links = crawl(url)
        emails_str = ";".join(sorted(emails))
        updated_emails.append(emails_str)
        print(f"  Found {len(emails)} emails, {len(links)} links")

df["emails"] = updated_emails
df.to_csv(OUTPUT_CSV, index=False)
print(f"\n[INFO] Updated CSV written to {OUTPUT_CSV}")



