# 🏠 SCRAPER NIERUCHOMOŚCI - POLSKA

Zaawansowany system scrapowania ogłoszeń nieruchomości z największych polskich portali + **inteligentne wykrywanie duplikatów**.

## ✨ **FUNKCJONALNOŚCI**

✅ **6 działających scraperów** (4 z Selenium + 2 z Requests)  
✅ **200+ ogłoszeń** z różnych portali  
✅ **🔍 DEDUPLIKACJA** - usuwa ~35% duplikatów między portalami  
✅ **Inteligentne porównywanie** tytułów, cen, powierzchni, lokalizacji  
✅ **Priorytet najlepszych źródeł** (Otodom > OLX > inne)  
✅ **Selenium** dla nowoczesnych portali JavaScript  
✅ **Anti-detection** zabezpieczenia  
✅ **Supabase** integration  
✅ **Automatyczne filtrowanie** danych  
✅ **🌍 GEOCODING** - automatyczne współrzędne geograficzne  
✅ **Parser adresów** - rozdzielanie lokalizacji na komponenty

## 🎯 **OBSŁUGIWANE PORTALE**

### 🚀 **Scrapery z Selenium** (JavaScript)
- **Freedom.pl** - 20 ogłoszeń z cenami
- **Gratka.pl** - 37 ogłoszeń 
- **Metrohouse.pl** - 63 ogłoszenia
- **Domiporta.pl** - 36 ogłoszeń z cenami

### 🌐 **Scrapery z Requests** (klasyczne)
- **OLX.pl** - 10+ ogłoszeń z cenami i lokalizacjami
- **Otodom.pl** - 40+ ogłoszeń

## 🔍 **DEDUPLIKACJA - NOWA FUNKCJONALNOŚĆ**

### ✨ **Jak działa:**
```
📊 Przed: 196 ogłoszeń z 6 portali
🧹 Po:   128 unikatowych ogłoszeń  
🔄 Duplikaty: 68 (35% skuteczności)
```

### 🛠️ **Algorytm podobieństwa:**
- **40%** - Fuzzy matching tytułów
- **25%** - Porównanie cen (±5% tolerancja)
- **15%** - Powierzchnia (±10% tolerancja)
- **10%** - Liczba pokoi (dokładne)
- **10%** - Lokalizacja (częściowe)

### 📊 **Ranking źródeł** (priorytety):
1. **otodom.pl** 🥇
2. **olx.pl** 🥈  
3. **domiporta.pl** 🥉
4. **gratka.pl**
5. **metrohouse.pl**
6. **freedom.pl**

## 📊 **WYNIKI TESTÓW Z DEDUPLIKACJĄ**

```bash
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

📊 Duplikaty per portal:
   • domiporta.pl: 11 duplikatów
   • freedom.pl: 19 duplikatów  
   • metrohouse.pl: 35 duplikatów
   • otodom.pl: 3 duplikatów

🎉 SUKCES! System scrapowania z deduplikacją działa!
```

## 🚀 **SZYBKI START**

### 1. Instalacja
```bash
git clone [repository]
cd scraper
pip install -r requirements.txt
```

### 2. Test z deduplikacją (POLECANE)
```bash
# Pełna demonstracja z deduplikacją
python complete_demo.py

# Test samej deduplikacji
python test_deduplicate.py

# Test Selenium bez deduplikacji
python test_selenium_scrapers.py
```

### 3. Konfiguracja Supabase (opcjonalna)
```bash
# Ustaw zmienne środowiskowe
$env:SUPABASE_URL="https://twoj-projekt.supabase.co"
$env:SUPABASE_KEY="twój_anon_key"

# Test połączenia
python test_supabase.py

# Pełny scraper z bazą + deduplikacją
python main.py
```

## 🔧 **ARCHITEKTURA**

```
scraper/
├── scrapers/           # Moduły scraperów
│   ├── freedom.py     # ⚡ Selenium 
│   ├── gratka.py      # ⚡ Selenium
│   ├── metrohouse.py  # ⚡ Selenium
│   ├── domiporta.py   # ⚡ Selenium
│   ├── olx.py         # 🌐 Requests
│   └── otodom.py      # 🌐 Requests
├── utils.py           # Obsługa Selenium + Requests + 🔍 DEDUPLIKACJA
├── config.py          # Konfiguracja + Selenium
├── supabase_utils.py  # Integracja z bazą
├── main.py            # Główny scraper + deduplikacja
├── complete_demo.py   # 🌟 Demo z deduplikacją
├── test_deduplicate.py # 🔍 Testy deduplikacji
└── test_*.py          # Testy i demonstracje
```

## ⚙️ **KONFIGURACJA**

### Selenium
```python
# config.py
SELENIUM_ENABLED = True
SELENIUM_HEADLESS = True  
SELENIUM_TIMEOUT = 20
SELENIUM_WAIT_TIME = 2
```

### Deduplikacja
```python
# Dostosuj próg podobieństwa
deduplicated = deduplicate_listings(
    all_listings, 
    similarity_threshold=75.0,    # 0-100%
    keep_best_source=True         # Priorytet najlepszych portali
)
```

### Supabase
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

## 📋 **DOSTĘPNE KOMENDY**

```bash
# Demo i testy główne
python complete_demo.py             # ⭐ Pełna demonstracja + deduplikacja
python test_deduplicate.py          # 🔍 Test deduplikacji
python test_selenium_scrapers.py    # Test Selenium
python working_demo.py              # Test bez Selenium

# Testy pomocnicze  
python test_scraper_no_db.py        # Test bez bazy
python test_supabase.py             # Test bazy danych

# Główne działanie
python main.py                      # ⭐ Pełny scraper + Supabase + deduplikacja

# Parser adresów i geocoding
python address_parser.py --process  # 🏠 Parsowanie adresów
python geocoding_updater.py --test  # 🌍 Test geocodingu
python geocoding_updater.py --update # 🌍 Uzupełnianie współrzędnych
python check_geocoding.py           # 📊 Sprawdzenie geocodingu

# Debug
python debug_selenium.py            # Debug portali z Selenium
python test_geocoding_system.py     # 🧪 Test systemu geocodingu
```

## 🛡️ **ZABEZPIECZENIA I OPTYMALIZACJE**

- **Random User-Agents** (fake-useragent)
- **Headless Selenium** z anti-detection
- **Losowe opóźnienia** między requestami
- **Timeout handling** i retry logic
- **Error handling** z fallback
- **🔍 Deduplikacja** - oszczędność ~35% miejsca w bazie
- **Priorytet źródeł** - zachowuje najlepsze dane

## 📈 **WYDAJNOŚĆ**

- **Selenium portale**: ~3-5 sekund/strona
- **Requests portale**: ~1-2 sekundy/strona  
- **Deduplikacja**: ~0.1 sekunda/100 ogłoszeń
- **Łącznie**: 200+ ogłoszeń → 128 unikatowych w ~3-4 minuty
- **Oszczędność**: 35% mniej danych w bazie
- **Concurrent scraping**: Możliwe rozszerzenie

## 🔄 **AUTOMATYZACJA**

### Windows Task Scheduler
```batch
# Uruchamiaj co godzinę z deduplikacją
schtasks /create /tn "Scraper" /tr "python C:\path\to\main.py" /sc hourly
```

### Linux/Mac Cron
```bash
# Uruchamiaj co godzinę z deduplikacją
0 * * * * cd /path/to/scraper && python main.py
```

## 🐛 **ROZWIĄZYWANIE PROBLEMÓW**

### Deduplikacja
```bash
# Za agresywna - zwiększ próg
similarity_threshold=85.0  # zamiast 75.0

# Za słaba - zmniejsz próg  
similarity_threshold=65.0  # zamiast 75.0

# Wyłącz priorytet źródeł
keep_best_source=False
```

### Selenium nie działa
```bash
# Sprawdź instalację
python -c "from selenium import webdriver; print('OK')"

# Zainstaluj ChromeDriver (Linux/Mac)
sudo apt install chromium-chromedriver
```

### Brak ogłoszeń
- Portale często zmieniają strukturę HTML
- Użyj `debug_selenium.py` do analizy
- Zaktualizuj selektory CSS w scraperach

### Blokowanie
- Zwiększ opóźnienia w `config.py`
- Selenium ma lepszą ochronę niż Requests
- Użyj proxy (opcjonalnie)

## 📄 **LICENCJA**

MIT License - używaj zgodnie z regulaminami scraperowanych portali.

## 🤝 **ROZWÓJ**

1. **Fork** repozytorium
2. **Dodaj nowy scraper** w `scrapers/`  
3. **Przetestuj** z `debug_selenium.py`
4. **Test deduplikacji** z `test_deduplicate.py`
5. **Utwórz PR** z opisem zmian

---

## 🌍 **GEOCODING I PARSER ADRESÓW**

### **Dodatkowe funkcjonalności:**
✅ **Parser adresów** - rozdziela lokalizacje na komponenty (miasto, dzielnica, ulica)  
✅ **Geocoding** - automatyczne współrzędne geograficzne (latitude, longitude)  
✅ **API Nominatim** - darmowe geocoding bez limitów  
✅ **Walidacja** - sprawdzanie czy współrzędne są w Polsce  

### **Szybki start geocoding:**
```bash
# 1. Dodaj kolumny do tabeli addresses (SQL w Supabase)
# 2. Test geocodingu
python geocoding_updater.py --test

# 3. Uzupełnij współrzędne
python geocoding_updater.py --update --max-addresses 50

# 4. Sprawdź wyniki
python check_geocoding.py
```

### **Dokumentacja:**
- `README_GEOCODING.md` - **Pełna dokumentacja geocodingu** 🌍
- `README_ADDRESS_PARSER.md` - **Dokumentacja parsera adresów** 🏠

---

## 🎉 **SUKCES!**

System scrapuje **200+ ogłoszeń** z **6 największych polskich portali nieruchomości**, **automatycznie usuwa ~35% duplikatów**, **parsuje adresy** i **dodaje współrzędne geograficzne**! 

**Testuj**: `python complete_demo.py`  
**Deduplikacja**: `python test_deduplicate.py`  
**Geocoding**: `python test_geocoding_system.py`  
**Dokumentacja**: `INSTRUKCJE_URUCHOMIENIA.md`