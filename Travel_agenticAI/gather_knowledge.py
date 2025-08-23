import os
import requests
from bs4 import BeautifulSoup
import time
import re

# --- 1. Configuration ---
KNOWLEDGE_BASE_DIR = "knowledge_base"
# Add any high-quality travel blog/guide URLs you want to scrape here
URLS_TO_SCRAPE = [
    "https://www.nomadicmatt.com/travel-guides/spain-travel-guide/",
    "https://www.ricksteves.com/europe/spain/itinerary",
    "https://www.theguardian.com/travel/2022/jul/25/a-local-guide-to-madrid-spain-bars-restaurants-and-hotels",
    "https://www.lonelyplanet.com/articles/top-things-to-do-in-spain"
]

# --- 2. The Scraper Function ---
def scrape_and_clean_article(url):
    """
    Scrapes the main content of an article from a URL, cleaning out boilerplate.
    """
    print(f"Scraping: {url}")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()  # Raise an exception for bad status codes

        soup = BeautifulSoup(response.text, 'html.parser')

        # --- Content Extraction Logic ---
        # This is the most crucial part. We try different common tags for main content.
        # You might need to adjust this based on the websites you scrape.
        main_content = soup.find('article') or soup.find('main') or soup.find(id='main-content') or soup.find(class_='post-content')
        
        if not main_content:
            print(f"Warning: Could not find a clear main content element for {url}. Falling back to body.")
            main_content = soup.body

        # Remove common unwanted elements like scripts, styles, navs, footers
        for element in main_content(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            element.decompose()

        # Get text and clean it up
        text = main_content.get_text(separator='\n', strip=True)
        # Remove excessive blank lines
        cleaned_text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return cleaned_text

    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

# --- 3. Main Execution ---
if __name__ == "__main__":
    if not os.path.exists(KNOWLEDGE_BASE_DIR):
        os.makedirs(KNOWLEDGE_BASE_DIR)

    print(f"--- Starting Knowledge Base Population from {len(URLS_TO_SCRAPE)} URLs ---")

    for url in URLS_TO_SCRAPE:
        content = scrape_and_clean_article(url)
        
        if content:
            # Create a simple filename from the URL
            filename = url.split("/")[-2] + ".txt"
            filepath = os.path.join(KNOWLEDGE_BASE_DIR, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Successfully saved content to {filepath}")
        else:
            print(f"Failed to retrieve content from {url}")

        # Be a good web citizen: wait a second between requests
        time.sleep(1)

    print("--- Knowledge Base Population Complete ---")

