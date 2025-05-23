# INSTRUKCJE URUCHOMIENIA SCRAPERA NIERUCHOMOŚCI

## ✅ GOTOWY DO UŻYCIA!

Scraper został pomyślnie zainstalowany i przetestowany. Oto jak go używać:

## 🚀 Szybki Start

### 1. Podstawowe pakiety są już zainstalowane
```bash
# Te pakiety zostały już zainstalowane:
# requests, beautifulsoup4, supabase, fake-useragent, python-dotenv
```

### 2. Przetestuj scraper (bez bazy danych)
```bash
python working_demo.py
```

### 3. Uruchom testy wszystkich scraperów
```bash
python test_scraper_no_db.py
```

## 📊 WYNIKI TESTÓW

**✅ DZIAŁAJĄCE SCRAPERY:**
- **OLX.pl** - pobiera 10+ ogłoszeń z cenami i lokalizacjami
- **Otodom.pl** - pobiera 40+ ogłoszeń (tytuły i linki)

**⚠️ DO POPRAWIENIA:**
- **Freedom.pl** - wymaga aktualizacji selektorów CSS
- **Gratka.pl** - wymaga aktualizacji selektorów CSS  
- **Metrohouse.pl** - wymaga aktualizacji selektorów CSS
- **Domiporta.pl** - wymaga aktualizacji selektorów CSS

## 🗃️ KONFIGURACJA SUPABASE (OPCJONALNA)

Jeśli chcesz zapisywać dane do bazy Supabase:

### 1. Stwórz konto na supabase.com

### 2. Utwórz tabelę (POPRAWIONA WERSJA):
```sql
CREATE TABLE ogloszenia (
    id SERIAL PRIMARY KEY,
    title TEXT,
    price NUMERIC,
    price_currency TEXT,
    price_original TEXT,
    location TEXT,
    url TEXT UNIQUE,
    area TEXT,
    rooms TEXT,
    description TEXT,
    source TEXT,
    scraped_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 3. Ustaw zmienne środowiskowe:
```bash
# Windows PowerShell:
$env:SUPABASE_URL="https://twoj-projekt.supabase.co"
$env:SUPABASE_KEY="twój_anon_key"

# Linux/Mac:
export SUPABASE_URL="https://twoj-projekt.supabase.co"
export SUPABASE_KEY="twój_anon_key"
```

### 4. Przetestuj połączenie z Supabase:
```bash
python test_supabase.py
```

### 5. Uruchom z zapisem do bazy:
```bash
python main.py
```

## 📁 DOSTĘPNE PLIKI

### Główne pliki:
- `working_demo.py` - **DZIAŁAJĄCA DEMONSTRACJA** (POLECANE)
- `test_scraper_no_db.py` - Test wszystkich scraperów bez bazy
- `test_supabase.py` - **TEST ZAPISU DO SUPABASE**
- `simple_test.py` - Test podstawowych funkcji
- `main.py` - Pełny scraper z zapisem do Supabase

### Scrapery (katalog `scrapers/`):
- `otodom.py` - **DZIAŁA** (40+ ogłoszeń)
- `olx.py` - **DZIAŁA** (10+ ogłoszeń)
- `freedom.py` - do poprawienia
- `gratka.py` - do poprawienia  
- `metrohouse.py` - do poprawienia
- `domiporta.py` - do poprawienia

### Pomocnicze:
- `utils.py` - Funkcje pomocnicze
- `supabase_utils.py` - Obsługa bazy danych (POPRAWIONA)
- `config.py` - Konfiguracja

## 🔧 DOSTOSOWYWANIE SCRAPERÓW

Aby poprawić scrapery które nie działają:

1. **Otwórz plik scrapera** (np. `scrapers/freedom.py`)
2. **Sprawdź strukturę HTML** strony w przeglądarce (F12)
3. **Zaktualizuj selektory CSS** w funkcji `parse_*_listing()`
4. **Przetestuj zmiany** używając `debug_scraper.py`

### Przykład aktualizacji selektorów:
```python
# Stare selektory:
offers = soup.select(".property-item")

# Nowe selektory (sprawdź w przeglądarce):
offers = soup.select(".listing-card") or soup.select("[data-testid='listing']")
```

## 🎯 PRZYKŁADOWE WYNIKI

Po uruchomieniu `working_demo.py` otrzymasz:

```
============================================================
DEMONSTRACJA SCRAPERA NIERUCHOMOŚCI
============================================================

=== PODSUMOWANIE ===
Łącznie pobrano: 12 ogłoszeń
OLX: 10 ogłoszeń
Przykładowe: 2 ogłoszeń

=== PRZYKŁADOWE OGŁOSZENIA ===
--- Ogłoszenie 1 ---
Tytuł: ✅ Ostatnie małe mieszkanie 38m² z ogródkiem ✅
Cena: 305579.7 zł
URL: https://www.otodom.pl/pl/oferta/...
Źródło: olx.pl
```

## 🚨 ROZWIĄZYWANIE PROBLEMÓW

### Błąd: ModuleNotFoundError
```bash
pip install requests beautifulsoup4 supabase fake-useragent python-dotenv
```

### Błąd: "Could not find column in schema cache"
To znaczy że tabela w Supabase nie ma wszystkich kolumn. Rozwiązania:

**1. Dodaj brakujące kolumny:**
```sql
ALTER TABLE ogloszenia 
ADD COLUMN IF NOT EXISTS scraper_version TEXT,
ADD COLUMN IF NOT EXISTS source_page INTEGER;
```

**2. Lub użyj kodu który automatycznie filtruje kolumny** (już naprawione w `supabase_utils.py`)

### Selektory nie działają
- Struktura HTML portali często się zmienia
- Sprawdź aktualną strukturę w przeglądarce (F12)
- Zaktualizuj selektory CSS w odpowiednim pliku

### Blokowanie przez portal
- Zwiększ opóźnienia między requestami
- Zmień User-Agent headers
- Użyj proxy (opcjonalnie)

## ⚡ GOTOWE KOMENDY

```bash
# Test podstawowy (POLECANE):
python working_demo.py

# Test wszystkich scraperów:
python test_scraper_no_db.py

# Test Supabase:
python test_supabase.py

# Pełny scraper z Supabase (po konfiguracji):
python main.py

# Debug konkretnego scrapera:
python debug_scraper.py
```

## 🎉 SUKCES!

Scraper nieruchomości jest gotowy do użycia! 
- ✅ Pobiera dane z OLX i Otodom
- ✅ Ekstraktuje ceny, tytuły, linki
- ✅ Zapisuje do Supabase (po konfiguracji)
- ✅ Gotowy do rozbudowy o kolejne portale
- ✅ Automatyczne filtrowanie kolumn bazy danych 