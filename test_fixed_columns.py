#!/usr/bin/env python3
"""
Test sprawdzenia poprawionych kolumn z area i rooms
"""
from supabase_utils import get_table_columns, _table_columns_cache

print("🔧 TEST POPRAWIONYCH KOLUMN")
print("="*60)

# Wyczyść cache
_table_columns_cache.clear()
print("✅ Cache kolumn wyczyszczony")

# Pobierz kolumny
print("\n📋 Pobieranie kolumn z tabeli...")
columns = get_table_columns('listings')

print(f"\n📊 WYNIK:")
print(f"   Liczba kolumn: {len(columns)}")
print(f"   Kolumny: {columns}")

# Sprawdź czy area i rooms są na liście
area_present = 'area' in columns
rooms_present = 'rooms' in columns

print(f"\n🔍 SPRAWDZENIE:")
print(f"   📐 area: {'✅' if area_present else '❌'}")
print(f"   🚪 rooms: {'✅' if rooms_present else '❌'}")

if area_present and rooms_present:
    print(f"\n🎉 SUCCESS: Kolumny area i rooms są dostępne!")
else:
    print(f"\n❌ PROBLEM: Brakuje kolumn area i/lub rooms")

print("="*60) 