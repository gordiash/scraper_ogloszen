#!/usr/bin/env python3
"""
TEST WYKRYWANIA DUPLIKATÓW OGŁOSZEŃ
Demonstracja funkcjonalności deduplikacji między portalami
"""
import logging
from datetime import datetime
from utils import deduplicate_listings, find_duplicates, generate_duplicate_report

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_data():
    """Tworzy dane testowe z duplikatami"""
    test_listings = [
        # Ogłoszenie 1 - Original (Otodom)
        {
            "title": "Mieszkanie 3-pokojowe, 65m², Warszawa-Mokotów",
            "price": 850000.0,
            "price_currency": "zł",
            "price_original": "850 000 zł",
            "location": "Warszawa, Mokotów",
            "url": "https://otodom.pl/mieszkanie-1",
            "area": "65 m²",
            "rooms": "3 pokoje",
            "description": "Piękne mieszkanie w centrum Mokotowa",
            "source": "otodom.pl",
            "scraped_at": datetime.now().isoformat()
        },
        
        # Ogłoszenie 2 - Duplikat z OLX (to samo mieszkanie)
        {
            "title": "3 pokojowe mieszkanie 65m2 Mokotów",
            "price": 850000.0,
            "price_currency": "zł",
            "price_original": "850 000 zł",
            "location": "Warszawa Mokotów",
            "url": "https://olx.pl/mieszkanie-mokotow-123",
            "area": "65m2",
            "rooms": "3 pok",
            "description": "Mieszkanie na sprzedaż",
            "source": "olx.pl",
            "scraped_at": datetime.now().isoformat()
        },
        
        # Ogłoszenie 3 - Duplikat z Gratka (to samo mieszkanie, trochę inna cena)
        {
            "title": "Sprzedam mieszkanie 3-pokojowe 65m² Mokotów",
            "price": 855000.0,
            "price_currency": "zł", 
            "price_original": "855 000 zł",
            "location": "Warszawa, Mokotów",
            "url": "https://gratka.pl/mieszkanie-mokotow-456",
            "area": "65 m²",
            "rooms": "3",
            "description": "",
            "source": "gratka.pl",
            "scraped_at": datetime.now().isoformat()
        },
        
        # Ogłoszenie 4 - Podobne ale inne mieszkanie
        {
            "title": "Mieszkanie 3-pokojowe, 70m², Warszawa-Mokotów",
            "price": 920000.0,
            "price_currency": "zł",
            "price_original": "920 000 zł",
            "location": "Warszawa, Mokotów",
            "url": "https://otodom.pl/mieszkanie-2", 
            "area": "70 m²",
            "rooms": "3 pokoje",
            "description": "Inne mieszkanie w Mokotowie",
            "source": "otodom.pl",
            "scraped_at": datetime.now().isoformat()
        },
        
        # Ogłoszenie 5 - Kompletnie inne
        {
            "title": "Kawalerka 25m², Warszawa-Wola",
            "price": 450000.0,
            "price_currency": "zł",
            "price_original": "450 000 zł",
            "location": "Warszawa, Wola",
            "url": "https://domiporta.pl/kawalerka-wola",
            "area": "25 m²",
            "rooms": "1 pokój",
            "description": "Mała kawalerka",
            "source": "domiporta.pl",
            "scraped_at": datetime.now().isoformat()
        },
        
        # Ogłoszenie 6 - Duplikat kawalerki z innego portalu
        {
            "title": "1-pokojowe mieszkanie 25m2 Wola centrum",
            "price": 450000.0,
            "price_currency": "zł",
            "price_original": "450.000 zł",
            "location": "Warszawa Wola",
            "url": "https://metrohouse.pl/kawalerka-wola-789",
            "area": "25m2",
            "rooms": "1",
            "description": "Kawalerka blisko metra",
            "source": "metrohouse.pl",
            "scraped_at": datetime.now().isoformat()
        }
    ]
    
    return test_listings

def test_duplicate_detection():
    """Testuje wykrywanie duplikatów"""
    print("="*80)
    print("🔍 TEST WYKRYWANIA DUPLIKATÓW OGŁOSZEŃ")
    print("="*80)
    
    # Stwórz dane testowe
    test_listings = create_test_data()
    
    print(f"📋 Utworzono {len(test_listings)} testowych ogłoszeń:")
    for i, listing in enumerate(test_listings, 1):
        title = listing['title']
        source = listing['source']
        price = listing['price']
        print(f"  {i}. {title[:50]}... ({source}) - {price:,.0f} zł")
    
    print(f"\n{'='*60}")
    print("🔍 ANALIZA DUPLIKATÓW")
    print("="*60)
    
    # Test z różnymi progami podobieństwa
    thresholds = [60.0, 75.0, 85.0]
    
    for threshold in thresholds:
        print(f"\n--- Próg podobieństwa: {threshold}% ---")
        
        unique_listings, duplicates = find_duplicates(test_listings, threshold)
        
        print(f"✅ Unikalne ogłoszenia: {len(unique_listings)}")
        print(f"🔄 Duplikaty: {len(duplicates)}")
        
        if duplicates:
            print("\n📊 Znalezione duplikaty:")
            for dup in duplicates:
                original_title = ""
                # Znajdź oryginał po URL
                for unique in unique_listings:
                    if unique.get('url') == dup.get('duplicate_of'):
                        original_title = unique.get('title', '')[:30]
                        break
                
                dup_title = dup.get('title', '')[:30]
                similarity = dup.get('similarity_score', 0)
                source = dup.get('source', '')
                
                print(f"  • {dup_title}... ({source}) - {similarity:.1f}% podobny do: {original_title}...")
    
    print(f"\n{'='*60}")
    print("🧹 TEST DEDUPLIKACJI")  
    print("="*60)
    
    # Test deduplikacji z zachowaniem najlepszego źródła
    deduplicated = deduplicate_listings(test_listings, similarity_threshold=75.0, keep_best_source=True)
    
    print(f"\n📋 Po deduplikacji (zachowano najlepsze źródła):")
    print(f"   Przed: {len(test_listings)} ogłoszeń")
    print(f"   Po: {len(deduplicated)} ogłoszeń")
    print(f"   Usunięto: {len(test_listings) - len(deduplicated)} duplikatów")
    
    print(f"\n✅ Końcowa lista unikatowych ogłoszeń:")
    for i, listing in enumerate(deduplicated, 1):
        title = listing['title']
        source = listing['source']
        price = listing['price']
        print(f"  {i}. {title[:50]}... ({source}) - {price:,.0f} zł")
    
    # Wygeneruj raport
    _, all_duplicates = find_duplicates(test_listings, 75.0)
    report = generate_duplicate_report(all_duplicates)
    
    print(f"\n{'='*60}")
    print(report)
    
    return deduplicated

def test_real_scrapers():
    """Testuje deduplikację na prawdziwych danych ze scraperów"""
    print(f"\n{'='*80}")
    print("🌐 TEST DEDUPLIKACJI NA PRAWDZIWYCH DANYCH")
    print("="*80)
    
    try:
        # Pobierz dane z kilku scraperów
        all_listings = []
        
        scrapers_to_test = [
            ("OLX.pl", "scrapers.olx", "get_olx_listings"),
            ("Otodom.pl", "scrapers.otodom", "get_otodom_listings"),
        ]
        
        for name, module_name, func_name in scrapers_to_test:
            try:
                print(f"\n⏳ Pobieranie z {name}...")
                module = __import__(module_name, fromlist=[func_name])
                scraper_func = getattr(module, func_name)
                
                listings = scraper_func(max_pages=1)
                print(f"✅ {name}: {len(listings)} ogłoszeń")
                all_listings.extend(listings)
                
            except Exception as e:
                print(f"⚠️ {name}: Błąd - {e}")
        
        if all_listings:
            print(f"\n📊 Łącznie pobrano: {len(all_listings)} ogłoszeń")
            
            # Deduplikacja
            deduplicated = deduplicate_listings(all_listings, similarity_threshold=80.0)
            
            print(f"\n🧹 Po deduplikacji:")
            print(f"   Przed: {len(all_listings)} ogłoszeń")  
            print(f"   Po: {len(deduplicated)} ogłoszeń")
            print(f"   Usunięto: {len(all_listings) - len(deduplicated)} potencjalnych duplikatów")
            
            # Pokaż przykłady
            if len(deduplicated) > 0:
                print(f"\n📋 Przykłady unikatowych ogłoszeń:")
                for i, listing in enumerate(deduplicated[:3], 1):
                    title = listing.get('title', 'Brak tytułu')
                    source = listing.get('source', '')
                    price = listing.get('price')
                    
                    print(f"  {i}. {title[:60]}...")
                    print(f"     Źródło: {source}")
                    if price:
                        currency = listing.get('price_currency', 'zł')
                        print(f"     Cena: {price:,.0f} {currency}")
        else:
            print("❌ Nie udało się pobrać żadnych ogłoszeń")
            
    except Exception as e:
        print(f"❌ Błąd w teście: {e}")
        logger.error(f"Błąd w test_real_scrapers: {e}", exc_info=True)

if __name__ == "__main__":
    try:
        # Test z danymi przykładowymi
        deduplicated = test_duplicate_detection()
        
        # Test z prawdziwymi danymi
        test_real_scrapers()
        
        print(f"\n{'='*80}")
        print("🎉 SUKCES! Testy wykrywania duplikatów zakończone!")
        print("="*80)
        print("💡 Jak używać:")
        print("   • from utils import deduplicate_listings")
        print("   • unique_listings = deduplicate_listings(all_listings)")
        print("   • Dostosuj próg podobieństwa (75% domyślnie)")
        print("   • Włącz/wyłącz priorytet najlepszych źródeł")
        
    except KeyboardInterrupt:
        print("\n⚠️ Test przerwany przez użytkownika")
    except Exception as e:
        print(f"\n❌ Błąd w testach: {e}")
        logging.error(f"Błąd w test_deduplicate: {e}", exc_info=True) 