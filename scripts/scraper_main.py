#!/usr/bin/env python3
"""
GŁÓWNY SKRYPT SCRAPERA - KOMPLETNY PIPELINE
Łączy scraping → parsing adresów → geocoding w jeden proces
"""
import logging
import sys
import os
import argparse
from datetime import datetime
from typing import List, Dict

# Dodaj główny katalog do ścieżki
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scrapers.otodom_scraper import get_otodom_listings
from src.parsers.address_parser import process_all_locations
from src.geocoding.geocoder import update_all_coordinates_improved
from supabase_utils import save_listings_to_supabase, get_supabase_client

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def print_banner():
    """Wyświetl banner aplikacji"""
    print("="*80)
    print("🏠 SCRAPER NIERUCHOMOŚCI - KOMPLETNY PIPELINE")
    print("="*80)
    print("📅 Data uruchomienia:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("🔗 Źródło: Otodom.pl")
    print("💾 Baza danych: Supabase")
    print("🌍 Geocoding: OpenStreetMap Nominatim")
    print("="*80)

def get_database_stats() -> Dict[str, int]:
    """Pobierz statystyki z bazy danych"""
    try:
        supabase = get_supabase_client()
        
        # Statystyki listings
        listings_result = supabase.table("listings").select("id", count="exact").execute()
        total_listings = listings_result.count
        
        # Statystyki addresses
        addresses_result = supabase.table("addresses").select("id", count="exact").execute()
        total_addresses = addresses_result.count
        
        # Statystyki geocoded
        geocoded_result = supabase.table("addresses").select("id", count="exact").not_.is_("latitude", "null").execute()
        geocoded_count = geocoded_result.count
        
        return {
            "total_listings": total_listings,
            "total_addresses": total_addresses,
            "geocoded_count": geocoded_count
        }
        
    except Exception as e:
        logger.error(f"❌ Błąd pobierania statystyk: {e}")
        return {
            "total_listings": 0,
            "total_addresses": 0,
            "geocoded_count": 0
        }

def print_stats(title: str, stats: Dict[str, int]):
    """Wyświetl statystyki"""
    print(f"\n📊 {title}")
    print("-" * 60)
    print(f"📋 Łącznie ogłoszeń: {stats['total_listings']:,}")
    print(f"📍 Łącznie adresów: {stats['total_addresses']:,}")
    print(f"🌍 Z współrzędnymi: {stats['geocoded_count']:,}")
    
    if stats['total_addresses'] > 0:
        geocoding_rate = (stats['geocoded_count'] / stats['total_addresses']) * 100
        print(f"📈 Pokrycie geocoding: {geocoding_rate:.1f}%")

def run_scraping_phase(max_pages: int) -> List[Dict]:
    """
    Faza 1: Scrapowanie ogłoszeń z Otodom.pl
    
    Args:
        max_pages: Maksymalna liczba stron do scrapowania
    
    Returns:
        List[Dict]: Lista pobranych ogłoszeń
    """
    print(f"\n🔍 FAZA 1: SCRAPOWANIE OTODOM.PL")
    print(f"📄 Maksymalna liczba stron: {max_pages}")
    print("-" * 60)
    
    try:
        listings = get_otodom_listings(max_pages=max_pages)
        
        if listings:
            print(f"✅ Pobrano {len(listings)} ogłoszeń z Otodom.pl")
            
            # Statystyki jakości danych
            with_price = len([l for l in listings if l.get('price')])
            with_location = len([l for l in listings if l.get('location')])
            with_area = len([l for l in listings if l.get('area')])
            
            print(f"💰 Z cenami: {with_price}/{len(listings)} ({with_price/len(listings)*100:.1f}%)")
            print(f"📍 Z lokalizacją: {with_location}/{len(listings)} ({with_location/len(listings)*100:.1f}%)")
            print(f"📐 Z powierzchnią: {with_area}/{len(listings)} ({with_area/len(listings)*100:.1f}%)")
            
            return listings
        else:
            print("❌ Nie pobrano żadnych ogłoszeń")
            return []
            
    except Exception as e:
        logger.error(f"❌ Błąd w fazie scrapowania: {e}")
        return []

def run_saving_phase(listings: List[Dict]) -> int:
    """
    Faza 2: Zapis ogłoszeń do bazy danych
    
    Args:
        listings: Lista ogłoszeń do zapisu
    
    Returns:
        int: Liczba zapisanych ogłoszeń
    """
    print(f"\n💾 FAZA 2: ZAPIS DO BAZY DANYCH")
    print(f"📋 Ogłoszeń do zapisu: {len(listings)}")
    print("-" * 60)
    
    try:
        saved_count = save_listings_to_supabase(listings)
        
        if saved_count > 0:
            print(f"✅ Zapisano {saved_count} nowych ogłoszeń")
            
            # Statystyki zapisu
            duplicate_count = len(listings) - saved_count
            if duplicate_count > 0:
                print(f"⏭️ Pominięto {duplicate_count} duplikatów")
                
            success_rate = (saved_count / len(listings)) * 100
            print(f"📈 Skuteczność zapisu: {success_rate:.1f}%")
        else:
            print("⚠️ Nie zapisano żadnych nowych ogłoszeń (wszystkie to duplikaty)")
            
        return saved_count
        
    except Exception as e:
        logger.error(f"❌ Błąd w fazie zapisu: {e}")
        return 0

def run_parsing_phase() -> bool:
    """
    Faza 3: Parsing adresów
    
    Returns:
        bool: True jeśli parsing się udał
    """
    print(f"\n📍 FAZA 3: PARSING ADRESÓW")
    print("-" * 60)
    
    try:
        # Uruchom parsing adresów (funkcja wyświetla własne statystyki)
        process_all_locations()
        print("✅ Parsing adresów zakończony")
        return True
        
    except Exception as e:
        logger.error(f"❌ Błąd w fazie parsingu adresów: {e}")
        return False

def run_geocoding_phase(max_addresses: int) -> bool:
    """
    Faza 4: Geocoding - uzupełnianie współrzędnych
    
    Args:
        max_addresses: Maksymalna liczba adresów do geocodingu
    
    Returns:
        bool: True jeśli geocoding się udał
    """
    print(f"\n🌍 FAZA 4: GEOCODING WSPÓŁRZĘDNYCH")
    print(f"📍 Maksymalna liczba adresów: {max_addresses}")
    print("-" * 60)
    
    try:
        # Uruchom geocoding (funkcja wyświetla własne statystyki)
        update_all_coordinates_improved(
            batch_size=50,
            max_addresses=max_addresses
        )
        print("✅ Geocoding zakończony")
        return True
        
    except Exception as e:
        logger.error(f"❌ Błąd w fazie geocodingu: {e}")
        return False

def run_complete_pipeline(max_pages: int = 5, max_geocoding_addresses: int = 100) -> bool:
    """
    Uruchom kompletny pipeline scrapera
    
    Args:
        max_pages: Maksymalna liczba stron do scrapowania
        max_geocoding_addresses: Maksymalna liczba adresów do geocodingu
    
    Returns:
        bool: True jeśli cały pipeline się udał
    """
    print_banner()
    
    # Statystyki początkowe
    initial_stats = get_database_stats()
    print_stats("STATYSTYKI POCZĄTKOWE", initial_stats)
    
    success_phases = 0
    total_phases = 4
    
    # FAZA 1: Scrapowanie
    listings = run_scraping_phase(max_pages)
    if listings:
        success_phases += 1
    
    # FAZA 2: Zapis do bazy
    if listings:
        saved_count = run_saving_phase(listings)
        if saved_count >= 0:  # 0 też jest sukcesem (duplikaty)
            success_phases += 1
    else:
        print("\n💾 FAZA 2: POMINIĘTO - brak ogłoszeń do zapisu")
    
    # FAZA 3: Parsing adresów
    if run_parsing_phase():
        success_phases += 1
    
    # FAZA 4: Geocoding
    if run_geocoding_phase(max_geocoding_addresses):
        success_phases += 1
    
    # Statystyki końcowe
    final_stats = get_database_stats()
    print_stats("STATYSTYKI KOŃCOWE", final_stats)
    
    # Podsumowanie zmian
    print(f"\n📈 ZMIANY W BAZIE DANYCH")
    print("-" * 60)
    print(f"📋 Nowe ogłoszenia: +{final_stats['total_listings'] - initial_stats['total_listings']}")
    print(f"📍 Nowe adresy: +{final_stats['total_addresses'] - initial_stats['total_addresses']}")
    print(f"🌍 Nowe współrzędne: +{final_stats['geocoded_count'] - initial_stats['geocoded_count']}")
    
    # Podsumowanie pipeline
    print(f"\n🎯 PODSUMOWANIE PIPELINE")
    print("=" * 80)
    print(f"✅ Udane fazy: {success_phases}/{total_phases}")
    print(f"📈 Skuteczność: {(success_phases/total_phases)*100:.1f}%")
    
    if success_phases == total_phases:
        print("🎉 PIPELINE ZAKOŃCZONY SUKCESEM!")
        return True
    else:
        print("⚠️ Pipeline zakończony z błędami")
        return False

def main():
    """Główna funkcja z argumentami CLI"""
    parser = argparse.ArgumentParser(
        description='Kompletny pipeline scrapera nieruchomości',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady użycia:
  python scripts/scraper_main.py                           # Domyślne ustawienia
  python scripts/scraper_main.py --pages 10               # 10 stron Otodom
  python scripts/scraper_main.py --geocoding-limit 200    # Max 200 adresów do geocodingu
  python scripts/scraper_main.py --pages 3 --geocoding-limit 50  # Kombinacja
        """
    )
    
    parser.add_argument(
        '--pages',
        type=int,
        default=5,
        help='Maksymalna liczba stron do scrapowania z Otodom.pl (domyślnie: 5)'
    )
    
    parser.add_argument(
        '--geocoding-limit',
        type=int,
        default=100,
        help='Maksymalna liczba adresów do geocodingu (domyślnie: 100)'
    )
    
    parser.add_argument(
        '--skip-scraping',
        action='store_true',
        help='Pomiń scrapowanie, uruchom tylko parsing i geocoding'
    )
    
    parser.add_argument(
        '--skip-geocoding',
        action='store_true',
        help='Pomiń geocoding, uruchom tylko scrapowanie i parsing'
    )
    
    parser.add_argument(
        '--stats-only',
        action='store_true',
        help='Pokaż tylko statystyki bazy danych'
    )
    
    args = parser.parse_args()
    
    try:
        if args.stats_only:
            # Tylko statystyki
            print_banner()
            stats = get_database_stats()
            print_stats("AKTUALNE STATYSTYKI", stats)
            return
        
        # Walidacja argumentów
        if args.pages < 1 or args.pages > 20:
            print("❌ Liczba stron musi być między 1 a 20")
            sys.exit(1)
            
        if args.geocoding_limit < 1 or args.geocoding_limit > 1000:
            print("❌ Limit geocodingu musi być między 1 a 1000")
            sys.exit(1)
        
        # Uruchom pipeline
        if args.skip_scraping and args.skip_geocoding:
            print("❌ Nie można pominąć zarówno scrapowania jak i geocodingu")
            sys.exit(1)
        
        # Modyfikowany pipeline
        if args.skip_scraping:
            print_banner()
            print("⏭️ Pomijam scrapowanie - uruchamiam tylko parsing i geocoding")
            
            success = True
            if run_parsing_phase():
                if not args.skip_geocoding:
                    success = run_geocoding_phase(args.geocoding_limit)
            else:
                success = False
                
        elif args.skip_geocoding:
            print_banner()
            print("⏭️ Pomijam geocoding - uruchamiam tylko scrapowanie i parsing")
            
            listings = run_scraping_phase(args.pages)
            success = False
            
            if listings:
                saved_count = run_saving_phase(listings)
                if saved_count >= 0:
                    success = run_parsing_phase()
        else:
            # Pełny pipeline
            success = run_complete_pipeline(
                max_pages=args.pages,
                max_geocoding_addresses=args.geocoding_limit
            )
        
        # Kod wyjścia
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Pipeline przerwany przez użytkownika")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Błąd krytyczny w pipeline: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 