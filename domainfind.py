import requests
from bs4 import BeautifulSoup

def find_company_website(company_name):
    query = f"{company_name} official website"
    url = f"https://www.google.com/search?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}  # Add a user-agent to avoid being blocked
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes
    except requests.RequestException as e:
        print(f"Error fetching search results: {e}")
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    for link in soup.find_all("a"):
        href = link.get("href")
        if href and "url?q=" in href and "webcache" not in href:  # Check if href is not None
            # Extract the actual URL from the Google redirect
            return href.split("url?q=")[1].split("&")[0]
    
    return None

# Example usage
company_name = "Example Company"
website = find_company_website(company_name)
print(f"Website: {website}")