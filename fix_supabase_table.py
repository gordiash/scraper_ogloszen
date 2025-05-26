#!/usr/bin/env python3
"""
NAPRAWA STRUKTURY TABELI SUPABASE
Sprawdza i dodaje brakujące kolumny do tabeli listings
"""
import logging
from datetime import datetime
from supabase_utils import get_supabase_client, test_supabase_connection

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_table_structure():
    """Sprawdza strukturę tabeli listings"""
    print("="*80)
    print("🔧 SPRAWDZANIE STRUKTURY TABELI SUPABASE")
    print("="*80)
    
    if not test_supabase_connection():
        print("❌ Brak połączenia z Supabase")
        return False
    
    try:
        supabase = get_supabase_client()
        
        # Sprawdź czy tabela istnieje i jakie ma kolumny
        print("📊 Sprawdzanie struktury tabeli 'listings'...")
        
        # Próbuj pobrać jeden rekord żeby zobaczyć strukturę
        result = supabase.table("listings").select("*").limit(1).execute()
        
        print("✅ Tabela 'listings' istnieje!")
        
        if result.data:
            # Jeśli są jakieś dane, pokaż strukturę
            sample_record = result.data[0]
            print(f"\n📋 ISTNIEJĄCE KOLUMNY:")
            for column in sorted(sample_record.keys()):
                print(f"   ✅ {column}")
        else:
            print("\n📋 Tabela jest pusta - nie można sprawdzić struktury")
            
        return True
        
    except Exception as e:
        error_str = str(e)
        if "does not exist" in error_str:
            print("❌ Tabela 'listings' nie istnieje!")
            print("\n💡 INSTRUKCJE TWORZENIA TABELI:")
            show_create_table_instructions()
        else:
            print(f"❌ Błąd sprawdzania tabeli: {e}")
        return False

def show_create_table_instructions():
    """Pokazuje instrukcje tworzenia tabeli"""
    print("🛠️ TWORZENIE TABELI W SUPABASE:")
    print("-" * 50)
    print("1. Otwórz https://app.supabase.com")
    print("2. Wybierz swój projekt")
    print("3. Przejdź do: Table Editor")
    print("4. Kliknij: Create a new table")
    print("5. Nazwa tabeli: listings")
    print("6. Dodaj kolumny:")
    print("")
    
    columns = [
        ("id", "int8", "Primary Key, Auto-increment"),
        ("title", "text", ""),
        ("price", "int8", ""),
        ("price_currency", "text", "Default: zł"),
        ("price_original", "text", ""),
        ("location", "text", ""),
        ("url", "text", "Unique constraint"),
        ("area", "text", ""),
        ("rooms", "text", ""),
        ("description", "text", "(Opcjonalne)"),
        ("source", "text", "Default: otodom.pl"),
        ("scraped_at", "timestamptz", "Default: now()")
    ]
    
    for name, type_name, note in columns:
        note_str = f" ({note})" if note else ""
        print(f"   • {name:<15} | {type_name:<12} {note_str}")
    
    print("\n7. Kliknij: Save")
    print("\n✅ Po utworzeniu tabeli uruchom ponownie scraper!")

def test_basic_insert():
    """Testuje podstawowy zapis do tabeli"""
    print(f"\n🧪 TEST ZAPISU DO TABELI:")
    print("-" * 50)
    
    try:
        supabase = get_supabase_client()
        
        # Testowe dane z tylko podstawowymi kolumnami
        test_data = {
            "title": "Test Ogłoszenie - można usunąć",
            "price": 999999,
            "location": "Test Location",
            "url": f"https://test-url-{datetime.now().isoformat()}.pl",
            "source": "test"
        }
        
        # Próbuj zapisać
        result = supabase.table("listings").insert(test_data).execute()
        
        if result.data:
            print("✅ Test zapisu UDANY!")
            print("💡 Tabela ma prawidłową strukturę")
            
            # Usuń testowy rekord
            supabase.table("listings").delete().eq("source", "test").execute()
            print("🗑️ Usunięto testowy rekord")
            return True
        else:
            print("❌ Test zapisu nie powiódł się")
            return False
            
    except Exception as e:
        print(f"❌ Błąd testu zapisu: {e}")
        if "column" in str(e):
            print("💡 Prawdopodobnie brakuje kolumn w tabeli")
            print("   Użyj instrukcji powyżej aby dodać brakujące kolumny")
        return False

def main():
    """Główna funkcja naprawy tabeli"""
    print("🔧 NARZĘDZIE NAPRAWY TABELI SUPABASE")
    print("=" * 80)
    
    # Sprawdź strukturę
    if check_table_structure():
        # Jeśli tabela istnieje, przetestuj zapis
        if test_basic_insert():
            print(f"\n🎉 SUKCES!")
            print("=" * 80)
            print("✅ Tabela działa prawidłowo")
            print("💡 Możesz teraz używać:")
            print("   python main_otodom_only.py --pages 5 --save-db")
        else:
            print(f"\n⚠️ PROBLEMY Z TABELĄ")
            print("=" * 80)
            print("❌ Tabela istnieje ale ma problemy ze strukturą")
            show_create_table_instructions()
    else:
        print(f"\n❌ TABELA NIE ISTNIEJE")
        print("=" * 80)
        show_create_table_instructions()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Przerwano przez użytkownika")
    except Exception as e:
        print(f"\n❌ Błąd krytyczny: {e}")
        logger.error(f"Błąd w fix_supabase_table: {e}", exc_info=True) 