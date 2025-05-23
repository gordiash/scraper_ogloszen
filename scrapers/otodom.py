"""
Scraper dla Otodom.pl (ZAKTUALIZOWANY)
Używa aktualnych selektorów CSS z grudnia 2024
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
            logger.info(f"🏠 Scrapuję Otodom.pl - strona {page}")
            
            # Otodom wymaga Selenium ze względu na nowoczesny JS
            soup = get_soup(url, use_selenium=True)
            
            # Nowe selektory dla Otodom (aktualne na grudzień 2024)
            offers = (soup.select("[data-cy='listing-item']") or 
                     soup.select(".es62z2j0") or 
                     soup.select("[data-testid='listing-item']") or
                     soup.select("article") or
                     soup.select(".listing-item"))
            
            if not offers:
                logger.warning(f"⚠️ Nie znaleziono ogłoszeń na stronie {page}")
                # Sprawdź czy strona się załadowała
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
                    logger.error(f"❌ Błąd parsowania ogłoszenia {i+1} z Otodom: {e}")
            
            random_delay()
            
        except Exception as e:
            logger.error(f"❌ Błąd pobierania strony {page} z Otodom.pl: {e}")
            
    logger.info(f"✅ Pobrano {len(listings)} ogłoszeń z Otodom.pl")
    return listings

def parse_otodom_listing(offer_element) -> Dict:
    """
    Parsuje pojedyncze ogłoszenie z Otodom.pl (ZAKTUALIZOWANE SELEKTORY)
    Na podstawie rzeczywistej struktury HTML ze strony listy
    
    Args:
        offer_element: Element BeautifulSoup z ogłoszeniem
    
    Returns:
        Dict: Dane ogłoszenia
    """
    # TYTUŁ - RZECZYWISTY SELEKTOR z HTML
    title_elem = (offer_element.select_one("[data-cy='listing-item-title']") or
                  offer_element.select_one("p.css-u3orbr") or
                  offer_element.select_one("h3") or
                  offer_element.select_one("h2"))
    title = clean_text(title_elem.get_text()) if title_elem else ""
    
    # CENA - RZECZYWISTY SELEKTOR z HTML
    price_elem = (offer_element.select_one("span.css-2bt9f1") or
                  offer_element.select_one("[data-sentry-element='Content']") or
                  offer_element.select_one("[data-cy='listing-item-price']") or
                  offer_element.select_one("[data-cy*='price']"))
    price_text = clean_text(price_elem.get_text()) if price_elem else ""
    price_data = extract_price(price_text)
    
    # LOKALIZACJA - RZECZYWISTY SELEKTOR z HTML
    location_elem = (offer_element.select_one("p.css-42r2ms") or
                     offer_element.select_one("[data-sentry-element='StyledParagraph']") or
                     offer_element.select_one("[data-cy='listing-item-location']"))
    location = clean_text(location_elem.get_text()) if location_elem else ""
    
    # Link do pełnego ogłoszenia
    link_elem = (offer_element.select_one("[data-cy='listing-item-link']") or
                 offer_element.select_one("a[href*='/oferta/']") or
                 offer_element.select_one("a"))
    url = link_elem.get("href") if link_elem else ""
    if url and not url.startswith("http"):
        url = f"https://www.otodom.pl{url}"
    
    # POWIERZCHNIA I POKOJE - RZECZYWISTE SELEKTORY z <dl> struktury
    area_text = ""
    rooms_text = ""
    
    # Szukaj w <dl> strukturze
    specs_list = offer_element.select_one("dl.css-9q2yy4")
    if specs_list:
        # Znajdź wszystkie pary dt/dd
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
    
    # Fallback selektory
    if not area_text:
        area_elem = offer_element.select_one("[title*='m²']")
        area_text = clean_text(area_elem.get_text()) if area_elem else ""
    
    if not rooms_text:
        rooms_elem = offer_element.select_one("[data-cy='listing-item-rooms']")
        rooms_text = clean_text(rooms_elem.get_text()) if rooms_elem else ""
    
    # Opis (skrócony z listing page)
    desc_elem = offer_element.select_one("[data-cy='listing-item-description']")
    description = clean_text(desc_elem.get_text()) if desc_elem else ""
    
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
        "description": description,
    }
    
    return listing

def get_detailed_otodom_listing(url: str) -> Dict:
    """
    Pobiera szczegółowe informacje z pojedynczej strony ogłoszenia Otodom
    Używa NOWYCH SELEKTORÓW podanych przez użytkownika
    
    Args:
        url: URL ogłoszenia
    
    Returns:
        Dict: Szczegółowe dane ogłoszenia
    """
    try:
        logger.info(f"🔍 Pobieranie szczegółów ogłoszenia: {url}")
        soup = get_soup(url, use_selenium=True)
        
        # CENA - NOWY SELEKTOR
        price_elem = (soup.select_one("[data-cy='adPageHeaderPrice']") or
                      soup.select_one("[aria-label='Cena']") or
                      soup.select_one("[data-sentry-element='Price']") or
                      soup.select_one(".css-1o51x5a"))
        price_text = clean_text(price_elem.get_text()) if price_elem else ""
        price_data = extract_price(price_text)
        
        # LOKALIZACJA - NOWY SELEKTOR  
        location_elem = (soup.select_one("[data-sentry-component='MapLink'] a") or
                        soup.select_one(".css-1jjm9oe") or
                        soup.select_one("[href='#map']"))
        location = clean_text(location_elem.get_text()) if location_elem else ""
        
        # POKOJE - NOWY SELEKTOR
        rooms_elem = None
        # Szukaj sekcji z "Liczba pokoi"
        for item in soup.select("[data-sentry-source-file='AdDetailItem.tsx']"):
            if "Liczba pokoi" in item.get_text():
                rooms_elem = item.select_one("p:last-child")
                break
        
        if not rooms_elem:
            rooms_elem = soup.select_one(".esen0m92:contains('pokoi') + .esen0m92")
        
        rooms_text = clean_text(rooms_elem.get_text()) if rooms_elem else ""
        
        # OPIS - NOWY SELEKTOR
        desc_elem = (soup.select_one("[data-cy='adPageAdDescription']") or
                     soup.select_one("[data-sentry-component='AdDescriptionBase']") or
                     soup.select_one(".css-i4vto6"))
        description = clean_text(desc_elem.get_text()) if desc_elem else ""
        
        # TYTUŁ
        title_elem = soup.select_one("h1")
        title = clean_text(title_elem.get_text()) if title_elem else ""
        
        # POWIERZCHNIA - ZAKTUALIZOWANY SELEKTOR
        area_text = ""
        # Szukaj sekcji z "Powierzchnia" używając nowych selektorów
        for item in soup.select("[data-sentry-source-file='AdDetailItem.tsx']"):
            if "Powierzchnia" in item.get_text():
                area_elem = item.select_one("p.esen0m92:last-child")
                if area_elem:
                    area_text = clean_text(area_elem.get_text())
                break
        
        # Fallback selektory
        if not area_text:
            area_elem = (soup.select_one(".esen0m92:contains('m²')") or
                        soup.select_one("[title*='m²']"))
            if area_elem:
                area_text = clean_text(area_elem.get_text())
        
        return {
            "title": title,
            "price": price_data["price"],
            "price_currency": price_data["currency"],
            "price_original": price_data["original"],
            "location": location,
            "url": url,
            "area": area_text,
            "rooms": rooms_text,
            "description": description,
            "source": "otodom.pl"
        }
        
    except Exception as e:
        logger.error(f"❌ Błąd pobierania szczegółów z {url}: {e}")
        return {} 