#!/usr/bin/env python3
"""
TEST GŁÓWNEGO SCRAPERA Z DEDUPLIKACJĄ (BEZ SUPABASE)
Symuluje działanie main.py ale bez zapisu do bazy danych
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
from utils import deduplicate_listings, generate_duplicate_report, find_duplicates

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
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

def run_scraper(scraper_name: str, max_pages: int = 1) -> List[Dict]:
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
        logger.info(f"🚀 Rozpoczynam scraping: {scraper_name}")
        listings = SCRAPERS[scraper_name](max_pages)
        logger.info(f"✅ Zakończono scraping {scraper_name}: {len(listings)} ogłoszeń")
        return listings
    except Exception as e:
        logger.error(f"❌ Błąd scrapera {scraper_name}: {e}")
        return []

def run_all_scrapers(max_pages: int = 1) -> Dict[str, List[Dict]]:
    """
    Uruchamia wszystkie scrapery
    
    Args:
        max_pages: Maksymalna liczba stron dla każdego portalu
    
    Returns:
        Dict: Wyniki z wszystkich scraperów
    """
    results = {}
    total_listings = 0
    
    print("="*80)
    print("🏠 GŁÓWNY SCRAPER Z DEDUPLIKACJĄ - TEST")
    print("="*80)
    
    for scraper_name in SCRAPERS.keys():
        try:
            listings = run_scraper(scraper_name, max_pages)
            results[scraper_name] = listings
            total_listings += len(listings)
        except Exception as e:
            logger.error(f"❌ Błąd uruchamiania scrapera {scraper_name}: {e}")
            results[scraper_name] = []
    
    print(f"\n📊 Podsumowanie pobierania:")
    print(f"   🏠 Całkowita liczba pobranych ogłoszeń: {total_listings}")
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
    print(f"\n{'='*60}")
    print("🔍 DEDUPLIKACJA OGŁOSZEŃ")
    print("="*60)
    
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
        logger.warning("❌ Brak ogłoszeń do deduplikacji")
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

def print_final_summary(results: Dict[str, List[Dict]], unique_listings: List[Dict]) -> None:
    """Wyświetla końcowe podsumowanie"""
    print(f"\n{'='*80}")
    print("📊 KOŃCOWE PODSUMOWANIE SCRAPERA Z DEDUPLIKACJĄ")
    print("="*80)
    
    total_raw = 0
    print("📋 Ogłoszenia per portal (przed deduplikacją):")
    for scraper_name, listings in results.items():
        count = len(listings)
        total_raw += count
        status = "✓" if count > 0 else "✗"
        print(f"  {status} {scraper_name:12} : {count:3} ogłoszeń")
    
    print("-"*80)
    print(f"📊 RAZEM przed deduplikacją: {total_raw} ogłoszeń")
    print(f"🧹 RAZEM po deduplikacji:  {len(unique_listings)} unikatowych ogłoszeń")
    
    if total_raw > 0:
        reduction_percentage = ((total_raw - len(unique_listings)) / total_raw) * 100
        print(f"🔄 Skuteczność deduplikacji: {reduction_percentage:.1f}% duplikatów usunięto")
    
    # Statystyki końcowe per portal
    if unique_listings:
        print("\n📈 Rozkład unikatowych ogłoszeń per portal:")
        unique_stats = {}
        listings_with_price = 0
        total_price = 0
        
        for listing in unique_listings:
            source = listing.get('source', 'nieznany')
            unique_stats[source] = unique_stats.get(source, 0) + 1
            
            # Statystyki cen
            if listing.get('price'):
                listings_with_price += 1
                total_price += listing['price']
        
        for source, count in sorted(unique_stats.items()):
            percentage = (count / len(unique_listings)) * 100
            print(f"  • {source:12} : {count:3} ogłoszeń ({percentage:.1f}%)")
        
        print(f"\n💰 Statystyki cenowe:")
        print(f"  • Ogłoszenia z cenami: {listings_with_price}/{len(unique_listings)}")
        if listings_with_price > 0:
            avg_price = total_price / listings_with_price
            print(f"  • Średnia cena: {avg_price:,.0f} zł")
    
    # Najdroższe oferty
    expensive_listings = [l for l in unique_listings if l.get('price') and l['price'] > 500000]
    if expensive_listings:
        expensive_listings.sort(key=lambda x: x['price'], reverse=True)
        print(f"\n💎 TOP 3 najdroższe unikatowe oferty:")
        for i, listing in enumerate(expensive_listings[:3]):
            price = listing['price']
            currency = listing.get('price_currency', 'zł')
            title = listing.get('title', 'Brak tytułu')[:50]
            source = listing.get('source', '')
            print(f"  {i+1}. {price:,.0f} {currency} - {title}... ({source})")
    
    print("="*80)

def main():
    """Główna funkcja testowa"""
    try:
        # Uruchom wszystkie scrapery (tylko 1 strona dla szybkości)
        results = run_all_scrapers(max_pages=1)
        
        # Deduplikacja ogłoszeń między portalami
        unique_listings = deduplicate_all_listings(results, similarity_threshold=75.0)
        
        # Wyświetl końcowe podsumowanie
        print_final_summary(results, unique_listings)
        
        # Raport o duplikatach
        if unique_listings:
            _, duplicates = find_duplicates(
                [listing for listings in results.values() for listing in listings], 
                75.0
            )
            
            if duplicates:
                print(f"\n{'='*60}")
                print("📄 RAPORT DUPLIKATÓW")
                print("="*60)
                report = generate_duplicate_report(duplicates)
                print(report)
        
        print(f"\n🎉 SUKCES! Test głównego scrapera z deduplikacją zakończony!")
        print(f"✅ Pobrano {len(unique_listings)} unikatowych ogłoszeń")
        print("\n💡 Aby uruchomić z zapisem do Supabase:")
        print("   1. Skonfiguruj zmienne środowiskowe Supabase")
        print("   2. Uruchom: python main.py")
        
    except KeyboardInterrupt:
        print("\n⚠️ Test przerwany przez użytkownika")
    except Exception as e:
        print(f"\n❌ Błąd w teście: {e}")
        logging.error(f"Błąd w test_main_with_deduplication: {e}", exc_info=True)

if __name__ == "__main__":
    main() 