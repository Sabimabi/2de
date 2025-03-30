import requests
import urllib.request
from bs4 import BeautifulSoup

# URL of Bitcoin page on CoinGecko
url = "https://www.coingecko.com/en/coins/bitcoin"

# Headers to mimic a browser visit
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}

# Function to fetch and save the CoinGecko Bitcoin page
def fetch_and_save_page():
    request = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(request) as response:
            page_content = response.read()

        print("Successfully fetched CoinGecko Bitcoin page!")

        # Save HTML content to a file
        with open("coingecko_bitcoin.html", "wb") as file:
            file.write(page_content)

    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}")

# Function to scrape latest 5 Bitcoin news
def get_bitcoin_news():
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        # Locate the news section (selectors may need to be updated if CoinGecko changes its structure)
        news_items = soup.select("div.tw-w-full.tw-relative")[:5]  # Selects the first 5 articles
        
        news_list = []
        for item in news_items:
            title_tag = item.select_one("a.tw-text-gray-900.tw-text-sm.tw-font-medium")
            link_tag = item.select_one("a.tw-text-gray-900.tw-text-sm.tw-font-medium")
            description_tag = item.select_one("p.tw-text-gray-700.tw-text-xs")
            
            if title_tag and link_tag:
                title = title_tag.text.strip()
                link = "https://www.coingecko.com" + link_tag["href"]
                description = description_tag.text.strip() if description_tag else "No description available"
                
                news_list.append({"title": title, "link": link, "description": description})

        return news_list
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return []

# Run both functions
fetch_and_save_page()
news = get_bitcoin_news()

# Print the latest 5 Bitcoin news
print("\nLatest Bitcoin News from CoinGecko:\n")
for idx, article in enumerate(news, start=1):
    print(f"{idx}. {article['title']}")
    print(f"   Link: {article['link']}")
    print(f"   Description: {article['description']}\n")
