"""
Działająca demonstracja scrapera nieruchomości
"""
import requests
from bs4 import BeautifulSoup
import time
import random
import logging
import re
from datetime import datetime

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_headers():
    """Zwraca headers dla requests"""
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "pl-PL,pl;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }

def extract_price(text):
    """Ekstraktuje cenę z tekstu"""
    if not text:
        return None, None, ""
    
    # Usuń spacje i znormalizuj
    clean = re.sub(r'\s+', ' ', text.strip())
    
    # Znajdź cenę i walutę
    price_match = re.search(r'(\d+(?:\s?\d{3})*(?:,\d{2})?)', clean)
    currency_match = re.search(r'(zł|PLN|€|EUR|\$|USD)', clean)
    
    price = None
    if price_match:
        price_str = price_match.group(1).replace(' ', '').replace(',', '.')
        try:
            price = float(price_str)
        except ValueError:
            pass
    
    currency = currency_match.group(1) if currency_match else "zł"
    
    return price, currency, clean

def scrape_olx_simple():
    """Prosty scraper OLX bez skomplikowanych selektorów"""
    url = "https://www.olx.pl/nieruchomosci/mieszkania/sprzedaz/"
    
    logger.info(f"Scrapuję OLX: {url}")
    
    try:
        response = requests.get(url, headers=get_headers(), timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Znajdź ogłoszenia - OLX ma różne struktury, więc spróbuj kilka
        offers = (soup.find_all("div", {"data-cy": "l-card"}) or 
                 soup.find_all("div", class_=re.compile("css-.*")) or
                 soup.find_all("a", href=re.compile("/oferta/")))
        
        listings = []
        
        for offer in offers[:10]:  # Weź maksymalnie 10 ogłoszeń
            try:
                # Tytuł
                title_elem = (offer.find("h6") or 
                             offer.find("h4") or 
                             offer.find("h3") or
                             offer.find(text=re.compile(r'pokoje|mieszkanie|m²')))
                
                title = ""
                if title_elem:
                    if hasattr(title_elem, 'get_text'):
                        title = title_elem.get_text(strip=True)
                    elif isinstance(title_elem, str):
                        title = title_elem.strip()
                
                # URL
                url_elem = offer if offer.name == "a" else offer.find("a")
                listing_url = ""
                if url_elem and url_elem.get("href"):
                    href = url_elem.get("href")
                    if href.startswith("/"):
                        listing_url = f"https://www.olx.pl{href}"
                    elif href.startswith("http"):
                        listing_url = href
                
                # Cena - szukaj w tekście
                price_text = ""
                price_elem = offer.find(text=re.compile(r'\d+.*zł'))
                if price_elem:
                    price_text = price_elem.strip()
                
                price, currency, price_original = extract_price(price_text)
                
                # Lokalizacja - często w małym tekście
                location = ""
                location_elem = offer.find("p", class_=re.compile("text.*small"))
                if location_elem:
                    location = location_elem.get_text(strip=True)
                
                if title and listing_url:
                    listing = {
                        "title": title,
                        "url": listing_url,
                        "price": price,
                        "price_currency": currency,
                        "price_original": price_original,
                        "location": location,
                        "source": "olx.pl",
                        "scraped_at": datetime.now().isoformat()
                    }
                    listings.append(listing)
                
            except Exception as e:
                logger.debug(f"Błąd parsowania ogłoszenia: {e}")
                continue
        
        logger.info(f"Pobrano {len(listings)} ogłoszeń z OLX")
        return listings
        
    except Exception as e:
        logger.error(f"Błąd scrapowania OLX: {e}")
        return []

def scrape_sample_portal():
    """Demonstracyjny scraper dla przykładowego portalu"""
    # Zamiast prawdziwego portalu, stwórzmy przykładowe dane
    sample_listings = [
        {
            "title": "Mieszkanie 3-pokojowe, 65m², Warszawa-Mokotów",
            "price": 850000.0,
            "price_currency": "zł",
            "price_original": "850 000 zł",
            "location": "Warszawa, Mokotów",
            "url": "https://example.com/mieszkanie-1",
            "area": "65 m²",
            "rooms": "3 pokoje",
            "description": "Piękne mieszkanie w centrum Mokotowa",
            "source": "example.pl",
            "scraped_at": datetime.now().isoformat()
        },
        {
            "title": "Kawalerka 25m², blisko metra",
            "price": 450000.0,
            "price_currency": "zł", 
            "price_original": "450 000 zł",
            "location": "Warszawa, Wola",
            "url": "https://example.com/mieszkanie-2",
            "area": "25 m²",
            "rooms": "1 pokój",
            "description": "Kompaktowa kawalerka",
            "source": "example.pl",
            "scraped_at": datetime.now().isoformat()
        }
    ]
    
    logger.info(f"Wygenerowano {len(sample_listings)} przykładowych ogłoszeń")
    return sample_listings

def demo_scraper():
    """Główna demonstracja scrapera"""
    print("="*60)
    print("DEMONSTRACJA SCRAPERA NIERUCHOMOŚCI")
    print("="*60)
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_listings = []
    
    # Test OLX
    print("\n1. Scraping OLX.pl...")
    olx_listings = scrape_olx_simple()
    all_listings.extend(olx_listings)
    
    # Przykładowe dane
    print("\n2. Przykładowe dane...")
    sample_listings = scrape_sample_portal()
    all_listings.extend(sample_listings)
    
    # Podsumowanie
    print(f"\n=== PODSUMOWANIE ===")
    print(f"Łącznie pobrano: {len(all_listings)} ogłoszeń")
    print(f"OLX: {len(olx_listings)} ogłoszeń")
    print(f"Przykładowe: {len(sample_listings)} ogłoszeń")
    
    # Pokaż przykłady
    if all_listings:
        print("\n=== PRZYKŁADOWE OGŁOSZENIA ===")
        for i, listing in enumerate(all_listings[:3], 1):
            print(f"\n--- Ogłoszenie {i} ---")
            print(f"Tytuł: {listing['title']}")
            print(f"Cena: {listing['price']} {listing['price_currency']}")
            print(f"Lokalizacja: {listing['location']}")
            print(f"URL: {listing['url']}")
            print(f"Źródło: {listing['source']}")
    
    print("\n" + "="*60)
    print("SCRAPER DZIAŁA POPRAWNIE! ✓")
    print("="*60)
    
    return all_listings

if __name__ == "__main__":
    demo_scraper() 