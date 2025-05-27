#!/usr/bin/env python3
"""
SPRAWDZENIE WYNIKÓW PARSOWANIA ADRESÓW
"""
from address_parser import get_supabase_client

def check_addresses():
    """Sprawdza wyniki parsowania adresów w bazie"""
    client = get_supabase_client()
    
    # Pobierz przykładowe adresy
    result = client.table('addresses').select('*').limit(10).execute()
    
    print("📊 PRZYKŁADOWE ADRESY Z BAZY:")
    print("="*60)
    
    for i, addr in enumerate(result.data, 1):
        print(f"{i}. ID: {addr['id']} | FK: {addr['foreign_key']}")
        print(f"   📍 Pełny: {addr['full_address']}")
        print(f"   🏙️ Miasto: {addr['city']}")
        print(f"   🏘️ Dzielnica: {addr['district']}")
        print(f"   🏠 Pod-dzielnica: {addr['sub_district']}")
        print(f"   🛣️ Ulica: {addr['street_name']}")
        print(f"   🗺️ Województwo: {addr['province']}")
        print()
    
    # Statystyki
    count_result = client.table('addresses').select('id', count='exact').execute()
    print(f"📈 ŁĄCZNA LICZBA ADRESÓW: {count_result.count}")
    
    # Statystyki miast
    cities_result = client.table('addresses').select('city').execute()
    cities = [addr['city'] for addr in cities_result.data if addr['city']]
    unique_cities = set(cities)
    print(f"🏙️ UNIKALNE MIASTA: {len(unique_cities)}")
    
    # Top 5 miast
    from collections import Counter
    city_counts = Counter(cities)
    print("\n🏆 TOP 5 MIAST:")
    for city, count in city_counts.most_common(5):
        print(f"   {city}: {count} ogłoszeń")

if __name__ == "__main__":
    check_addresses() 