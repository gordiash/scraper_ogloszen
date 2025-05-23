"""
Test scrapera bez zapisu do bazy danych
"""
import logging
import sys
from datetime import datetime

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_freedom_scraper():
    """Test scrapera Freedom.pl bez bazy danych"""
    try:
        # Import z naszego modułu
        from scrapers.freedom import get_freedom_listings
        
        print("=== Test scrapera Freedom.pl ===")
        logger.info("Rozpoczynam test Freedom.pl...")
        
        # Pobierz tylko 1 stronę do testu
        listings = get_freedom_listings(max_pages=1)
        
        print(f"✓ Pobrano {len(listings)} ogłoszeń")
        
        if listings:
            print("\nPrzykładowe ogłoszenie:")
            listing = listings[0]
            for key, value in listing.items():
                print(f"  {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"✗ Błąd testu Freedom.pl: {e}")
        logger.error(f"Błąd: {e}")
        return False

def test_multiple_scrapers():
    """Test wielu scraperów bez bazy danych"""
    scrapers_to_test = [
        ("freedom", "scrapers.freedom", "get_freedom_listings"),
        ("otodom", "scrapers.otodom", "get_otodom_listings"),
        ("gratka", "scrapers.gratka", "get_gratka_listings"),
    ]
    
    results = {}
    
    for scraper_name, module_name, function_name in scrapers_to_test:
        try:
            print(f"\n=== Test {scraper_name} ===")
            
            # Dynamiczny import
            module = __import__(module_name, fromlist=[function_name])
            scraper_func = getattr(module, function_name)
            
            # Uruchom scraper (tylko 1 strona)
            listings = scraper_func(max_pages=1)
            
            results[scraper_name] = len(listings)
            print(f"✓ {scraper_name}: {len(listings)} ogłoszeń")
            
            if listings:
                print(f"   Przykład: {listings[0].get('title', 'Brak tytułu')[:50]}...")
            
        except Exception as e:
            results[scraper_name] = 0
            print(f"✗ {scraper_name}: Błąd - {e}")
    
    return results

def print_summary(results):
    """Podsumowanie testów"""
    print("\n" + "="*50)
    print("PODSUMOWANIE TESTÓW SCRAPERÓW")
    print("="*50)
    
    total = 0
    for scraper_name, count in results.items():
        status = "✓" if count > 0 else "✗"
        print(f"{status} {scraper_name:12} : {count:3} ogłoszeń")
        total += count
    
    print("-"*50)
    print(f"RAZEM: {total} ogłoszeń")
    print("="*50)

if __name__ == "__main__":
    print("=== TEST SCRAPERÓW NIERUCHOMOŚCI ===")
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test pojedynczego scrapera
    freedom_success = test_freedom_scraper()
    
    # Test wielu scraperów
    if freedom_success:
        results = test_multiple_scrapers()
        print_summary(results)
    
    print("\n=== KONIEC TESTÓW ===")
    print("Uwaga: To są testy bez zapisu do bazy danych!")
    print("Aby zapisać dane do Supabase, skonfiguruj zmienne środowiskowe i uruchom main.py") 