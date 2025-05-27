#!/usr/bin/env python3
"""
SCRAPER OTODOM.PL
Scraper dla portalu Otodom.pl z pełną obsługą Selenium
"""
import logging
import sys
import os
from typing import List, Dict

# Dodaj główny katalog do ścieżki
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils import get_soup, random_delay, clean_text, extract_price

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_otodom_listings(max_pages: int = 5) -> List[Dict]:
    """
    Pobiera ogłoszenia z Otodom.pl
    
    Args:
        max_pages: Maksymalna liczba stron do przeskanowania
    
    Returns:
        List[Dict]: Lista ogłoszeń
    """
    listings = []
    base_url = "https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/cala-polska"
    
    for page in range(1, max_pages + 1):
        try:
            # Konstruuj URL z parametrami
            if page == 1:
                url = f"{base_url}?viewType=listing"
            else:
                url = f"{base_url}?viewType=listing&page={page}"
                
            logger.info(f"🏠 Scrapuję Otodom.pl - strona {page}")
            logger.info(f"🔗 URL: {url}")
            
            # Używamy Selenium dla Otodom
            soup = get_soup(url, use_selenium=True)
            
            # Selektory dla kontenerów ogłoszeń
            offers = (soup.select("[data-cy='listing-item']") or 
                     soup.select("article.css-136g1q2") or 
                     soup.select("article") or
                     soup.select(".listing-item"))
            
            if not offers:
                logger.warning(f"⚠️ Nie znaleziono ogłoszeń na stronie {page}")
                if "otodom" not in soup.get_text().lower():
                    logger.error("❌ Strona nie załadowała się prawidłowo")
                break
            
            logger.info(f"📋 Znaleziono {len(offers)} ogłoszeń na stronie {page}")
            
            for i, offer in enumerate(offers):
                try:
                    listing = parse_otodom_listing(offer)
                    if listing:
                        listing["source"] = "otodom.pl"
                        listing["source_page"] = page
                        listing["source_position"] = i + 1
                        listings.append(listing)
                        logger.debug(f"✅ Parsowano ogłoszenie {i+1}: {listing.get('title', '')[:30]}...")
                except Exception as e:
                    logger.error(f"❌ Błąd parsowania ogłoszenia {i+1}: {e}")
            
            random_delay()
            
        except Exception as e:
            logger.error(f"❌ Błąd pobierania strony {page}: {e}")
            
    logger.info(f"✅ Pobrano ŁĄCZNIE {len(listings)} ogłoszeń z Otodom.pl")
    return listings

def parse_otodom_listing(offer_element) -> Dict:
    """
    Parsuje pojedyncze ogłoszenie z Otodom.pl
    
    Args:
        offer_element: Element BeautifulSoup z ogłoszeniem
    
    Returns:
        Dict: Dane ogłoszenia
    """
    # TYTUŁ
    title_elem = (offer_element.select_one("[data-cy='listing-item-title']") or
                  offer_element.select_one("p.css-u3orbr") or
                  offer_element.select_one("h3") or
                  offer_element.select_one("h2"))
    title = clean_text(title_elem.get_text()) if title_elem else ""
    
    # CENA
    price_elem = (offer_element.select_one("span.css-2bt9f1") or
                  offer_element.select_one("[data-sentry-element='Content']") or
                  offer_element.select_one("[data-cy*='price']"))
    price_text = clean_text(price_elem.get_text()) if price_elem else ""
    price_data = extract_price(price_text)
    
    # LOKALIZACJA
    location_elem = (offer_element.select_one("p.css-42r2ms") or
                     offer_element.select_one("[data-sentry-element='StyledParagraph']") or
                     offer_element.select_one("[data-cy='listing-item-location']"))
    location = clean_text(location_elem.get_text()) if location_elem else ""
    
    # LINK
    link_elem = (offer_element.select_one("[data-cy='listing-item-link']") or
                 offer_element.select_one("a[href*='/oferta/']") or
                 offer_element.select_one("a"))
    url = link_elem.get("href") if link_elem else ""
    if url and not url.startswith("http"):
        url = f"https://www.otodom.pl{url}"
    
    # POWIERZCHNIA I POKOJE z <dl> struktury
    area_text = ""
    rooms_text = ""
    
    specs_list = offer_element.select_one("dl.css-9q2yy4")
    if specs_list:
        dt_elements = specs_list.select("dt")
        dd_elements = specs_list.select("dd")
        
        for i, dt in enumerate(dt_elements):
            dt_text = clean_text(dt.get_text())
            if i < len(dd_elements):
                dd_text = clean_text(dd_elements[i].get_text())
                
                if "powierzchnia" in dt_text.lower():
                    area_text = dd_text
                elif "pokoi" in dt_text.lower() or "pokój" in dt_text.lower():
                    rooms_text = dd_text
    
    # Fallback dla powierzchni
    if not area_text:
        area_elem = offer_element.select_one("span:contains('m²')")
        area_text = clean_text(area_elem.get_text()) if area_elem else ""
    
    # Sprawdź czy mamy podstawowe dane
    if not title and not url:
        return None
    
    listing = {
        "title": title,
        "price": price_data["price"],
        "price_currency": price_data["currency"],
        "price_original": price_data["original"],
        "location": location,
        "url": url,
        "area": area_text,
        "rooms": rooms_text,
        "description": "",
        "source": "otodom.pl"
    }
    
    return listing

if __name__ == "__main__":
    """Test scrapera"""
    print("🧪 TEST SCRAPERA OTODOM.PL")
    print("="*60)
    
    try:
        listings = get_otodom_listings(max_pages=2)
        
        if listings:
            print(f"✅ Pobrano {len(listings)} ogłoszeń")
            
            # Statystyki
            with_price = len([l for l in listings if l.get('price')])
            with_location = len([l for l in listings if l.get('location')])
            
            print(f"💰 Z cenami: {with_price}/{len(listings)}")
            print(f"📍 Z lokalizacją: {with_location}/{len(listings)}")
            
            # Przykład
            if listings:
                listing = listings[0]
                print(f"\n📋 PRZYKŁAD:")
                print(f"   Tytuł: {listing.get('title', '')[:50]}...")
                print(f"   Cena: {listing.get('price', 0):,} {listing.get('price_currency', 'zł')}")
                print(f"   Lokalizacja: {listing.get('location', '')}")
        else:
            print("❌ Nie pobrano żadnych ogłoszeń")
            
    except Exception as e:
        print(f"❌ Błąd: {e}") 