"""
Scraper dla Gratka.pl z obsługą Selenium
"""
import logging
from typing import List, Dict
from utils import get_soup, random_delay, clean_text, extract_price
from datetime import datetime

logger = logging.getLogger(__name__)

def get_gratka_listings(max_pages: int = 3) -> List[Dict]:
    """
    Pobiera ogłoszenia z Gratka.pl używając Selenium
    
    Args:
        max_pages: Maksymalna liczba stron do przeskanowania
    
    Returns:
        List[Dict]: Lista ogłoszeń
    """
    listings = []
    base_url = "https://gratka.pl/nieruchomosci/mieszkania/sprzedaz"
    
    for page in range(1, max_pages + 1):
        try:
            url = f"{base_url}?page={page}" if page > 1 else base_url
            logger.info(f"Scrapuję Gratka.pl - strona {page} (Selenium)")
            
            # Używamy Selenium dla tego portalu
            soup = get_soup(url, use_selenium=True)
            
            # Zaktualizowane selektory dla Gratka.pl - używamy "card" które zostały znalezione
            offers = (soup.select(".card") or
                     soup.select("article[data-testid='listing-item']") or
                     soup.select(".listing-item") or 
                     soup.select(".offer-item") or
                     soup.select("article.teaser") or
                     soup.select("[data-testid='property-item']") or
                     soup.select(".property-card"))
            
            if not offers:
                logger.warning(f"Nie znaleziono ogłoszeń na stronie {page}")
                # Sprawdź alternatywne struktury
                all_cards = soup.select("[class*='card']")
                all_divs_with_listing = soup.select("div[class*='listing']")
                logger.info(f"Znaleziono {len(all_cards)} elementów z 'card' i {len(all_divs_with_listing)} divów z 'listing'")
                
                # Spróbuj ogólniejszych selektorów
                offers = all_cards or soup.select("div[class*='listing']") or soup.select("div[class*='offer']")
                
                if not offers:
                    break
            
            logger.info(f"Znaleziono {len(offers)} ogłoszeń na stronie {page}")
            
            for offer in offers:
                try:
                    listing = parse_gratka_listing(offer)
                    if listing:
                        listing["source"] = "gratka.pl"
                        listing["scraped_at"] = datetime.now().isoformat()
                        listings.append(listing)
                except Exception as e:
                    logger.error(f"Błąd parsowania ogłoszenia Gratka: {e}")
            
            random_delay()
            
        except Exception as e:
            logger.error(f"Błąd pobierania strony {page} z Gratka.pl: {e}")
            
    logger.info(f"Pobrano {len(listings)} ogłoszeń z Gratka.pl")
    return listings

def parse_gratka_listing(offer_element) -> Dict:
    """
    Parsuje pojedyncze ogłoszenie z Gratka.pl
    
    Args:
        offer_element: Element BeautifulSoup z ogłoszeniem
    
    Returns:
        Dict: Dane ogłoszenia
    """
    # Tytuł - różne możliwe selektory dla Gratka
    title_elem = (offer_element.select_one("h2 a") or
                  offer_element.select_one(".listing-title") or 
                  offer_element.select_one("h3") or
                  offer_element.select_one("h2") or
                  offer_element.select_one("[data-testid='listing-title']") or
                  offer_element.select_one("a[title]"))
    
    title = ""
    if title_elem:
        title = clean_text(title_elem.get_text()) or title_elem.get("title", "")
    
    # Cena - Gratka ma specyficzną strukturę cen
    price_elem = (offer_element.select_one("[data-testid='listing-price']") or
                  offer_element.select_one(".listing-price") or
                  offer_element.select_one("[class*='price']") or
                  offer_element.select_one(".price") or
                  offer_element.select_one("span[class*='amount']"))
    
    price_text = clean_text(price_elem.get_text()) if price_elem else ""
    price_data = extract_price(price_text)
    
    # Lokalizacja
    location_elem = (offer_element.select_one("[data-testid='listing-location']") or
                     offer_element.select_one(".listing-location") or
                     offer_element.select_one("[class*='location']") or
                     offer_element.select_one("[class*='address']"))
    location = clean_text(location_elem.get_text()) if location_elem else ""
    
    # Link
    link_elem = (offer_element.select_one("a[href*='/nieruchomosci/']") or
                 offer_element.select_one("a[href*='/mieszkanie/']") or
                 offer_element.select_one("a"))
    
    url = ""
    if link_elem:
        url = link_elem.get("href", "")
        if url and not url.startswith("http"):
            url = f"https://gratka.pl{url}"
    
    # Powierzchnia
    area_elem = (offer_element.select_one("[data-testid='listing-area']") or
                 offer_element.select_one("[class*='area']") or
                 offer_element.select_one("[class*='surface']") or
                 offer_element.select_one("span[class*='m2']"))
    area_text = clean_text(area_elem.get_text()) if area_elem else ""
    
    # Liczba pokoi
    rooms_elem = (offer_element.select_one("[data-testid='listing-rooms']") or
                  offer_element.select_one("[class*='room']") or
                  offer_element.select_one("[class*='bedroom']"))
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
        "description": "",  # Gratka zwykle nie pokazuje opisu w liście
    }
    
    return listing 