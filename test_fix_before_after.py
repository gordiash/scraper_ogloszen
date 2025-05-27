#!/usr/bin/env python3
"""
TEST POPRAWKI: PRZED I PO
"""
from address_parser import get_supabase_client, parse_location_string

def test_fix_before_after():
    """Test pokazujący różnicę przed i po poprawce"""
    
    print('🔧 TEST POPRAWKI: PRZED I PO')
    print('='*60)
    
    try:
        client = get_supabase_client()
        
        # Pobierz 10 adresów bez miasta
        result = client.table('addresses').select('id, full_address, city, district').is_('city', 'null').limit(10).execute()
        
        if not result.data:
            print('✅ Wszystkie adresy mają wypełnione miasto!')
            return
        
        print(f'📊 Testuje poprawkę na {len(result.data)} adresach bez miasta:')
        print('='*60)
        
        improved_count = 0
        
        for i, addr in enumerate(result.data, 1):
            print(f'{i}. "{addr["full_address"]}"')
            print(f'   PRZED: city={addr["city"]}, district={addr["district"]}')
            
            # Parsuj z nową logiką
            parsed = parse_location_string(addr["full_address"])
            new_city = parsed.get("city")
            new_district = parsed.get("district")
            
            print(f'   PO:    city={new_city}, district={new_district}')
            
            # Sprawdź czy poprawka pomogła
            if new_city and not addr["city"]:
                print(f'   ✅ POPRAWKA: Miasto uzupełnione z "{addr["district"]}" → "{new_city}"')
                improved_count += 1
            else:
                print(f'   ⚠️ Brak poprawy')
            print()
        
        print(f'📈 PODSUMOWANIE:')
        print(f'   🔧 Poprawek zastosowanych: {improved_count}/{len(result.data)}')
        print(f'   📊 Procent poprawy: {improved_count/len(result.data)*100:.1f}%')
        
    except Exception as e:
        print(f'❌ Błąd: {e}')

if __name__ == "__main__":
    test_fix_before_after() 