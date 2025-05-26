#!/usr/bin/env python3
"""
TEST ZAPISU POJEDYNCZEGO OGŁOSZENIA
"""
from otodom_only_scraper import get_otodom_listings
from supabase_utils import save_listing

print("🧪 TEST ZAPISU POJEDYNCZEGO OGŁOSZENIA")
print("="*60)

# Pobierz kilka ogłoszeń
listings = get_otodom_listings(max_pages=1)

if listings:
    # Znajdź ogłoszenie z pełnymi danymi
    complete_listing = None
    for listing in listings:
        if (listing.get('area') and listing.get('rooms') and 
            listing.get('area') != '' and listing.get('rooms') != '' and
            str(listing.get('area')) != 'None' and str(listing.get('rooms')) != 'None'):
            complete_listing = listing
            break
    
    if complete_listing:
        print(f"📋 Znaleziono ogłoszenie z pełnymi danymi:")
        print(f"   Tytuł: {complete_listing.get('title', '')[:50]}...")
        print(f"   Area: '{complete_listing.get('area')}'")
        print(f"   Rooms: '{complete_listing.get('rooms')}'")
        print(f"   Price: {complete_listing.get('price')}")
        print(f"   Location: {complete_listing.get('location', '')[:50]}...")
        print(f"   URL: {complete_listing.get('url', '')[:50]}...")
        
        # Dodaj unikalny timestamp do URL żeby uniknąć duplikatów
        import datetime
        original_url = complete_listing.get('url', '')
        test_url = f"{original_url}?test={datetime.datetime.now().timestamp()}"
        complete_listing['url'] = test_url
        complete_listing['title'] = f"[TEST] {complete_listing.get('title', '')}"
        
        print(f"\n💾 PRÓBA ZAPISU:")
        result = save_listing(complete_listing, require_complete=False)
        
        if result:
            print("✅ Zapis się udał!")
            
            # Sprawdź co zostało zapisane
            from supabase_utils import get_supabase_client
            supabase = get_supabase_client()
            saved_result = supabase.table('listings').select('*').eq('url', test_url).execute()
            
            if saved_result.data:
                saved_record = saved_result.data[0]
                print(f"\n📊 CO ZOSTAŁO ZAPISANE:")
                print(f"   ID: {saved_record.get('id')}")
                print(f"   Title: {saved_record.get('title')}")
                print(f"   Area: '{saved_record.get('area')}' (type: {type(saved_record.get('area'))})")
                print(f"   Rooms: '{saved_record.get('rooms')}' (type: {type(saved_record.get('rooms'))})")
                print(f"   Price: {saved_record.get('price')}")
                
                # Usuń testowy rekord
                supabase.table('listings').delete().eq('url', test_url).execute()
                print(f"\n🗑️ Usunięto testowy rekord")
            else:
                print("❌ Nie znaleziono zapisanego rekordu")
        else:
            print("❌ Zapis się nie udał")
    else:
        print("❌ Nie znaleziono ogłoszenia z pełnymi danymi")
        print("📊 Sprawdzam pierwsze 3 ogłoszenia:")
        for i, listing in enumerate(listings[:3], 1):
            print(f"\n{i}. {listing.get('title', '')[:30]}...")
            print(f"   Area: '{listing.get('area')}' (type: {type(listing.get('area'))})")
            print(f"   Rooms: '{listing.get('rooms')}' (type: {type(listing.get('rooms'))})")
else:
    print("❌ Brak ogłoszeń do testowania")

print("="*60) 