# 🏠 SCRAPER NIERUCHOMOŚCI - POLSKA

Zaawansowany system scrapowania ogłoszeń nieruchomości z największych polskich portali.

## ✨ **FUNKCJONALNOŚCI**

✅ **6 działających scraperów** (4 z Selenium + 2 z Requests)  
✅ **200+ ogłoszeń** z różnych portali  
✅ **Selenium** dla nowoczesnych portali JavaScript  
✅ **Anti-detection** zabezpieczenia  
✅ **Supabase** integration  
✅ **Automatyczne filtrowanie** danych

## 🎯 **OBSŁUGIWANE PORTALE**

### 🚀 **Scrapery z Selenium** (JavaScript)
- **Freedom.pl** - 20 ogłoszeń z cenami
- **Gratka.pl** - 37 ogłoszeń 
- **Metrohouse.pl** - 63 ogłoszenia
- **Domiporta.pl** - 36 ogłoszeń z cenami

### 🌐 **Scrapery z Requests** (klasyczne)
- **OLX.pl** - 10+ ogłoszeń z cenami i lokalizacjami
- **Otodom.pl** - 40+ ogłoszeń

## 📊 **WYNIKI TESTÓW**

```bash
============================================================
PODSUMOWANIE TESTÓW SELENIUM
============================================================
Freedom.pl     :  20 ogłoszeń ✓ DZIAŁA
Gratka.pl      :  37 ogłoszeń ✓ DZIAŁA  
Metrohouse.pl  :  63 ogłoszeń ✓ DZIAŁA
Domiporta.pl   :  36 ogłoszeń ✓ DZIAŁA

Działające scrapery: 4/4
Łącznie ogłoszeń: 156

🎉 SUKCES! Wszystkie scrapery z Selenium działają!
```

## 🚀 **SZYBKI START**

### 1. Instalacja
```bash
git clone [repository]
cd scraper
pip install -r requirements.txt
```

### 2. Test wszystkich scraperów
```bash
# Test z Selenium (POLECANE)
python test_selenium_scrapers.py

# Pełna demonstracja wszystkich portali
python complete_demo.py

# Test bez Selenium
python working_demo.py
```

### 3. Konfiguracja Supabase (opcjonalna)
```bash
# Ustaw zmienne środowiskowe
$env:SUPABASE_URL="https://twoj-projekt.supabase.co"
$env:SUPABASE_KEY="twój_anon_key"

# Test połączenia
python test_supabase.py

# Pełny scraper z bazą
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
├── utils.py           # Obsługa Selenium + Requests
├── config.py          # Konfiguracja + Selenium
├── supabase_utils.py  # Integracja z bazą
├── main.py            # Główny scraper
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
# Testy główne
python test_selenium_scrapers.py    # Test Selenium (NAJLEPSZY)
python complete_demo.py             # Pełna demonstracja
python working_demo.py              # Test bez Selenium

# Testy pomocnicze  
python test_scraper_no_db.py        # Test bez bazy
python test_supabase.py             # Test bazy danych

# Główne działanie
python main.py                      # Pełny scraper + Supabase

# Debug
python debug_selenium.py            # Debug portali z Selenium
```

## 🛡️ **ZABEZPIECZENIA**

- **Random User-Agents** (fake-useragent)
- **Headless Selenium** z anti-detection
- **Losowe opóźnienia** między requestami
- **Timeout handling** i retry logic
- **Error handling** z fallback

## 📈 **WYDAJNOŚĆ**

- **Selenium portale**: ~3-5 sekund/strona
- **Requests portale**: ~1-2 sekundy/strona  
- **Łącznie**: 200+ ogłoszeń w ~2-3 minuty
- **Concurrent scraping**: Możliwe rozszerzenie

## 🔄 **AUTOMATYZACJA**

### Windows Task Scheduler
```batch
# Uruchamiaj co godzinę
schtasks /create /tn "Scraper" /tr "python C:\path\to\main.py" /sc hourly
```

### Linux/Mac Cron
```bash
# Uruchamiaj co godzinę
0 * * * * cd /path/to/scraper && python main.py
```

## 🐛 **ROZWIĄZYWANIE PROBLEMÓW**

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
4. **Utwórz PR** z opisem zmian

---

## 🎉 **SUKCES!**

System scrapuje **200+ ogłoszeń** z **6 największych polskich portali nieruchomości** i jest gotowy do użycia produkcyjnego! 

**Testuj**: `python complete_demo.py`  
**Dokumentacja**: `INSTRUKCJE_URUCHOMIENIA.md` 