#fancy but still does not work

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.safari.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time
import random
import re

def setup_stealth_driver():
    """Set up Safari with stealth options"""
    options = Options()
    
    # Enable headless mode (optional - comment out if you want visible browser)
    # options.add_argument("--headless")
    
    # Set user agent to mimic real browser
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
    ]
    
    options.add_argument(f"user-agent={random.choice(user_agents)}")
    
    # Disable automation flags
    #options.add_experimental_option("excludeSwitches", ["enable-automation"])
    #options.add_experimental_option('useAutomationExtension', False)
    
    
    
    driver = webdriver.Safari(options=options)
    # Execute JavaScript to remove automation flags (Safari compatible)
    
    driver.execute_script("""
        // Override the webdriver property
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
            enumerable: true,
            configurable: true
        });
        
        // Override other automation detection properties
        window.chrome = {
            runtime: {},
            // Add other chrome properties if needed
        };
    """)
    # Execute CDP commands to avoid detection
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def human_like_mouse_movement(driver, element):
    """Simulate human-like mouse movement"""
    actions = ActionChains(driver)
    
    # Move to element with slight randomness
    actions.move_to_element_with_offset(
        element, 
        random.randint(-5, 5), 
        random.randint(-5, 5)
    )
    actions.perform()
    time.sleep(random.uniform(0.1, 0.5))

def random_scroll(driver):
    """Perform random scrolling to mimic human behavior"""
    scroll_amount = random.randint(200, 800)
    driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
    time.sleep(random.uniform(0.5, 2))

def search_bing_with_safari(query, num_pages=1):
    """
    Search Bing for LinkedIn profiles using Safari WebDriver with anti-detection measures.
    """
    driver = setup_stealth_driver()
    wait = WebDriverWait(driver, 15)

    try:
        # Add random delay before starting
        time.sleep(random.uniform(1, 3))
        
        # Go to Bing
        driver.get("https://www.bing.com")
        
        # Wait for page to load
        time.sleep(random.uniform(2, 4))

        # Find search box with multiple selectors
        search_selectors = [
            (By.NAME, "q"),
            (By.ID, "sb_form_q"),
            (By.CSS_SELECTOR, "input[type='search']"),
            (By.CSS_SELECTOR, "input[name='q']")
        ]
        
        search_box = None
        for by, value in search_selectors:
            try:
                search_box = wait.until(EC.presence_of_element_located((by, value)))
                break
            except:
                continue
        
        if not search_box:
            raise Exception("Search box not found")

        # Simulate human-like interaction with the search box
        human_like_mouse_movement(driver, search_box)
        time.sleep(random.uniform(0.5, 1.5))

        # Type slowly like a human
        for char in query:
            search_box.send_keys(char)
            time.sleep(random.uniform(0.05, 0.2))
        
        # Add slight delay before pressing enter
        time.sleep(random.uniform(0.5, 1.5))
        search_box.send_keys(Keys.RETURN)
         #2. PAUSE THE SCRIPT - Wait for user input
        #input("Please manually log in, solve any CAPTCHAs, and press Enter in this terminal to continue...")
        print('fix captcha now')
        time.sleep(30)
        print('resuming')
        # Wait for results with explicit condition
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h2 a")))
        time.sleep(random.uniform(2, 4))

        # Perform random scroll to mimic human behavior
        random_scroll(driver)

        linkedin_urls = []

        for page in range(num_pages):
            print(f"Scraping page {page + 1}...")

            # Extract LinkedIn profile URLs with better selectors
            results = driver.find_elements(By.CSS_SELECTOR, "h2 a")
            for result in results:
                try:
                    href = result.get_attribute("href")
                    if href and re.search(r'linkedin\.com/in/', href, re.IGNORECASE):
                        # Clean the URL (remove tracking parameters)
                        clean_url = re.sub(r'\?.*', '', href)
                        if clean_url not in linkedin_urls:
                            linkedin_urls.append(clean_url)
                except Exception as e:
                    print(f"Error extracting URL: {e}")
                    continue

            if page < num_pages - 1:  # Don't try to go to next page on last page
                # Find next page button instead of constructing URL
                next_selectors = [
                    (By.CSS_SELECTOR, "a.sb_pagN"),
                    (By.CSS_SELECTOR, "a[title='Next page']"),
                    (By.XPATH, "//a[contains(text(), 'Next')]"),
                    (By.CSS_SELECTOR, "a[aria-label='Next page']")
                ]
                
                next_button = None
                for by, value in next_selectors:
                    try:
                        next_button = driver.find_element(by, value)
                        break
                    except:
                        continue
                
                if next_button:
                    # Scroll to button and click
                    driver.execute_script("arguments[0].scrollIntoView();", next_button)
                    time.sleep(random.uniform(1, 2))
                    
                    # Simulate human-like click
                    human_like_mouse_movement(driver, next_button)
                    next_button.click()
                    
                    # Wait for next page to load
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h2 a")))
                    time.sleep(random.uniform(2, 4))
                    
                    # Random scroll on new page
                    random_scroll(driver)
                else:
                    print("Next page button not found. Stopping.")
                    break

        return linkedin_urls

    except Exception as e:
        print(f"Error during scraping: {e}")
        # Take screenshot for debugging
        driver.save_screenshot(f"error_screenshot_{int(time.time())}.png")
        return []
    finally:
        # Add random delay before quitting
        time.sleep(random.uniform(1, 3))
        driver.quit()

def main():
    # Search queries (rotate to avoid patterns)
    queries = [
        "site:linkedin.com/in/ manager",
        "site:linkedin.com/in/ \"project manager\"",
        "site:linkedin.com/in/ \"senior manager\"",
        "site:linkedin.com/in/ \"product manager\"",
        "site:linkedin.com/in/ \"marketing manager\""
    ]

    all_profiles = []
    
    for i, query in enumerate(queries):
        print(f"Processing query {i+1}/{len(queries)}: {query}")
        
        # Scrape 1-2 pages per query to avoid detection
        num_pages = random.randint(1, 2)
        
        linkedin_profiles = search_bing_with_safari(query, num_pages=num_pages)
        
        if linkedin_profiles:
            print(f"Found {len(linkedin_profiles)} profiles for this query")
            all_profiles.extend(linkedin_profiles)
        else:
            print("No profiles found for this query")
        
        # Add significant delay between queries
        if i < len(queries) - 1:
            delay = random.uniform(30, 120)  # 30 seconds to 2 minutes
            print(f"Waiting {delay:.1f} seconds before next query...")
            time.sleep(delay)

    # Remove duplicates while preserving order
    unique_profiles = []
    seen = set()
    for profile in all_profiles:
        if profile not in seen:
            seen.add(profile)
            unique_profiles.append(profile)

    # Print results
    if unique_profiles:
        print(f"\nFound {len(unique_profiles)} unique LinkedIn profiles:")
        for i, profile in enumerate(unique_profiles, 1):
            print(f"{i}. {profile}")
        
        # Save to file
        with open("linkedin_profiles.txt", "w") as f:
            for profile in unique_profiles:
                f.write(f"{profile}\n")
        print(f"\nResults saved to 'linkedin_profiles.txt'")
    else:
        print("No LinkedIn profiles found.")

if __name__ == "__main__":
    print("Starting LinkedIn profile scraper...")
    print("Note: This may take several minutes due to anti-bot protection measures.")
    main()