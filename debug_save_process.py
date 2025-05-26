#!/usr/bin/env python3
"""
DEBUG PROCESU ZAPISU DO BAZY DANYCH
"""
from otodom_only_scraper import get_otodom_listings
from supabase_utils import save_listing, get_table_columns

print("🔍 DEBUG PROCESU ZAPISU DO BAZY")
print("="*60)

# Pobierz jedno ogłoszenie
listings = get_otodom_listings(max_pages=1)

if listings:
    listing = listings[0]
    print(f"📋 Testowane ogłoszenie:")
    print(f"   Tytuł: {listing.get('title', '')[:50]}...")
    print(f"   Area: '{listing.get('area')}' (type: {type(listing.get('area'))})")
    print(f"   Rooms: '{listing.get('rooms')}' (type: {type(listing.get('rooms'))})")
    
    # Sprawdź kolumny tabeli
    print(f"\n📊 Kolumny w tabeli:")
    columns = get_table_columns("listings")
    print(f"   {columns}")
    
    # Sprawdź filtrowanie danych
    print(f"\n🔍 FILTROWANIE DANYCH:")
    
    all_possible_data = {
        "title": listing.get("title"),
        "price": int(float(listing.get("price"))) if listing.get("price") is not None else None,
        "price_currency": listing.get("price_currency", "zł"),
        "price_original": listing.get("price_original"),
        "location": listing.get("location"),
        "url": listing.get("url"),
        "area": listing.get("area"),
        "rooms": listing.get("rooms"),
        "description": listing.get("description"),
        "source": listing.get("source", "otodom.pl")
    }
    
    print("Wszystkie dane przed filtrowaniem:")
    for key, value in all_possible_data.items():
        print(f"   {key}: '{value}' (type: {type(value)})")
    
    # Filtruj dane jak w funkcji save_listing
    data_to_save = {}
    for column, value in all_possible_data.items():
        in_columns = column in columns
        not_none = value is not None
        not_empty = value != ""
        not_str_none = str(value) != "None"
        
        print(f"\n🔸 {column}:")
        print(f"   Wartość: '{value}'")
        print(f"   W kolumnach: {in_columns}")
        print(f"   Nie None: {not_none}")
        print(f"   Nie empty: {not_empty}")
        print(f"   Nie str 'None': {not_str_none}")
        print(f"   str(value): '{str(value)}'")
        
        if in_columns and not_none and not_empty and not_str_none:
            data_to_save[column] = value
            print(f"   ✅ DODANO do zapisu")
        else:
            print(f"   ❌ ODRZUCONO")
    
    print(f"\n💾 DANE DO ZAPISU:")
    for key, value in data_to_save.items():
        print(f"   {key}: '{value}'")
    
    print(f"\n🧪 TEST ZAPISU (bez faktycznego zapisu):")
    print(f"Czy 'area' będzie zapisane: {'area' in data_to_save}")
    print(f"Czy 'rooms' będzie zapisane: {'rooms' in data_to_save}")
    
else:
    print("❌ Brak ogłoszeń do testowania")

print("="*60) 