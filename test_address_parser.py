#!/usr/bin/env python3
"""
TEST PARSERA ADRESÓW
Testuje funkcjonalność rozdzielania lokalizacji na komponenty
"""
from address_parser import parse_location_string, test_address_parsing, get_listings_locations

def test_real_data_sample():
    """Test na rzeczywistych danych z bazy (jeśli dostępne)"""
    print("🔍 TEST NA RZECZYWISTYCH DANYCH Z BAZY")
    print("="*60)
    
    try:
        locations = get_listings_locations()
        
        if locations:
            print(f"📊 Znaleziono {len(locations)} lokalizacji w bazie")
            print("\n📋 Pierwsze 10 przykładów z bazy:")
            print("-"*60)
            
            for i, (listing_id, location) in enumerate(locations[:10], 1):
                if location:
                    print(f"\n{i}. ID: {listing_id}")
                    print(f"   📍 Oryginalny: '{location}'")
                    
                    parsed = parse_location_string(location)
                    print(f"   🏙️ Miasto: {parsed.get('city', 'brak')}")
                    print(f"   🏘️ Dzielnica: {parsed.get('district', 'brak')}")
                    print(f"   🏠 Pod-dzielnica: {parsed.get('sub_district', 'brak')}")
                    print(f"   🛣️ Ulica: {parsed.get('street_name', 'brak')}")
                    print(f"   🗺️ Województwo: {parsed.get('province', 'brak')}")
        else:
            print("❌ Brak danych w bazie lub brak połączenia")
            
    except Exception as e:
        print(f"❌ Błąd dostępu do bazy: {e}")
        print("💡 Sprawdź konfigurację Supabase w .env")

def test_edge_cases():
    """Test przypadków brzegowych"""
    print("\n🧪 TEST PRZYPADKÓW BRZEGOWYCH")
    print("="*60)
    
    edge_cases = [
        "",  # Pusty string
        "   ",  # Same spacje
        "Warszawa",  # Tylko miasto
        "ul. Marszałkowska 123",  # Tylko ulica
        "Warszawa, ul. Marszałkowska 123, Śródmieście",  # Odwrócona kolejność
        "Kraków - Stare Miasto - ul. Floriańska",  # Myślniki zamiast przecinków
        "Gdańsk/Wrzeszcz/Grunwaldzka 45",  # Slashe
        "WARSZAWA, MOKOTÓW, UL. PUŁAWSKA",  # Wielkie litery
        "warszawa, mokotów, ul. puławska",  # Małe litery
        "Wrocław, Krzyki, os. Powstańców Śląskich 123/45",  # Numer z mieszkaniem
    ]
    
    for i, location in enumerate(edge_cases, 1):
        print(f"\n{i}. '{location}'")
        parsed = parse_location_string(location)
        
        print(f"   🏙️ Miasto: {parsed.get('city', 'brak')}")
        print(f"   🏘️ Dzielnica: {parsed.get('district', 'brak')}")
        print(f"   🏠 Pod-dzielnica: {parsed.get('sub_district', 'brak')}")
        print(f"   🛣️ Ulica: {parsed.get('street_name', 'brak')}")
        print(f"   🗺️ Województwo: {parsed.get('province', 'brak')}")

def test_statistics():
    """Statystyki parsowania na rzeczywistych danych"""
    print("\n📊 STATYSTYKI PARSOWANIA")
    print("="*60)
    
    try:
        locations = get_listings_locations()
        
        if not locations:
            print("❌ Brak danych do analizy")
            return
        
        # Statystyki
        total_count = len(locations)
        empty_count = 0
        parsed_stats = {
            'city': 0,
            'district': 0,
            'sub_district': 0,
            'street_name': 0,
            'province': 0
        }
        
        print(f"🔍 Analizuję {total_count} lokalizacji...")
        
        for listing_id, location in locations:
            if not location or location.strip() == "":
                empty_count += 1
                continue
            
            parsed = parse_location_string(location)
            
            for field in parsed_stats:
                if parsed.get(field):
                    parsed_stats[field] += 1
        
        # Wyniki
        valid_count = total_count - empty_count
        
        print(f"\n📋 WYNIKI ANALIZY:")
        print(f"   📊 Łącznie lokalizacji: {total_count}")
        print(f"   ✅ Niepuste lokalizacje: {valid_count}")
        print(f"   ❌ Puste lokalizacje: {empty_count}")
        
        if valid_count > 0:
            print(f"\n📈 SKUTECZNOŚĆ PARSOWANIA:")
            for field, count in parsed_stats.items():
                percentage = (count / valid_count) * 100
                field_name = {
                    'city': 'Miasta',
                    'district': 'Dzielnice',
                    'sub_district': 'Pod-dzielnice',
                    'street_name': 'Ulice',
                    'province': 'Województwa'
                }[field]
                print(f"   🏷️ {field_name}: {count}/{valid_count} ({percentage:.1f}%)")
        
    except Exception as e:
        print(f"❌ Błąd analizy: {e}")

def main():
    """Główna funkcja testowa"""
    print("🏠 KOMPLEKSOWY TEST PARSERA ADRESÓW")
    print("="*80)
    
    # Test 1: Przykłady testowe
    test_address_parsing()
    
    # Test 2: Przypadki brzegowe
    test_edge_cases()
    
    # Test 3: Rzeczywiste dane z bazy
    test_real_data_sample()
    
    # Test 4: Statystyki
    test_statistics()
    
    print("\n" + "="*80)
    print("🎉 TESTY ZAKOŃCZONE!")
    print("="*80)
    print("💡 Następne kroki:")
    print("   1. Sprawdź wyniki testów powyżej")
    print("   2. Utwórz tabelę 'addresses' w Supabase jeśli nie istnieje")
    print("   3. Uruchom: python address_parser.py --process")
    print("="*80)

if __name__ == "__main__":
    main() 