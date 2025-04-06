import requests
from bs4 import BeautifulSoup

def crawl(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    for link in soup.find_all('a', href=True):
        print(link['href'])  # Extract URLs

crawl('https://google.com')


print('hello')