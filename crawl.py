import os
import re
import time
import pandas as pd
from urllib.parse import urljoin, urlparse

from playwright.sync_api import sync_playwright

# Optional stealth
try:
    from playwright_stealth import stealth_sync
    HAS_STEALTH = True
except:
    HAS_STEALTH = False


# ============================
# CONFIG
# ============================

INPUT_CSV = "emailsout/scraped_emails.csv"
OUTPUT_CSV = "crawlout/urls_updated.csv"

DEPTH = 1
MAX_PAGES = 20
DOMAIN_ONLY = True


# ============================
# EMAIL REGEX
# ============================

EMAIL_RE = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)


# ============================
# HELPERS
# ============================

def normalize_email_text(text: str) -> str:
    if not text:
        return ""

    return (
        text.replace("[at]", "@")
            .replace("(at)", "@")
            .replace(" at ", "@")
            .replace("[dot]", ".")
            .replace("(dot)", ".")
            .replace(" dot ", ".")
    )


def get_emails(text):
    text = normalize_email_text(text)
    return set(EMAIL_RE.findall(text))


def same_domain(a, b):
    return urlparse(a).netloc == urlparse(b).netloc


def normalize_url(base, link):
    if not link:
        return None
    link = link.strip()

    if link.startswith(("mailto:", "javascript:", "#")):
        return None

    return urljoin(base, link)


# ============================
# PLAYWRIGHT DRIVER
# ============================

def create_browser(playwright):
    browser = playwright.chromium.launch(
        headless=True,
        args=[
            "--disable-blink-features=AutomationControlled",
        ]
    )

    context = browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        viewport={"width": 1280, "height": 800},
        java_script_enabled=True,
    )

    return browser, context


# ============================
# CORE PAGE SCRAPER
# ============================

def scrape_page(page, url):
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)

        # wait for JS rendering
        page.wait_for_timeout(1500)

        # scroll to trigger lazy load
        for _ in range(3):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1000)

        html = page.content()
        text = page.inner_text("body")

        # scripts often contain emails (React/Next.js)
        scripts = page.evaluate("""
            () => Array.from(document.scripts)
                      .map(s => s.innerText || "")
                      .join(" ")
        """)

        return html + " " + text + " " + scripts

    except Exception:
        return ""


# ============================
# LINK EXTRACTION
# ============================

def extract_links(page, base_url):
    links = set()

    try:
        anchors = page.query_selector_all("a[href]")
        for a in anchors:
            href = a.get_attribute("href")
            url = normalize_url(base_url, href)
            if url:
                links.add(url)

    except:
        pass

    return links


# ============================
# CRAWLER
# ============================

def crawl_site(context, start_url):
    page = context.new_page()

    visited = set()
    queue = [(start_url, 0)]
    discovered = set()
    emails = set()

    while queue and len(visited) < MAX_PAGES:
        url, depth = queue.pop(0)

        if url in visited:
            continue

        if DOMAIN_ONLY and not same_domain(start_url, url):
            continue

        print("Visiting:", url)

        html_blob = scrape_page(page, url)
        emails.update(get_emails(html_blob))

        links = extract_links(page, url)

        new_links = links - discovered
        discovered.update(links)

        if depth < DEPTH:
            for link in new_links:
                if DOMAIN_ONLY and not same_domain(start_url, link):
                    continue
                if link not in visited:
                    queue.append((link, depth + 1))

        visited.add(url)

    page.close()
    return emails


# ============================
# MAIN
# ============================

def main():
    df = pd.read_csv(INPUT_CSV)

    if "emails" not in df.columns:
        df["emails"] = ""

    updated = []

    with sync_playwright() as p:
        browser, context = create_browser(p)

        # stealth injection (if available)
        if HAS_STEALTH:
            stealth_sync(context)

        for idx, row in df.iterrows():
            url = str(row["site"]).strip()
            existing = str(row.get("emails", "")).strip()

            if not url or url == "nan" or (existing and existing != "nan"):
                updated.append(existing)
                continue

            print(f"[{idx+1}/{len(df)}] {url}")

            try:
                emails = crawl_site(context, url)
                updated.append(";".join(sorted(emails)))

            except Exception as e:
                print("ERROR:", e)
                updated.append("")

        browser.close()

    df["emails"] = updated

    os.makedirs("crawlout", exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)

    print("Finished:", OUTPUT_CSV)


if __name__ == "__main__":
    main()