"""
Prosty test scrapera bez Supabase
"""
import requests
from bs4 import BeautifulSoup
import logging
import time
import random

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_simple_scraping():
    """Prosty test pobierania strony"""
    url = "https://freedom.pl"
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        logger.info(f"Pobieranie strony: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.find("title")
        
        print(f"✓ Pobrano stronę: {url}")
        print(f"✓ Tytuł strony: {title.get_text() if title else 'Brak tytułu'}")
        print(f"✓ Rozmiar HTML: {len(response.text)} znaków")
        
        return True
        
    except Exception as e:
        print(f"✗ Błąd: {e}")
        return False

def test_price_extraction():
    """Test ekstraktowania ceny"""
    import re
    
    test_prices = [
        "500 000 zł",
        "1 200 000 PLN",
        "€850,000",
        "750000 zł",
        "Cena: 600 000 zł"
    ]
    
    print("\n=== Test ekstraktowania cen ===")
    
    for price_text in test_prices:
        # Prosta ekstraktacja ceny
        price_clean = re.sub(r'\s+', ' ', price_text.strip())
        price_match = re.search(r'(\d+(?:\s\d{3})*(?:,\d{3})*)', price_clean)
        currency_match = re.search(r'(zł|PLN|€|EUR|\$|USD)', price_clean)
        
        price_value = None
        if price_match:
            price_str = price_match.group(1).replace(' ', '').replace(',', '')
            try:
                price_value = float(price_str)
            except ValueError:
                pass
        
        currency = currency_match.group(1) if currency_match else "zł"
        
        print(f"'{price_text}' -> {price_value} {currency}")

if __name__ == "__main__":
    print("=== Test prostego scrapera ===")
    
    # Test połączenia
    success = test_simple_scraping()
    
    # Test ekstraktowania cen
    test_price_extraction()
    
    if success:
        print("\n✓ Podstawowe funkcje działają poprawnie!")
    else:
        print("\n✗ Wystąpiły problemy z połączeniem") 