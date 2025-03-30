import requests
import urllib.request
from bs4 import BeautifulSoup
import time
import os
import csv

# Dictionary of cryptocurrencies with their CoinGecko URLs and local file paths
crypto_data = {
    "BTC": {"url": "https://www.coingecko.com/en/coins/bitcoin", "file": "web/bitcoin.html"},
    "ETH": {"url": "https://www.coingecko.com/en/coins/ethereum", "file": "web/eu.html"},
    "ADA": {"url": "https://www.coingecko.com/en/coins/cardano", "file": "web/cardano.html"},
    "XRP": {"url": "https://www.coingecko.com/en/coins/xrp", "file": "web/xrp.html"},
    "DOGE": {"url": "https://www.coingecko.com/en/coins/dogecoin", "file": "web/doge.html"},
    "LTC": {"url": "https://www.coingecko.com/en/coins/litecoin", "file": "web/lite.html"},
    "BNB": {"url": "https://www.coingecko.com/en/coins/binancecoin", "file": "web/bnb.html"},
    "SOL": {"url": "https://www.coingecko.com/en/coins/solana", "file": "web/sol.html"},
    "DOT": {"url": "https://www.coingecko.com/en/coins/polkadot", "file": "web/dot.html"},
    "AVAX": {"url": "https://www.coingecko.com/en/coins/avalanche", "file": "web/avax.html"},
}

# Headers to mimic a browser visit
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}

# Function to fetch and save HTML pages
def fetch_and_save_pages():
    os.makedirs("web", exist_ok=True)  # Ensure "web" directory exists

    for symbol, data in crypto_data.items():
        url, file_path = data["url"], data["file"]
        request = urllib.request.Request(url, headers=headers)

        try:
            with urllib.request.urlopen(request) as response:
                page_content = response.read()

            with open(file_path, "wb") as file:
                file.write(page_content)

            print(f"✅ Successfully saved {symbol} page!")

            # Pause between requests to prevent blocking
            time.sleep(2)

        except urllib.error.HTTPError as e:
            print(f" HTTP Error for {symbol}: {e.code} - {e.reason}")
        except urllib.error.URLError as e:
            print(f" URL Error for {symbol}: {e.reason}")

# Function to extract news from saved HTML files
def extract_crypto_news(crypto_symbol, keywords=None):
    crypto_symbol = crypto_symbol.upper()

    if crypto_symbol not in crypto_data:
        print(f"❌ Invalid cryptocurrency! Choose from: {list(crypto_data.keys())}")
        return []

    file_path = crypto_data[crypto_symbol]["file"]

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")
    except FileNotFoundError:
        print(f"❌ Error: HTML file for {crypto_symbol} not found at {file_path}")
        return []

    # Locate the news section
    news_section = soup.find("div", class_="tw-my-6 lg:tw-mb-12")
    if not news_section:
        print(f"❌ Could not find news section for {crypto_symbol}")
        return []

    # Extract latest 80 news articles (for filtering)
    news_items = news_section.find_all(
        "div", class_="tw-border-0 tw-border-b tw-border-solid tw-border-gray-200 dark:tw-border-moon-700 tw-pb-5 tw-flex tw-flex-col", 
        limit=80
    )

    extracted_news = []
    for item in news_items:
        title_tag = item.find("div", class_="tw-mb-4 tw-font-bold tw-text-gray-900 dark:tw-text-moon-50 tw-text-lg md:tw-text-xl tw-leading-7")
        link_tag = item.find("a", href=True)
        description_tag = item.find("div", class_="tw-my-1 tw-text-gray-700 dark:tw-text-moon-100 tw-font-semibold tw-text-sm tw-leading-5")
        date_tag = item.find("time")

        if title_tag and link_tag:
            title = title_tag.text.strip()
            link = link_tag["href"]
            if not link.startswith("http"):
                link = "https://www.coingecko.com" + link  # Ensure valid URL

            description = description_tag.text.strip() if description_tag else "No description available"
            publication_date = date_tag.text.strip() if date_tag else "No date available"

            # Apply keyword filtering
            if keywords:
                if not any(keyword.lower() in title.lower() or keyword.lower() in description.lower() for keyword in keywords):
                    continue

            # Append news in dictionary format
            extracted_news.append({
                "title": title,
                "link": link,
                "publication_date": publication_date,
                "description": description
            })

            # Stop if we have 8 filtered articles
            if len(extracted_news) >= 8:
                break

    return extracted_news  # ✅ Returns a list of dictionaries

# Function to save extracted news to a CSV file
def save_news_to_csv(news_list, filename):
    os.makedirs("news_data", exist_ok=True)  # Create a folder for CSV files if it doesn't exist

    filepath = os.path.join("news_data", filename)

    with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["title", "link", "publication_date", "description"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(news_list)

    print(f"✅ News saved successfully to {filepath}")

# --- Main Execution ---
if __name__ == "__main__":
    # Step 1: Download and save CoinGecko pages
    fetch_and_save_pages()

    # Step 2: Ask user for input
    crypto_symbol = input("\nEnter cryptocurrency symbol (BTC/ETH/ADA/XRP/DOGE/LTC/BNB/SOL/DOT/AVAX): ").strip().upper()
    keyword_input = input("Enter keywords (comma-separated) or press Enter to skip: ").strip()
    keywords = [kw.strip() for kw in keyword_input.split(",")] if keyword_input else None

    # Step 3: Extract and display news
    news_list = extract_crypto_news(crypto_symbol, keywords)

    print(f"\n📢 Latest {crypto_symbol} News:\n")
    for news in news_list:
        print(f"- {news['title']} ({news['publication_date']})\n  {news['link']}\n  {news['description']}\n")

    # Step 4: Save news to CSV
    if news_list:
        filename = input("Enter filename for the CSV (e.g., btc_news.csv): ").strip()
        save_news_to_csv(news_list, filename)
    else:
        print("❌ No news found to save.")