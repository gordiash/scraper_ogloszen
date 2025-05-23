"""
Scraper dla Otodom.pl
"""
import logging
from typing import List, Dict
from utils import get_soup, random_delay, clean_text, extract_price

logger = logging.getLogger(__name__)

def get_otodom_listings(max_pages: int = 3) -> List[Dict]:
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
            url = f"{base_url}?page={page}"
            logger.info(f"Scrapuję Otodom.pl - strona {page}")
            
            # Otodom często używa JS - może wymagać Selenium
            soup = get_soup(url, use_selenium=True)
            
            # Selektory dla Otodom (mogą się zmieniać)
            offers = (soup.select("[data-cy='listing-item']") or 
                     soup.select(".es62z2j0") or 
                     soup.select(".listing-item"))
            
            if not offers:
                logger.warning(f"Nie znaleziono ogłoszeń na stronie {page}")
                break
            
            for offer in offers:
                try:
                    listing = parse_otodom_listing(offer)
                    if listing:
                        listing["source"] = "otodom.pl"
                        listing["source_page"] = page
                        listings.append(listing)
                except Exception as e:
                    logger.error(f"Błąd parsowania ogłoszenia Otodom: {e}")
            
            random_delay()
            
        except Exception as e:
            logger.error(f"Błąd pobierania strony {page} z Otodom.pl: {e}")
            
    logger.info(f"Pobrano {len(listings)} ogłoszeń z Otodom.pl")
    return listings

def parse_otodom_listing(offer_element) -> Dict:
    """
    Parsuje pojedyncze ogłoszenie z Otodom.pl
    
    Args:
        offer_element: Element BeautifulSoup z ogłoszeniem
    
    Returns:
        Dict: Dane ogłoszenia
    """
    # Tytuł
    title_elem = (offer_element.select_one("[data-cy='listing-item-title']") or
                  offer_element.select_one(".e1nbpvi60") or
                  offer_element.select_one("h3"))
    title = clean_text(title_elem.get_text()) if title_elem else ""
    
    # Cena
    price_elem = (offer_element.select_one("[data-cy='listing-item-price']") or
                  offer_element.select_one(".e1l1avn10") or
                  offer_element.select_one(".price"))
    price_text = clean_text(price_elem.get_text()) if price_elem else ""
    price_data = extract_price(price_text)
    
    # Lokalizacja
    location_elem = (offer_element.select_one("[data-cy='listing-item-location']") or
                     offer_element.select_one(".e1nbpvi61") or
                     offer_element.select_one(".location"))
    location = clean_text(location_elem.get_text()) if location_elem else ""
    
    # Link
    link_elem = offer_element.select_one("a")
    url = link_elem.get("href") if link_elem else ""
    if url and not url.startswith("http"):
        url = f"https://www.otodom.pl{url}"
    
    # Powierzchnia
    area_elem = offer_element.select_one("[data-cy='listing-item-area']")
    area_text = clean_text(area_elem.get_text()) if area_elem else ""
    
    # Liczba pokoi
    rooms_elem = offer_element.select_one("[data-cy='listing-item-rooms']")
    rooms_text = clean_text(rooms_elem.get_text()) if rooms_elem else ""
    
    # Opis (skrócony)
    desc_elem = offer_element.select_one(".listing-item-description")
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