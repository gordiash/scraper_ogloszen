"""
Główny scraper nieruchomości - pobiera dane ze wszystkich portali
"""
import logging
import sys
from datetime import datetime
from typing import List, Dict

# Import scraperów
from scrapers.freedom import get_freedom_listings
from scrapers.otodom import get_otodom_listings
from scrapers.metrohouse import get_metrohouse_listings
from scrapers.domiporta import get_domiporta_listings
from scrapers.gratka import get_gratka_listings
from scrapers.olx import get_olx_listings

# Import utils
from supabase_utils import save_batch_listings

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Konfiguracja scraperów
SCRAPERS = {
    "freedom": get_freedom_listings,
    "otodom": get_otodom_listings,
    "metrohouse": get_metrohouse_listings,
    "domiporta": get_domiporta_listings,
    "gratka": get_gratka_listings,
    "olx": get_olx_listings,
}

def run_scraper(scraper_name: str, max_pages: int = 2) -> List[Dict]:
    """
    Uruchamia scraper dla konkretnego portalu
    
    Args:
        scraper_name: Nazwa scrapera
        max_pages: Maksymalna liczba stron
    
    Returns:
        List[Dict]: Lista ogłoszeń
    """
    if scraper_name not in SCRAPERS:
        logger.error(f"Nieznany scraper: {scraper_name}")
        return []
    
    try:
        logger.info(f"Rozpoczynam scraping: {scraper_name}")
        listings = SCRAPERS[scraper_name](max_pages)
        logger.info(f"Zakończono scraping {scraper_name}: {len(listings)} ogłoszeń")
        return listings
    except Exception as e:
        logger.error(f"Błąd scrapera {scraper_name}: {e}")
        return []

def run_all_scrapers(max_pages: int = 2) -> Dict[str, List[Dict]]:
    """
    Uruchamia wszystkie scrapery
    
    Args:
        max_pages: Maksymalna liczba stron dla każdego portalu
    
    Returns:
        Dict: Wyniki z wszystkich scraperów
    """
    results = {}
    total_listings = 0
    
    for scraper_name in SCRAPERS.keys():
        try:
            listings = run_scraper(scraper_name, max_pages)
            results[scraper_name] = listings
            total_listings += len(listings)
        except Exception as e:
            logger.error(f"Błąd uruchamiania scrapera {scraper_name}: {e}")
            results[scraper_name] = []
    
    logger.info(f"Całkowita liczba pobranych ogłoszeń: {total_listings}")
    return results

def save_all_to_supabase(results: Dict[str, List[Dict]]) -> None:
    """
    Zapisuje wszystkie wyniki do Supabase
    
    Args:
        results: Wyniki scraperów
    """
    total_saved = 0
    
    for scraper_name, listings in results.items():
        if listings:
            # Dodaj timestamp do wszystkich ogłoszeń
            for listing in listings:
                listing["scraped_at"] = datetime.now().isoformat()
                listing["scraper_version"] = "1.0"
            
            saved_count = save_batch_listings(listings)
            total_saved += saved_count
            logger.info(f"Zapisano {saved_count}/{len(listings)} ogłoszeń z {scraper_name}")
    
    logger.info(f"Całkowita liczba zapisanych ogłoszeń: {total_saved}")

def print_summary(results: Dict[str, List[Dict]]) -> None:
    """Wyświetla podsumowanie scraperów"""
    print("\n" + "="*50)
    print("PODSUMOWANIE SCRAPERÓW NIERUCHOMOŚCI")
    print("="*50)
    
    total = 0
    for scraper_name, listings in results.items():
        count = len(listings)
        total += count
        status = "✓" if count > 0 else "✗"
        print(f"{status} {scraper_name:12} : {count:3} ogłoszeń")
    
    print("-"*50)
    print(f"RAZEM: {total} ogłoszeń")
    print("="*50)

def main():
    """Główna funkcja programu"""
    logger.info("Rozpoczynam scraping portali nieruchomości")
    
    # Uruchom wszystkie scrapery
    results = run_all_scrapers(max_pages=2)
    
    # Wyświetl podsumowanie
    print_summary(results)
    
    # Zapisz do Supabase
    try:
        save_all_to_supabase(results)
    except Exception as e:
        logger.error(f"Błąd zapisu do Supabase: {e}")
    
    logger.info("Zakończono scraping")

if __name__ == "__main__":
    main() 