# 🏠 SCRAPER NIERUCHOMOŚCI - DOKUMENTACJA

## 📋 Opis projektu

Automatyczny scraper nieruchomości z portalu Otodom.pl z kompletnym pipeline:
- 🔍 **Scrapowanie** ogłoszeń z Otodom.pl
- 📍 **Parsing adresów** na komponenty (miasto, dzielnica, ulica)
- 🌍 **Geocoding** - uzupełnianie współrzędnych geograficznych
- 💾 **Zapis do bazy** Supabase z walidacją

## 🚀 Szybki start

### 1. Instalacja zależności
```bash
pip install -r requirements.txt
```

### 2. Konfiguracja Supabase
```bash
# Skopiuj plik przykładowy
cp env_example.txt .env

# Edytuj .env i uzupełnij:
SUPABASE_URL=https://twoj-projekt.supabase.co
SUPABASE_KEY=twoj_anon_key
```

### 3. Uruchomienie kompletnego pipeline
```bash
# Automatyczny pipeline (scraping + parsing + geocoding)
python scripts/scraper_main.py --pages 5 --geocoding-limit 100

# Tylko scraping
python src/scrapers/otodom_scraper.py

# Tylko parsing adresów
python src/parsers/address_parser.py --process

# Tylko geocoding
python src/geocoding/geocoder.py --update
```

## 📁 Struktura projektu

```
scraper/
├── scripts/                    # Główne skrypty
│   └── scraper_main.py        # Kompletny pipeline
├── src/                       # Kod źródłowy
│   ├── scrapers/              # Scrapery portali
│   │   └── otodom_scraper.py  # Scraper Otodom.pl
│   ├── parsers/               # Parsery danych
│   │   └── address_parser.py  # Parser adresów
│   └── geocoding/             # Geocoding
│       └── geocoder.py        # Geocoder współrzędnych
├── .github/workflows/         # GitHub Actions
│   └── scraper.yml           # Automatyczne scrapowanie
├── docs/                      # Dokumentacja
├── sql/                       # Skrypty SQL
└── tests/                     # Testy
```

## 🔧 Konfiguracja

### Zmienne środowiskowe (.env)
```bash
SUPABASE_URL=https://twoj-projekt.supabase.co
SUPABASE_KEY=twoj_anon_key
```

### Struktura bazy danych

#### Tabela `listings`
```sql
CREATE TABLE listings (
    id SERIAL PRIMARY KEY,
    title TEXT,
    price INTEGER,
    price_currency TEXT DEFAULT 'zł',
    price_original TEXT,
    location TEXT,
    url TEXT UNIQUE,
    area TEXT,
    rooms TEXT,
    description TEXT,
    source TEXT DEFAULT 'otodom.pl',
    scraped_at TIMESTAMP DEFAULT NOW()
);
```

#### Tabela `addresses`
```sql
CREATE TABLE addresses (
    id SERIAL PRIMARY KEY,
    full_address TEXT NOT NULL,
    street_name TEXT,
    district TEXT,
    sub_district TEXT,
    city TEXT,
    province TEXT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    foreign_key INTEGER REFERENCES listings(id)
);
```

## 🤖 GitHub Actions

Projekt zawiera automatyczne scrapowanie przez GitHub Actions:

### Harmonogram
- **Codziennie o 6:00 UTC** (8:00 czasu polskiego)
- **Ręczne uruchomienie** przez GitHub UI

### Konfiguracja secrets
W ustawieniach repozytorium dodaj:
- `SUPABASE_URL` - URL projektu Supabase
- `SUPABASE_KEY` - Klucz anon/public

### Uruchomienie ręczne
1. Przejdź do zakładki **Actions**
2. Wybierz **Scraper nieruchomości**
3. Kliknij **Run workflow**

## 📊 Funkcjonalności

### 🔍 Scrapowanie
- **Portal**: Otodom.pl
- **Dane**: Tytuł, cena, lokalizacja, powierzchnia, pokoje, URL
- **Technologia**: Selenium (obsługa JavaScript)
- **Anti-detection**: Losowe opóźnienia, User-Agent

### 📍 Parsing adresów
- **Rozdzielanie** lokalizacji na komponenty
- **Normalizacja** nazw miast i ulic
- **Obsługa** różnych formatów adresów
- **Walidacja** poprawności danych

### 🌍 Geocoding
- **API**: OpenStreetMap Nominatim
- **Skuteczność**: ~92% (ulepszone zapytania)
- **Fallback**: Zapytania uproszczone
- **Walidacja**: Sprawdzanie granic Polski
- **Rate limiting**: Zgodnie z wymaganiami API

### 💾 Baza danych
- **Platforma**: Supabase (PostgreSQL)
- **Deduplikacja**: Automatyczne wykrywanie duplikatów
- **Walidacja**: Sprawdzanie kompletności danych
- **Indeksy**: Optymalizacja wydajności

## 📈 Statystyki

### Wydajność scrapowania
- **~40-50 ogłoszeń** na stronę Otodom.pl
- **~200-250 ogłoszeń** z 5 stron
- **Czas**: ~2-3 minuty na stronę (Selenium)

### Skuteczność geocodingu
- **92%** skuteczność z uproszczonymi zapytaniami
- **100%** dla głównych miast Polski
- **Fallback**: Dodatkowe ~5-10% skuteczności

### Jakość danych
- **95%+** ogłoszeń z tytułem i URL
- **80%+** ogłoszeń z ceną
- **70%+** ogłoszeń z lokalizacją
- **60%+** ogłoszeń z powierzchnią/pokojami

## 🛠️ Rozwój

### Dodawanie nowych portali
1. Stwórz nowy scraper w `src/scrapers/`
2. Zaimplementuj funkcję `get_[portal]_listings()`
3. Dodaj do `scripts/scraper_main.py`

### Ulepszanie geocodingu
1. Edytuj `src/geocoding/geocoder.py`
2. Dodaj nowe poprawki miast w `city_fixes`
3. Dostosuj progi podobieństwa

### Testy
```bash
# Test scrapera
python src/scrapers/otodom_scraper.py

# Test parsera
python src/parsers/address_parser.py --test

# Test geocodera
python src/geocoding/geocoder.py --test
```

## 🔍 Rozwiązywanie problemów

### Błędy scrapowania
- **Selenium timeout**: Zwiększ `SELENIUM_TIMEOUT` w utils.py
- **Brak ogłoszeń**: Sprawdź selektory CSS (mogły się zmienić)
- **Blokowanie**: Zwiększ opóźnienia między requestami

### Błędy geocodingu
- **Niska skuteczność**: Sprawdź jakość danych adresowych
- **Rate limiting**: Zwiększ `DELAY_BETWEEN_REQUESTS`
- **Błędne współrzędne**: Sprawdź walidację granic Polski

### Błędy bazy danych
- **Connection error**: Sprawdź zmienne środowiskowe
- **Missing columns**: Uruchom skrypty SQL z katalogu `sql/`
- **Duplicate key**: Normalne - duplikaty są pomijane

## 📞 Wsparcie

### Logi
- **Plik**: `scraper.log`
- **Poziom**: INFO (można zmienić na DEBUG)
- **Rotacja**: Automatyczna

### Monitoring
- **GitHub Actions**: Logi w zakładce Actions
- **Supabase**: Dashboard z metrykami
- **Lokalne**: Szczegółowe logi w konsoli

### Kontakt
- **Issues**: GitHub Issues dla błędów
- **Dokumentacja**: Ten plik README
- **Konfiguracja**: Pliki w katalogu `docs/`

---

## 🎯 Roadmapa

### Krótkoterminowe
- [ ] Dodanie OLX.pl scraper
- [ ] Dashboard z wykresami
- [ ] Alerty email o nowych ofertach

### Długoterminowe  
- [ ] Analiza trendów cenowych
- [ ] API REST do eksportu danych
- [ ] Mapa z lokalizacjami
- [ ] Funkcje AI do kategoryzacji

---

**Ostatnia aktualizacja**: Grudzień 2024  
**Wersja**: 2.0  
**Status**: Produkcyjny ✅ 