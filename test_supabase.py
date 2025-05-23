"""
Test zapisu do Supabase z działającymi danymi
"""
import logging
from datetime import datetime
from working_demo import scrape_olx_simple, scrape_sample_portal
from supabase_utils import save_batch_listings, get_supabase_client

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_supabase_connection():
    """Test połączenia z Supabase"""
    try:
        supabase = get_supabase_client()
        # Sprawdź czy tabela istnieje
        result = supabase.table("ogloszenia").select("count", count="exact").execute()
        logger.info(f"✓ Połączenie z Supabase działa. Tabela ma {result.count} rekordów.")
        return True
    except Exception as e:
        logger.error(f"✗ Błąd połączenia z Supabase: {e}")
        return False

def test_save_to_supabase():
    """Test zapisu do Supabase"""
    print("=== TEST ZAPISU DO SUPABASE ===")
    
    # Test połączenia
    if not test_supabase_connection():
        print("✗ Nie można połączyć się z Supabase. Sprawdź konfigurację.")
        return False
    
    # Pobierz dane
    print("\n1. Pobieranie danych...")
    olx_listings = scrape_olx_simple()
    sample_listings = scrape_sample_portal()
    all_listings = olx_listings + sample_listings
    
    if not all_listings:
        print("✗ Brak danych do zapisu")
        return False
    
    print(f"✓ Pobrano {len(all_listings)} ogłoszeń")
    
    # Zapisz do bazy
    print("\n2. Zapisywanie do Supabase...")
    saved_count = save_batch_listings(all_listings)
    
    print(f"\n=== WYNIKI ===")
    print(f"Pobrano ogłoszeń: {len(all_listings)}")
    print(f"Zapisano do bazy: {saved_count}")
    print(f"Sukces: {saved_count > 0}")
    
    return saved_count > 0

if __name__ == "__main__":
    print("="*50)
    print("TEST INTEGRACJI SCRAPER + SUPABASE")
    print("="*50)
    
    success = test_save_to_supabase()
    
    if success:
        print("\n🎉 SUKCES! Scraper zapisuje dane do Supabase!")
    else:
        print("\n❌ BŁĄD! Sprawdź konfigurację Supabase.")
        print("\nSprawdź:")
        print("1. Czy tabela 'ogloszenia' istnieje w Supabase")
        print("2. Czy zmienne SUPABASE_URL i SUPABASE_KEY są ustawione")
        print("3. Czy masz uprawnienia do zapisu") 