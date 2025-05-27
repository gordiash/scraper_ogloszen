# 🌍 GEOCODING SYSTEM - UZUPEŁNIANIE WSPÓŁRZĘDNYCH GEOGRAFICZNYCH

System do automatycznego uzupełniania kolumn `longitude` i `latitude` w tabeli `addresses` na podstawie danych adresowych.

## ✨ **FUNKCJONALNOŚCI**

✅ **Automatyczne geocoding** polskich adresów  
✅ **API Nominatim** (OpenStreetMap) - darmowe i bez limitów  
✅ **Inteligentne budowanie zapytań** na podstawie komponentów adresu  
✅ **Walidacja współrzędnych** - sprawdzanie czy są w Polsce  
✅ **Batch processing** - przetwarzanie w partiach  
✅ **Rate limiting** - respektowanie limitów API  
✅ **Retry logic** - ponowne próby przy błędach  
✅ **Szczegółowe statystyki** i raporty  

## 🎯 **WYMAGANIA**

### **1. Dodanie kolumn do tabeli addresses**
```sql
-- Wykonaj w SQL Editor Supabase
ALTER TABLE addresses 
ADD COLUMN IF NOT EXISTS latitude DECIMAL(10, 8),
ADD COLUMN IF NOT EXISTS longitude DECIMAL(11, 8);
```

### **2. Instalacja zależności**
```bash
# requests jest już w requirements.txt
pip install requests
```

## 🚀 **UŻYCIE**

### **1. Test geocodingu**
```bash
# Test na przykładowych adresach
python geocoding_updater.py --test
```

### **2. Sprawdzenie stanu bazy**
```bash
# Sprawdź ile adresów ma już współrzędne
python check_geocoding.py
```

### **3. Aktualizacja współrzędnych**
```bash
# Aktualizuj wszystkie adresy bez współrzędnych
python geocoding_updater.py --update

# Ograniczenie do 100 adresów
python geocoding_updater.py --update --max-addresses 100

# Mniejszy batch (domyślnie 50)
python geocoding_updater.py --update --batch-size 25

# Tryb testowy (bez zapisu)
python geocoding_updater.py --update --dry-run
```

## 📊 **PRZYKŁADOWE WYNIKI**

### **Test geocodingu:**
```
🧪 TEST GEOCODINGU
============================================================

1. Test adresu:
   📍 Zapytanie: ul. Puławska, Mokotów, Warszawa, Polska
   ✅ Współrzędne: 52.201376, 21.024498
   🗺️ Google Maps: https://maps.google.com/?q=52.201376,21.024498

2. Test adresu:
   📍 Zapytanie: Stare Miasto, Kraków, Polska
   ✅ Współrzędne: 50.061389, 19.938333
   🗺️ Google Maps: https://maps.google.com/?q=50.061389,19.938333
```

### **Aktualizacja bazy:**
```
🌍 GEOCODING UPDATER - UZUPEŁNIANIE WSPÓŁRZĘDNYCH
================================================================================
📊 Parametry:
   • Rozmiar batcha: 50
   • Maksymalne adresy: wszystkie
   • Opóźnienie między requestami: 1.1s

🔄 PRZETWARZANIE BATCHA 1
📋 Adresy w batchu: 50
------------------------------------------------------------
✅ 1/50 - ID 123: 52.201376, 21.024498
✅ 2/50 - ID 124: 50.061389, 19.938333
⚠️ 3/50 - Brak współrzędnych dla ID 125: Nieznane Miasto, Polska

📊 WYNIKI BATCHA:
   ✅ Sukces: 45
   ❌ Błędy: 3
   ⏭️ Pominięte: 2

📊 PODSUMOWANIE GEOCODINGU
================================================================================
📋 Łącznie przetworzonych: 200
✅ Pomyślnie geocodowanych: 180
❌ Błędów geocodingu: 15
⏭️ Pominiętych: 5
📈 Skuteczność: 90.0%
```

## 🔧 **ALGORYTM GEOCODINGU**

### **1. Budowanie zapytania**
```python
# Priorytet komponentów:
1. Ulica (ul. Marszałkowska)
2. Dzielnica/Pod-dzielnica (Śródmieście)  
3. Miasto (Warszawa) - OBOWIĄZKOWE
4. Województwo (mazowieckie)
5. Kraj (Polska) - ZAWSZE DODAWANE

# Przykład: "ul. Marszałkowska, Śródmieście, Warszawa, Polska"
```

### **2. API Nominatim**
```python
# Parametry zapytania:
- format: json
- limit: 1 (tylko najlepszy wynik)
- countrycodes: pl (tylko Polska)
- addressdetails: 1 (szczegóły adresu)
```

### **3. Walidacja wyników**
```python
# Sprawdzenie granic Polski:
- Latitude: 49.0 - 54.9
- Longitude: 14.1 - 24.2

# Odrzucenie wyników poza Polską
```

## 📈 **WYDAJNOŚĆ I LIMITY**

### **Rate Limiting:**
- **Nominatim**: 1 request/sekunda (wymagane)
- **Batch size**: 50 adresów (domyślnie)
- **Opóźnienie między batchami**: 5 sekund

### **Typowa wydajność:**
- **50 adresów**: ~1 minuta
- **500 adresów**: ~10 minut  
- **1000 adresów**: ~20 minut
- **Skuteczność**: 85-95% (zależy od jakości adresów)

### **Błędy i retry:**
- **3 próby** dla każdego adresu
- **Exponential backoff** przy błędach HTTP
- **Timeout**: 10 sekund na request

## 🔍 **SPRAWDZANIE WYNIKÓW**

### **Podstawowe statystyki:**
```bash
python check_geocoding.py
```

### **Przykładowy output:**
```
🌍 SPRAWDZENIE WYNIKÓW GEOCODINGU
============================================================
📊 STATYSTYKI GEOCODINGU:
   📋 Łącznie adresów: 1000
   ✅ Z współrzędnymi: 890
   ❌ Bez współrzędnych: 110
   📈 Skuteczność geocodingu: 89.0%

📍 PRZYKŁADOWE ADRESY Z WSPÓŁRZĘDNYMI:
------------------------------------------------------------
1. Warszawa, Mokotów
   📍 Współrzędne: 52.201376, 21.024498
   🗺️ Google Maps: https://maps.google.com/?q=52.201376,21.024498

🏙️ TOP 10 MIAST Z WSPÓŁRZĘDNYMI:
------------------------------------------------------------
    1. Warszawa      : 178 adresów (20.0%)
    2. Kraków        :  61 adresów (6.9%)
    3. Wrocław       :  66 adresów (7.4%)
```

## 🛠️ **ROZWIĄZYWANIE PROBLEMÓW**

### **Niska skuteczność geocodingu:**
1. **Sprawdź jakość adresów** w tabeli addresses
2. **Dodaj brakujące miasta** do głównych miast
3. **Popraw format adresów** (usuń błędne znaki)

### **Błędy API:**
```bash
# Sprawdź połączenie internetowe
curl "https://nominatim.openstreetmap.org/search?q=Warszawa&format=json"

# Zwiększ timeout w kodzie
TIMEOUT = 15  # zamiast 10
```

### **Współrzędne poza Polską:**
```sql
-- Znajdź nieprawidłowe współrzędne
SELECT id, city, latitude, longitude 
FROM addresses 
WHERE latitude < 49.0 OR latitude > 54.9 
   OR longitude < 14.1 OR longitude > 24.2;

-- Usuń nieprawidłowe współrzędne
UPDATE addresses 
SET latitude = NULL, longitude = NULL 
WHERE latitude < 49.0 OR latitude > 54.9;
```

## 📊 **PRZYDATNE ZAPYTANIA SQL**

### **Statystyki geocodingu:**
```sql
SELECT 
    COUNT(*) as total,
    COUNT(latitude) as with_coords,
    ROUND(COUNT(latitude)::decimal / COUNT(*) * 100, 1) as success_rate
FROM addresses;
```

### **Miasta bez współrzędnych:**
```sql
SELECT city, COUNT(*) as count
FROM addresses 
WHERE latitude IS NULL 
GROUP BY city 
ORDER BY count DESC 
LIMIT 10;
```

### **Mapa zasięgu:**
```sql
SELECT 
    MIN(latitude) as min_lat,
    MAX(latitude) as max_lat,
    MIN(longitude) as min_lon,
    MAX(longitude) as max_lon
FROM addresses 
WHERE latitude IS NOT NULL;
```

### **Adresy w promieniu (przykład - 10km od Warszawy):**
```sql
SELECT id, city, district, latitude, longitude,
       SQRT(POW(latitude - 52.2297, 2) + POW(longitude - 21.0122, 2)) * 111 as distance_km
FROM addresses 
WHERE latitude IS NOT NULL
  AND SQRT(POW(latitude - 52.2297, 2) + POW(longitude - 21.0122, 2)) * 111 < 10
ORDER BY distance_km;
```

## 🎯 **NASTĘPNE KROKI**

### **1. Przygotowanie:**
```bash
# 1. Dodaj kolumny do tabeli (SQL)
# 2. Sprawdź obecny stan
python check_geocoding.py
```

### **2. Test:**
```bash
# 3. Przetestuj geocoding
python geocoding_updater.py --test
```

### **3. Aktualizacja:**
```bash
# 4. Uruchom geocoding (start z małą liczbą)
python geocoding_updater.py --update --max-addresses 50

# 5. Sprawdź wyniki
python check_geocoding.py

# 6. Kontynuuj dla wszystkich adresów
python geocoding_updater.py --update
```

## 🔄 **AUTOMATYZACJA**

### **Cron job (Linux/Mac):**
```bash
# Geocoding nowych adresów codziennie o 3:00
0 3 * * * cd /path/to/scraper && python geocoding_updater.py --update --max-addresses 100
```

### **Task Scheduler (Windows):**
```batch
# Utwórz zadanie w Task Scheduler
python C:\path\to\scraper\geocoding_updater.py --update --max-addresses 100
```

## 📁 **PLIKI PROJEKTU**

- `geocoding_updater.py` - **Główny system geocodingu** ⭐
- `check_geocoding.py` - **Sprawdzanie wyników** 📊
- `add_coordinates_columns.sql` - **SQL do dodania kolumn** 🗄️
- `README_GEOCODING.md` - **Ta dokumentacja** 📖

---

**Stworzony w grudniu 2024**  
**API**: Nominatim (OpenStreetMap)  
**Licencja**: Do użytku prywatnego/edukacyjnego zgodnie z polityką Nominatim 