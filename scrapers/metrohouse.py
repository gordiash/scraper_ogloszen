"""
Scraper dla Metrohouse.pl z obsługą Selenium
"""
import logging
from typing import List, Dict
from utils import get_soup, random_delay, clean_text, extract_price
from datetime import datetime

logger = logging.getLogger(__name__)

def get_metrohouse_listings(max_pages: int = 3) -> List[Dict]:
    """
    Pobiera ogłoszenia z Metrohouse.pl używając Selenium
    
    Args:
        max_pages: Maksymalna liczba stron do przeskanowania
    
    Returns:
        List[Dict]: Lista ogłoszeń
    """
    listings = []
    # Metrohouse używa innej struktury URL
    base_url = "https://metrohouse.pl/na-sprzedaz/mieszkanie/-/rynek-wtorny"
    
    for page in range(1, max_pages + 1):
        try:
            url = f"{base_url}?page={page}" if page > 1 else base_url
            logger.info(f"Scrapuję Metrohouse.pl - strona {page} (Selenium)")
            
            # Używamy Selenium dla tego portalu
            soup = get_soup(url, use_selenium=True)
            
            # Zaktualizowane selektory dla Metrohouse.pl - używamy "item" które znaleziono
            offers = (soup.select(".item-box") or
                     soup.select("[class*='item']") or
                     soup.select(".property-list-item") or
                     soup.select("article.property-item") or 
                     soup.select(".offer-box") or
                     soup.select("[data-testid='property-card']") or
                     soup.select(".listing-card") or
                     soup.select(".property-card"))
            
            if not offers:
                logger.warning(f"Nie znaleziono ogłoszeń na stronie {page}")
                # Sprawdź alternatywne struktury
                all_items = soup.select("[class*='item']")
                all_divs_with_property = soup.select("div[class*='property']")
                logger.info(f"Znaleziono {len(all_items)} elementów z 'item' i {len(all_divs_with_property)} divów z 'property'")
                
                # Spróbuj ogólniejszych selektorów
                offers = all_items or soup.select("div[class*='property']") or soup.select("div[class*='offer']")
                
                if not offers:
                    break
            
            logger.info(f"Znaleziono {len(offers)} ogłoszeń na stronie {page}")
            
            for offer in offers:
                try:
                    listing = parse_metrohouse_listing(offer)
                    if listing:
                        listing["source"] = "metrohouse.pl"
                        listing["scraped_at"] = datetime.now().isoformat()
                        listings.append(listing)
                except Exception as e:
                    logger.error(f"Błąd parsowania ogłoszenia Metrohouse: {e}")
            
            random_delay()
            
        except Exception as e:
            logger.error(f"Błąd pobierania strony {page} z Metrohouse.pl: {e}")
            
    logger.info(f"Pobrano {len(listings)} ogłoszeń z Metrohouse.pl")
    return listings

def parse_metrohouse_listing(offer_element) -> Dict:
    """
    Parsuje pojedyncze ogłoszenie z Metrohouse.pl
    
    Args:
        offer_element: Element BeautifulSoup z ogłoszeniem
    
    Returns:
        Dict: Dane ogłoszenia
    """
    # Tytuł - różne możliwe selektory dla Metrohouse
    title_elem = (offer_element.select_one(".property-title") or
                  offer_element.select_one("h2") or 
                  offer_element.select_one("h3") or
                  offer_element.select_one(".offer-title") or
                  offer_element.select_one("[data-testid='property-title']") or
                  offer_element.select_one("a[title]"))
    
    title = ""
    if title_elem:
        title = clean_text(title_elem.get_text()) or title_elem.get("title", "")
    
    # Cena - Metrohouse ma swoją strukturę cen
    price_elem = (offer_element.select_one(".property-price") or
                  offer_element.select_one(".offer-price") or
                  offer_element.select_one("[class*='price']") or
                  offer_element.select_one(".price") or
                  offer_element.select_one("[data-testid='price']"))
    
    price_text = clean_text(price_elem.get_text()) if price_elem else ""
    price_data = extract_price(price_text)
    
    # Lokalizacja
    location_elem = (offer_element.select_one(".property-location") or
                     offer_element.select_one(".offer-location") or
                     offer_element.select_one("[class*='location']") or
                     offer_element.select_one("[class*='address']") or
                     offer_element.select_one("[data-testid='location']"))
    location = clean_text(location_elem.get_text()) if location_elem else ""
    
    # Link
    link_elem = (offer_element.select_one("a[href*='/mieszkanie/']") or
                 offer_element.select_one("a[href*='/oferta/']") or
                 offer_element.select_one("a[href*='/sprzedaz/']") or
                 offer_element.select_one("a"))
    
    url = ""
    if link_elem:
        url = link_elem.get("href", "")
        if url and not url.startswith("http"):
            url = f"https://metrohouse.pl{url}"
    
    # Powierzchnia
    area_elem = (offer_element.select_one(".property-area") or
                 offer_element.select_one("[class*='area']") or
                 offer_element.select_one("[class*='surface']") or
                 offer_element.select_one("span[class*='m2']") or
                 offer_element.select_one("[data-testid='area']"))
    area_text = clean_text(area_elem.get_text()) if area_elem else ""
    
    # Liczba pokoi
    rooms_elem = (offer_element.select_one(".property-rooms") or
                  offer_element.select_one("[class*='room']") or
                  offer_element.select_one("[class*='bedroom']") or
                  offer_element.select_one("[data-testid='rooms']"))
    rooms_text = clean_text(rooms_elem.get_text()) if rooms_elem else ""
    
    # Podstawowe walidacje
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
        "description": "",  # Metrohouse zwykle nie pokazuje opisu w liście
    }
    
    return listing 