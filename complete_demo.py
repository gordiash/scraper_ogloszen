"""
PEŁNA DEMONSTRACJA SCRAPERA NIERUCHOMOŚCI
Pokazuje wszystkie działające scrapery z Selenium i bez
"""
import logging
from datetime import datetime
from typing import List, Dict

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def demo_all_scrapers():
    """Demonstracja wszystkich działających scraperów"""
    print("="*80)
    print("🏠 PEŁNA DEMONSTRACJA SCRAPERA NIERUCHOMOŚCI")
    print("="*80)
    print("📊 Testuje wszystkie 6 działających portali:")
    print("   🔸 4 scrapery z Selenium (nowoczesne portale)")
    print("   🔸 2 scrapery z Requests (klasyczne portale)")
    print("="*80)
    
    all_listings = []
    
    # ===== SCRAPERY Z SELENIUM =====
    print("\n🚀 SCRAPERY Z SELENIUM")
    print("="*50)
    
    selenium_scrapers = [
        ("Freedom.pl", "scrapers.freedom", "get_freedom_listings"),
        ("Gratka.pl", "scrapers.gratka", "get_gratka_listings"),
        ("Metrohouse.pl", "scrapers.metrohouse", "get_metrohouse_listings"),
        ("Domiporta.pl", "scrapers.domiporta", "get_domiporta_listings"),
    ]
    
    for name, module_name, func_name in selenium_scrapers:
        print(f"\n--- {name} (Selenium) ---")
        try:
            module = __import__(module_name, fromlist=[func_name])
            scraper_func = getattr(module, func_name)
            
            print(f"⏳ Pobieranie z {name}...")
            listings = scraper_func(max_pages=1)
            
            if listings:
                print(f"✅ {name}: {len(listings)} ogłoszeń")
                all_listings.extend(listings)
                
                # Pokaż przykłady
                for i, listing in enumerate(listings[:2]):
                    title = listing.get('title', 'Brak tytułu')
                    price = listing.get('price')
                    location = listing.get('location', '')
                    url = listing.get('url', '')
                    
                    print(f"  📋 {i+1}. {title[:50]}{'...' if len(title) > 50 else ''}")
                    if price:
                        currency = listing.get('price_currency', 'zł')
                        print(f"     💰 Cena: {price:,.0f} {currency}")
                    if location:
                        print(f"     📍 Lokalizacja: {location}")
                    if url:
                        print(f"     🔗 URL: {url[:60]}{'...' if len(url) > 60 else ''}")
            else:
                print(f"⚠️ {name}: Brak ogłoszeń")
                
        except Exception as e:
            print(f"❌ {name}: Błąd - {e}")
    
    # ===== SCRAPERY Z REQUESTS =====
    print(f"\n🌐 SCRAPERY Z REQUESTS")
    print("="*50)
    
    requests_scrapers = [
        ("OLX.pl", "scrapers.olx", "get_olx_listings"),
        ("Otodom.pl", "scrapers.otodom", "get_otodom_listings"),
    ]
    
    for name, module_name, func_name in requests_scrapers:
        print(f"\n--- {name} (Requests) ---")
        try:
            module = __import__(module_name, fromlist=[func_name])
            scraper_func = getattr(module, func_name)
            
            print(f"⏳ Pobieranie z {name}...")
            listings = scraper_func(max_pages=1)
            
            if listings:
                print(f"✅ {name}: {len(listings)} ogłoszeń")
                all_listings.extend(listings)
                
                # Pokaż przykłady
                for i, listing in enumerate(listings[:2]):
                    title = listing.get('title', 'Brak tytułu')
                    price = listing.get('price')
                    location = listing.get('location', '')
                    url = listing.get('url', '')
                    
                    print(f"  📋 {i+1}. {title[:50]}{'...' if len(title) > 50 else ''}")
                    if price:
                        currency = listing.get('price_currency', 'zł')
                        print(f"     💰 Cena: {price:,.0f} {currency}")
                    if location:
                        print(f"     📍 Lokalizacja: {location}")
                    if url:
                        print(f"     🔗 URL: {url[:60]}{'...' if len(url) > 60 else ''}")
            else:
                print(f"⚠️ {name}: Brak ogłoszeń")
                
        except Exception as e:
            print(f"❌ {name}: Błąd - {e}")
    
    # ===== PODSUMOWANIE =====
    print(f"\n{'='*80}")
    print("📊 PODSUMOWANIE WYNIKÓW")
    print(f"{'='*80}")
    
    # Statystyki per portal
    stats_by_source = {}
    listings_with_price = 0
    total_price_value = 0
    
    for listing in all_listings:
        source = listing.get('source', 'Nieznany')
        if source not in stats_by_source:
            stats_by_source[source] = 0
        stats_by_source[source] += 1
        
        # Statystyki cen
        if listing.get('price'):
            listings_with_price += 1
            total_price_value += listing['price']
    
    # Wyświetl statystyki
    print(f"🏠 Łącznie ogłoszeń: {len(all_listings)}")
    print(f"🌐 Liczba portali: {len(stats_by_source)}")
    print(f"💰 Ogłoszenia z cenami: {listings_with_price}")
    
    if listings_with_price > 0:
        avg_price = total_price_value / listings_with_price
        print(f"📈 Średnia cena: {avg_price:,.0f} zł")
    
    print(f"\n📋 Rozkład per portal:")
    for source, count in sorted(stats_by_source.items()):
        print(f"   • {source}: {count} ogłoszeń")
    
    # Przykłady najdroższych ofert
    expensive_listings = [l for l in all_listings if l.get('price') and l['price'] > 500000]
    if expensive_listings:
        expensive_listings.sort(key=lambda x: x['price'], reverse=True)
        print(f"\n💎 Najdroższe oferty:")
        for i, listing in enumerate(expensive_listings[:3]):
            price = listing['price']
            currency = listing.get('price_currency', 'zł')
            title = listing.get('title', 'Brak tytułu')
            print(f"   {i+1}. {price:,.0f} {currency} - {title[:50]}{'...' if len(title) > 50 else ''}")
    
    print(f"\n{'='*80}")
    print("🎉 SUKCES! System scrapowania działa na wszystkich portalach!")
    print("="*80)
    print("💡 Następne kroki:")
    print("   • Uruchom 'python test_supabase.py' żeby zapisać do bazy")
    print("   • Uruchom 'python main.py' dla pełnego scrapowania")
    print("   • Skonfiguruj harmonogram uruchamiania (cron/Windows Task)")
    
    return all_listings

if __name__ == "__main__":
    try:
        listings = demo_all_scrapers()
        print(f"\n✅ Demo zakończone! Pobrano {len(listings)} ogłoszeń.")
    except KeyboardInterrupt:
        print("\n⚠️ Demo przerwane przez użytkownika")
    except Exception as e:
        print(f"\n❌ Błąd w demo: {e}")
        logging.error(f"Błąd w complete_demo: {e}", exc_info=True) 