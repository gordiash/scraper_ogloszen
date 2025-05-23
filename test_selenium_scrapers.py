"""
Test scraperów z obsługą Selenium
"""
import logging
from datetime import datetime

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_selenium_scrapers():
    """Testuje scrapery z obsługą Selenium"""
    print("="*60)
    print("TEST SCRAPERÓW Z SELENIUM")
    print("="*60)
    
    # Import scraperów
    try:
        from scrapers.freedom import get_freedom_listings
        from scrapers.gratka import get_gratka_listings
        from scrapers.metrohouse import get_metrohouse_listings
        from scrapers.domiporta import get_domiporta_listings
        
        scrapers = [
            ("Freedom.pl", get_freedom_listings),
            ("Gratka.pl", get_gratka_listings),
            ("Metrohouse.pl", get_metrohouse_listings),
            ("Domiporta.pl", get_domiporta_listings),
        ]
        
        results = {}
        
        for name, scraper_func in scrapers:
            print(f"\n--- TESTOWANIE: {name} ---")
            try:
                # Test tylko pierwszej strony
                listings = scraper_func(max_pages=1)
                results[name] = len(listings)
                
                print(f"✓ {name}: {len(listings)} ogłoszeń")
                
                # Pokaż przykłady
                if listings:
                    for i, listing in enumerate(listings[:2]):
                        print(f"  {i+1}. {listing.get('title', 'Brak tytułu')[:50]}...")
                        if listing.get('price'):
                            print(f"     Cena: {listing['price']} {listing.get('price_currency', 'zł')}")
                        if listing.get('location'):
                            print(f"     Lokalizacja: {listing['location']}")
                        if listing.get('url'):
                            print(f"     URL: {listing['url'][:60]}...")
                else:
                    print(f"  ⚠️ Brak ogłoszeń - możliwy problem z selektorami")
                    
            except Exception as e:
                print(f"✗ {name}: BŁĄD - {e}")
                results[name] = 0
        
        # Podsumowanie
        print(f"\n{'='*60}")
        print("PODSUMOWANIE TESTÓW SELENIUM")
        print(f"{'='*60}")
        
        total_listings = sum(results.values())
        working_scrapers = sum(1 for count in results.values() if count > 0)
        
        for name, count in results.items():
            status = "✓ DZIAŁA" if count > 0 else "✗ PROBLEM"
            print(f"{name:<15}: {count:>3} ogłoszeń {status}")
        
        print(f"\nDziałające scrapery: {working_scrapers}/4")
        print(f"Łącznie ogłoszeń: {total_listings}")
        
        return working_scrapers > 0
        
    except Exception as e:
        print(f"BŁĄD KRYTYCZNY: {e}")
        return False

def check_selenium_installation():
    """Sprawdza czy Selenium jest zainstalowany"""
    print("--- SPRAWDZANIE SELENIUM ---")
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        print("✓ Selenium jest zainstalowany")
        
        # Test prostego uruchomienia
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        
        driver = webdriver.Chrome(options=options)
        driver.get("https://www.google.com")
        driver.quit()
        print("✓ Chrome WebDriver działa")
        return True
        
    except ImportError:
        print("✗ Selenium nie jest zainstalowany")
        print("Zainstaluj: pip install selenium")
        return False
    except Exception as e:
        print(f"✗ Problem z Chrome WebDriver: {e}")
        print("Sprawdź czy ChromeDriver jest w PATH")
        return False

if __name__ == "__main__":
    print("TESTY SCRAPERÓW Z SELENIUM")
    print("="*60)
    
    # Sprawdź Selenium
    selenium_ok = check_selenium_installation()
    
    if selenium_ok:
        # Uruchom testy
        success = test_selenium_scrapers()
        
        if success:
            print("\n🎉 SUKCES! Przynajmniej jeden scraper z Selenium działa!")
        else:
            print("\n❌ PROBLEM! Żaden scraper z Selenium nie działa.")
            print("\nMożliwe przyczyny:")
            print("1. Portale zmieniły strukturę HTML")
            print("2. ChromeDriver nie jest zainstalowany")
            print("3. Problemy z siecią")
    else:
        print("\n❌ Nie można testować - Selenium nie działa")
        print("\nAby zainstalować Selenium:")
        print("pip install selenium")
        print("\nAby zainstalować ChromeDriver:")
        print("1. Pobierz z: https://chromedriver.chromium.org/")
        print("2. Dodaj do PATH") 