"""
Plik do testowania poszczególnych scraperów
"""
import logging
from scrapers.freedom import get_freedom_listings
from scrapers.otodom import get_otodom_listings

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)

def test_freedom():
    """Test scrapera Freedom.pl"""
    print("Testowanie Freedom.pl...")
    listings = get_freedom_listings(max_pages=1)
    print(f"Pobrano {len(listings)} ogłoszeń")
    
    if listings:
        print("Przykładowe ogłoszenie:")
        for key, value in listings[0].items():
            print(f"  {key}: {value}")

def test_otodom():
    """Test scrapera Otodom.pl"""
    print("\nTestowanie Otodom.pl...")
    listings = get_otodom_listings(max_pages=1)
    print(f"Pobrano {len(listings)} ogłoszeń")
    
    if listings:
        print("Przykładowe ogłoszenie:")
        for key, value in listings[0].items():
            print(f"  {key}: {value}")

if __name__ == "__main__":
    # Uruchom testy
    test_freedom()
    test_otodom() 