#!/usr/bin/env python3
"""
MAIN SCRAPER - TYLKO OTODOM.PL
Uproszczona wersja scrapująca wyłącznie Otodom.pl z opcjonalnym zapisem do Supabase
"""
import logging
from typing import List, Dict
from otodom_only_scraper import get_otodom_listings
from utils import deduplicate_listings

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def scrape_otodom_only(max_pages: int = 5, save_to_db: bool = False) -> List[Dict]:
    """
    Główna funkcja scrapowania tylko Otodom.pl
    
    Args:
        max_pages: Maksymalna liczba stron do przeskanowania
        save_to_db: Czy zapisać do bazy danych Supabase
    
    Returns:
        List[Dict]: Lista unikatowych ogłoszeń
    """
    print("="*80)
    print("🏠 SCRAPER NIERUCHOMOŚCI - TYLKO OTODOM.PL")
    print("="*80)
    print(f"📊 Parametry:")
    print(f"   • Maksymalnie stron: {max_pages}")
    print(f"   • Zapis do bazy: {'Tak' if save_to_db else 'Nie'}")
    print("="*80)
    
    try:
        # Scrapuj Otodom.pl
        print("\n🚀 SCRAPOWANIE OTODOM.PL")
        print("-" * 50)
        listings = get_otodom_listings(max_pages=max_pages)
        
        if not listings:
            print("❌ Nie pobrano żadnych ogłoszeń")
            return []
        
        print(f"\n📊 WYNIKI SCRAPOWANIA:")
        print(f"   🏠 Łącznie ogłoszeń: {len(listings)}")
        
        # Statystyki jakości danych
        with_price = len([l for l in listings if l.get('price')])
        with_location = len([l for l in listings if l.get('location')])
        with_area = len([l for l in listings if l.get('area')])
        with_rooms = len([l for l in listings if l.get('rooms')])
        
        print(f"   💰 Z cenami: {with_price}/{len(listings)} ({with_price/len(listings)*100:.1f}%)")
        print(f"   📍 Z lokalizacją: {with_location}/{len(listings)} ({with_location/len(listings)*100:.1f}%)")
        print(f"   📐 Z powierzchnią: {with_area}/{len(listings)} ({with_area/len(listings)*100:.1f}%)")
        print(f"   🚪 Z pokojami: {with_rooms}/{len(listings)} ({with_rooms/len(listings)*100:.1f}%)")
        
        # Deduplikacja (usuwanie duplikatów w ramach Otodom)
        print(f"\n🔄 DEDUPLIKACJA:")
        print("-" * 50)
        deduplicated = deduplicate_listings(listings, similarity_threshold=75.0)
        
        removed_count = len(listings) - len(deduplicated)
        if removed_count > 0:
            print(f"   ✅ Usunięto {removed_count} duplikatów")
            print(f"   📋 Pozostało {len(deduplicated)} unikatowych ogłoszeń")
        else:
            print(f"   ✅ Nie znaleziono duplikatów")
            print(f"   📋 Wszystkie {len(deduplicated)} ogłoszeń są unikatowe")
        
        # Statystyki cen
        listings_with_prices = [l for l in deduplicated if l.get('price')]
        if listings_with_prices:
            prices = [l['price'] for l in listings_with_prices]
            avg_price = sum(prices) / len(prices)
            min_price = min(prices)
            max_price = max(prices)
            
            print(f"\n💰 STATYSTYKI CEN:")
            print(f"   📈 Średnia cena: {avg_price:,.0f} zł")
            print(f"   🔽 Najniższa cena: {min_price:,.0f} zł")
            print(f"   🔼 Najwyższa cena: {max_price:,.0f} zł")
        
        # Zapis do bazy danych
        if save_to_db:
            print(f"\n💾 ZAPIS DO BAZY DANYCH:")
            print("-" * 50)
            try:
                from supabase_utils import save_listings_to_supabase
                success_count = save_listings_to_supabase(deduplicated)
                print(f"   ✅ Zapisano {success_count}/{len(deduplicated)} ogłoszeń do Supabase")
            except ImportError:
                print("   ❌ Brak modułu supabase_utils - pomijam zapis do bazy")
            except Exception as e:
                print(f"   ❌ Błąd zapisu do bazy: {e}")
        
        # Pokaż przykłady najlepszych ofert
        print(f"\n🏆 NAJLEPSZE OFERTY:")
        print("-" * 50)
        sorted_by_price = sorted(listings_with_prices, key=lambda x: x['price'])
        
        print("💎 Najtańsze:")
        for i, listing in enumerate(sorted_by_price[:3], 1):
            title = listing.get('title', 'Brak tytułu')[:50]
            price = listing.get('price', 0)
            location = listing.get('location', '')[:30]
            print(f"   {i}. {price:,.0f} zł - {title}... ({location})")
        
        print("\n💰 Najdroższe:")
        for i, listing in enumerate(sorted_by_price[-3:], 1):
            title = listing.get('title', 'Brak tytułu')[:50]
            price = listing.get('price', 0)
            location = listing.get('location', '')[:30]
            print(f"   {i}. {price:,.0f} zł - {title}... ({location})")
        
        return deduplicated
        
    except KeyboardInterrupt:
        print("\n⚠️ Przerwano przez użytkownika")
        return []
    except Exception as e:
        print(f"\n❌ Błąd ogólny: {e}")
        logger.error(f"Błąd w main_otodom_only: {e}", exc_info=True)
        return []

if __name__ == "__main__":
    """Uruchom scraper z linii komend"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Scraper Otodom.pl')
    parser.add_argument('--pages', type=int, default=5, help='Maksymalna liczba stron (domyślnie: 5)')
    parser.add_argument('--save-db', action='store_true', help='Zapisz do bazy danych Supabase')
    parser.add_argument('--quiet', action='store_true', help='Tryb cichy (mniej logów)')
    
    args = parser.parse_args()
    
    # Ustaw poziom logowania
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    
    try:
        # Uruchom scraping
        listings = scrape_otodom_only(
            max_pages=args.pages,
            save_to_db=args.save_db
        )
        
        print(f"\n{'='*80}")
        print("🎉 SCRAPOWANIE ZAKOŃCZONE!")
        print("="*80)
        print(f"📊 Wyniki:")
        print(f"   • Pobrano {len(listings)} unikatowych ogłoszeń")
        print(f"   • Źródło: Otodom.pl")
        if args.save_db:
            print(f"   • Zapisano do bazy danych Supabase")
        
        print(f"\n💡 Następne kroki:")
        print(f"   • Uruchom ponownie z --pages {args.pages*2} dla większej ilości danych")
        print(f"   • Dodaj --save-db aby zapisać do bazy danych")
        print(f"   • Sprawdź logi w scraper.log")
        
    except Exception as e:
        print(f"\n❌ Błąd krytyczny: {e}")
        exit(1) 