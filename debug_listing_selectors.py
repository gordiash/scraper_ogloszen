#!/usr/bin/env python3
"""
DEBUG SELEKTORÓW NA STRONACH LIST OGŁOSZEŃ
Analizuje rzeczywiste selektory CSS na stronach wyników wyszukiwania
"""
import logging
from utils import get_soup

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_otodom_listing_page():
    """Debug selektorów na stronie listy Otodom.pl"""
    print("="*80)
    print("🔍 DEBUG SELEKTORÓW - OTODOM.PL LISTA OGŁOSZEŃ")
    print("="*80)
    
    try:
        url = "https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/cala-polska?page=1"
        print(f"🌐 Analizuję: {url}")
        
        soup = get_soup(url, use_selenium=True)
        
        # Znajdź kontener ogłoszeń
        offers = soup.select("[data-cy='listing-item']")
        print(f"\n📋 Znaleziono {len(offers)} ogłoszeń")
        
        if offers:
            # Analizuj pierwsze ogłoszenie
            first_offer = offers[0]
            print(f"\n🎯 ANALIZA PIERWSZEGO OGŁOSZENIA:")
            print("="*50)
            
            # Zapisz HTML pierwszego ogłoszenia do pliku
            with open("debug_first_offer_otodom.html", "w", encoding="utf-8") as f:
                f.write(str(first_offer))
            print(f"💾 Zapisano HTML do: debug_first_offer_otodom.html")
            
            # Szukaj wszystkich możliwych selektorów cen
            print(f"\n💰 POTENCJALNE SELEKTORY CEN:")
            price_selectors = [
                "[data-cy*='price']",
                "[class*='price']",
                "[data-testid*='price']",
                "span:contains('zł')",
                "div:contains('zł')",
                "p:contains('zł')",
            ]
            
            for selector in price_selectors:
                try:
                    elements = first_offer.select(selector)
                    if elements:
                        print(f"   ✅ {selector}: {len(elements)} elementów")
                        for i, elem in enumerate(elements[:2]):
                            text = elem.get_text()[:50]
                            print(f"      {i+1}. '{text}...'")
                except Exception as e:
                    print(f"   ❌ {selector}: błąd - {e}")
            
            # Szukaj wszystkich możliwych selektorów lokalizacji
            print(f"\n📍 POTENCJALNE SELEKTORY LOKALIZACJI:")
            location_selectors = [
                "[data-cy*='location']",
                "[class*='location']",
                "[data-testid*='location']",
                "span:contains(',')",
                "div:contains(',')",
                "p:contains(',')",
            ]
            
            for selector in location_selectors:
                try:
                    elements = first_offer.select(selector)
                    if elements:
                        print(f"   ✅ {selector}: {len(elements)} elementów")
                        for i, elem in enumerate(elements[:2]):
                            text = elem.get_text()[:50]
                            print(f"      {i+1}. '{text}...'")
                except Exception as e:
                    print(f"   ❌ {selector}: błąd - {e}")
            
            # Szukaj wszystkich możliwych selektorów powierzchni
            print(f"\n📐 POTENCJALNE SELEKTORY POWIERZCHNI:")
            area_selectors = [
                "[data-cy*='area']",
                "[class*='area']",
                "[data-testid*='area']",
                "span:contains('m²')",
                "div:contains('m²')",
                "p:contains('m²')",
            ]
            
            for selector in area_selectors:
                try:
                    elements = first_offer.select(selector)
                    if elements:
                        print(f"   ✅ {selector}: {len(elements)} elementów")
                        for i, elem in enumerate(elements[:2]):
                            text = elem.get_text()[:30]
                            print(f"      {i+1}. '{text}...'")
                except Exception as e:
                    print(f"   ❌ {selector}: błąd - {e}")
        
    except Exception as e:
        print(f"❌ Błąd w debugowaniu Otodom: {e}")

def debug_gratka_listing_page():
    """Debug selektorów na stronie listy Gratka.pl"""
    print(f"\n{'='*80}")
    print("🔍 DEBUG SELEKTORÓW - GRATKA.PL LISTA OGŁOSZEŃ")
    print("="*80)
    
    try:
        url = "https://gratka.pl/nieruchomosci/mieszkania/sprzedaz"
        print(f"🌐 Analizuję: {url}")
        
        soup = get_soup(url, use_selenium=True)
        
        # Znajdź kontener ogłoszeń
        offers = soup.select(".card")
        print(f"\n📋 Znaleziono {len(offers)} ogłoszeń")
        
        if offers:
            # Analizuj pierwsze ogłoszenie
            first_offer = offers[0]
            print(f"\n🎯 ANALIZA PIERWSZEGO OGŁOSZENIA:")
            print("="*50)
            
            # Zapisz HTML pierwszego ogłoszenia do pliku
            with open("debug_first_offer_gratka.html", "w", encoding="utf-8") as f:
                f.write(str(first_offer))
            print(f"💾 Zapisano HTML do: debug_first_offer_gratka.html")
            
            # Pokaż wszystkie klasy CSS w ogłoszeniu
            print(f"\n🎨 WSZYSTKIE KLASY CSS W OGŁOSZENIU:")
            all_elements_with_class = first_offer.select("[class]")
            unique_classes = set()
            for elem in all_elements_with_class:
                classes = elem.get("class", [])
                if isinstance(classes, list):
                    unique_classes.update(classes)
                else:
                    unique_classes.add(classes)
            
            sorted_classes = sorted(unique_classes)
            for i, css_class in enumerate(sorted_classes[:20]):  # Pokaż pierwsze 20
                print(f"   {i+1:2d}. .{css_class}")
            
            if len(sorted_classes) > 20:
                print(f"   ... i {len(sorted_classes) - 20} więcej")
            
            # Szukaj elementów z tekstem zawierającym ceny
            print(f"\n💰 ELEMENTY Z CENAMI:")
            price_elements = first_offer.find_all(text=lambda text: text and 'zł' in text)
            for i, price_text in enumerate(price_elements[:5]):
                parent = price_text.parent
                parent_class = parent.get("class", [])
                print(f"   {i+1}. '{price_text.strip()[:30]}...' (klasa: {parent_class})")
        
    except Exception as e:
        print(f"❌ Błąd w debugowaniu Gratka: {e}")

def analyze_html_structure():
    """Analizuje ogólną strukturę HTML"""
    print(f"\n{'='*80}")
    print("📊 ANALIZA STRUKTURY HTML")
    print("="*80)
    
    # Sprawdź czy mamy zapisane pliki HTML
    try:
        with open("debug_first_offer_otodom.html", "r", encoding="utf-8") as f:
            otodom_html = f.read()
            print(f"📄 Otodom HTML: {len(otodom_html)} znaków")
            
            # Znajdź data-cy atrybuty
            import re
            data_cy_attrs = re.findall(r'data-cy="([^"]*)"', otodom_html)
            unique_data_cy = set(data_cy_attrs)
            
            print(f"🏷️ data-cy atrybuty w ogłoszeniu Otodom:")
            for attr in sorted(unique_data_cy):
                print(f"   • data-cy='{attr}'")
                
    except FileNotFoundError:
        print("❌ Nie znaleziono pliku debug_first_offer_otodom.html")
    
    try:
        with open("debug_first_offer_gratka.html", "r", encoding="utf-8") as f:
            gratka_html = f.read()
            print(f"\n📄 Gratka HTML: {len(gratka_html)} znaków")
            
    except FileNotFoundError:
        print("❌ Nie znaleziono pliku debug_first_offer_gratka.html")

if __name__ == "__main__":
    try:
        # Debug Otodom
        debug_otodom_listing_page()
        
        # Debug Gratka
        debug_gratka_listing_page()
        
        # Analiza struktury
        analyze_html_structure()
        
        print(f"\n{'='*80}")
        print("🎉 DEBUG ZAKOŃCZONY!")
        print("="*80)
        print("💡 Następne kroki:")
        print("   1. Sprawdź pliki debug_first_offer_*.html")
        print("   2. Zaktualizuj selektory na podstawie wyników")
        print("   3. Przetestuj ponownie scrapery")
        
    except KeyboardInterrupt:
        print("\n⚠️ Debug przerwany przez użytkownika")
    except Exception as e:
        print(f"\n❌ Błąd ogólny: {e}")
        logging.error(f"Błąd w debug_listing_selectors: {e}", exc_info=True) 