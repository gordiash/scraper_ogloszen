"""
Scraper dla Metrohouse.pl
"""
import logging
from typing import List, Dict
from utils import get_soup, random_delay, clean_text, extract_price

logger = logging.getLogger(__name__)

def get_metrohouse_listings(max_pages: int = 3) -> List[Dict]:
    """
    Pobiera ogłoszenia z Metrohouse.pl
    
    Args:
        max_pages: Maksymalna liczba stron do przeskanowania
    
    Returns:
        List[Dict]: Lista ogłoszeń
    """
    listings = []
    base_url = "https://metrohouse.pl/mieszkania-sprzedaz"
    
    for page in range(1, max_pages + 1):
        try:
            url = f"{base_url}?page={page}"
            logger.info(f"Scrapuję Metrohouse.pl - strona {page}")
            
            soup = get_soup(url)
            
            # Selektory dla Metrohouse
            offers = (soup.select(".property-item") or 
                     soup.select(".offer-item") or 
                     soup.select(".listing-item"))
            
            if not offers:
                logger.warning(f"Nie znaleziono ogłoszeń na stronie {page}")
                break
            
            for offer in offers:
                try:
                    listing = parse_metrohouse_listing(offer)
                    if listing:
                        listing["source"] = "metrohouse.pl"
                        listing["source_page"] = page
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
    # Tytuł
    title_elem = (offer_element.select_one(".property-title") or
                  offer_element.select_one(".offer-title") or
                  offer_element.select_one("h2") or
                  offer_element.select_one("h3"))
    title = clean_text(title_elem.get_text()) if title_elem else ""
    
    # Cena
    price_elem = (offer_element.select_one(".property-price") or
                  offer_element.select_one(".offer-price") or
                  offer_element.select_one(".price"))
    price_text = clean_text(price_elem.get_text()) if price_elem else ""
    price_data = extract_price(price_text)
    
    # Lokalizacja
    location_elem = (offer_element.select_one(".property-location") or
                     offer_element.select_one(".offer-location") or
                     offer_element.select_one(".location"))
    location = clean_text(location_elem.get_text()) if location_elem else ""
    
    # Link
    link_elem = offer_element.select_one("a")
    url = link_elem.get("href") if link_elem else ""
    if url and not url.startswith("http"):
        url = f"https://metrohouse.pl{url}"
    
    # Powierzchnia
    area_elem = (offer_element.select_one(".property-area") or
                 offer_element.select_one(".area"))
    area_text = clean_text(area_elem.get_text()) if area_elem else ""
    
    # Liczba pokoi
    rooms_elem = (offer_element.select_one(".property-rooms") or
                  offer_element.select_one(".rooms"))
    rooms_text = clean_text(rooms_elem.get_text()) if rooms_elem else ""
    
    # Opis (skrócony)
    desc_elem = offer_element.select_one(".property-description")
    description = clean_text(desc_elem.get_text()) if desc_elem else ""
    
    listing = {
        "title": title,
        "price": price_data["price"],
        "price_currency": price_data["currency"],
        "price_original": price_data["original"],
        "location": location,
        "url": url,
        "area": area_text,
        "rooms": rooms_text,
        "description": description,
    }
    
    return listing if title and url else None 