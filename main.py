"""
Główny scraper nieruchomości - pobiera dane ze wszystkich portali z deduplikacją
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
from utils import deduplicate_listings, generate_duplicate_report, find_duplicates

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

def deduplicate_all_listings(results: Dict[str, List[Dict]], 
                           similarity_threshold: float = 75.0) -> List[Dict]:
    """
    Usuwa duplikaty ze wszystkich pobranych ogłoszeń
    
    Args:
        results: Wyniki scraperów
        similarity_threshold: Próg podobieństwa (0-100)
    
    Returns:
        List[Dict]: Lista unikatowych ogłoszeń
    """
    logger.info("🔍 Rozpoczynam deduplikację ogłoszeń...")
    
    # Połącz wszystkie ogłoszenia w jedną listę
    all_listings = []
    for scraper_name, listings in results.items():
        for listing in listings:
            # Dodaj timestamp i metadata
            listing["scraped_at"] = datetime.now().isoformat()
            listing["scraper_version"] = "1.0"
        all_listings.extend(listings)
    
    if not all_listings:
        logger.warning("Brak ogłoszeń do deduplikacji")
        return []
    
    logger.info(f"📊 Łącznie ogłoszeń przed deduplikacją: {len(all_listings)}")
    
    # Znajdź duplikaty
    unique_listings, duplicates = find_duplicates(all_listings, similarity_threshold)
    
    if duplicates:
        logger.info(f"🔄 Znaleziono {len(duplicates)} duplikatów:")
        
        # Statystyki duplikatów per portal
        duplicate_stats = {}
        for dup in duplicates:
            source = dup.get('source', 'nieznany')
            duplicate_stats[source] = duplicate_stats.get(source, 0) + 1
        
        for source, count in sorted(duplicate_stats.items()):
            logger.info(f"   • {source}: {count} duplikatów")
        
        # Pokaż przykłady wysokopodobnych duplikatów
        high_similarity_dups = [d for d in duplicates if d.get('similarity_score', 0) >= 90]
        if high_similarity_dups:
            logger.info(f"🔴 Bardzo podobne ogłoszenia (90%+): {len(high_similarity_dups)}")
            for dup in high_similarity_dups[:3]:
                title = dup.get('title', 'Brak tytułu')[:50]
                source = dup.get('source', '')
                similarity = dup.get('similarity_score', 0)
                logger.info(f"   • {title}... ({source}) - {similarity:.1f}%")
    
    # Deduplikacja z zachowaniem najlepszych źródeł
    deduplicated = deduplicate_listings(all_listings, 
                                      similarity_threshold=similarity_threshold, 
                                      keep_best_source=True)
    
    logger.info(f"✅ Po deduplikacji: {len(deduplicated)} unikatowych ogłoszeń")
    logger.info(f"🧹 Usunięto: {len(all_listings) - len(deduplicated)} duplikatów")
    
    return deduplicated

def save_all_to_supabase(unique_listings: List[Dict]) -> None:
    """
    Zapisuje unikatowe ogłoszenia do Supabase
    
    Args:
        unique_listings: Lista unikatowych ogłoszeń
    """
    if not unique_listings:
        logger.warning("Brak ogłoszeń do zapisu")
        return
    
    logger.info(f"💾 Zapisuję {len(unique_listings)} unikatowych ogłoszeń do Supabase...")
    
    try:
        saved_count = save_batch_listings(unique_listings)
        logger.info(f"✅ Zapisano {saved_count}/{len(unique_listings)} ogłoszeń")
        
        if saved_count < len(unique_listings):
            logger.warning(f"⚠️ Nie zapisano {len(unique_listings) - saved_count} ogłoszeń (prawdopodobnie już istnieją)")
        
    except Exception as e:
        logger.error(f"❌ Błąd zapisu do Supabase: {e}")

def print_summary(results: Dict[str, List[Dict]], unique_listings: List[Dict]) -> None:
    """Wyświetla podsumowanie scraperów z informacją o deduplikacji"""
    print("\n" + "="*60)
    print("PODSUMOWANIE SCRAPERÓW NIERUCHOMOŚCI Z DEDUPLIKACJĄ")
    print("="*60)
    
    total_raw = 0
    print("📊 Ogłoszenia per portal (przed deduplikacją):")
    for scraper_name, listings in results.items():
        count = len(listings)
        total_raw += count
        status = "✓" if count > 0 else "✗"
        print(f"  {status} {scraper_name:12} : {count:3} ogłoszeń")
    
    print("-"*60)
    print(f"📋 RAZEM przed deduplikacją: {total_raw} ogłoszeń")
    print(f"🧹 RAZEM po deduplikacji:  {len(unique_listings)} unikatowych ogłoszeń")
    print(f"🔄 Usunięto duplikatów:    {total_raw - len(unique_listings)}")
    
    # Statystyki końcowe per portal
    if unique_listings:
        print("\n📈 Rozkład unikatowych ogłoszeń per portal:")
        unique_stats = {}
        for listing in unique_listings:
            source = listing.get('source', 'nieznany')
            unique_stats[source] = unique_stats.get(source, 0) + 1
        
        for source, count in sorted(unique_stats.items()):
            percentage = (count / len(unique_listings)) * 100
            print(f"  • {source:12} : {count:3} ogłoszeń ({percentage:.1f}%)")
    
    print("="*60)

def main():
    """Główna funkcja programu z deduplikacją"""
    logger.info("🚀 Rozpoczynam scraping portali nieruchomości z deduplikacją")
    
    # Uruchom wszystkie scrapery
    results = run_all_scrapers(max_pages=2)
    
    # Deduplikacja ogłoszeń między portalami
    unique_listings = deduplicate_all_listings(results, similarity_threshold=75.0)
    
    # Wyświetl podsumowanie
    print_summary(results, unique_listings)
    
    # Zapisz unikatowe ogłoszenia do Supabase
    if unique_listings:
        try:
            save_all_to_supabase(unique_listings)
        except Exception as e:
            logger.error(f"❌ Błąd zapisu do Supabase: {e}")
    else:
        logger.warning("⚠️ Brak unikatowych ogłoszeń do zapisu")
    
    logger.info("✅ Zakończono scraping z deduplikacją")

if __name__ == "__main__":
    main() 