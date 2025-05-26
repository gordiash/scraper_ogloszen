#!/usr/bin/env python3
"""
SPRAWDZENIE KONFIGURACJI ZMIENNYCH ŚRODOWISKOWYCH
"""
import os
from dotenv import load_dotenv

print("🔧 SPRAWDZANIE KONFIGURACJI SUPABASE")
print("="*60)

# Sprawdź czy jest plik .env
env_file_exists = os.path.exists('.env')
print(f"📄 Plik .env istnieje: {'Tak' if env_file_exists else 'Nie'}")

if env_file_exists:
    # Wczytaj .env
    load_dotenv()
    print("✅ Wczytano plik .env")
else:
    print("⚠️ Brak pliku .env - sprawdzam zmienne systemowe")

print("\n🔍 ZMIENNE ŚRODOWISKOWE:")
print("-"*40)

# Sprawdź zmienne
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

print(f"SUPABASE_URL: {'✅ ustawiona' if supabase_url else '❌ brak'}")
if supabase_url:
    # Pokaż pierwsze i ostatnie znaki dla bezpieczeństwa
    masked_url = f"{supabase_url[:15]}...{supabase_url[-10:]}" if len(supabase_url) > 25 else supabase_url
    print(f"  Wartość: {masked_url}")

print(f"SUPABASE_KEY: {'✅ ustawiona' if supabase_key else '❌ brak'}")
if supabase_key:
    # Pokaż tylko pierwsze kilka znaków dla bezpieczeństwa
    masked_key = f"{supabase_key[:15]}...{supabase_key[-5:]}" if len(supabase_key) > 20 else "***"
    print(f"  Wartość: {masked_key}")

# Test konfiguracji Supabase
print(f"\n🧪 TEST KONFIGURACJI:")
print("-"*40)

try:
    from supabase_utils import get_supabase_client, test_supabase_connection
    
    # Test utworzenia klienta
    client = get_supabase_client()
    print("✅ Klient Supabase został utworzony")
    
    # Test połączenia
    print("🔄 Sprawdzam połączenie z bazą danych...")
    connection_result = test_supabase_connection()
    if connection_result:
        print("✅ Połączenie z Supabase działa!")
        
        # Test struktury tabeli
        from supabase_utils import get_table_columns
        print("🔄 Sprawdzam strukturę tabeli...")
        columns = get_table_columns("listings")
        print(f"📋 Tabela 'listings' ma {len(columns)} kolumn")
        
    else:
        print("❌ Błąd połączenia z Supabase")
        
except Exception as e:
    print(f"❌ Błąd konfiguracji: {e}")
    import traceback
    print("Szczegóły błędu:")
    print(traceback.format_exc())

print(f"\n💡 INSTRUKCJE:")
print("-"*40)
print("Jeśli brak konfiguracji:")
print("1. Skopiuj env_example.txt jako .env")
print("2. Wypełnij prawdziwe dane Supabase")
print("3. Lub ustaw zmienne systemowe:")
print("   $env:SUPABASE_URL='https://twój-projekt.supabase.co'")
print("   $env:SUPABASE_KEY='twój_klucz'")
print("="*60) 