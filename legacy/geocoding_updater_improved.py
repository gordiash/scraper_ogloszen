#!/usr/bin/env python3
"""
GEOCODING UPDATER - ULEPSZONA WERSJA
Uzupełnia współrzędne geograficzne z uproszczonymi zapytaniami
"""
import logging
import time
import requests
from typing import Dict, List, Optional, Tuple
from supabase_utils import get_supabase_client

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Konfiguracja geocodingu
NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org/search"
DELAY_BETWEEN_REQUESTS = 1.1
MAX_RETRIES = 3

def build_simple_search_query(address_data: Dict) -> str:
    """
    Buduje UPROSZCZONE zapytanie wyszukiwania - tylko najważniejsze elementy
    
    Args:
        address_data: Słownik z danymi adresu
    
    Returns:
        str: Uproszczone zapytanie do geocodingu
    """
    components = []
    
    # 1. Ulica (bez "ul.", "al." itp.) - tylko nazwa
    if address_data.get('street_name'):
        street = address_data['street_name']
        # Usuń prefiksy ul., al., pl., os.
        street = street.replace('Ul. ', '').replace('Al. ', '').replace('Pl. ', '').replace('Os. ', '')
        street = street.replace('ul. ', '').replace('al. ', '').replace('pl. ', '').replace('os. ', '')
        if street:
            components.append(street)
    
    # 2. Miasto (obowiązkowe) - bez dzielnic!
    if address_data.get('city'):
        city = address_data['city']
        # Popraw znane błędy w nazwach miast
        city_fixes = {
            'Gdański': 'Pruszcz Gdański',
            'Łomianki': 'Łomianki',  # OK
            'Oleśnica': 'Oleśnica',  # OK
        }
        city = city_fixes.get(city, city)
        components.append(city)
    
    # 3. Zawsze dodaj "Polska"
    components.append("Polska")
    
    query = ", ".join(components)
    logger.debug(f"Uproszczone zapytanie geocoding: {query}")
    return query

def build_fallback_query(address_data: Dict) -> str:
    """
    Buduje zapytanie fallback - tylko miasto + Polska
    """
    if address_data.get('city'):
        city = address_data['city']
        # Popraw znane błędy
        city_fixes = {
            'Gdański': 'Pruszcz Gdański',
        }
        city = city_fixes.get(city, city)
        return f"{city}, Polska"
    return "Polska"

def geocode_address_improved(query: str, fallback_query: str = None) -> Optional[Tuple[float, float]]:
    """
    Pobiera współrzędne z próbą fallback
    """
    params = {
        'q': query,
        'format': 'json',
        'limit': 1,
        'countrycodes': 'pl',
        'addressdetails': 1,
        'extratags': 1
    }
    
    headers = {
        'User-Agent': 'Polish Real Estate Scraper/1.0 (educational purpose)'
    }
    
    # Próba 1: Główne zapytanie
    for attempt in range(MAX_RETRIES):
        try:
            logger.debug(f"Geocoding attempt {attempt + 1}: {query}")
            response = requests.get(NOMINATIM_BASE_URL, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data and len(data) > 0:
                result = data[0]
                lat = float(result['lat'])
                lon = float(result['lon'])
                
                # Walidacja współrzędnych dla Polski
                if 49.0 <= lat <= 54.9 and 14.1 <= lon <= 24.2:
                    logger.debug(f"Znaleziono współrzędne (główne): {lat}, {lon}")
                    return (lat, lon)
                else:
                    logger.warning(f"Współrzędne poza Polską: {lat}, {lon}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Błąd HTTP podczas geocodingu (próba {attempt + 1}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(2 ** attempt)
        except (ValueError, KeyError) as e:
            logger.error(f"Błąd parsowania odpowiedzi geocodingu: {e}")
            break
        except Exception as e:
            logger.error(f"Nieoczekiwany błąd geocodingu: {e}")
            break
    
    # Próba 2: Fallback query (jeśli podane)
    if fallback_query and fallback_query != query:
        logger.debug(f"Próba fallback: {fallback_query}")
        time.sleep(DELAY_BETWEEN_REQUESTS)
        
        params['q'] = fallback_query
        
        try:
            response = requests.get(NOMINATIM_BASE_URL, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data and len(data) > 0:
                result = data[0]
                lat = float(result['lat'])
                lon = float(result['lon'])
                
                if 49.0 <= lat <= 54.9 and 14.1 <= lon <= 24.2:
                    logger.debug(f"Znaleziono współrzędne (fallback): {lat}, {lon}")
                    return (lat, lon)
                    
        except Exception as e:
            logger.error(f"Błąd fallback geocodingu: {e}")
    
    logger.warning(f"Brak wyników geocodingu dla: {query}")
    return None

def get_addresses_without_coordinates(limit: int = 100) -> List[Dict]:
    """
    Pobiera adresy bez współrzędnych z bazy danych
    
    Args:
        limit: Maksymalna liczba adresów do pobrania
    
    Returns:
        List[Dict]: Lista adresów bez współrzędnych
    """
    supabase = get_supabase_client()
    
    try:
        # Pobierz adresy gdzie longitude I latitude są null (oba muszą być null)
        result = supabase.table("addresses").select("*").is_('latitude', 'null').is_('longitude', 'null').limit(limit).execute()
        
        if result.data:
            logger.info(f"📊 Znaleziono {len(result.data)} adresów bez współrzędnych")
            return result.data
        else:
            logger.info("✅ Wszystkie adresy mają już współrzędne")
            return []
            
    except Exception as e:
        logger.error(f"❌ Błąd pobierania adresów: {e}")
        return []

def update_address_coordinates(address_id: int, latitude: float, longitude: float) -> bool:
    """Aktualizuje współrzędne dla adresu"""
    supabase = get_supabase_client()
    
    try:
        result = supabase.table("addresses").update({
            "latitude": latitude,
            "longitude": longitude
        }).eq("id", address_id).execute()
        
        if result.data:
            logger.debug(f"✅ Zaktualizowano współrzędne dla adresu ID {address_id}")
            return True
        else:
            logger.warning(f"⚠️ Nie udało się zaktualizować adresu ID {address_id}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Błąd aktualizacji adresu ID {address_id}: {e}")
        return False

def process_geocoding_batch_improved(addresses: List[Dict]) -> Dict[str, int]:
    """
    Przetwarza batch adresów z ulepszonym algorytmem
    """
    stats = {
        "processed": 0,
        "success": 0,
        "failed": 0,
        "skipped": 0,
        "fallback_success": 0
    }
    
    for i, address in enumerate(addresses, 1):
        try:
            address_id = address['id']
            
            # Sprawdź czy już ma współrzędne
            if address.get('latitude') and address.get('longitude'):
                logger.debug(f"Adres ID {address_id} już ma współrzędne - pomijam")
                stats["skipped"] += 1
                continue
            
            # Buduj zapytania
            main_query = build_simple_search_query(address)
            fallback_query = build_fallback_query(address)
            
            if not main_query or main_query == "Polska":
                logger.warning(f"Pusty adres dla ID {address_id} - pomijam")
                stats["skipped"] += 1
                continue
            
            # Geocoding z fallback
            coordinates = geocode_address_improved(main_query, fallback_query)
            
            if coordinates:
                latitude, longitude = coordinates
                
                # Sprawdź czy użyto fallback
                was_fallback = main_query != fallback_query and fallback_query in str(coordinates)
                
                # Aktualizuj w bazie
                if update_address_coordinates(address_id, latitude, longitude):
                    stats["success"] += 1
                    if was_fallback:
                        stats["fallback_success"] += 1
                    logger.info(f"✅ {i}/{len(addresses)} - ID {address_id}: {latitude:.6f}, {longitude:.6f}")
                else:
                    stats["failed"] += 1
                    logger.error(f"❌ {i}/{len(addresses)} - Błąd zapisu ID {address_id}")
            else:
                stats["failed"] += 1
                logger.warning(f"⚠️ {i}/{len(addresses)} - Brak współrzędnych dla ID {address_id}: {main_query}")
            
            stats["processed"] += 1
            
            # Opóźnienie między requestami
            if i < len(addresses):
                time.sleep(DELAY_BETWEEN_REQUESTS)
                
        except Exception as e:
            stats["failed"] += 1
            logger.error(f"❌ Błąd przetwarzania adresu ID {address.get('id', 'unknown')}: {e}")
    
    return stats

def update_all_coordinates_improved(batch_size: int = 50, max_addresses: int = None) -> None:
    """
    Główna funkcja z ulepszonym algorytmem i obsługą offset
    """
    print("="*80)
    print("🌍 GEOCODING UPDATER - ULEPSZONA WERSJA")
    print("="*80)
    print(f"📊 Parametry:")
    print(f"   • Rozmiar batcha: {batch_size}")
    print(f"   • Maksymalne adresy: {max_addresses or 'wszystkie'}")
    print(f"   • Uproszczone zapytania: TAK")
    print(f"   • Fallback queries: TAK")
    print("="*80)
    
    total_stats = {
        "processed": 0,
        "success": 0,
        "failed": 0,
        "skipped": 0,
        "fallback_success": 0
    }
    
    processed_count = 0
    batch_number = 1
    
    while True:
        # Pobierz następny batch z offset
        remaining_limit = batch_size
        if max_addresses:
            remaining_limit = min(batch_size, max_addresses - processed_count)
            if remaining_limit <= 0:
                break
        
        # Pobierz następny batch (zawsze pierwsze 50 bez współrzędnych)
        addresses = get_addresses_without_coordinates(limit=remaining_limit)
        
        if not addresses:
            print("✅ Wszystkie adresy mają już współrzędne!")
            break
        
        print(f"\n🔄 PRZETWARZANIE BATCHA {batch_number}")
        print(f"📋 Adresy w batchu: {len(addresses)}")
        print("-" * 60)
        
        # Przetwórz batch
        batch_stats = process_geocoding_batch_improved(addresses)
        
        # Aktualizuj statystyki
        for key in total_stats:
            total_stats[key] += batch_stats[key]
        
        processed_count += len(addresses)
        
        # Podsumowanie batcha
        print(f"\n📊 WYNIKI BATCHA {batch_number}:")
        print(f"   ✅ Sukces: {batch_stats['success']}")
        print(f"   🔄 Fallback sukces: {batch_stats['fallback_success']}")
        print(f"   ❌ Błędy: {batch_stats['failed']}")
        print(f"   ⏭️ Pominięte: {batch_stats['skipped']}")
        
        # Sprawdź czy osiągnięto limit
        if max_addresses and processed_count >= max_addresses:
            break
        
        # Jeśli batch był mniejszy niż limit, to koniec
        if len(addresses) < batch_size:
            print(f"📄 Ostatni batch - pobrano {len(addresses)} < {batch_size}")
            break
        
        batch_number += 1
        
        # Opóźnienie między batchami
        print(f"⏳ Opóźnienie 5 sekund przed następnym batchem...")
        time.sleep(5)
    
    # Podsumowanie końcowe
    print("\n" + "="*80)
    print("📊 PODSUMOWANIE ULEPSZONEGO GEOCODINGU")
    print("="*80)
    print(f"📋 Łącznie przetworzonych: {total_stats['processed']}")
    print(f"✅ Pomyślnie geocodowanych: {total_stats['success']}")
    print(f"🔄 Sukces przez fallback: {total_stats['fallback_success']}")
    print(f"❌ Błędów geocodingu: {total_stats['failed']}")
    print(f"⏭️ Pominiętych: {total_stats['skipped']}")
    
    if total_stats['processed'] > 0:
        success_rate = (total_stats['success'] / total_stats['processed']) * 100
        print(f"📈 Skuteczność: {success_rate:.1f}%")
        
        if total_stats['fallback_success'] > 0:
            fallback_rate = (total_stats['fallback_success'] / total_stats['success']) * 100
            print(f"🔄 Udział fallback: {fallback_rate:.1f}%")
    
    print("="*80)

def test_improved_geocoding():
    """Testuje ulepszone geocoding"""
    print("🧪 TEST ULEPSZONEGO GEOCODINGU")
    print("="*60)
    
    test_addresses = [
        {
            'id': 'test1',
            'city': 'Warszawa',
            'district': 'Rakowiec',
            'street_name': 'Ul. Mołdawska'
        },
        {
            'id': 'test2',
            'city': 'Gdański',  # Błędna nazwa
            'street_name': 'Ul. Mazepy'
        },
        {
            'id': 'test3',
            'city': 'Poznań',
            'district': 'Centrum',
            'street_name': 'Ul. Garbary'
        }
    ]
    
    for i, address in enumerate(test_addresses, 1):
        print(f"\n{i}. Test adresu:")
        
        # Stare zapytanie
        old_query = f"{address.get('street_name', '')}, {address.get('district', '')}, {address.get('city', '')}, Polska"
        old_query = old_query.replace(', , ', ', ').strip(', ')
        
        # Nowe zapytanie
        new_query = build_simple_search_query(address)
        fallback_query = build_fallback_query(address)
        
        print(f"   📍 Stare zapytanie: {old_query}")
        print(f"   🔧 Nowe zapytanie: {new_query}")
        print(f"   🔄 Fallback: {fallback_query}")
        
        # Test nowego geocodingu
        coordinates = geocode_address_improved(new_query, fallback_query)
        if coordinates:
            lat, lon = coordinates
            print(f"   ✅ Współrzędne: {lat:.6f}, {lon:.6f}")
        else:
            print(f"   ❌ Nie znaleziono współrzędnych")
        
        if i < len(test_addresses):
            time.sleep(DELAY_BETWEEN_REQUESTS)
    
    print("="*60)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Ulepszona wersja geocoding updater')
    parser.add_argument('--test', action='store_true', help='Uruchom test ulepszonego geocodingu')
    parser.add_argument('--update', action='store_true', help='Aktualizuj współrzędne z ulepszonym algorytmem')
    parser.add_argument('--batch-size', type=int, default=50, help='Rozmiar batcha')
    parser.add_argument('--max-addresses', type=int, help='Maksymalna liczba adresów')
    
    args = parser.parse_args()
    
    try:
        if args.test:
            test_improved_geocoding()
        elif args.update:
            update_all_coordinates_improved(
                batch_size=args.batch_size,
                max_addresses=args.max_addresses
            )
        else:
            print("🌍 GEOCODING UPDATER - ULEPSZONA WERSJA")
            print("Użycie:")
            print("  python geocoding_updater_improved.py --test           # Test")
            print("  python geocoding_updater_improved.py --update         # Aktualizuj")
            print("  python geocoding_updater_improved.py --update --max-addresses 50")
            
    except KeyboardInterrupt:
        print("\n⚠️ Przerwano przez użytkownika")
    except Exception as e:
        print(f"\n❌ Błąd krytyczny: {e}")
        logger.error(f"Błąd w geocoding_updater_improved: {e}", exc_info=True) 