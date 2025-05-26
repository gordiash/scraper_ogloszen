#!/usr/bin/env python3
"""
Porównanie danych po czasie scrapingu - stare vs nowe
"""
from supabase_utils import get_supabase_client

print("📊 PORÓWNANIE DANYCH PO CZASIE SCRAPINGU")
print("="*80)

supabase = get_supabase_client()
result = supabase.table('listings').select('title, area, rooms, scraped_at').order('scraped_at', desc=True).limit(15).execute()

if result.data:
    print("🕐 NAJNOWSZE REKORDY (z czasem scrapingu):")
    print("-"*80)
    
    for i, record in enumerate(result.data, 1):
        title = record.get('title', '')[:45]
        area = record.get('area')
        rooms = record.get('rooms')
        scraped_at = record.get('scraped_at', '')[:16]
        
        # Sprawdź czy to stare dane (z 'None') czy nowe (prawidłowe)
        area_status = "✅" if area and area != 'None' else "❌"
        rooms_status = "✅" if rooms and rooms != 'None' else "❌"
        
        print(f"{i:2d}. {scraped_at} | {area_status} Area: '{area}' | {rooms_status} Rooms: '{rooms}'")
        print(f"     {title}...")
        print()
        
        # Pokaż tylko pierwsze 10 dla czytelności
        if i >= 10:
            break
    
    # Statystyki
    good_area = len([r for r in result.data if r.get('area') and r.get('area') != 'None'])
    good_rooms = len([r for r in result.data if r.get('rooms') and r.get('rooms') != 'None'])
    
    print("="*80)
    print("📈 STATYSTYKI:")
    print(f"   📐 Prawidłowe area:  {good_area}/{len(result.data)} ({good_area/len(result.data)*100:.1f}%)")
    print(f"   🚪 Prawidłowe rooms: {good_rooms}/{len(result.data)} ({good_rooms/len(result.data)*100:.1f}%)")
    
    # Sprawdź kiedy nastąpiła poprawa
    old_data = [r for r in result.data if r.get('area') == 'None']
    new_data = [r for r in result.data if r.get('area') and r.get('area') != 'None']
    
    if old_data and new_data:
        oldest_good = min([r.get('scraped_at', '') for r in new_data])
        newest_bad = max([r.get('scraped_at', '') for r in old_data])
        
        print(f"\n🔄 MOMENT NAPRAWY:")
        print(f"   ❌ Ostatnie złe dane:      {newest_bad[:16]}")
        print(f"   ✅ Pierwsze dobre dane:    {oldest_good[:16]}")
        print(f"   🎯 Problem został naprawiony między tymi momentami!")
    
else:
    print("❌ Brak danych do porównania")

print("="*80) 