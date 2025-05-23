# INSTRUKCJE URUCHOMIENIA SCRAPERA NIERUCHOMOŚCI

## ✅ GOTOWY DO UŻYCIA! + 🔍 WYKRYWANIE DUPLIKATÓW

Scraper został pomyślnie zainstalowany i przetestowany z pełną obsługą Selenium i **zaawansowanym wykrywaniem duplikatów między portalami**. Oto jak go używać:

## 🚀 Szybki Start

### 1. Podstawowe pakiety są już zainstalowane
```bash
# Te pakiety zostały już zainstalowane:
# requests, beautifulsoup4, supabase, fake-useragent, python-dotenv, selenium
# + nowe: fuzzywuzzy, python-Levenshtein (do wykrywania duplikatów)
```

### 2. ✨ NOWA FUNKCJA: Test deduplikacji
```bash
python test_deduplicate.py
```

### 3. Przetestuj scrapery z Selenium + deduplikacją
```bash
python complete_demo.py
```

### 4. Przetestuj wszystkie scrapery (bez bazy danych)
```bash
python test_scraper_no_db.py
```

## 🔍 **NOWA FUNKCJONALNOŚĆ: WYKRYWANIE DUPLIKATÓW**

### ✨ **Co to daje:**
- **Automatyczne wykrywanie** tego samego ogłoszenia na różnych portalach
- **Inteligentne porównywanie** tytułów, cen, powierzchni, pokoi, lokalizacji
- **Zachowanie najlepszego źródła** (np. Otodom ma priorytet nad OLX)
- **Szczegółowe raporty** o znalezionych duplikatach
- **Konfigurowalne progi** podobieństwa (75% domyślnie)

### 🎯 **Przykładowe wyniki:**
```
🔍 WYKRYWANIE DUPLIKATÓW
📊 Łącznie pobrano: 196 ogłoszeń
🧹 Po deduplikacji:  128 unikatowych ogłoszeń
🔄 Usunięto duplikatów: 68

📊 Duplikaty per portal:
   • domiporta.pl: 11 duplikatów
   • freedom.pl: 19 duplikatów
   • metrohouse.pl: 35 duplikatów
   • otodom.pl: 3 duplikatów
```

### 🛠️ **Jak działają algorithmy:**

1. **Normalizacja tekstu** - usuwa interpunkcję, słowa nieistotne
2. **Fuzzy matching** tytułów (waga 40%)
3. **Porównanie cen** - tolerancja do 5% różnicy (waga 25%)  
4. **Powierzchnia** - tolerancja do 10% różnicy (waga 15%)
5. **Liczba pokoi** - dokładne dopasowanie (waga 10%)
6. **Lokalizacja** - podobieństwo częściowe (waga 10%)

### 📊 **Ranking portali** (najlepsze mają priorytet):
1. **otodom.pl** - najwyższy priorytet
2. **olx.pl** 
3. **domiporta.pl**
4. **gratka.pl**
5. **metrohouse.pl**
6. **freedom.pl** - najniższy priorytet

## 📊 WYNIKI TESTÓW - AKTUALNE STANIE Z DEDUPLIKACJĄ

### ✅ **DZIAŁAJĄCE SCRAPERY Z SELENIUM:**
- **Freedom.pl** - **20 ogłoszeń** z cenami i linkami
- **Gratka.pl** - **37 ogłoszeń** z linkami
- **Metrohouse.pl** - **63 ogłoszenia** z linkami
- **Domiporta.pl** - **36 ogłoszeń** z cenami i linkami

### ✅ **DZIAŁAJĄCE SCRAPERY Z REQUESTS:**
- **OLX.pl** - **10+ ogłoszeń** z cenami i lokalizacjami
- **Otodom.pl** - **40+ ogłoszeń** (tytuły i linki)

## 📈 **PODSUMOWANIE WYDAJNOŚCI Z DEDUPLIKACJĄ:**
- **Wszystkie 6 portali działają**: 6/6 ✅
- **Przed deduplikacją**: ~196 ogłoszeń
- **Po deduplikacji**: ~128 unikatowych ogłoszeń  
- **Skuteczność deduplikacji**: ~35% duplikatów wykryte i usunięte
- **Oszczędność miejsca w bazie**: znaczące!

## 🔧 KONFIGURACJA SELENIUM

Selenium jest już skonfigurowane i gotowe do użycia:
- **Headless mode**: Domyślnie włączony
- **Timeout**: 20 sekund
- **User-Agent**: Losowy (anti-detection)
- **Anti-bot protection**: Podstawowe zabezpieczenia

### Konfiguracja w `config.py`:
```python
SELENIUM_ENABLED = True
SELENIUM_HEADLESS = True
SELENIUM_TIMEOUT = 20
SELENIUM_WAIT_TIME = 2
```

## 🔍 KONFIGURACJA DEDUPLIKACJI

### Dostosuj próg podobieństwa:
```python
# W utils.py lub podczas wywołania:
deduplicated = deduplicate_listings(all_listings, 
                                   similarity_threshold=75.0,  # 0-100%
                                   keep_best_source=True)
```

### Progi podobieństwa:
- **90%+**: Bardzo podobne (prawdopodobnie duplikaty)
- **75-89%**: Średnio podobne (wymagają weryfikacji)
- **60-74%**: Słabo podobne
- **<60%**: Różne ogłoszenia

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

### 5. Uruchom z zapisem do bazy (z deduplikacją):
```bash
python main.py
```

## 📁 DOSTĘPNE PLIKI

### Główne pliki:
- `complete_demo.py` - **PEŁNA DEMONSTRACJA Z DEDUPLIKACJĄ** (POLECANE) ⭐
- `test_deduplicate.py` - **TEST WYKRYWANIA DUPLIKATÓW** (NOWE) 🔍
- `test_main_with_deduplication.py` - **TEST GŁÓWNEGO SCRAPERA Z DEDUPLIKACJĄ** (NOWE) 🎯
- `test_selenium_scrapers.py` - Test wszystkich scraperów z Selenium
- `working_demo.py` - Działająca demonstracja bez Selenium
- `test_scraper_no_db.py` - Test wszystkich scraperów bez bazy
- `test_supabase.py` - **TEST ZAPISU DO SUPABASE**
- `main.py` - **Pełny scraper z zapisem do Supabase + DEDUPLIKACJA** ⭐

### Scrapery z Selenium (katalog `scrapers/`):
- `freedom.py` - **DZIAŁA** (20 ogłoszeń) ⚡ Selenium
- `gratka.py` - **DZIAŁA** (37 ogłoszeń) ⚡ Selenium
- `metrohouse.py` - **DZIAŁA** (63 ogłoszenia) ⚡ Selenium
- `domiporta.py` - **DZIAŁA** (36 ogłoszeń) ⚡ Selenium

### Scrapery z Requests:
- `otodom.py` - **DZIAŁA** (40+ ogłoszeń)
- `olx.py` - **DZIAŁA** (10+ ogłoszeń)

### Pomocnicze:
- `utils.py` - Funkcje pomocnicze + **obsługa Selenium + DEDUPLIKACJA** 🔍
- `supabase_utils.py` - Obsługa bazy danych (POPRAWIONA)
- `config.py` - Konfiguracja + **ustawienia Selenium**
- `debug_selenium.py` - **NARZĘDZIE DEBUG dla portali z Selenium**

## 🎯 PRZYKŁADOWE WYNIKI Z DEDUPLIKACJĄ

Po uruchomieniu `complete_demo.py` otrzymasz:

```
================================================================================
🏠 PEŁNA DEMONSTRACJA SCRAPERA NIERUCHOMOŚCI
================================================================================
📊 Testuje wszystkie 6 działających portali:
   🔸 4 scrapery z Selenium (nowoczesne portale)
   🔸 2 scrapery z Requests (klasyczne portale)
   🔸 ✨ WYKRYWANIE DUPLIKATÓW między portalami

🔍 WYKRYWANIE DUPLIKATÓW
📊 Łącznie pobrano: 196 ogłoszeń
🧹 Po deduplikacji: 128 unikatowych ogłoszeń
🔄 Usunięto duplikatów: 68

📊 PODSUMOWANIE WYNIKÓW (po deduplikacji)
🏠 Unikatowe ogłoszenia: 128
💰 Ogłoszenia z cenami: 26
📈 Średnia cena: 1,351,921 zł

🎉 SUKCES! System scrapowania z deduplikacją działa!
```

## 🚨 ROZWIĄZYWANIE PROBLEMÓW

### Błąd: ModuleNotFoundError (nowe biblioteki)
```bash
pip install fuzzywuzzy python-Levenshtein
```

### Błąd: ChromeDriver
Jeśli brak ChromeDriver:
1. **Windows**: ChromeDriver powinien być automatycznie dostępny
2. **Linux/Mac**: `sudo apt install chromium-chromedriver` lub pobierz z https://chromedriver.chromium.org/

### Selenium działa wolno
- To normalne - Selenium ładuje pełną stronę z JavaScript
- Typowy czas: 3-5 sekund na stronę
- Można zmniejszyć `SELENIUM_WAIT_TIME` w config.py

### Deduplikacja działa za agresywnie
- Zwiększ próg podobieństwa z 75% do 85-90%
- Wyłącz priorytet źródeł: `keep_best_source=False`
- Sprawdź logi, które ogłoszenia są oznaczane jako duplikaty

### Deduplikacja nie wykrywa oczywistych duplikatów
- Zmniejsz próg podobieństwa z 75% do 60-70%
- Sprawdź czy ogłoszenia mają wypełnione podstawowe pola (tytuł, cena)

### Blokowanie przez portal
- Zwiększ opóźnienia między requestami
- Zmień User-Agent headers (automatyczne)
- Selenium ma lepszą ochronę przed wykryciem

### Błąd: "Could not find column in schema cache"
To znaczy że tabela w Supabase nie ma wszystkich kolumn. **Rozwiązanie automatyczne** - kod filtruje kolumny.

## ⚡ GOTOWE KOMENDY

```bash
# Test z deduplikacją (NAJLEPSZY):
python complete_demo.py

# Test samej deduplikacji:
python test_deduplicate.py

# Test głównego scrapera z deduplikacją (bez Supabase):
python test_main_with_deduplication.py

# Test Selenium:
python test_selenium_scrapers.py

# Test bez Selenium:
python working_demo.py

# Test wszystkich scraperów:
python test_scraper_no_db.py

# Test Supabase:
python test_supabase.py

# Pełny scraper z Supabase + deduplikacja (po konfiguracji):
python main.py

# Debug konkretnego portalu:
python debug_selenium.py
```

## 🎉 SUKCES!

Scraper nieruchomości z deduplikacją jest w pełni gotowy:
- ✅ **6 działających scraperów** (4 z Selenium + 2 z Requests)
- ✅ Pobiera **200+ ogłoszeń** z największych polskich portali
- ✅ **🔍 DEDUPLIKACJA** - usuwa ~35% duplikatów między portalami
- ✅ **Inteligentne porównywanie** na podstawie wielu kryteriów
- ✅ **Priorytet najlepszych źródeł** (Otodom > OLX > inne)
- ✅ Ekstraktuje ceny, tytuły, linki, lokalizacje
- ✅ **Selenium** dla nowoczesnych portali z JavaScript
- ✅ Zapisuje do Supabase (po konfiguracji)
- ✅ **Anti-detection** zabezpieczenia
- ✅ Automatyczne filtrowanie kolumn bazy danych
- ✅ **Szczegółowe raporty** o duplikatach
- ✅ Gotowy do rozbudowy o kolejne portale

---

## 🌟 **NAJWAŻNIEJSZE KOMENDY DLA UŻYTKOWNIKA**

### 🚀 **Dla początkujących:**
```bash
# 1. Szybka demonstracja wszystkiego
python complete_demo.py

# 2. Test deduplikacji na przykładach  
python test_deduplicate.py
```

### 🔧 **Dla zaawansowanych:**
```bash
# 1. Test głównego scrapera (jak main.py ale bez bazy)
python test_main_with_deduplication.py

# 2. Główny scraper z zapisem do Supabase (po konfiguracji)
python main.py
```

### 🛠️ **Do debugowania:**
```bash
# 1. Test tylko scraperów Selenium
python test_selenium_scrapers.py

# 2. Debug konkretnego portalu
python debug_selenium.py
``` 