#!/usr/bin/env python3
"""
TEST POPRAWKI NA RZECZYWISTYCH DANYCH Z BAZY
"""
from address_parser import get_listings_locations, parse_location_string

def test_real_data():
    """Test poprawki na rzeczywistych danych z bazy"""
    
    print('🔍 TEST POPRAWKI NA RZECZYWISTYCH DANYCH Z BAZY')
    print('='*60)
    
    # Pobierz pierwsze 15 lokalizacji z bazy
    locations = get_listings_locations()[:15]
    
    if not locations:
        print('❌ Brak danych w bazie')
        return
    
    print(f'📊 Testuje na {len(locations)} lokalizacjach z bazy')
    print('='*60)
    
    improved_count = 0
    
    for i, (listing_id, location) in enumerate(locations, 1):
        if not location:
            continue
            
        print(f'\n{i}. "{location}"')
        parsed = parse_location_string(location)
        
        city = parsed.get('city', 'brak')
        district = parsed.get('district', 'brak')
        
        print(f'   🏙️ Miasto: {city}')
        print(f'   🏘️ Dzielnica: {district}')
        
        # Sprawdź czy poprawka pomogła
        if city != 'brak' and district == 'brak':
            print(f'   ✅ POPRAWKA: Miasto uzupełnione')
            improved_count += 1
        elif city != 'brak' and district != 'brak':
            print(f'   ℹ️ Oba pola wypełnione')
        else:
            print(f'   ⚠️ Brak miasta')
    
    print(f'\n📈 PODSUMOWANIE:')
    print(f'   🔧 Poprawek zastosowanych: {improved_count}')
    print(f'   📊 Procent poprawy: {improved_count/len(locations)*100:.1f}%')

if __name__ == "__main__":
    test_real_data() 