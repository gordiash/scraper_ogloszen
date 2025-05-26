from supabase import create_client, Client
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Załaduj zmienne środowiskowe z pliku .env
load_dotenv()

# Konfiguracja Supabase z zmiennych środowiskowych lub domyślne
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://twoj-projekt.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "twój_anon_key")

logger = logging.getLogger(__name__)

# Cache dla istniejących kolumn - żeby nie sprawdzać za każdym razem
_table_columns_cache = {}

# Wymagane pola dla kompletnego ogłoszenia
REQUIRED_FIELDS = [
    'title',      # Tytuł ogłoszenia
    'price',      # Cena (liczba)
    'location',   # Lokalizacja 
    'url',        # Link do ogłoszenia
    'area',       # Powierzchnia
    'rooms',      # Liczba pokoi
    'source'      # Źródło (portal)
]

def validate_listing_completeness(listing: dict) -> tuple[bool, list]:
    """
    Sprawdza czy ogłoszenie ma wszystkie wymagane pola wypełnione
    
    Args:
        listing: Słownik z danymi ogłoszenia
    
    Returns:
        tuple: (is_complete, missing_fields)
            - is_complete: True jeśli wszystkie wymagane pola są wypełnione
            - missing_fields: Lista brakujących/pustych pól
    """
    missing_fields = []
    
    for field in REQUIRED_FIELDS:
        value = listing.get(field)
        
        # Sprawdź czy pole istnieje i nie jest puste
        if value is None or value == "" or value == 0:
            missing_fields.append(field)
        
        # Specjalne sprawdzenie dla price - musi być liczbą > 0
        elif field == "price":
            try:
                price_num = float(value) if isinstance(value, str) else value
                if price_num <= 0:
                    missing_fields.append(f"{field} (≤0)")
            except (ValueError, TypeError):
                missing_fields.append(f"{field} (invalid)")
    
    is_complete = len(missing_fields) == 0
    return is_complete, missing_fields

def get_supabase_client() -> Client:
    """Zwraca klienta Supabase"""
    # Sprawdź czy konfiguracja jest poprawna - zmienne środowiskowe powinny być ustawione
    if SUPABASE_URL == "https://twoj-projekt.supabase.co" or SUPABASE_KEY == "twój_anon_key" or not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError(
            "❌ Brak konfiguracji Supabase!\n"
            "💡 Aby zapisywać do bazy danych:\n"
            "   1. Skopiuj env_example.txt jako .env\n"
            "   2. Uzupełnij własnymi danymi Supabase\n"
            "   3. Lub ustaw zmienne środowiskowe:\n"
            "      $env:SUPABASE_URL=\"https://twój-projekt.supabase.co\"\n"
            "      $env:SUPABASE_KEY=\"twój_anon_key\""
        )
    
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def get_table_columns(table: str = "listings") -> list:
    """
    Sprawdza jakie kolumny istnieją w tabeli
    
    Returns:
        list: Lista nazw kolumn
    """
    # Sprawdź cache
    if table in _table_columns_cache:
        return _table_columns_cache[table]
    
    supabase = get_supabase_client()
    try:
        # Próbuj pobrać jeden rekord żeby zobaczyć strukturę
        result = supabase.table(table).select("*").limit(1).execute()
        
        if result.data:
            # Jeśli są dane, pobierz nazwy kolumn
            columns = list(result.data[0].keys())
        else:
            # Jeśli tabela pusta, spróbuj z podstawowym zapytaniem
            # i sprawdź błąd żeby ustalić dostępne kolumny
            columns = ['id', 'title', 'price', 'location', 'url', 'area', 'rooms', 'source', 'scraped_at']
            logger.warning(f"Tabela {table} jest pusta - używam podstawowych kolumn z area i rooms")
        
        _table_columns_cache[table] = columns
        logger.info(f"📋 Dostępne kolumny w tabeli '{table}': {', '.join(columns)}")
        return columns
        
    except Exception as e:
        logger.error(f"❌ Błąd sprawdzania kolumn tabeli {table}: {e}")
        # Zwróć podstawowe kolumny jako fallback (z area i rooms)
        return ['id', 'title', 'price', 'location', 'url', 'area', 'rooms', 'source', 'scraped_at']

def save_listing(listing: dict, table: str = "listings", require_complete: bool = True) -> bool:
    """
    Zapisuje ogłoszenie do tabeli Supabase
    
    Args:
        listing: Słownik z danymi ogłoszenia
        table: Nazwa tabeli w Supabase
        require_complete: Czy wymagać kompletnych danych (domyślnie True)
    
    Returns:
        bool: True jeśli zapis się udał, False w przeciwnym razie
    """
    # WALIDACJA KOMPLETNOŚCI DANYCH
    if require_complete:
        is_complete, missing_fields = validate_listing_completeness(listing)
        if not is_complete:
            title = listing.get('title', 'Brak tytułu')[:30]
            logger.warning(f"❌ Niepełne dane - pomijam: {title}... (brak: {', '.join(missing_fields)})")
            return False
    
    supabase = get_supabase_client()
    try:
        # Sprawdź czy ogłoszenie już istnieje (po URL)
        existing = supabase.table(table).select("*").eq("url", listing.get("url")).execute()
        if existing.data:
            logger.debug(f"Ogłoszenie już istnieje: {listing.get('url')}")
            return False
        
        # Pobierz dostępne kolumny
        available_columns = get_table_columns(table)
        
        # WSZYSTKIE MOŻLIWE DANE - będziemy filtrować tylko te które istnieją
        all_possible_data = {
            "title": listing.get("title"),
            "price": int(float(listing.get("price"))) if listing.get("price") is not None else None,
            "price_currency": listing.get("price_currency", "zł"),
            "price_original": listing.get("price_original"),
            "location": listing.get("location"),
            "url": listing.get("url"),
            "area": listing.get("area"),
            "rooms": listing.get("rooms"),
            "description": listing.get("description"),
            "source": listing.get("source", "otodom.pl"),
            "scraped_at": datetime.now().isoformat()
        }
        
        # FILTRUJ tylko te kolumny które istnieją w tabeli I MAJĄ WARTOŚCI
        data_to_save = {}
        for column, value in all_possible_data.items():
            if column in available_columns and value is not None and value != "" and str(value) != "None":
                data_to_save[column] = value
        
        # Zapisz nowe ogłoszenie - używa tylko istniejących kolumn
        result = supabase.table(table).insert(data_to_save).execute()
        logger.info(f"✅ Zapisano: {listing.get('title', 'Brak tytułu')[:30]}...")
        return True
        
    except Exception as e:
        error_msg = str(e)
        if "column" in error_msg and "not" in error_msg:
            logger.warning(f"⚠️ Kolumna nie istnieje w tabeli - pomijam: {error_msg}")
            logger.info("💡 Uruchom: python fix_supabase_table.py aby naprawić strukturę tabeli")
            # Wyczyść cache kolumn - może się zmienić
            if table in _table_columns_cache:
                del _table_columns_cache[table]
        else:
            logger.error(f"❌ Błąd zapisu do Supabase: {e}")
        return False

def save_listings_to_supabase(listings: list, table: str = "listings", require_complete: bool = True) -> int:
    """
    Zapisuje listę ogłoszeń do Supabase z walidacją kompletności danych
    FUNKCJA UŻYWANA PRZEZ main_otodom_only.py
    
    Args:
        listings: Lista słowników z danymi ogłoszeń
        table: Nazwa tabeli w Supabase
        require_complete: Czy wymagać kompletnych danych (domyślnie True)
    
    Returns:
        int: Liczba zapisanych ogłoszeń
    """
    if not listings:
        logger.warning("Brak ogłoszeń do zapisania")
        return 0
    
    logger.info(f"🎯 Rozpoczynam zapis {len(listings)} ogłoszeń do Supabase...")
    if require_complete:
        logger.info(f"📋 Walidacja kompletności danych: WŁĄCZONA")
        logger.info(f"🔍 Wymagane pola: {', '.join(REQUIRED_FIELDS)}")
    else:
        logger.info(f"📋 Walidacja kompletności danych: WYŁĄCZONA")
    
    # Pre-walidacja - sprawdź ile ogłoszeń jest kompletnych
    if require_complete:
        complete_count = 0
        incomplete_listings = []
        
        for listing in listings:
            is_complete, missing_fields = validate_listing_completeness(listing)
            if is_complete:
                complete_count += 1
            else:
                title = listing.get('title', 'Brak tytułu')[:30]
                incomplete_listings.append((title, missing_fields))
        
        logger.info(f"📊 Pre-walidacja: {complete_count}/{len(listings)} ogłoszeń kompletnych ({complete_count/len(listings)*100:.1f}%)")
        
        if incomplete_listings:
            logger.warning(f"⚠️ Znaleziono {len(incomplete_listings)} niepełnych ogłoszeń:")
            for title, missing in incomplete_listings[:5]:  # Pokaż max 5 przykładów
                logger.warning(f"   • {title}... (brak: {', '.join(missing)})")
            if len(incomplete_listings) > 5:
                logger.warning(f"   • ... i {len(incomplete_listings) - 5} więcej")
    
    saved_count = 0
    skipped_duplicates = 0
    skipped_incomplete = 0
    error_count = 0
    
    for i, listing in enumerate(listings, 1):
        try:
            # Sprawdź kompletność przed zapisem
            if require_complete:
                is_complete, missing_fields = validate_listing_completeness(listing)
                if not is_complete:
                    skipped_incomplete += 1
                    continue
            
            # Spróbuj zapisać
            if save_listing(listing, table, require_complete=False):  # Walidacja już wykonana
                saved_count += 1
            else:
                skipped_duplicates += 1
            
            # Progress info co 10 ogłoszeń
            if i % 10 == 0:
                total_skipped = skipped_duplicates + skipped_incomplete
                logger.info(f"📊 Postęp: {i}/{len(listings)} - zapisane: {saved_count}, pominięte: {total_skipped}")
                
        except Exception as e:
            error_count += 1
            logger.error(f"❌ Błąd zapisu ogłoszenia {i}: {e}")
    
    # Podsumowanie
    logger.info(f"🎉 Zakończono zapis do Supabase:")
    logger.info(f"   ✅ Zapisane: {saved_count}")
    logger.info(f"   ⏭️ Pominięte (duplikaty): {skipped_duplicates}")
    if require_complete and skipped_incomplete > 0:
        logger.info(f"   📝 Pominięte (niepełne dane): {skipped_incomplete}")
    logger.info(f"   ❌ Błędy: {error_count}")
    
    # Dodatkowe statystyki
    total_processed = saved_count + skipped_duplicates + skipped_incomplete + error_count
    if total_processed > 0:
        save_rate = (saved_count / total_processed) * 100
        logger.info(f"📈 Skuteczność zapisu: {save_rate:.1f}% ({saved_count}/{total_processed})")
    
    return saved_count

def save_batch_listings(listings: list, table: str = "listings", require_complete: bool = True) -> int:
    """
    Alias dla kompatybilności wstecznej
    
    Args:
        listings: Lista słowników z danymi ogłoszeń
        table: Nazwa tabeli w Supabase
        require_complete: Czy wymagać kompletnych danych (domyślnie True)
    
    Returns:
        int: Liczba zapisanych ogłoszeń
    """
    return save_listings_to_supabase(listings, table, require_complete)

def test_supabase_connection() -> bool:
    """
    Testuje połączenie z Supabase
    
    Returns:
        bool: True jeśli połączenie działa
    """
    try:
        supabase = get_supabase_client()
        # Próbuj pobrać informację o tabeli
        result = supabase.table("listings").select("id").limit(1).execute()
        logger.info("✅ Połączenie z Supabase działa!")
        return True
    except Exception as e:
        logger.error(f"❌ Błąd połączenia z Supabase: {e}")
        logger.error("💡 Sprawdź konfigurację w .env:")
        logger.error("   SUPABASE_URL=https://twój-projekt.supabase.co")
        logger.error("   SUPABASE_KEY=twój_anon_key")
        return False

def create_table_if_not_exists():
    """
    Informacja o tworzeniu tabeli
    """
    logger.info("💡 Aby stworzyć tabelę 'listings' w Supabase:")
    logger.info("   1. Otwórz https://app.supabase.com")
    logger.info("   2. Przejdź do Table Editor")
    logger.info("   3. Stwórz nową tabelę 'listings' z kolumnami:")
    logger.info("      - id (int8, primary key, auto-increment)")
    logger.info("      - title (text)")
    logger.info("      - price (int8)")
    logger.info("      - price_currency (text, default 'zł')")
    logger.info("      - price_original (text)")
    logger.info("      - location (text)")
    logger.info("      - url (text, unique)")
    logger.info("      - area (text)")
    logger.info("      - rooms (text)")
    logger.info("      - description (text)")
    logger.info("      - source (text, default 'otodom.pl')")
    logger.info("      - scraped_at (timestamptz, default now())") 