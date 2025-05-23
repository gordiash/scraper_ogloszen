"""
Scraper dla OLX.pl/nieruchomosci
"""
import logging
from typing import List, Dict
from utils import get_soup, random_delay, clean_text, extract_price

logger = logging.getLogger(__name__)

def get_olx_listings(max_pages: int = 3) -> List[Dict]:
    """
    Pobiera ogłoszenia z OLX.pl/nieruchomosci
    
    Args:
        max_pages: Maksymalna liczba stron do przeskanowania
    
    Returns:
        List[Dict]: Lista ogłoszeń
    """
    listings = []
    base_url = "https://www.olx.pl/nieruchomosci/mieszkania/sprzedaz"
    
    for page in range(1, max_pages + 1):
        try:
            url = f"{base_url}/?page={page}"
            logger.info(f"Scrapuję OLX.pl - strona {page}")
            
            # OLX może wymagać Selenium ze względu na JS
            soup = get_soup(url, use_selenium=False)
            
            # Selektory dla OLX (często się zmieniają)
            offers = (soup.select("[data-cy='l-card']") or 
                     soup.select(".offer-wrapper") or 
                     soup.select(".listing-item"))
            
            if not offers:
                logger.warning(f"Nie znaleziono ogłoszeń na stronie {page}")
                break
            
            for offer in offers:
                try:
                    listing = parse_olx_listing(offer)
                    if listing:
                        listing["source"] = "olx.pl"
                        listing["source_page"] = page
                        listings.append(listing)
                except Exception as e:
                    logger.error(f"Błąd parsowania ogłoszenia OLX: {e}")
            
            random_delay()
            
        except Exception as e:
            logger.error(f"Błąd pobierania strony {page} z OLX.pl: {e}")
            
    logger.info(f"Pobrano {len(listings)} ogłoszeń z OLX.pl")
    return listings

def parse_olx_listing(offer_element) -> Dict:
    """
    Parsuje pojedyncze ogłoszenie z OLX.pl
    
    Args:
        offer_element: Element BeautifulSoup z ogłoszeniem
    
    Returns:
        Dict: Dane ogłoszenia
    """
    # Tytuł
    title_elem = (offer_element.select_one("[data-cy='listing-ad-title']") or
                  offer_element.select_one(".offer-titlebox h3") or
                  offer_element.select_one("h3") or
                  offer_element.select_one("h2"))
    title = clean_text(title_elem.get_text()) if title_elem else ""
    
    # Cena
    price_elem = (offer_element.select_one("p[data-testid='ad-price']") or
                  offer_element.select_one(".price") or
                  offer_element.select_one(".offer-price"))
    price_text = clean_text(price_elem.get_text()) if price_elem else ""
    price_data = extract_price(price_text)
    
    # Lokalizacja
    location_elem = (offer_element.select_one("p[data-testid='location-date']") or
                     offer_element.select_one(".offer-titlebox .breadcrumb") or
                     offer_element.select_one(".location"))
    location = clean_text(location_elem.get_text()) if location_elem else ""
    
    # Link
    link_elem = offer_element.select_one("a")
    url = link_elem.get("href") if link_elem else ""
    if url and not url.startswith("http"):
        url = f"https://www.olx.pl{url}"
    
    # Parametry (powierzchnia, pokoje) - OLX ma różne podejścia
    params_elem = offer_element.select(".param")
    area_text = ""
    rooms_text = ""
    
    for param in params_elem:
        param_text = clean_text(param.get_text())
        if "m²" in param_text:
            area_text = param_text
        elif "pokoje" in param_text or "pokój" in param_text:
            rooms_text = param_text
    
    # Opis (skrócony)
    desc_elem = offer_element.select_one(".offer-item-description")
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