#!/usr/bin/env python3
"""
GEOCODING UPDATER - UZUPEŁNIANIE WSPÓŁRZĘDNYCH GEOGRAFICZNYCH
Pobiera adresy z tabeli addresses i uzupełnia kolumny longitude i latitude
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
DELAY_BETWEEN_REQUESTS = 1.1  # Nominatim wymaga min 1 sekunda między requestami
MAX_RETRIES = 3

def build_search_query(address_data: Dict) -> str:
    """
    Buduje zapytanie wyszukiwania na podstawie danych adresowych
    
    Args:
        address_data: Słownik z danymi adresu
    
    Returns:
        str: Zapytanie do geocodingu
    """
    # Priorytet komponentów adresu
    components = []
    
    # Ulica (najważniejsza jeśli istnieje)
    if address_data.get('street_name'):
        components.append(address_data['street_name'])
    
    # Dzielnica/pod-dzielnica
    if address_data.get('district'):
        components.append(address_data['district'])
    elif address_data.get('sub_district'):
        components.append(address_data['sub_district'])
    
    # Miasto (obowiązkowe)
    if address_data.get('city'):
        components.append(address_data['city'])
    
    # Województwo (opcjonalne, ale pomocne)
    if address_data.get('province'):
        components.append(address_data['province'])
    
    # Zawsze dodaj "Polska" dla lepszej precyzji
    components.append("Polska")
    
    query = ", ".join(components)
    logger.debug(f"Zapytanie geocoding: {query}")
    return query

def geocode_address(query: str) -> Optional[Tuple[float, float]]:
    """
    Pobiera współrzędne geograficzne dla podanego adresu
    
    Args:
        query: Zapytanie adresowe
    
    Returns:
        Tuple[float, float]: (latitude, longitude) lub None
    """
    params = {
        'q': query,
        'format': 'json',
        'limit': 1,
        'countrycodes': 'pl',  # Ograniczenie do Polski
        'addressdetails': 1,
        'extratags': 1
    }
    
    headers = {
        'User-Agent': 'Polish Real Estate Scraper/1.0 (educational purpose)'
    }
    
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
                    logger.debug(f"Znaleziono współrzędne: {lat}, {lon}")
                    return (lat, lon)
                else:
                    logger.warning(f"Współrzędne poza Polską: {lat}, {lon}")
                    return None
            else:
                logger.warning(f"Brak wyników geocodingu dla: {query}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Błąd HTTP podczas geocodingu (próba {attempt + 1}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
        except (ValueError, KeyError) as e:
            logger.error(f"Błąd parsowania odpowiedzi geocodingu: {e}")
            break
        except Exception as e:
            logger.error(f"Nieoczekiwany błąd geocodingu: {e}")
            break
    
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
        # Pobierz adresy gdzie longitude lub latitude jest null
        result = supabase.table("addresses").select("*").or_(
            "longitude.is.null,latitude.is.null"
        ).limit(limit).execute()
        
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
    """
    Aktualizuje współrzędne dla konkretnego adresu
    
    Args:
        address_id: ID adresu w bazie
        latitude: Szerokość geograficzna
        longitude: Długość geograficzna
    
    Returns:
        bool: True jeśli aktualizacja się udała
    """
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

def process_geocoding_batch(addresses: List[Dict]) -> Dict[str, int]:
    """
    Przetwarza batch adresów do geocodingu
    
    Args:
        addresses: Lista adresów do przetworzenia
    
    Returns:
        Dict: Statystyki przetwarzania
    """
    stats = {
        "processed": 0,
        "success": 0,
        "failed": 0,
        "skipped": 0
    }
    
    for i, address in enumerate(addresses, 1):
        try:
            address_id = address['id']
            
            # Sprawdź czy już ma współrzędne
            if address.get('latitude') and address.get('longitude'):
                logger.debug(f"Adres ID {address_id} już ma współrzędne - pomijam")
                stats["skipped"] += 1
                continue
            
            # Buduj zapytanie
            query = build_search_query(address)
            
            if not query or query == "Polska":
                logger.warning(f"Pusty adres dla ID {address_id} - pomijam")
                stats["skipped"] += 1
                continue
            
            # Geocoding
            coordinates = geocode_address(query)
            
            if coordinates:
                latitude, longitude = coordinates
                
                # Aktualizuj w bazie
                if update_address_coordinates(address_id, latitude, longitude):
                    stats["success"] += 1
                    logger.info(f"✅ {i}/{len(addresses)} - ID {address_id}: {latitude:.6f}, {longitude:.6f}")
                else:
                    stats["failed"] += 1
                    logger.error(f"❌ {i}/{len(addresses)} - Błąd zapisu ID {address_id}")
            else:
                stats["failed"] += 1
                logger.warning(f"⚠️ {i}/{len(addresses)} - Brak współrzędnych dla ID {address_id}: {query}")
            
            stats["processed"] += 1
            
            # Opóźnienie między requestami (wymagane przez Nominatim)
            if i < len(addresses):
                time.sleep(DELAY_BETWEEN_REQUESTS)
                
        except Exception as e:
            stats["failed"] += 1
            logger.error(f"❌ Błąd przetwarzania adresu ID {address.get('id', 'unknown')}: {e}")
    
    return stats

def update_all_coordinates(batch_size: int = 50, max_addresses: int = None) -> None:
    """
    Główna funkcja aktualizująca wszystkie współrzędne
    
    Args:
        batch_size: Rozmiar batcha do przetworzenia
        max_addresses: Maksymalna liczba adresów (None = wszystkie)
    """
    print("="*80)
    print("🌍 GEOCODING UPDATER - UZUPEŁNIANIE WSPÓŁRZĘDNYCH")
    print("="*80)
    print(f"📊 Parametry:")
    print(f"   • Rozmiar batcha: {batch_size}")
    print(f"   • Maksymalne adresy: {max_addresses or 'wszystkie'}")
    print(f"   • Opóźnienie między requestami: {DELAY_BETWEEN_REQUESTS}s")
    print("="*80)
    
    total_stats = {
        "processed": 0,
        "success": 0,
        "failed": 0,
        "skipped": 0
    }
    
    processed_count = 0
    
    while True:
        # Pobierz następny batch
        remaining_limit = batch_size
        if max_addresses:
            remaining_limit = min(batch_size, max_addresses - processed_count)
            if remaining_limit <= 0:
                break
        
        addresses = get_addresses_without_coordinates(limit=remaining_limit)
        
        if not addresses:
            print("✅ Wszystkie adresy mają już współrzędne!")
            break
        
        print(f"\n🔄 PRZETWARZANIE BATCHA {processed_count//batch_size + 1}")
        print(f"📋 Adresy w batchu: {len(addresses)}")
        print("-" * 60)
        
        # Przetwórz batch
        batch_stats = process_geocoding_batch(addresses)
        
        # Aktualizuj statystyki
        for key in total_stats:
            total_stats[key] += batch_stats[key]
        
        processed_count += len(addresses)
        
        # Podsumowanie batcha
        print(f"\n📊 WYNIKI BATCHA:")
        print(f"   ✅ Sukces: {batch_stats['success']}")
        print(f"   ❌ Błędy: {batch_stats['failed']}")
        print(f"   ⏭️ Pominięte: {batch_stats['skipped']}")
        
        # Sprawdź czy osiągnięto limit
        if max_addresses and processed_count >= max_addresses:
            break
        
        # Jeśli batch był mniejszy niż limit, to koniec
        if len(addresses) < batch_size:
            break
        
        # Opóźnienie między batchami
        if len(addresses) == batch_size:
            print(f"⏳ Opóźnienie 5 sekund przed następnym batchem...")
            time.sleep(5)
    
    # Podsumowanie końcowe
    print("\n" + "="*80)
    print("📊 PODSUMOWANIE GEOCODINGU")
    print("="*80)
    print(f"📋 Łącznie przetworzonych: {total_stats['processed']}")
    print(f"✅ Pomyślnie geocodowanych: {total_stats['success']}")
    print(f"❌ Błędów geocodingu: {total_stats['failed']}")
    print(f"⏭️ Pominiętych: {total_stats['skipped']}")
    
    if total_stats['processed'] > 0:
        success_rate = (total_stats['success'] / total_stats['processed']) * 100
        print(f"📈 Skuteczność: {success_rate:.1f}%")
    
    print("="*80)

def test_geocoding():
    """Testuje geocoding na przykładowych adresach"""
    print("🧪 TEST GEOCODINGU")
    print("="*60)
    
    test_addresses = [
        {
            'id': 'test1',
            'city': 'Warszawa',
            'district': 'Mokotów',
            'street_name': 'ul. Puławska'
        },
        {
            'id': 'test2',
            'city': 'Kraków',
            'district': 'Stare Miasto'
        },
        {
            'id': 'test3',
            'city': 'Gdańsk',
            'district': 'Wrzeszcz',
            'street_name': 'ul. Grunwaldzka'
        },
        {
            'id': 'test4',
            'city': 'Poznań',
            'street_name': 'ul. Święty Marcin'
        },
        {
            'id': 'test5',
            'city': 'Wrocław',
            'district': 'Krzyki'
        }
    ]
    
    for i, address in enumerate(test_addresses, 1):
        print(f"\n{i}. Test adresu:")
        query = build_search_query(address)
        print(f"   📍 Zapytanie: {query}")
        
        coordinates = geocode_address(query)
        if coordinates:
            lat, lon = coordinates
            print(f"   ✅ Współrzędne: {lat:.6f}, {lon:.6f}")
            print(f"   🗺️ Google Maps: https://maps.google.com/?q={lat},{lon}")
        else:
            print(f"   ❌ Nie znaleziono współrzędnych")
        
        # Opóźnienie między testami
        if i < len(test_addresses):
            time.sleep(DELAY_BETWEEN_REQUESTS)
    
    print("="*60)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Geocoding updater dla tabeli addresses')
    parser.add_argument('--test', action='store_true', help='Uruchom test geocodingu')
    parser.add_argument('--update', action='store_true', help='Aktualizuj współrzędne w bazie')
    parser.add_argument('--batch-size', type=int, default=50, help='Rozmiar batcha (domyślnie: 50)')
    parser.add_argument('--max-addresses', type=int, help='Maksymalna liczba adresów do przetworzenia')
    parser.add_argument('--dry-run', action='store_true', help='Tryb testowy - bez zapisu do bazy')
    
    args = parser.parse_args()
    
    try:
        if args.test:
            test_geocoding()
        elif args.update:
            if args.dry_run:
                print("🧪 TRYB TESTOWY - bez zapisu do bazy")
                # W trybie dry-run można pokazać co by się stało
                addresses = get_addresses_without_coordinates(limit=5)
                for addr in addresses:
                    query = build_search_query(addr)
                    print(f"Adres ID {addr['id']}: {query}")
            else:
                update_all_coordinates(
                    batch_size=args.batch_size,
                    max_addresses=args.max_addresses
                )
        else:
            print("🌍 GEOCODING UPDATER")
            print("Użycie:")
            print("  python geocoding_updater.py --test           # Test geocodingu")
            print("  python geocoding_updater.py --update         # Aktualizuj wszystkie")
            print("  python geocoding_updater.py --update --max-addresses 100  # Limit")
            print("  python geocoding_updater.py --update --dry-run  # Test bez zapisu")
            
    except KeyboardInterrupt:
        print("\n⚠️ Przerwano przez użytkownika")
    except Exception as e:
        print(f"\n❌ Błąd krytyczny: {e}")
        logger.error(f"Błąd w geocoding_updater: {e}", exc_info=True) 