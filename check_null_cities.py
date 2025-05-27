#!/usr/bin/env python3
"""
SPRAWDZENIE ADRESÓW BEZ MIASTA W BAZIE
"""
from address_parser import get_supabase_client

def check_null_cities():
    """Sprawdza adresy bez miasta w bazie addresses"""
    
    print('🔍 SPRAWDZENIE ADRESÓW BEZ MIASTA W BAZIE')
    print('='*60)
    
    try:
        client = get_supabase_client()
        
        # Sprawdź adresy gdzie city jest null
        result = client.table('addresses').select('full_address, city, district').is_('city', 'null').limit(20).execute()
        
        if result.data:
            print(f'📊 Znaleziono {len(result.data)} adresów bez miasta:')
            print('='*60)
            
            for i, addr in enumerate(result.data, 1):
                print(f'{i}. "{addr["full_address"]}"')
                print(f'   🏙️ Miasto: {addr["city"]}')
                print(f'   🏘️ Dzielnica: {addr["district"]}')
                print()
        else:
            print('✅ Wszystkie adresy mają wypełnione miasto!')
            
        # Sprawdź statystyki ogólne
        total_result = client.table('addresses').select('id', count='exact').execute()
        null_city_result = client.table('addresses').select('id', count='exact').is_('city', 'null').execute()
        
        total_count = total_result.count
        null_count = null_city_result.count
        
        print(f'📈 STATYSTYKI:')
        print(f'   📊 Łącznie adresów: {total_count}')
        print(f'   ❌ Bez miasta: {null_count}')
        print(f'   ✅ Z miastem: {total_count - null_count}')
        print(f'   📈 Procent z miastem: {((total_count - null_count) / total_count * 100):.1f}%')
        
    except Exception as e:
        print(f'❌ Błąd: {e}')

if __name__ == "__main__":
    check_null_cities() 