from bs4 import BeautifulSoup

# Allowed cryptocurrencies and their respective HTML files
crypto_files = {
    "BTC": "work/bitcoin.html",
    "ETH": "work/eu.html",
    "ADA": "work/cardano.html",
    "XRP": "work/xrp.html",
    "DOGE": "work/doge.html",
    "LTC": "work/lite.html",
    "BNB": "work/bnb.html",
    "SOL": "work/sol.html",
    "DOT": "work/dot.html",
    "AVAX": "work/avax.html"
}

def extract_crypto_news(crypto_symbol, keywords=None):
    """
    Extracts the latest 8 news articles for a given cryptocurrency.
    Filters by keywords and returns the output in a structured dictionary format.
    
    :param crypto_symbol: Cryptocurrency symbol (BTC, ETH, ADA, XRP, DOGE, LTC, BNB, SOL, DOT, AVAX)
    :param keywords: List of keywords to filter articles (optional)
    :return: List of dictionaries containing news details
    """
    crypto_symbol = crypto_symbol.upper()

    if crypto_symbol not in crypto_files:
        print(f"❌ Invalid cryptocurrency! Choose from: {list(crypto_files.keys())}")
        return []

    file_path = crypto_files[crypto_symbol]

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")
    except FileNotFoundError:
        print(f"❌ Error: HTML file for {crypto_symbol} not found: {file_path}")
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

# --- Example Usage ---
if __name__ == "__main__":
    crypto_symbol = input("Enter cryptocurrency symbol (BTC/ETH/ADA/XRP/DOGE/LTC/BNB/SOL/DOT/AVAX): ").strip().upper()
    keyword_input = input("Enter keywords (comma-separated) or press Enter to skip: ").strip()
    keywords = [kw.strip() for kw in keyword_input.split(",")] if keyword_input else None

    news_list = extract_crypto_news(crypto_symbol, keywords)

    print(f"\n📰 Latest {crypto_symbol} News:\n")
    for news in news_list:
        print(news)

