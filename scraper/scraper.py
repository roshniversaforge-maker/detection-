import requests
from bs4 import BeautifulSoup
import time
import random

def fetch_reviews_live(url):
    """
    Attempts to scrape actual reviews from a given Flipkart/Amazon URL.
    Note: Real scraping often gets blocked without advanced proxies/Selenium.
    """
    headers = {
        'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/91.0.4472.124 Safari/537.36'),
        'Accept-Language': 'en-US, en;q=0.5'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return []
            
        soup = BeautifulSoup(response.content, 'html.parser')
        reviews = []
        
        # Super basic approach depending on platform:
        if 'amazon' in url.lower():
            # Amazon review block class is usually 'review-text-content'
            blocks = soup.find_all('span', {'data-hook': 'review-body'})
            for b in blocks:
                text = b.get_text(separator=' ', strip=True)
                if text:
                    reviews.append(text)
                    
        elif 'flipkart' in url.lower():
            # Flipkart review class usually varies but often 't-ZTKy' or 'ZmyqYM'
            blocks = soup.find_all('div', class_='t-ZTKy')
            for b in blocks:
                text = b.get_text(separator=' ', strip=True)
                if text:
                    reviews.append(text)
                    
        return reviews
    except Exception as e:
        print(f"Scraping error: {e}")
        return []

def get_simulated_reviews():
    """
    Fallback mechanism that returns a realistic set of mixed reviews.
    Useful for demonstration when live requests are blocked by CAPTCHA.
    """
    print("Using simulated fallback reviews due to potential bot-block...")
    return [
        "This product is amazing! It works exactly as described and feels premium.",
        "best product ever best product ever best product ever",
        "Delivery was quick and the item was nicely packaged. Would recommend.",
        "Very bad product, broke on the first day. Terrible quality.",
        "100% genuine guaranteed absolutely mind blowing wow",
        "Decent product, matches the description online.",
        "buy this now buy this now",
        "Not bad for the price, but could be better. The material feels slightly cheap.",
        "Review in exchange for discount. Product is perfectly flawlessly amazing.",
        "Fantastic finish and great utility. A must buy for everyone."
    ]

def extract_reviews(url):
    """
    Main extraction function. Tries to scrape, falls back onto mock data if failed.
    """
    print(f"Extracting reviews from URL: {url}")
    live_reviews = fetch_reviews_live(url)
    
    if live_reviews and len(live_reviews) > 3:
        print(f"Successfully scraped {len(live_reviews)} reviews.")
        return live_reviews
    else:
        # Fallback to simulated data if scrape is blocked or yields too few
        return get_simulated_reviews()
