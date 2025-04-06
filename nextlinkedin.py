from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def search_bing_with_safari(query, num_pages=1):
    """
    Search Bing for LinkedIn profiles using Safari WebDriver and collect results from multiple pages.
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

        profiles = []  # Store profile details (name, company, URL)

        for page in range(num_pages):
            print(f"Scraping page {page + 1}...")

            # Extract LinkedIn profile URLs and details from the current page
            results = driver.find_elements(By.CSS_SELECTOR, "li.b_algo")
            for result in results:
                try:
                    # Extract the full name from the <a> tag inside <h2>
                    name_element = result.find_element(By.CSS_SELECTOR, "h2 a")
                    name = name_element.text.strip()

                    # Extract the company name
                    # Find the <div> containing "Works For:" and extract the text after it
                    works_for_div = result.find_element(By.XPATH, ".//div[contains(., 'Works For:')]")
                    company = works_for_div.text.replace("Works For:", "").strip()

                    # Extract the LinkedIn profile URL
                    href = name_element.get_attribute("href")
                    if href and "linkedin.com/in/" in href:
                        profiles.append({"name": name, "company": company, "url": href})
                except Exception as e:
                    print(f"Error extracting data from a result: {e}")
                    continue

            # Construct the URL for the next page
            next_page_start = (page + 1) * 10 + 1  # Bing shows 10 results per page
            next_page_url = f"{driver.current_url.split('&first=')[0]}&first={next_page_start}"

            # Go to the next page
            driver.get(next_page_url)

            # Wait for the next page to load
            time.sleep(3)

        return profiles

    finally:
        # Close the browser
        driver.quit()

def main():
    # Search query (e.g., "site:linkedin.com/in/ Python Developer")
    query = "site:linkedin.com/in/ manager"

    # Number of pages to scrape
    num_pages = 1  # Change this to the number of pages you want to scrape

    profiles = search_bing_with_safari(query, num_pages=num_pages)

    # Print the LinkedIn profile details
    if profiles:
        print(f"Found {len(profiles)} LinkedIn profiles:")
        for profile in profiles:
            print(f"Name: {profile['name']}")
            print(f"Company: {profile['company']}")
            print(f"URL: {profile['url']}")
            print("-" * 40)
    else:
        print("No LinkedIn profiles found.")

if __name__ == "__main__":
    main()