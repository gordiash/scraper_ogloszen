"""
Debug scrapera - pokaż pobrane dane
"""
import logging
from scrapers.otodom import get_otodom_listings

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)

def debug_otodom():
    """Debugowanie scrapera Otodom"""
    print("=== DEBUGOWANIE OTODOM.PL ===")
    
    listings = get_otodom_listings(max_pages=1)
    
    print(f"\nPobrano {len(listings)} ogłoszeń:")
    
    for i, listing in enumerate(listings[:5]):  # Pokaż tylko 5 pierwszych
        print(f"\n--- Ogłoszenie {i+1} ---")
        for key, value in listing.items():
            if value:  # Pokaż tylko niepuste wartości
                print(f"{key:15}: {value}")
        print("-" * 40)

if __name__ == "__main__":
    debug_otodom() 