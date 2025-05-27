#!/usr/bin/env python3
"""
DEBUG ZAPYTAŃ GEOCODINGU
Sprawdza jakie zapytania są generowane dla problematycznych adresów
"""
from geocoding_updater import build_search_query, geocode_address
from supabase_utils import get_supabase_client
import time

def debug_failed_addresses():
    """Debuguje adresy, które nie zostały geocodowane"""
    print("🔍 DEBUG ZAPYTAŃ GEOCODINGU")
    print("="*80)
    
    # Pobierz przykładowe adresy bez współrzędnych
    client = get_supabase_client()
    result = client.table('addresses').select('*').is_('latitude', 'null').limit(10).execute()
    
    if not result.data:
        print("✅ Wszystkie adresy mają już współrzędne!")
        return
    
    print(f"📊 Analizuję {len(result.data)} adresów bez współrzędnych:")
    print("-"*80)
    
    for i, addr in enumerate(result.data, 1):
        print(f"\n{i}. ID: {addr['id']}")
        print(f"   📍 Pełny adres: {addr['full_address']}")
        print(f"   🏙️ Miasto: {addr.get('city', 'brak')}")
        print(f"   🏘️ Dzielnica: {addr.get('district', 'brak')}")
        print(f"   🏠 Pod-dzielnica: {addr.get('sub_district', 'brak')}")
        print(f"   🛣️ Ulica: {addr.get('street_name', 'brak')}")
        print(f"   🗺️ Województwo: {addr.get('province', 'brak')}")
        
        # Generuj zapytanie
        query = build_search_query(addr)
        print(f"   🔍 Zapytanie geocoding: '{query}'")
        
        # Sprawdź czy zapytanie ma sens
        if query == "Polska":
            print("   ❌ PROBLEM: Zapytanie zawiera tylko 'Polska'!")
        elif not addr.get('city'):
            print("   ❌ PROBLEM: Brak miasta w adresie!")
        elif len(query.split(',')) < 2:
            print("   ❌ PROBLEM: Zapytanie zbyt krótkie!")
        else:
            print("   ✅ Zapytanie wygląda OK")
            
            # Opcjonalnie: przetestuj geocoding
            if i <= 3:  # Tylko pierwsze 3 dla oszczędności API
                print("   🌐 Testowanie geocoding...")
                try:
                    coords = geocode_address(query)
                    if coords:
                        lat, lon = coords
                        print(f"   ✅ Znaleziono: {lat:.6f}, {lon:.6f}")
                    else:
                        print("   ❌ Brak wyników z API")
                except Exception as e:
                    print(f"   ❌ Błąd API: {e}")
                
                time.sleep(1.2)  # Rate limiting
        
        print("-"*40)

def analyze_query_patterns():
    """Analizuje wzorce w zapytaniach"""
    print("\n🔍 ANALIZA WZORCÓW ZAPYTAŃ")
    print("="*80)
    
    client = get_supabase_client()
    result = client.table('addresses').select('*').limit(20).execute()
    
    query_patterns = {}
    
    for addr in result.data:
        query = build_search_query(addr)
        parts_count = len(query.split(','))
        
        if parts_count not in query_patterns:
            query_patterns[parts_count] = []
        
        query_patterns[parts_count].append({
            'id': addr['id'],
            'query': query,
            'has_coords': bool(addr.get('latitude'))
        })
    
    print("📊 WZORCE ZAPYTAŃ (liczba części oddzielonych przecinkami):")
    print("-"*80)
    
    for parts_count in sorted(query_patterns.keys()):
        queries = query_patterns[parts_count]
        with_coords = sum(1 for q in queries if q['has_coords'])
        total = len(queries)
        success_rate = (with_coords / total * 100) if total > 0 else 0
        
        print(f"\n{parts_count} części: {total} zapytań, {with_coords} z współrzędnymi ({success_rate:.1f}%)")
        
        # Pokaż przykłady
        for j, query_info in enumerate(queries[:3], 1):
            status = "✅" if query_info['has_coords'] else "❌"
            print(f"   {j}. {status} ID {query_info['id']}: {query_info['query']}")

def test_manual_queries():
    """Testuje ręcznie poprawione zapytania"""
    print("\n🧪 TEST RĘCZNYCH POPRAWEK")
    print("="*80)
    
    # Przykłady problematycznych adresów z poprawkami
    test_cases = [
        {
            'original': 'Ul. Mołdawska, Rakowiec, Warszawa, Mazowieckie, Polska',
            'fixed': 'Mołdawska, Warszawa, Polska'
        },
        {
            'original': 'Ul. Mazepy, Gdański, Pomorskie, Polska',
            'fixed': 'Mazepy, Pruszcz Gdański, Polska'
        },
        {
            'original': 'Ul. Garbary, Centrum, Poznań, Wielkopolskie, Polska',
            'fixed': 'Garbary, Poznań, Polska'
        },
        {
            'original': 'Ul. Święty Marcin, Centrum, Poznań, Wielkopolskie, Polska',
            'fixed': 'Święty Marcin, Poznań, Polska'
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. Test poprawki:")
        print(f"   📍 Oryginalne: {case['original']}")
        print(f"   🔧 Poprawione: {case['fixed']}")
        
        # Test obu wersji
        for version, query in [('Oryginalne', case['original']), ('Poprawione', case['fixed'])]:
            try:
                coords = geocode_address(query)
                if coords:
                    lat, lon = coords
                    print(f"   {version}: ✅ {lat:.6f}, {lon:.6f}")
                else:
                    print(f"   {version}: ❌ Brak wyników")
            except Exception as e:
                print(f"   {version}: ❌ Błąd: {e}")
            
            time.sleep(1.2)

if __name__ == "__main__":
    try:
        debug_failed_addresses()
        analyze_query_patterns()
        test_manual_queries()
        
        print("\n💡 WNIOSKI:")
        print("   • Sprawdź czy zapytania nie są zbyt szczegółowe")
        print("   • Usuń nadmiarowe informacje (dzielnice, województwa)")
        print("   • Uprość zapytania do: ulica + miasto + Polska")
        print("   • Rozważ alternatywne API geocodingu")
        
    except Exception as e:
        print(f"❌ Błąd: {e}") 