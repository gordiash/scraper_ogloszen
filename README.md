# Scraper Nieruchomości

Modularny web scraper do pobierania ogłoszeń nieruchomości z wielu portali i zapisywania ich do bazy Supabase.

## Obsługiwane Portale

- **Freedom.pl** - sieć biur nieruchomości
- **Otodom.pl** - największy portal nieruchomości w Polsce
- **Metrohouse.pl** - portal z mieszkaniami i domami
- **Domiporta.pl** - portal z ofertami nieruchomości
- **Gratka.pl** - portal ogłoszeniowy z nieruchomościami
- **OLX.pl/nieruchomosci** - sekcja nieruchomości OLX

## Wymagania

- Python 3.8+
- Google Chrome (dla Selenium)
- Konto Supabase

## Instalacja

1. **Sklonuj repozytorium:**
```bash
git clone <repo-url>
cd scraper
```

2. **Zainstaluj zależności:**
```bash
pip install -r requirements.txt
```

3. **Skonfiguruj zmienne środowiskowe:**
Stwórz plik `.env` w katalogu głównym:
```
SUPABASE_URL=https://twoj-projekt.supabase.co
SUPABASE_KEY=twój_anon_key
```

4. **Utwórz tabelę w Supabase:**
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
    source_page INTEGER,
    scraped_at TIMESTAMP,
    scraper_version TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Użycie

### Uruchomienie wszystkich scraperów:
```bash
python main.py
```

### Uruchomienie konkretnego scrapera:
```python
from scrapers.freedom import get_freedom_listings

listings = get_freedom_listings(max_pages=3)
print(f"Pobrano {len(listings)} ogłoszeń")
```

## Struktura Projektu

```
scraper/
├── config.py              # Konfiguracja
├── utils.py               # Funkcje pomocnicze
├── supabase_utils.py      # Obsługa Supabase
├── main.py               # Główny plik uruchamiający
├── requirements.txt      # Zależności
├── scrapers/            # Scrapery dla poszczególnych portali
│   ├── __init__.py
│   ├── freedom.py
│   ├── otodom.py
│   ├── metrohouse.py
│   ├── domiporta.py
│   ├── gratka.py
│   └── olx.py
└── README.md
```

## Konfiguracja

### config.py
- URL i klucz do Supabase
- Ustawienia opóźnień między requestami
- Lista User-Agent headers

### Dostosowywanie scraperów
Selektory CSS w scraperach mogą wymagać aktualizacji, jeśli portale zmienią swoją strukturę HTML.

## Funkcje

### Automatyczne funkcje:
- **Rate limiting** - losowe opóźnienia między requestami
- **Retry logic** - ponowne próby w przypadku błędów
- **Deduplication** - sprawdzanie duplikatów po URL
- **Error handling** - logowanie błędów
- **Selenium support** - dla stron z JavaScript

### Ekstraktowane dane:
- Tytuł ogłoszenia
- Cena (wartość numeryczna + waluta)
- Lokalizacja
- Powierzchnia
- Liczba pokoi
- Opis (jeśli dostępny)
- URL źródłowy
- Metadata (źródło, czas scrapowania)

## Logowanie

Logi są zapisywane do:
- `scraper.log` - plik z logami
- `stdout` - wyjście standardowe

## Troubleshooting

### Błędy połączenia:
- Sprawdź połączenie internetowe
- Niektóre portale mogą blokować automated requests

### Selektory nie działają:
- Sprawdź czy portal nie zmienił struktury HTML
- Zaktualizuj selektory CSS w odpowiednim scraperze

### Selenium errors:
- Upewnij się, że Google Chrome jest zainstalowany
- Sprawdź czy ChromeDriver jest dostępny

## Etyka i Zgodność

- Scraper respektuje robots.txt
- Implementuje rate limiting
- Nie przeciąża serwerów
- Używany tylko do celów edukacyjnych/badawczych

## Dalszy Rozwój

Możliwe rozszerzenia:
- Dodanie więcej portali
- Filtrowanie po lokalizacji/cenie
- API endpoints
- Dashboard do wizualizacji danych
- Scheduled tasks (cron jobs)
- Alerty cenowe

## Licencja

Ten projekt jest przeznaczony wyłącznie do celów edukacyjnych. 