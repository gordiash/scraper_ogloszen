#!/usr/bin/env python3
"""
TEST POŁĄCZENIA Z SUPABASE
Sprawdza konfigurację i połączenie z bazą danych
"""
import logging
from supabase_utils import test_supabase_connection, create_table_if_not_exists
from config import SUPABASE_URL, SUPABASE_KEY

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Test konfiguracji Supabase"""
    print("="*80)
    print("🗄️ TEST POŁĄCZENIA Z SUPABASE")
    print("="*80)
    
    # Sprawdź konfigurację
    print("📋 KONFIGURACJA:")
    print(f"   URL: {SUPABASE_URL}")
    print(f"   Key: {SUPABASE_KEY[:20]}..." if len(SUPABASE_KEY) > 20 else f"   Key: {SUPABASE_KEY}")
    
    # Test połączenia
    print(f"\n🔌 TEST POŁĄCZENIA:")
    if test_supabase_connection():
        print("✅ Połączenie działa!")
        print("\n💡 Możesz teraz używać:")
        print("   python main_otodom_only.py --pages 3 --save-db")
    else:
        print("❌ Połączenie nie działa")
        print("\n🛠️ INSTRUKCJE KONFIGURACJI:")
        print("1. Stwórz konto na https://app.supabase.com")
        print("2. Stwórz nowy projekt")
        print("3. Przejdź do Settings → API")
        print("4. Skopiuj URL i anon key")
        print("5. Stwórz plik .env:")
        print("   SUPABASE_URL=https://twój-projekt.supabase.co")
        print("   SUPABASE_KEY=twój_anon_key")
        
        print(f"\n📊 TWORZENIE TABELI:")
        create_table_if_not_exists()
    
    print(f"\n{'='*80}")
    print("🎉 TEST ZAKOŃCZONY!")
    print("="*80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Test przerwany przez użytkownika")
    except Exception as e:
        print(f"\n❌ Błąd testu: {e}")
        logger.error(f"Błąd w test_supabase: {e}", exc_info=True) 