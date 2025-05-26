#!/usr/bin/env python3
"""
Sprawdzenie kompletności najnowszych zapisanych danych
"""
from supabase_utils import get_supabase_client

def check_latest_data():
    """Sprawdź kompletność najnowszych danych"""
    print("🔍 SPRAWDZANIE KOMPLETNOŚCI NAJNOWSZYCH DANYCH")
    print("=" * 60)
    
    supabase = get_supabase_client()
    result = supabase.table('listings').select('title, price, area, rooms, location, scraped_at').order('scraped_at', desc=True).limit(5).execute()
    
    if result.data:
        print(f"📊 Najnowsze {len(result.data)} zapisanych ogłoszeń:")
        print("-" * 60)
        
        for i, listing in enumerate(result.data, 1):
            title = listing.get('title', '')[:35]
            price = listing.get('price', 0)
            area = listing.get('area', '')
            rooms = listing.get('rooms', '')
            location = listing.get('location', '')[:25]
            scraped_at = listing.get('scraped_at', '')[:16]
            
            print(f"{i}. {title}...")
            print(f"   🕐 Scraped: {scraped_at}")
            print(f"   💰 Cena: {price:,} zł {'✅' if price > 0 else '❌'}")
            print(f"   📐 Area: '{area}' {'✅' if area else '❌'}")
            print(f"   🚪 Rooms: '{rooms}' {'✅' if rooms else '❌'}")
            print(f"   📍 Location: '{location}...' {'✅' if location else '❌'}")
            
            # Sprawdź kompletność
            complete = all([price > 0, area, rooms, location])
            print(f"   🎯 Kompletne: {'✅' if complete else '❌'}")
            print()
        
        # Statystyki kompletności
        complete_count = 0
        for listing in result.data:
            if all([
                listing.get('price', 0) > 0,
                listing.get('area', ''),
                listing.get('rooms', ''),
                listing.get('location', '')
            ]):
                complete_count += 1
        
        print("=" * 60)
        print(f"📈 KOMPLETNOŚĆ DANYCH: {complete_count}/{len(result.data)} ({complete_count/len(result.data)*100:.1f}%)")
        
    else:
        print("❌ Brak danych w bazie")

if __name__ == "__main__":
    check_latest_data() 