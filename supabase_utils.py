from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY
import logging

logger = logging.getLogger(__name__)

def get_supabase_client() -> Client:
    """Zwraca klienta Supabase"""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def save_listing(listing: dict, table: str = "ogloszenia") -> bool:
    """
    Zapisuje ogłoszenie do tabeli Supabase
    
    Args:
        listing: Słownik z danymi ogłoszenia
        table: Nazwa tabeli w Supabase
    
    Returns:
        bool: True jeśli zapis się udał, False w przeciwnym razie
    """
    supabase = get_supabase_client()
    try:
        # Sprawdź czy ogłoszenie już istnieje (po URL)
        existing = supabase.table(table).select("*").eq("url", listing.get("url")).execute()
        if existing.data:
            logger.info(f"Ogłoszenie już istnieje: {listing.get('url')}")
            return False
        
        # Filtruj tylko podstawowe kolumny które na pewno istnieją
        filtered_listing = {
            "title": listing.get("title"),
            "price": listing.get("price"),
            "price_currency": listing.get("price_currency"),
            "price_original": listing.get("price_original"),
            "location": listing.get("location"),
            "url": listing.get("url"),
            "area": listing.get("area"),
            "rooms": listing.get("rooms"),
            "description": listing.get("description"),
            "source": listing.get("source"),
            "scraped_at": listing.get("scraped_at")
        }
        
        # Usuń None values
        filtered_listing = {k: v for k, v in filtered_listing.items() if v is not None}
            
        # Zapisz nowe ogłoszenie
        result = supabase.table(table).insert(filtered_listing).execute()
        logger.info(f"Zapisano ogłoszenie: {listing.get('title', 'Brak tytułu')}")
        return True
    except Exception as e:
        logger.error(f"Błąd zapisu do Supabase: {e}")
        return False

def save_batch_listings(listings: list, table: str = "ogloszenia") -> int:
    """
    Zapisuje listę ogłoszeń do Supabase
    
    Args:
        listings: Lista słowników z danymi ogłoszeń
        table: Nazwa tabeli w Supabase
    
    Returns:
        int: Liczba zapisanych ogłoszeń
    """
    saved_count = 0
    for listing in listings:
        if save_listing(listing, table):
            saved_count += 1
    return saved_count

def create_table_if_not_exists():
    """
    Tworzy tabelę ogłoszeń jeśli nie istnieje
    Uwaga: To wymaga uprawnień admin w Supabase
    """
    supabase = get_supabase_client()
    try:
        # Ten kod wymaga uprawnień admin - lepiej stworzyć tabelę ręcznie
        # w interfejsie Supabase
        pass
    except Exception as e:
        logger.error(f"Błąd tworzenia tabeli: {e}") 