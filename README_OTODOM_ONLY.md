# 🏠 SCRAPER OTODOM.PL

Uproszczony scraper nieruchomości działający wyłącznie z portalem **Otodom.pl**.

## ✨ **FUNKCJE**

### 🎯 **GŁÓWNE MOŻLIWOŚCI:**
- ✅ **Scraping tylko Otodom.pl** - skoncentrowany na jednym źródle
- ✅ **Wysoka jakość danych** - 90%+ wszystkich pól wypełnionych
- ✅ **Deduplikacja** - automatyczne usuwanie duplikatów
- ✅ **Obsługa viewType=listing** - zgodnie z podanym URL
- ✅ **Szczegółowe informacje** - pobieranie pełnych opisów
- ✅ **Zapis do Supabase** - opcjonalny

### 📊 **POBIERANE DANE:**
- **Tytuł ogłoszenia**
- **Cena** (90%+ wypełnienia)
- **Lokalizacja** (100% wypełnienia)
- **Powierzchnia** (98%+ wypełnienia)
- **Liczba pokoi** (98%+ wypełnienia)
- **Opis** (dla szczegółów)
- **URL ogłoszenia**

## 🚀 **UŻYCIE**

### **1. Podstawowy test**
```bash
python otodom_only_scraper.py
```

### **2. Główny scraper**
```bash
# Standardowe użycie (5 stron)
python main_otodom_only.py

# Więcej stron
python main_otodom_only.py --pages 10

# Z zapisem do bazy danych
python main_otodom_only.py --pages 5 --save-db

# Tryb cichy
python main_otodom_only.py --pages 3 --quiet
```

## 📋 **PRZYKŁADOWE WYNIKI**

```
📊 WYNIKI SCRAPOWANIA:
   🏠 Łącznie ogłoszeń: 71
   💰 Z cenami: 64/71 (90.1%)
   📍 Z lokalizacją: 71/71 (100.0%)
   📐 Z powierzchnią: 70/71 (98.6%)
   🚪 Z pokojami: 70/71 (98.6%)

🔄 DEDUPLIKACJA:
   ✅ Usunięto 10 duplikatów
   📋 Pozostało 61 unikatowych ogłoszeń

💰 STATYSTYKI CEN:
   📈 Średnia cena: 780,054 zł
   🔽 Najniższa cena: 164,000 zł
   🔼 Najwyższa cena: 5,200,000 zł
```

## ⚙️ **KONFIGURACJA**

### **Wymagane pliki:**
- `otodom_only_scraper.py` - główny scraper
- `main_otodom_only.py` - interfejs CLI
- `utils.py` - funkcje pomocnicze
- `requirements.txt` - zależności

### **Opcjonalne:**
- `supabase_utils.py` - zapis do bazy danych
- `.env` - konfiguracja Supabase

## 🛠 **TECHNICZNE SZCZEGÓŁY**

### **URL docelowy:**
```
https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/cala-polska?viewType=listing
```

### **Technologie:**
- **Selenium** - obsługa JavaScript
- **BeautifulSoup** - parsowanie HTML
- **Fuzzy matching** - deduplikacja

### **Selektory CSS:**
```css
/* Lista ogłoszeń */
[data-cy='listing-item']           /* Kontener ogłoszenia */
[data-cy='listing-item-title']     /* Tytuł */
span.css-2bt9f1                   /* Cena */
p.css-42r2ms                      /* Lokalizacja */
dl.css-9q2yy4                     /* Powierzchnia/pokoje */

/* Strona szczegółów */
[data-cy='adPageHeaderPrice']      /* Cena */
[data-sentry-component='MapLink'] /* Lokalizacja */
[data-cy='adPageAdDescription']   /* Opis */
```

## 📈 **WYDAJNOŚĆ**

### **Typowe wyniki:**
- **3 strony** → ~60-70 ogłoszeń → ~50-60 unikatowych
- **5 stron** → ~100-120 ogłoszeń → ~80-100 unikatowych
- **10 stron** → ~200-250 ogłoszeń → ~170-200 unikatowych

### **Czas wykonania:**
- **1 strona** → ~10 sekund
- **5 stron** → ~50 sekund
- **10 stron** → ~1.5 minuty

## 🔧 **ROZWIĄZYWANIE PROBLEMÓW**

### **Częste problemy:**

1. **Timeout przeglądarki**
   ```bash
   # Uruchom ponownie - zazwyczaj pomaga
   python otodom_only_scraper.py
   ```

2. **Brak ogłoszeń**
   ```bash
   # Sprawdź czy strona się ładuje
   # Zwiększ delay w utils.py
   ```

3. **Problemy z Selenium**
   ```bash
   # Zainstaluj ponownie Chrome/chromedriver
   pip install --upgrade selenium
   ```

## 📊 **DEDUPLIKACJA**

### **Algorytm podobieństwa:**
- **40%** - podobieństwo tytułów (fuzzy matching)
- **25%** - cena (±5% tolerancja)
- **15%** - powierzchnia (±10% tolerancja)
- **10%** - liczba pokoi (dokładne dopasowanie)
- **10%** - lokalizacja (częściowe dopasowanie)

### **Próg domyślny:** 75%

## 💾 **ZAPIS DO BAZY DANYCH**

### **Konfiguracja Supabase:**
```bash
# W pliku .env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

### **Struktura tabeli:**
```sql
CREATE TABLE listings (
    id SERIAL PRIMARY KEY,
    title TEXT,
    price INTEGER,
    price_currency TEXT DEFAULT 'zł',
    location TEXT,
    url TEXT UNIQUE,
    area TEXT,
    rooms TEXT,
    description TEXT,
    source TEXT DEFAULT 'otodom.pl',
    scraped_at TIMESTAMP DEFAULT NOW()
);
```

## 🎯 **NASTĘPNE KROKI**

1. **Rozszerzenie** - dodanie filtrów cenowych/lokalizacyjnych
2. **Automatyzacja** - cron jobs dla regularnego scrapowania
3. **API** - utworzenie REST API dla danych
4. **Dashboard** - wizualizacja danych w time

---

**Stworzony w grudniu 2024**  
**Autor:** System AI + człowiek  
**Licencja:** Do użytku prywatnego/edukacyjnego 