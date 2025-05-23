#!/usr/bin/env python3
"""
TEST ZAKTUALIZOWANEGO SCRAPERA OTODOM.PL
Z nowymi selektorami CSS (grudzień 2024)
"""
import logging
from scrapers.otodom import get_otodom_listings, get_detailed_otodom_listing

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_otodom_scraper():
    """Test zaktualizowanego scrapera Otodom.pl"""
    print("="*80)
    print("🏠 TEST ZAKTUALIZOWANEGO SCRAPERA OTODOM.PL")
    print("="*80)
    print("📝 Używa nowych selektorów CSS podanych przez użytkownika:")
    print("   • Cena: [data-cy='adPageHeaderPrice'] / [aria-label='Cena']")
    print("   • Lokalizacja: [data-sentry-component='MapLink'] a")
    print("   • Pokoje: [data-sentry-source-file='AdDetailItem.tsx']")
    print("   • Opis: [data-cy='adPageAdDescription']")
    print("="*80)
    
    try:
        # Test podstawowy - lista ogłoszeń
        print("\n🚀 KROK 1: Pobieranie listy ogłoszeń...")
        listings = get_otodom_listings(max_pages=1)
        
        if listings:
            print(f"✅ Pobrano {len(listings)} ogłoszeń z Otodom.pl")
            
            # Pokaż przykłady
            print(f"\n📋 PRZYKŁADY POBRANYCH OGŁOSZEŃ:")
            for i, listing in enumerate(listings[:3], 1):
                title = listing.get('title', 'Brak tytułu')
                price = listing.get('price')
                location = listing.get('location', '')
                url = listing.get('url', '')
                area = listing.get('area', '')
                rooms = listing.get('rooms', '')
                
                print(f"\n  {i}. {title[:60]}{'...' if len(title) > 60 else ''}")
                if price:
                    currency = listing.get('price_currency', 'zł')
                    print(f"     💰 Cena: {price:,.0f} {currency}")
                if location:
                    print(f"     📍 Lokalizacja: {location}")
                if area:
                    print(f"     📐 Powierzchnia: {area}")
                if rooms:
                    print(f"     🚪 Pokoje: {rooms}")
                if url:
                    print(f"     🔗 URL: {url[:70]}{'...' if len(url) > 70 else ''}")
            
            # Test szczegółowych danych
            if listings and listings[0].get('url'):
                print(f"\n🔍 KROK 2: Test pobierania szczegółów ogłoszenia...")
                first_url = listings[0]['url']
                detailed = get_detailed_otodom_listing(first_url)
                
                if detailed and detailed.get('title'):
                    print("✅ Pobrano szczegółowe dane ogłoszenia:")
                    print(f"   📝 Tytuł: {detailed.get('title', '')[:60]}...")
                    if detailed.get('price'):
                        currency = detailed.get('price_currency', 'zł')
                        print(f"   💰 Cena: {detailed['price']:,.0f} {currency}")
                    if detailed.get('location'):
                        print(f"   📍 Lokalizacja: {detailed.get('location', '')}")
                    if detailed.get('rooms'):
                        print(f"   🚪 Pokoje: {detailed.get('rooms', '')}")
                    if detailed.get('description'):
                        desc = detailed.get('description', '')[:100]
                        print(f"   📖 Opis: {desc}...")
                else:
                    print("⚠️ Nie udało się pobrać szczegółów (możliwe że selektory wymagają dalszych poprawek)")
        else:
            print("❌ Nie pobrano żadnych ogłoszeń")
            print("💡 Możliwe przyczyny:")
            print("   • Selektory wymagają dalszego dostosowania")
            print("   • Portal wprowadził nowe zabezpieczenia anti-bot")
            print("   • Selenium wymaga dodatkowej konfiguracji")
            
    except Exception as e:
        print(f"❌ Błąd w teście: {e}")
        logger.error(f"Błąd w test_otodom_updated: {e}", exc_info=True)

def test_otodom_debug():
    """Debug scrapera Otodom - analiza HTML"""
    print(f"\n{'='*60}")
    print("🔧 DEBUG SCRAPERA OTODOM.PL")
    print("="*60)
    
    try:
        from utils import get_soup
        
        url = "https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/cala-polska?page=1"
        print(f"🌐 Analizuję stronę: {url}")
        
        soup = get_soup(url, use_selenium=True)
        
        # Sprawdź ogólną strukturę
        print(f"\n📊 Analiza struktury HTML:")
        print(f"   • Całkowita długość HTML: {len(str(soup))} znaków")
        print(f"   • Czy zawiera 'otodom': {'✅' if 'otodom' in soup.get_text().lower() else '❌'}")
        
        # Szukaj potencjalnych kontenerów z ogłoszeniami
        potential_containers = [
            "[data-cy='listing-item']",
            ".es62z2j0", 
            "[data-testid='listing-item']",
            "article",
            ".listing-item",
            "[data-cy*='listing']",
            "[class*='listing']"
        ]
        
        print(f"\n🔍 Szukanie kontenerów ogłoszeń:")
        for selector in potential_containers:
            elements = soup.select(selector)
            print(f"   • {selector}: {len(elements)} elementów")
            
        # Szukaj elementów z cenami
        price_selectors = [
            "[data-cy='adPageHeaderPrice']",
            "[aria-label='Cena']",
            ".css-1o51x5a",
            "[data-cy*='price']",
            "[class*='price']"
        ]
        
        print(f"\n💰 Szukanie elementów z cenami:")
        for selector in price_selectors:
            elements = soup.select(selector)
            print(f"   • {selector}: {len(elements)} elementów")
            if elements:
                sample_text = elements[0].get_text()[:50]
                print(f"     Przykład: '{sample_text}...'")
        
        # Sprawdź czy jest JavaScript
        scripts = soup.select("script")
        print(f"\n🔧 Informacje o JavaScript:")
        print(f"   • Liczba skryptów: {len(scripts)}")
        print(f"   • Czy strona wymaga JS: {'✅' if len(scripts) > 10 else '❌'}")
        
    except Exception as e:
        print(f"❌ Błąd w debugowaniu: {e}")

if __name__ == "__main__":
    try:
        # Test główny
        test_otodom_scraper()
        
        # Debug jeśli potrzebny
        print(f"\n🤔 Chcesz uruchomić debug? (t/n): ", end="")
        # Automatycznie uruchom debug dla kompletności
        print("t")
        test_otodom_debug()
        
        print(f"\n{'='*80}")
        print("🎉 TEST ZAKOŃCZONY!")
        print("="*80)
        print("💡 Wskazówki:")
        print("   • Jeśli nie ma ogłoszeń - selektory wymagają poprawy")
        print("   • Sprawdź logi Selenium w terminalu")
        print("   • Otodom często zmienia strukturę HTML")
        print("   • Skorzystaj z developer tools w przeglądarce")
        
    except KeyboardInterrupt:
        print("\n⚠️ Test przerwany przez użytkownika")
    except Exception as e:
        print(f"\n❌ Błąd ogólny: {e}")
        logging.error(f"Błąd w test_otodom_updated: {e}", exc_info=True) 