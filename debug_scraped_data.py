#!/usr/bin/env python3
"""
DEBUG DANYCH POBIERANYCH PRZEZ SCRAPER
"""
from otodom_only_scraper import get_otodom_listings

print("🔍 DEBUG DANYCH ZE SCRAPERA")
print("="*60)

# Pobierz kilka ogłoszeń
listings = get_otodom_listings(max_pages=1)

if listings:
    print(f"📊 Pobrano {len(listings)} ogłoszeń. Sprawdzam pierwsze 3:")
    print("-"*60)
    
    for i, listing in enumerate(listings[:3], 1):
        print(f"\n{i}. {listing.get('title', 'Brak tytułu')[:50]}...")
        print(f"   💰 Price: '{listing.get('price')}' (type: {type(listing.get('price'))})")
        print(f"   📍 Location: '{listing.get('location')}'")
        print(f"   📐 Area: '{listing.get('area')}' (type: {type(listing.get('area'))})")
        print(f"   🚪 Rooms: '{listing.get('rooms')}' (type: {type(listing.get('rooms'))})")
        print(f"   🔗 URL: '{listing.get('url')[:60]}...'")
        print(f"   📄 Description: '{listing.get('description')[:30]}...'")
        
        # Sprawdź czy to None, pusty string czy inna wartość
        area = listing.get('area')
        rooms = listing.get('rooms')
        
        if area is None:
            print(f"   ⚠️ Area is None")
        elif area == "":
            print(f"   ⚠️ Area is empty string")
        elif str(area) == "None":
            print(f"   ⚠️ Area is string 'None'")
        else:
            print(f"   ✅ Area has value: '{area}'")
            
        if rooms is None:
            print(f"   ⚠️ Rooms is None")
        elif rooms == "":
            print(f"   ⚠️ Rooms is empty string")
        elif str(rooms) == "None":
            print(f"   ⚠️ Rooms is string 'None'")
        else:
            print(f"   ✅ Rooms has value: '{rooms}'")
    
    # Statystyki area i rooms
    print(f"\n📊 STATYSTYKI:")
    print("-"*40)
    
    area_stats = {}
    rooms_stats = {}
    
    for listing in listings:
        area = listing.get('area')
        rooms = listing.get('rooms')
        
        if area is None:
            area_key = "None"
        elif area == "":
            area_key = "empty_string"
        elif str(area) == "None":
            area_key = "string_None"
        else:
            area_key = "has_value"
        area_stats[area_key] = area_stats.get(area_key, 0) + 1
        
        if rooms is None:
            rooms_key = "None"
        elif rooms == "":
            rooms_key = "empty_string"  
        elif str(rooms) == "None":
            rooms_key = "string_None"
        else:
            rooms_key = "has_value"
        rooms_stats[rooms_key] = rooms_stats.get(rooms_key, 0) + 1
    
    print("📐 Area stats:")
    for key, count in area_stats.items():
        print(f"   {key}: {count}")
    
    print("🚪 Rooms stats:")
    for key, count in rooms_stats.items():
        print(f"   {key}: {count}")
    
else:
    print("❌ Brak ogłoszeń do sprawdzenia")

print("="*60) 