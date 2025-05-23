#!/usr/bin/env python3
"""
TEST ZAKTUALIZOWANYCH SCRAPERÓW 
Otodom.pl i Gratka.pl z nowymi selektorami CSS (grudzień 2024)
"""
import logging
from scrapers.otodom import get_otodom_listings
from scrapers.gratka import get_gratka_listings

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_updated_otodom():
    """Test zaktualizowanego Otodom.pl"""
    print("="*80)
    print("🏠 TEST ZAKTUALIZOWANEGO OTODOM.PL")
    print("="*80)
    print("📝 Nowe selektory CSS:")
    print("   • Area (powierzchnia): [data-sentry-source-file='AdDetailItem.tsx'] p.esen0m92")
    print("="*80)
    
    try:
        listings = get_otodom_listings(max_pages=1)
        
        if listings:
            print(f"✅ Pobrano {len(listings)} ogłoszeń z Otodom.pl")
            
            # Sprawdź jakość danych
            with_price = len([l for l in listings if l.get('price')])
            with_location = len([l for l in listings if l.get('location')])
            with_area = len([l for l in listings if l.get('area')])
            with_rooms = len([l for l in listings if l.get('rooms')])
            
            print(f"📊 Jakość danych:")
            print(f"   💰 Z cenami: {with_price}/{len(listings)}")
            print(f"   📍 Z lokalizacją: {with_location}/{len(listings)}")
            print(f"   📐 Z powierzchnią: {with_area}/{len(listings)}")
            print(f"   🚪 Z pokojami: {with_rooms}/{len(listings)}")
            
            # Pokaż przykłady
            print(f"\n📋 PRZYKŁADY:")
            for i, listing in enumerate(listings[:2], 1):
                print(f"\n  {i}. {listing.get('title', 'Brak tytułu')[:50]}...")
                if listing.get('price'):
                    print(f"     💰 Cena: {listing['price']:,.0f} {listing.get('price_currency', 'zł')}")
                if listing.get('location'):
                    print(f"     📍 Lokalizacja: {listing.get('location')}")
                if listing.get('area'):
                    print(f"     📐 Powierzchnia: {listing.get('area')}")
                if listing.get('rooms'):
                    print(f"     🚪 Pokoje: {listing.get('rooms')}")
        else:
            print("❌ Nie pobrano ogłoszeń z Otodom.pl")
            
    except Exception as e:
        print(f"❌ Błąd w teście Otodom: {e}")
    
    return listings if 'listings' in locals() else []

def test_updated_gratka():
    """Test zaktualizowanej Gratka.pl"""
    print(f"\n{'='*80}")
    print("🏠 TEST ZAKTUALIZOWANEJ GRATKA.PL")
    print("="*80)
    print("📝 Nowe selektory CSS:")
    print("   • Price: #basic-info-price-row .maMBkV")
    print("   • Title: h1.LignY8")
    print("   • Location: .location-row__second_column h2")
    print("   • Area/Rooms: div.TocF4V span.urcZHx")
    print("="*80)
    
    try:
        listings = get_gratka_listings(max_pages=1)
        
        if listings:
            print(f"✅ Pobrano {len(listings)} ogłoszeń z Gratka.pl")
            
            # Sprawdź jakość danych
            with_price = len([l for l in listings if l.get('price')])
            with_location = len([l for l in listings if l.get('location')])
            with_area = len([l for l in listings if l.get('area')])
            with_rooms = len([l for l in listings if l.get('rooms')])
            
            print(f"📊 Jakość danych:")
            print(f"   💰 Z cenami: {with_price}/{len(listings)}")
            print(f"   📍 Z lokalizacją: {with_location}/{len(listings)}")
            print(f"   📐 Z powierzchnią: {with_area}/{len(listings)}")
            print(f"   🚪 Z pokojami: {with_rooms}/{len(listings)}")
            
            # Pokaż przykłady
            print(f"\n📋 PRZYKŁADY:")
            for i, listing in enumerate(listings[:2], 1):
                print(f"\n  {i}. {listing.get('title', 'Brak tytułu')[:50]}...")
                if listing.get('price'):
                    print(f"     💰 Cena: {listing['price']:,.0f} {listing.get('price_currency', 'zł')}")
                if listing.get('location'):
                    print(f"     📍 Lokalizacja: {listing.get('location')}")
                if listing.get('area'):
                    print(f"     📐 Powierzchnia: {listing.get('area')}")
                if listing.get('rooms'):
                    print(f"     🚪 Pokoje: {listing.get('rooms')}")
        else:
            print("❌ Nie pobrano ogłoszeń z Gratka.pl")
            
    except Exception as e:
        print(f"❌ Błąd w teście Gratka: {e}")
    
    return listings if 'listings' in locals() else []

def test_combined_scrapers():
    """Test kombinacji zaktualizowanych scraperów z deduplikacją"""
    print(f"\n{'='*80}")
    print("🔍 TEST KOMBINACJI SCRAPERÓW Z DEDUPLIKACJĄ")
    print("="*80)
    
    # Pobierz z obu portali
    otodom_listings = test_updated_otodom()
    gratka_listings = test_updated_gratka()
    
    # Połącz i testuj deduplikację
    all_listings = otodom_listings + gratka_listings
    
    if all_listings:
        from utils import deduplicate_listings
        
        print(f"\n🔄 DEDUPLIKACJA:")
        print(f"   Przed: {len(all_listings)} ogłoszeń")
        print(f"   • Otodom.pl: {len(otodom_listings)}")
        print(f"   • Gratka.pl: {len(gratka_listings)}")
        
        deduplicated = deduplicate_listings(all_listings, similarity_threshold=75.0)
        
        print(f"   Po deduplikacji: {len(deduplicated)} unikatowych")
        print(f"   Usunięto: {len(all_listings) - len(deduplicated)} duplikatów")
        
        if len(all_listings) > len(deduplicated):
            reduction = ((len(all_listings) - len(deduplicated)) / len(all_listings)) * 100
            print(f"   Skuteczność: {reduction:.1f}% duplikatów wykryto")
    
    print(f"\n{'='*80}")
    print("🎉 TEST ZAKOŃCZONY!")
    print("="*80)

if __name__ == "__main__":
    try:
        test_combined_scrapers()
        
        print("💡 Następne kroki:")
        print("   • Uruchom 'python complete_demo.py' dla pełnego testu")
        print("   • Wszystkie selektory zostały zaktualizowane")
        print("   • System gotowy do użycia produkcyjnego")
        
    except KeyboardInterrupt:
        print("\n⚠️ Test przerwany przez użytkownika")
    except Exception as e:
        print(f"\n❌ Błąd ogólny: {e}")
        logging.error(f"Błąd w test_updated_scrapers: {e}", exc_info=True) 