#!/usr/bin/env python3
"""
TEST SYSTEMU GEOCODINGU
Sprawdza czy system geocodingu działa poprawnie
"""
import sys
import time
from geocoding_updater import (
    build_search_query, 
    geocode_address, 
    get_addresses_without_coordinates,
    test_geocoding
)
from check_geocoding import check_geocoding_results

def test_build_query():
    """Test budowania zapytań geocodingu"""
    print("🧪 TEST BUDOWANIA ZAPYTAŃ")
    print("="*50)
    
    test_cases = [
        {
            'name': 'Pełny adres',
            'data': {
                'street_name': 'ul. Marszałkowska',
                'district': 'Śródmieście',
                'city': 'Warszawa',
                'province': 'mazowieckie'
            },
            'expected': 'ul. Marszałkowska, Śródmieście, Warszawa, mazowieckie, Polska'
        },
        {
            'name': 'Tylko miasto',
            'data': {
                'city': 'Kraków'
            },
            'expected': 'Kraków, Polska'
        },
        {
            'name': 'Miasto + dzielnica',
            'data': {
                'city': 'Gdańsk',
                'district': 'Wrzeszcz'
            },
            'expected': 'Wrzeszcz, Gdańsk, Polska'
        },
        {
            'name': 'Z pod-dzielnicą',
            'data': {
                'city': 'Poznań',
                'sub_district': 'Osiedle Kosmonautów'
            },
            'expected': 'Osiedle Kosmonautów, Poznań, Polska'
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        query = build_search_query(case['data'])
        expected = case['expected']
        
        print(f"{i}. {case['name']}:")
        print(f"   📍 Wynik: {query}")
        print(f"   ✅ Oczekiwane: {expected}")
        print(f"   {'✅ PASS' if query == expected else '❌ FAIL'}")
        print()

def test_api_connection():
    """Test połączenia z API Nominatim"""
    print("🌐 TEST POŁĄCZENIA Z API")
    print("="*50)
    
    # Test prostego zapytania
    test_query = "Warszawa, Polska"
    print(f"📍 Testowe zapytanie: {test_query}")
    
    try:
        coordinates = geocode_address(test_query)
        
        if coordinates:
            lat, lon = coordinates
            print(f"✅ Połączenie działa!")
            print(f"📍 Współrzędne Warszawy: {lat:.6f}, {lon:.6f}")
            
            # Sprawdź czy współrzędne są rozsądne dla Warszawy
            if 52.0 <= lat <= 52.5 and 20.8 <= lon <= 21.3:
                print("✅ Współrzędne są prawidłowe dla Warszawy")
            else:
                print("⚠️ Współrzędne wydają się nieprawidłowe")
                
        else:
            print("❌ Nie udało się pobrać współrzędnych")
            
    except Exception as e:
        print(f"❌ Błąd połączenia z API: {e}")

def test_database_connection():
    """Test połączenia z bazą danych"""
    print("🗄️ TEST POŁĄCZENIA Z BAZĄ")
    print("="*50)
    
    try:
        from supabase_utils import get_supabase_client
        
        client = get_supabase_client()
        
        # Sprawdź czy tabela addresses istnieje
        result = client.table("addresses").select("id").limit(1).execute()
        print("✅ Połączenie z tabelą addresses działa!")
        
        # Sprawdź czy kolumny longitude i latitude istnieją
        try:
            coords_result = client.table("addresses").select("id, latitude, longitude").limit(1).execute()
            print("✅ Kolumny latitude i longitude istnieją!")
            
            # Sprawdź ile adresów jest bez współrzędnych
            addresses = get_addresses_without_coordinates(limit=5)
            print(f"📊 Znaleziono {len(addresses)} adresów bez współrzędnych (z pierwszych 5)")
            
        except Exception as e:
            print(f"❌ Kolumny latitude/longitude nie istnieją: {e}")
            print("💡 Uruchom: add_coordinates_columns.sql w Supabase")
            
    except Exception as e:
        print(f"❌ Błąd połączenia z bazą: {e}")
        print("💡 Sprawdź konfigurację Supabase w .env")

def run_full_test():
    """Uruchamia pełny test systemu"""
    print("🚀 PEŁNY TEST SYSTEMU GEOCODINGU")
    print("="*80)
    
    # Test 1: Budowanie zapytań
    test_build_query()
    
    # Test 2: Połączenie z API
    test_api_connection()
    time.sleep(1.5)  # Respektuj rate limit
    
    # Test 3: Połączenie z bazą
    test_database_connection()
    
    # Test 4: Test geocodingu na przykładach
    print("\n🧪 TEST GEOCODINGU NA PRZYKŁADACH")
    print("="*50)
    test_geocoding()
    
    # Test 5: Sprawdzenie stanu bazy
    print("\n📊 SPRAWDZENIE STANU BAZY")
    print("="*50)
    try:
        check_geocoding_results()
    except Exception as e:
        print(f"❌ Błąd sprawdzania bazy: {e}")
    
    print("\n🎉 TEST ZAKOŃCZONY!")
    print("="*80)
    print("💡 NASTĘPNE KROKI:")
    print("   1. Jeśli wszystko działa - uruchom: python geocoding_updater.py --update --max-addresses 10")
    print("   2. Sprawdź wyniki: python check_geocoding.py")
    print("   3. Kontynuuj dla wszystkich adresów: python geocoding_updater.py --update")

if __name__ == "__main__":
    try:
        run_full_test()
    except KeyboardInterrupt:
        print("\n⚠️ Test przerwany przez użytkownika")
    except Exception as e:
        print(f"\n❌ Błąd krytyczny w teście: {e}")
        sys.exit(1) 