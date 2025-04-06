from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def get_company_names(query, num_pages=1):
    """
    Search Bing for LinkedIn profiles using Safari WebDriver and extract company names.
    """
    # Set up the Safari WebDriver
    driver = webdriver.Safari()

    try:
        # Go to Bing
        driver.get("https://www.bing.com")

        # Find the search box and enter the query
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)

        # Wait for the results to load
        time.sleep(3)

        company_names = []  # Store company names

        for page in range(num_pages):
            print(f"Scraping page {page + 1}...")

            # Extract company names from the current page
            results = driver.find_elements(By.CSS_SELECTOR, "li.b_algo")
            for result in results:
                try:
                    # Extract the company name from the <strong> tags in the b_caption div
                    caption = result.find_element(By.CSS_SELECTOR, "div.b_caption")
                    strong_tags = caption.find_elements(By.TAG_NAME, "strong")
                    
                    # Look for the company name in the <strong> tags
                    company = None
                    for tag in strong_tags:
                        if " at " in tag.text:
                            company = tag.text.split(" at ")[-1].strip()
                            break
                    
                    if company:
                        company_names.append(company)
                except Exception as e:
                    print(f"Error extracting company name from a result: {e}")
                    continue

            # Construct the URL for the next page
            next_page_start = (page + 1) * 10 + 1  # Bing shows 10 results per page
            next_page_url = f"{driver.current_url.split('&first=')[0]}&first={next_page_start}"

            # Go to the next page
            driver.get(next_page_url)

            # Wait for the next page to load
            time.sleep(3)

        return company_names

    finally:
        # Close the browser
        driver.quit()

def main():
    # Search query (e.g., "site:linkedin.com/in/ Python Developer")
    query = "site:linkedin.com/in/ manager"

    # Number of pages to scrape
    num_pages = 1  # Change this to the number of pages you want to scrape

    company_names = get_company_names(query, num_pages=num_pages)

    # Print the company names
    if company_names:
        print(f"Found {len(company_names)} company names:")
        for company in company_names:
            print(company)
    else:
        print("No company names found.")

if __name__ == "__main__":
    main()