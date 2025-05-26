#!/usr/bin/env python3
"""
SPRAWDZENIE NAJNOWSZYCH REKORDÓW
"""
from supabase_utils import get_supabase_client

print("📊 SPRAWDZANIE NAJNOWSZYCH REKORDÓW")
print("="*60)

supabase = get_supabase_client()
result = supabase.table('listings').select('*').order('id', desc=True).limit(5).execute()

if result.data:
    print(f"🔍 Ostatnie {len(result.data)} rekordów w bazie:")
    print("-"*60)
    
    for i, record in enumerate(result.data, 1):
        title = record.get('title', '')[:40]
        area = record.get('area')
        rooms = record.get('rooms')
        price = record.get('price')
        
        print(f"{i}. {title}...")
        print(f"   💰 Price: {price}")
        print(f"   📐 Area: '{area}' ({'✅' if area else '❌'})")
        print(f"   🚪 Rooms: '{rooms}' ({'✅' if rooms else '❌'})")
        print(f"   🎯 Kompletne: {'✅' if area and rooms and price else '❌'}")
        print()
    
    # Statystyki
    with_area = sum(1 for r in result.data if r.get('area'))
    with_rooms = sum(1 for r in result.data if r.get('rooms'))
    with_price = sum(1 for r in result.data if r.get('price'))
    
    print("📈 STATYSTYKI NAJNOWSZYCH REKORDÓW:")
    print(f"   📐 Z area: {with_area}/{len(result.data)} ({with_area/len(result.data)*100:.1f}%)")
    print(f"   🚪 Z rooms: {with_rooms}/{len(result.data)} ({with_rooms/len(result.data)*100:.1f}%)")
    print(f"   💰 Z price: {with_price}/{len(result.data)} ({with_price/len(result.data)*100:.1f}%)")
    
else:
    print("❌ Brak rekordów w bazie")

print("="*60) 