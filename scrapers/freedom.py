"""
Scraper dla Freedom.pl z obsługą Selenium
"""
import logging
from typing import List, Dict
from utils import get_soup, random_delay, clean_text, extract_price
from datetime import datetime

logger = logging.getLogger(__name__)

def get_freedom_listings(max_pages: int = 3) -> List[Dict]:
    """
    Pobiera ogłoszenia z Freedom.pl używając Selenium
    
    Args:
        max_pages: Maksymalna liczba stron do przeskanowania
    
    Returns:
        List[Dict]: Lista ogłoszeń
    """
    listings = []
    # Używamy search URL z filtrami sprzedaży mieszkań
    base_url = "https://freedom.pl/nieruchomosci/?action=search&type_nier=mieszkanie&tr_type=sprzedaz"
    
    for page in range(1, max_pages + 1):
        try:
            url = f"{base_url}&page={page}" if page > 1 else base_url
            logger.info(f"Scrapuję Freedom.pl - strona {page} (Selenium)")
            
            # Używamy Selenium dla tego portalu
            soup = get_soup(url, use_selenium=True)
            
            # Freedom.pl używa klas z "offert"
            offers = (soup.select(".offert-box") or 
                     soup.select(".offert") or
                     soup.select("[class*='offert']") or
                     soup.select(".property-item") or 
                     soup.select("article"))
            
            if not offers:
                logger.warning(f"Nie znaleziono ogłoszeń na stronie {page}")
                # Debug informacje
                offert_divs = soup.select("div[class*='offert']")
                all_offerts = soup.select("[class*='offert']")
                logger.info(f"Znaleziono {len(offert_divs)} divów z 'offert' i {len(all_offerts)} elementów z 'offert'")
                
                # Spróbuj fallback
                offers = all_offerts
                
                if not offers:
                    break
            
            logger.info(f"Znaleziono {len(offers)} potencjalnych ogłoszeń na stronie {page}")
            
            for offer in offers:
                try:
                    listing = parse_freedom_listing(offer)
                    if listing:
                        listing["source"] = "freedom.pl"
                        listing["scraped_at"] = datetime.now().isoformat()
                        listings.append(listing)
                except Exception as e:
                    logger.error(f"Błąd parsowania ogłoszenia Freedom: {e}")
            
            random_delay()
            
        except Exception as e:
            logger.error(f"Błąd pobierania strony {page} z Freedom.pl: {e}")
            
    logger.info(f"Pobrano {len(listings)} ogłoszeń z Freedom.pl")
    return listings

def parse_freedom_listing(offer_element) -> Dict:
    """
    Parsuje pojedyncze ogłoszenie z Freedom.pl
    
    Args:
        offer_element: Element BeautifulSoup z ogłoszeniem
    
    Returns:
        Dict: Dane ogłoszenia
    """
    # Tytuł - Freedom używa specyficznej struktury
    title_elem = (offer_element.select_one(".offert-title") or
                  offer_element.select_one(".title") or
                  offer_element.select_one("h2") or 
                  offer_element.select_one("h3") or
                  offer_element.select_one("a[title]"))
    
    title = ""
    if title_elem:
        title = clean_text(title_elem.get_text()) or title_elem.get("title", "")
    
    # Cena - Freedom ma klasy z "price"
    price_elem = (offer_element.select_one(".offert-price") or
                  offer_element.select_one(".price") or
                  offer_element.select_one("[class*='price']") or
                  offer_element.select_one("[class*='cena']"))
    
    price_text = clean_text(price_elem.get_text()) if price_elem else ""
    price_data = extract_price(price_text)
    
    # Lokalizacja
    location_elem = (offer_element.select_one(".offert-location") or
                     offer_element.select_one(".location") or
                     offer_element.select_one("[class*='location']") or
                     offer_element.select_one("[class*='address']"))
    location = clean_text(location_elem.get_text()) if location_elem else ""
    
    # Link - Freedom ma specyficzne URLe
    link_elem = (offer_element.select_one("a[href*='/nieruchomosc/']") or
                 offer_element.select_one("a[href*='/mieszkanie/']") or
                 offer_element.select_one("a[href*='/oferta/']") or
                 offer_element.select_one("a"))
    
    url = ""
    if link_elem:
        url = link_elem.get("href", "")
        if url and not url.startswith("http"):
            url = f"https://freedom.pl{url}"
    
    # Powierzchnia - może być w details
    area_elem = (offer_element.select_one(".offert-area") or
                 offer_element.select_one("[class*='area']") or
                 offer_element.select_one("[class*='surface']") or
                 offer_element.select_one("span[class*='m2']"))
    
    area_text = ""
    if area_elem:
        area_text = clean_text(area_elem.get_text())
    else:
        # Szukaj wzorca m2 w całym tekście elementu
        full_text = clean_text(offer_element.get_text())
        import re
        area_match = re.search(r'(\d+(?:,\d+)?\s*m2)', full_text)
        area_text = area_match.group(1) if area_match else ""
    
    # Liczba pokoi
    rooms_elem = (offer_element.select_one(".offert-rooms") or
                  offer_element.select_one("[class*='room']") or
                  offer_element.select_one("[class*='bedroom']"))
    
    rooms_text = ""
    if rooms_elem:
        rooms_text = clean_text(rooms_elem.get_text())
    else:
        # Szukaj wzorca pokoi w tekście
        full_text = clean_text(offer_element.get_text())
        import re
        rooms_match = re.search(r'(\d+)\s*pok', full_text)
        rooms_text = rooms_match.group(1) if rooms_match else ""
    
    # Podstawowe walidacje - chcemy przynajmniej tytuł lub cenę
    if not title and not price_data.get("price"):
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
    }
    
    return listing 