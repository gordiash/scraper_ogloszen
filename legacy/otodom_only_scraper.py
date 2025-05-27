#!/usr/bin/env python3
"""
SCRAPER TYLKO DLA OTODOM.PL
Uproszczona wersja scrapująca wyłącznie Otodom.pl
"""
import logging
from typing import List, Dict
from utils import get_soup, random_delay, clean_text, extract_price

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_otodom_listings(max_pages: int = 5) -> List[Dict]:
    """
    Pobiera ogłoszenia TYLKO z Otodom.pl
    
    Args:
        max_pages: Maksymalna liczba stron do przeskanowania
    
    Returns:
        List[Dict]: Lista ogłoszeń
    """
    listings = []
    # URL z parametrem viewType=listing zgodnie z życzeniem
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
                    logger.error(f"❌ Błąd parsowania ogłoszenia {i+1}: {e}")
            
            random_delay()
            
        except Exception as e:
            logger.error(f"❌ Błąd pobierania strony {page}: {e}")
            
    logger.info(f"✅ Pobrano ŁĄCZNIE {len(listings)} ogłoszeń z Otodom.pl")
    return listings

def parse_otodom_listing(offer_element) -> Dict:
    """
    Parsuje pojedyncze ogłoszenie z Otodom.pl
    Używa zaktualizowanych selektorów CSS
    
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

def get_detailed_otodom_listing(url: str) -> Dict:
    """
    Pobiera szczegółowe informacje z pojedynczej strony ogłoszenia Otodom
    Używa selektorów podanych przez użytkownika dla stron szczegółów
    
    Args:
        url: URL ogłoszenia
    
    Returns:
        Dict: Szczegółowe dane ogłoszenia
    """
    try:
        logger.info(f"🔍 Pobieranie szczegółów: {url}")
        soup = get_soup(url, use_selenium=True)
        
        # CENA - selektory ze strony szczegółów
        price_elem = (soup.select_one("[data-cy='adPageHeaderPrice']") or
                      soup.select_one("[aria-label='Cena']") or
                      soup.select_one("[data-sentry-element='Price']") or
                      soup.select_one(".css-1o51x5a"))
        price_text = clean_text(price_elem.get_text()) if price_elem else ""
        price_data = extract_price(price_text)
        
        # LOKALIZACJA - selektory ze strony szczegółów
        location_elem = (soup.select_one("[data-sentry-component='MapLink'] a") or
                        soup.select_one(".css-1jjm9oe") or
                        soup.select_one("[href='#map']"))
        location = clean_text(location_elem.get_text()) if location_elem else ""
        
        # POKOJE - selektory ze strony szczegółów
        rooms_elem = None
        for item in soup.select("[data-sentry-source-file='AdDetailItem.tsx']"):
            if "Liczba pokoi" in item.get_text():
                rooms_elem = item.select_one("p:last-child")
                break
        rooms_text = clean_text(rooms_elem.get_text()) if rooms_elem else ""
        
        # OPIS - selektory ze strony szczegółów
        desc_elem = (soup.select_one("[data-cy='adPageAdDescription']") or
                     soup.select_one("[data-sentry-component='AdDescriptionBase']") or
                     soup.select_one(".css-i4vto6"))
        description = clean_text(desc_elem.get_text()) if desc_elem else ""
        
        # TYTUŁ
        title_elem = soup.select_one("h1")
        title = clean_text(title_elem.get_text()) if title_elem else ""
        
        # POWIERZCHNIA - selektory ze strony szczegółów
        area_text = ""
        for item in soup.select("[data-sentry-source-file='AdDetailItem.tsx']"):
            if "Powierzchnia" in item.get_text():
                area_elem = item.select_one("p.esen0m92:last-child")
                if area_elem:
                    area_text = clean_text(area_elem.get_text())
                break
        
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

if __name__ == "__main__":
    """Testuj scraper bezpośrednio"""
    print("="*80)
    print("🏠 SCRAPER TYLKO DLA OTODOM.PL")
    print("="*80)
    
    try:
        # Test podstawowy
        listings = get_otodom_listings(max_pages=2)
        
        if listings:
            print(f"\n✅ Pobrano {len(listings)} ogłoszeń z Otodom.pl")
            
            # Statystyki
            with_price = len([l for l in listings if l.get('price')])
            with_location = len([l for l in listings if l.get('location')])
            with_area = len([l for l in listings if l.get('area')])
            with_rooms = len([l for l in listings if l.get('rooms')])
            
            print(f"\n📊 JAKOŚĆ DANYCH:")
            print(f"   💰 Z cenami: {with_price}/{len(listings)} ({with_price/len(listings)*100:.1f}%)")
            print(f"   📍 Z lokalizacją: {with_location}/{len(listings)} ({with_location/len(listings)*100:.1f}%)")
            print(f"   📐 Z powierzchnią: {with_area}/{len(listings)} ({with_area/len(listings)*100:.1f}%)")
            print(f"   🚪 Z pokojami: {with_rooms}/{len(listings)} ({with_rooms/len(listings)*100:.1f}%)")
            
            # Przykłady
            print(f"\n📋 PRZYKŁADY OGŁOSZEŃ:")
            for i, listing in enumerate(listings[:3], 1):
                print(f"\n  {i}. {listing.get('title', 'Brak tytułu')[:60]}...")
                if listing.get('price'):
                    print(f"     💰 Cena: {listing['price']:,.0f} {listing.get('price_currency', 'zł')}")
                if listing.get('location'):
                    print(f"     📍 Lokalizacja: {listing.get('location')}")
                if listing.get('area'):
                    print(f"     📐 Powierzchnia: {listing.get('area')}")
                if listing.get('rooms'):
                    print(f"     🚪 Pokoje: {listing.get('rooms')}")
                if listing.get('url'):
                    print(f"     🔗 URL: {listing.get('url')[:60]}...")
            
            # Test szczegółów dla pierwszego ogłoszenia
            if listings and listings[0].get('url'):
                print(f"\n🔍 TEST SZCZEGÓŁÓW OGŁOSZENIA:")
                detailed = get_detailed_otodom_listing(listings[0]['url'])
                if detailed:
                    print(f"   ✅ Pobrano szczegółowe dane")
                    if detailed.get('description'):
                        desc = detailed.get('description', '')[:100]
                        print(f"   📖 Opis: {desc}...")
                else:
                    print(f"   ❌ Nie udało się pobrać szczegółów")
        else:
            print("❌ Nie pobrano żadnych ogłoszeń")
            
    except KeyboardInterrupt:
        print("\n⚠️ Przerwano przez użytkownika")
    except Exception as e:
        print(f"\n❌ Błąd: {e}")
        logger.error(f"Błąd w otodom_only_scraper: {e}", exc_info=True)
        
    print(f"\n{'='*80}")
    print("🎉 TEST ZAKOŃCZONY!")
    print("="*80) 