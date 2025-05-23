"""
Scraper dla Domiporta.pl z obsługą Selenium
"""
import logging
from typing import List, Dict
from utils import get_soup, random_delay, clean_text, extract_price
from datetime import datetime

logger = logging.getLogger(__name__)

def get_domiporta_listings(max_pages: int = 3) -> List[Dict]:
    """
    Pobiera ogłoszenia z Domiporta.pl używając Selenium
    
    Args:
        max_pages: Maksymalna liczba stron do przeskanowania
    
    Returns:
        List[Dict]: Lista ogłoszeń
    """
    listings = []
    base_url = "https://www.domiporta.pl/mieszkanie/sprzedam"
    
    for page in range(1, max_pages + 1):
        try:
            url = f"{base_url}?PageNumber={page}" if page > 1 else base_url
            logger.info(f"Scrapuję Domiporta.pl - strona {page} (Selenium)")
            
            # Używamy Selenium dla tego portalu
            soup = get_soup(url, use_selenium=True)
            
            # Zaktualizowane selektory dla Domiporta.pl
            offers = (soup.select("article.sneakpeak") or
                     soup.select(".property-item") or 
                     soup.select(".offer-item") or
                     soup.select("[data-testid='property-card']") or
                     soup.select(".listing-card") or
                     soup.select(".search-result"))
            
            if not offers:
                logger.warning(f"Nie znaleziono ogłoszeń na stronie {page}")
                # Sprawdź alternatywne struktury
                all_articles = soup.select("article")
                all_divs_with_sneakpeak = soup.select("div[class*='sneakpeak']")
                logger.info(f"Znaleziono {len(all_articles)} elementów article i {len(all_divs_with_sneakpeak)} divów z 'sneakpeak'")
                
                # Spróbuj ogólniejszych selektorów
                offers = soup.select("div[class*='sneakpeak']") or soup.select("div[class*='offer']")
                
                if not offers:
                    break
            
            logger.info(f"Znaleziono {len(offers)} ogłoszeń na stronie {page}")
            
            for offer in offers:
                try:
                    listing = parse_domiporta_listing(offer)
                    if listing:
                        listing["source"] = "domiporta.pl"
                        listing["scraped_at"] = datetime.now().isoformat()
                        listings.append(listing)
                except Exception as e:
                    logger.error(f"Błąd parsowania ogłoszenia Domiporta: {e}")
            
            random_delay()
            
        except Exception as e:
            logger.error(f"Błąd pobierania strony {page} z Domiporta.pl: {e}")
            
    logger.info(f"Pobrano {len(listings)} ogłoszeń z Domiporta.pl")
    return listings

def parse_domiporta_listing(offer_element) -> Dict:
    """
    Parsuje pojedyncze ogłoszenie z Domiporta.pl
    
    Args:
        offer_element: Element BeautifulSoup z ogłoszeniem
    
    Returns:
        Dict: Dane ogłoszenia
    """
    # Tytuł - różne możliwe selektory dla Domiporta
    title_elem = (offer_element.select_one(".sneakpeak__title a") or
                  offer_element.select_one("h2 a") or
                  offer_element.select_one("h3 a") or 
                  offer_element.select_one(".property-title") or
                  offer_element.select_one("[data-testid='property-title']") or
                  offer_element.select_one("a[title]"))
    
    title = ""
    if title_elem:
        title = clean_text(title_elem.get_text()) or title_elem.get("title", "")
    
    # Cena - Domiporta ma swoją strukturę cen
    price_elem = (offer_element.select_one(".sneakpeak__price") or
                  offer_element.select_one(".property-price") or
                  offer_element.select_one("[class*='price']") or
                  offer_element.select_one(".price") or
                  offer_element.select_one("[data-testid='price']"))
    
    price_text = clean_text(price_elem.get_text()) if price_elem else ""
    price_data = extract_price(price_text)
    
    # Lokalizacja
    location_elem = (offer_element.select_one(".sneakpeak__location") or
                     offer_element.select_one(".property-location") or
                     offer_element.select_one("[class*='location']") or
                     offer_element.select_one("[class*='address']") or
                     offer_element.select_one("[data-testid='location']"))
    location = clean_text(location_elem.get_text()) if location_elem else ""
    
    # Link
    link_elem = (offer_element.select_one("a[href*='/nieruchomosc/']") or
                 offer_element.select_one("a[href*='/mieszkanie/']") or
                 offer_element.select_one("a[href*='/oferta/']") or
                 offer_element.select_one("a"))
    
    url = ""
    if link_elem:
        url = link_elem.get("href", "")
        if url and not url.startswith("http"):
            url = f"https://www.domiporta.pl{url}"
    
    # Powierzchnia
    area_elem = (offer_element.select_one(".sneakpeak__details") or
                 offer_element.select_one("[class*='area']") or
                 offer_element.select_one("[class*='surface']") or
                 offer_element.select_one("span[class*='m2']") or
                 offer_element.select_one("[data-testid='area']"))
    
    # W Domiporta powierzchnia często jest w details razem z pokojami
    area_text = ""
    if area_elem:
        details_text = clean_text(area_elem.get_text())
        # Szukaj wzorca m2 w tekście
        import re
        area_match = re.search(r'(\d+(?:,\d+)?\s*m2)', details_text)
        area_text = area_match.group(1) if area_match else details_text
    
    # Liczba pokoi
    rooms_text = ""
    if area_elem:
        details_text = clean_text(area_elem.get_text())
        # Szukaj wzorca pokoi
        import re
        rooms_match = re.search(r'(\d+)\s*pok', details_text)
        rooms_text = rooms_match.group(1) if rooms_match else ""
    
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
        "description": "",  # Domiporta zwykle nie pokazuje opisu w liście
    }
    
    return listing 