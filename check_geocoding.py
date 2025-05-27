#!/usr/bin/env python3
"""
SPRAWDZENIE WYNIKÓW GEOCODINGU
Analizuje współrzędne geograficzne w tabeli addresses
"""
from supabase_utils import get_supabase_client

def check_geocoding_results():
    """Sprawdza wyniki geocodingu w bazie addresses"""
    print("🌍 SPRAWDZENIE WYNIKÓW GEOCODINGU")
    print("="*60)
    
    client = get_supabase_client()
    
    try:
        # Pobierz statystyki ogólne
        total_result = client.table('addresses').select('id', count='exact').execute()
        total_count = total_result.count
        
        # Adresy z współrzędnymi
        with_coords_result = client.table('addresses').select('id', count='exact').not_.is_('latitude', 'null').not_.is_('longitude', 'null').execute()
        with_coords_count = with_coords_result.count
        
        # Adresy bez współrzędnych
        without_coords_count = total_count - with_coords_count
        
        print(f"📊 STATYSTYKI GEOCODINGU:")
        print(f"   📋 Łącznie adresów: {total_count}")
        print(f"   ✅ Z współrzędnymi: {with_coords_count}")
        print(f"   ❌ Bez współrzędnych: {without_coords_count}")
        
        if total_count > 0:
            success_rate = (with_coords_count / total_count) * 100
            print(f"   📈 Skuteczność geocodingu: {success_rate:.1f}%")
        
        # Przykładowe adresy z współrzędnymi
        if with_coords_count > 0:
            print(f"\n📍 PRZYKŁADOWE ADRESY Z WSPÓŁRZĘDNYMI:")
            print("-"*60)
            
            coords_result = client.table('addresses').select('*').not_.is_('latitude', 'null').limit(5).execute()
            
            for i, addr in enumerate(coords_result.data, 1):
                city = addr.get('city', 'brak')
                district = addr.get('district', '')
                lat = addr.get('latitude')
                lon = addr.get('longitude')
                
                print(f"{i}. {city}" + (f", {district}" if district else ""))
                print(f"   📍 Współrzędne: {lat:.6f}, {lon:.6f}")
                print(f"   🗺️ Google Maps: https://maps.google.com/?q={lat},{lon}")
                print()
        
        # Adresy bez współrzędnych (do dalszego przetworzenia)
        if without_coords_count > 0:
            print(f"❌ ADRESY BEZ WSPÓŁRZĘDNYCH (pierwsze 5):")
            print("-"*60)
            
            no_coords_result = client.table('addresses').select('*').or_('latitude.is.null,longitude.is.null').limit(5).execute()
            
            for i, addr in enumerate(no_coords_result.data, 1):
                full_address = addr.get('full_address', '')
                city = addr.get('city', 'brak')
                district = addr.get('district', '')
                
                print(f"{i}. ID: {addr['id']}")
                print(f"   📍 Pełny adres: {full_address}")
                print(f"   🏙️ Miasto: {city}")
                print(f"   🏘️ Dzielnica: {district}")
                print()
        
        # Rozkład geograficzny (top miasta)
        if with_coords_count > 0:
            print(f"🏙️ TOP 10 MIAST Z WSPÓŁRZĘDNYMI:")
            print("-"*60)
            
            cities_result = client.table('addresses').select('city').not_.is_('latitude', 'null').execute()
            
            # Policz miasta
            from collections import Counter
            cities = [addr['city'] for addr in cities_result.data if addr.get('city')]
            city_counts = Counter(cities)
            
            for i, (city, count) in enumerate(city_counts.most_common(10), 1):
                percentage = (count / with_coords_count) * 100
                print(f"   {i:2d}. {city:<15} : {count:3d} adresów ({percentage:.1f}%)")
        
    except Exception as e:
        print(f"❌ Błąd: {e}")

def check_coordinate_quality():
    """Sprawdza jakość współrzędnych (czy są w Polsce)"""
    print(f"\n🔍 SPRAWDZENIE JAKOŚCI WSPÓŁRZĘDNYCH")
    print("="*60)
    
    client = get_supabase_client()
    
    try:
        # Pobierz wszystkie współrzędne
        coords_result = client.table('addresses').select('id, city, latitude, longitude').not_.is_('latitude', 'null').execute()
        
        if not coords_result.data:
            print("❌ Brak współrzędnych do sprawdzenia")
            return
        
        # Granice Polski (przybliżone)
        POLAND_BOUNDS = {
            'lat_min': 49.0,
            'lat_max': 54.9,
            'lon_min': 14.1,
            'lon_max': 24.2
        }
        
        valid_coords = 0
        invalid_coords = []
        
        for addr in coords_result.data:
            lat = addr.get('latitude')
            lon = addr.get('longitude')
            
            if (POLAND_BOUNDS['lat_min'] <= lat <= POLAND_BOUNDS['lat_max'] and 
                POLAND_BOUNDS['lon_min'] <= lon <= POLAND_BOUNDS['lon_max']):
                valid_coords += 1
            else:
                invalid_coords.append(addr)
        
        total_coords = len(coords_result.data)
        
        print(f"📊 JAKOŚĆ WSPÓŁRZĘDNYCH:")
        print(f"   📋 Łącznie sprawdzonych: {total_coords}")
        print(f"   ✅ W granicach Polski: {valid_coords}")
        print(f"   ❌ Poza Polską: {len(invalid_coords)}")
        
        if total_coords > 0:
            quality_rate = (valid_coords / total_coords) * 100
            print(f"   📈 Jakość: {quality_rate:.1f}%")
        
        # Pokaż nieprawidłowe współrzędne
        if invalid_coords:
            print(f"\n❌ NIEPRAWIDŁOWE WSPÓŁRZĘDNE:")
            print("-"*60)
            
            for i, addr in enumerate(invalid_coords[:5], 1):
                city = addr.get('city', 'brak')
                lat = addr.get('latitude')
                lon = addr.get('longitude')
                
                print(f"{i}. ID: {addr['id']} - {city}")
                print(f"   📍 Współrzędne: {lat:.6f}, {lon:.6f}")
                print(f"   🗺️ Sprawdź: https://maps.google.com/?q={lat},{lon}")
                print()
    
    except Exception as e:
        print(f"❌ Błąd sprawdzania jakości: {e}")

if __name__ == "__main__":
    try:
        check_geocoding_results()
        check_coordinate_quality()
        
        print("\n💡 NASTĘPNE KROKI:")
        print("   • Uruchom geocoding_updater.py --update aby uzupełnić brakujące współrzędne")
        print("   • Sprawdź nieprawidłowe współrzędne i popraw je ręcznie")
        print("   • Użyj współrzędnych do analiz geograficznych i map")
        
    except Exception as e:
        print(f"❌ Błąd: {e}") 