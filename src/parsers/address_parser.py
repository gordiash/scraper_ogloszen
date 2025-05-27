#!/usr/bin/env python3
"""
PARSER ADRESÓW - ROZDZIELANIE LOKALIZACJI Z BAZY SUPABASE
Pobiera dane z kolumny location w tabeli listings i rozdziela je na części w tabeli addresses
"""
import logging
import re
import sys
import os
from typing import Dict, List, Optional, Tuple

# Dodaj główny katalog do ścieżki
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from supabase_utils import get_supabase_client

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Słownik województw polskich
POLISH_PROVINCES = {
    'dolnośląskie', 'kujawsko-pomorskie', 'lubelskie', 'lubuskie', 'łódzkie',
    'małopolskie', 'mazowieckie', 'opolskie', 'podkarpackie', 'podlaskie',
    'pomorskie', 'śląskie', 'świętokrzyskie', 'warmińsko-mazurskie',
    'wielkopolskie', 'zachodniopomorskie'
}

# Główne miasta polskie
MAJOR_CITIES = {
    'warszawa', 'kraków', 'łódź', 'wrocław', 'poznań', 'gdańsk', 'szczecin',
    'bydgoszcz', 'lublin', 'białystok', 'katowice', 'gdynia', 'częstochowa',
    'radom', 'sosnowiec', 'toruń', 'kielce', 'gliwice', 'zabrze', 'bytom',
    'olsztyn', 'bielsko-biała', 'rzeszów', 'ruda śląska', 'rybnik'
}

def normalize_location_text(text: str) -> str:
    """Normalizuje tekst lokalizacji"""
    if not text:
        return ""
    
    # Usuń nadmiarowe spacje i znaki
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Zamień na małe litery dla porównań
    text = text.lower()
    
    # Usuń zbędne znaki interpunkcyjne
    text = re.sub(r'[^\w\s,.-]', '', text)
    
    return text

def parse_location_string(location: str) -> Dict[str, Optional[str]]:
    """
    Parsuje string lokalizacji na komponenty adresu
    
    Args:
        location: String z lokalizacją
    
    Returns:
        Dict z komponentami adresu
    """
    result = {
        'street_name': None,
        'district': None,
        'sub_district': None,
        'city': None,
        'province': None
    }
    
    if not location:
        return result
    
    # Normalizuj tekst
    normalized = normalize_location_text(location)
    
    # Podziel po przecinkach
    parts = [part.strip() for part in normalized.split(',')]
    
    if not parts:
        return result
    
    # Analiza części
    street_indicators = ['ul.', 'ulica', 'al.', 'aleja', 'pl.', 'plac', 'os.', 'osiedle']
    
    for i, part in enumerate(parts):
        part_lower = part.lower()
        
        # Sprawdź czy to województwo
        if any(prov in part_lower for prov in POLISH_PROVINCES):
            result['province'] = part.title()
            continue
        
        # Sprawdź czy to główne miasto
        if any(city in part_lower for city in MAJOR_CITIES):
            result['city'] = part.title()
            continue
        
        # Sprawdź czy to ulica
        if any(indicator in part_lower for indicator in street_indicators):
            result['street_name'] = part.title()
            continue
        
        # Logika przypisania na podstawie pozycji
        if i == 0:
            # Pierwsza część - prawdopodobnie miasto
            result['city'] = part.title()
        elif i == 1:
            # Druga część - prawdopodobnie dzielnica
            result['district'] = part.title()
        elif i == 2:
            # Trzecia część - może być pod-dzielnicą lub ulicą
            if any(indicator in part_lower for indicator in street_indicators):
                result['street_name'] = part.title()
            else:
                result['sub_district'] = part.title()
        elif i == 3:
            # Czwarta część - prawdopodobnie ulica jeśli nie została jeszcze przypisana
            if not result['street_name']:
                result['street_name'] = part.title()
    
    # Post-processing: jeśli nie znaleziono miasta w głównych miastach,
    # ale pierwsza część wygląda jak miasto
    if not result['city'] and parts:
        first_part = parts[0].title()
        # Sprawdź czy pierwsza część może być miastem (nie zawiera typowych wskaźników ulic)
        if not any(indicator in first_part.lower() for indicator in street_indicators):
            result['city'] = first_part
    
    # NOWA LOGIKA: Jeśli city jest null, spróbuj uzupełnić z district
    if not result['city'] and result['district']:
        # Sprawdź czy district wygląda jak miasto (nie zawiera wskaźników ulic)
        district_text = result['district'].lower()
        if not any(indicator in district_text for indicator in street_indicators):
            # Przenieś district do city i wyczyść district
            result['city'] = result['district']
            result['district'] = None
            logger.debug(f"Przeniesiono '{result['city']}' z district do city")
    
    return result

def create_addresses_table():
    """Tworzy tabelę addresses jeśli nie istnieje"""
    supabase = get_supabase_client()
    
    # Sprawdź czy tabela istnieje
    try:
        result = supabase.table("addresses").select("id").limit(1).execute()
        logger.info("✅ Tabela 'addresses' już istnieje")
        return True
    except Exception as e:
        logger.warning(f"⚠️ Tabela 'addresses' nie istnieje: {e}")
        logger.info("💡 Utwórz tabelę 'addresses' w Supabase:")
        logger.info("""
CREATE TABLE addresses (
    id SERIAL PRIMARY KEY,
    full_address TEXT NOT NULL,
    street_name TEXT,
    district TEXT,
    sub_district TEXT,
    city TEXT,
    province TEXT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    foreign_key INTEGER REFERENCES listings(id)
);
        """)
        return False

def get_listings_locations() -> List[Tuple[int, str]]:
    """
    Pobiera wszystkie lokalizacje z tabeli listings (z paginacją)
    
    Returns:
        List[Tuple[int, str]]: Lista (id, location)
    """
    supabase = get_supabase_client()
    all_locations = []
    page_size = 1000
    offset = 0
    
    try:
        while True:
            # Pobierz stronę danych
            result = supabase.table("listings").select("id, location").range(offset, offset + page_size - 1).execute()
            
            if not result.data:
                break
                
            # Dodaj lokalizacje z tej strony
            page_locations = [(row['id'], row['location']) for row in result.data if row.get('location')]
            all_locations.extend(page_locations)
            
            logger.info(f"📄 Strona {offset//page_size + 1}: pobrano {len(page_locations)} lokalizacji")
            
            # Jeśli otrzymaliśmy mniej niż page_size rekordów, to koniec
            if len(result.data) < page_size:
                break
                
            offset += page_size
        
        logger.info(f"📊 ŁĄCZNIE pobrano {len(all_locations)} lokalizacji z tabeli listings")
        return all_locations
            
    except Exception as e:
        logger.error(f"❌ Błąd pobierania lokalizacji: {e}")
        return []

def save_parsed_address(listing_id: int, full_address: str, parsed_components: Dict) -> bool:
    """
    Zapisuje sparsowany adres do tabeli addresses
    
    Args:
        listing_id: ID z tabeli listings
        full_address: Pełny adres oryginalny
        parsed_components: Sparsowane komponenty adresu
    
    Returns:
        bool: True jeśli zapis się udał
    """
    supabase = get_supabase_client()
    
    try:
        # Sprawdź czy adres już istnieje dla tego listing_id
        existing = supabase.table("addresses").select("id").eq("foreign_key", listing_id).execute()
        
        if existing.data:
            logger.debug(f"Adres dla listing_id {listing_id} już istnieje")
            return False
        
        # Przygotuj dane do zapisu
        address_data = {
            "full_address": full_address,
            "street_name": parsed_components.get('street_name'),
            "district": parsed_components.get('district'),
            "sub_district": parsed_components.get('sub_district'),
            "city": parsed_components.get('city'),
            "province": parsed_components.get('province'),
            "foreign_key": listing_id
        }
        
        # Usuń puste wartości
        address_data = {k: v for k, v in address_data.items() if v is not None and v != ""}
        
        # Zapisz do bazy
        result = supabase.table("addresses").insert(address_data).execute()
        
        if result.data:
            logger.debug(f"✅ Zapisano adres dla listing_id {listing_id}")
            return True
        else:
            logger.warning(f"⚠️ Nie udało się zapisać adresu dla listing_id {listing_id}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Błąd zapisu adresu dla listing_id {listing_id}: {e}")
        return False

def process_all_locations():
    """
    Główna funkcja - przetwarza wszystkie lokalizacje z tabeli listings
    """
    print("="*80)
    print("🏠 PARSER ADRESÓW - ROZDZIELANIE LOKALIZACJI")
    print("="*80)
    
    # Sprawdź czy tabela addresses istnieje
    if not create_addresses_table():
        print("❌ Tabela 'addresses' nie istnieje. Utwórz ją najpierw w Supabase.")
        return
    
    # Pobierz wszystkie lokalizacje
    locations = get_listings_locations()
    
    if not locations:
        print("❌ Brak lokalizacji do przetworzenia")
        return
    
    print(f"📊 Znaleziono {len(locations)} lokalizacji do przetworzenia")
    print("-"*80)
    
    # Statystyki
    processed_count = 0
    saved_count = 0
    skipped_count = 0
    error_count = 0
    
    # Przetwarzaj każdą lokalizację
    for i, (listing_id, location) in enumerate(locations, 1):
        try:
            if not location or location.strip() == "":
                skipped_count += 1
                continue
            
            # Parsuj lokalizację
            parsed = parse_location_string(location)
            
            # Zapisz do bazy
            if save_parsed_address(listing_id, location, parsed):
                saved_count += 1
            else:
                skipped_count += 1
            
            processed_count += 1
            
            # Pokaż progress co 50 rekordów
            if i % 50 == 0:
                print(f"📊 Postęp: {i}/{len(locations)} - zapisane: {saved_count}, pominięte: {skipped_count}")
            
            # Pokaż przykłady pierwszych 5 parsowań
            if i <= 5:
                print(f"\n{i}. Listing ID: {listing_id}")
                print(f"   📍 Oryginalny: '{location}'")
                print(f"   🏙️ Miasto: {parsed.get('city', 'brak')}")
                print(f"   🏘️ Dzielnica: {parsed.get('district', 'brak')}")
                print(f"   🏠 Pod-dzielnica: {parsed.get('sub_district', 'brak')}")
                print(f"   🛣️ Ulica: {parsed.get('street_name', 'brak')}")
                print(f"   🗺️ Województwo: {parsed.get('province', 'brak')}")
                
        except Exception as e:
            error_count += 1
            logger.error(f"❌ Błąd przetwarzania lokalizacji {listing_id}: {e}")
    
    # Podsumowanie
    print("\n" + "="*80)
    print("📊 PODSUMOWANIE PARSOWANIA ADRESÓW")
    print("="*80)
    print(f"📋 Łącznie lokalizacji: {len(locations)}")
    print(f"✅ Przetworzone: {processed_count}")
    print(f"💾 Zapisane do bazy: {saved_count}")
    print(f"⏭️ Pominięte: {skipped_count}")
    print(f"❌ Błędy: {error_count}")
    
    if processed_count > 0:
        success_rate = (saved_count / processed_count) * 100
        print(f"📈 Skuteczność: {success_rate:.1f}%")
    
    print("="*80)

if __name__ == "__main__":
    """Test parsera adresów"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Parser adresów z bazy Supabase')
    parser.add_argument('--test', action='store_true', help='Uruchom test parsowania')
    parser.add_argument('--process', action='store_true', help='Przetwórz wszystkie adresy z bazy')
    
    args = parser.parse_args()
    
    try:
        if args.test:
            # Test parsowania
            test_locations = [
                "Warszawa, Mokotów, ul. Puławska 123",
                "Kraków, Stare Miasto",
                "Gdańsk, Wrzeszcz, Grunwaldzka"
            ]
            
            print("🧪 TEST PARSOWANIA ADRESÓW")
            print("="*60)
            
            for i, location in enumerate(test_locations, 1):
                print(f"\n{i}. '{location}'")
                parsed = parse_location_string(location)
                
                print(f"   🏙️ Miasto: {parsed.get('city', 'brak')}")
                print(f"   🏘️ Dzielnica: {parsed.get('district', 'brak')}")
                print(f"   🛣️ Ulica: {parsed.get('street_name', 'brak')}")
                
        elif args.process:
            process_all_locations()
        else:
            print("🏠 PARSER ADRESÓW")
            print("Użycie:")
            print("  python address_parser.py --test      # Test parsowania")
            print("  python address_parser.py --process   # Przetwórz wszystkie adresy")
            
    except KeyboardInterrupt:
        print("\n⚠️ Przerwano przez użytkownika")
    except Exception as e:
        print(f"\n❌ Błąd krytyczny: {e}")
        logger.error(f"Błąd w address_parser: {e}", exc_info=True) 