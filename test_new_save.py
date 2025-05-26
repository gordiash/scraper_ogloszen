#!/usr/bin/env python3
"""
Test zapisu nowego ogłoszenia z prawidłowymi area i rooms
"""
from otodom_only_scraper import get_otodom_listings
from supabase_utils import save_listing, get_supabase_client
import datetime

print("🧪 TEST ZAPISU NOWEGO OGŁOSZENIA")
print("="*60)

# Pobierz kilka ogłoszeń
listings = get_otodom_listings(max_pages=1)

if listings:
    # Weź pierwsze ogłoszenie z dobrymi danymi
    test_listing = None
    for listing in listings:
        if (listing.get('area') and listing.get('rooms') and 
            listing.get('area') != 'None' and listing.get('rooms') != 'None'):
            test_listing = listing.copy()  # Kopiuj żeby nie zmieniać oryginału
            break
    
    if test_listing:
        # Zmodyfikuj URL żeby był unikalny
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        original_url = test_listing.get('url', '')
        test_listing['url'] = f"{original_url}?test_fixed_columns={timestamp}"
        test_listing['title'] = f"[TEST FIXED] {test_listing.get('title', '')[:40]}..."
        
        print(f"📋 DANE DO ZAPISU:")
        print(f"   Tytuł: {test_listing.get('title')}")
        print(f"   📐 Area: '{test_listing.get('area')}' (type: {type(test_listing.get('area'))})")
        print(f"   🚪 Rooms: '{test_listing.get('rooms')}' (type: {type(test_listing.get('rooms'))})")
        print(f"   💰 Price: {test_listing.get('price')}")
        print(f"   📍 Location: {test_listing.get('location', '')[:40]}...")
        
        # Zapisz do bazy
        print(f"\n💾 ZAPIS DO BAZY:")
        success = save_listing(test_listing, require_complete=False)
        
        if success:
            print("✅ Zapis się udał!")
            
            # Sprawdź co zostało faktycznie zapisane
            supabase = get_supabase_client()
            result = supabase.table('listings').select('*').eq('url', test_listing['url']).execute()
            
            if result.data:
                saved = result.data[0]
                print(f"\n📊 CO ZOSTAŁO ZAPISANE W BAZIE:")
                print(f"   ID: {saved.get('id')}")
                print(f"   Tytuł: {saved.get('title')}")
                print(f"   📐 Area: '{saved.get('area')}' ({'✅' if saved.get('area') else '❌'})")
                print(f"   🚪 Rooms: '{saved.get('rooms')}' ({'✅' if saved.get('rooms') else '❌'})")
                print(f"   💰 Price: {saved.get('price')}")
                print(f"   📍 Location: {saved.get('location', '')[:40]}...")
                
                # Sprawdź czy area i rooms są prawidłowe
                area_ok = saved.get('area') and saved.get('area') != 'None' and saved.get('area') != ''
                rooms_ok = saved.get('rooms') and saved.get('rooms') != 'None' and saved.get('rooms') != ''
                
                print(f"\n🎯 WYNIK TESTU:")
                print(f"   📐 Area zapisana prawidłowo: {'✅' if area_ok else '❌'}")
                print(f"   🚪 Rooms zapisane prawidłowo: {'✅' if rooms_ok else '❌'}")
                
                if area_ok and rooms_ok:
                    print(f"   🎉 SUCCESS: Problem z area i rooms został naprawiony!")
                else:
                    print(f"   ❌ PROBLEM: Nadal są problemy z zapisem area/rooms")
                
                # Usuń testowy rekord
                supabase.table('listings').delete().eq('url', test_listing['url']).execute()
                print(f"\n🗑️ Usunięto testowy rekord")
            else:
                print("❌ Nie znaleziono zapisanego rekordu")
        else:
            print("❌ Zapis się nie udał")
    else:
        print("❌ Nie znaleziono ogłoszenia z dobrymi danymi")
else:
    print("❌ Nie pobrano żadnych ogłoszeń")

print("="*60) 