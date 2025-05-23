import requests
from bs4 import BeautifulSoup
import time
import random
import logging
from fake_useragent import UserAgent
import re
from typing import List, Dict, Tuple, Optional

try:
    from config import DEFAULT_DELAY, MAX_RETRIES, TIMEOUT, SELENIUM_HEADLESS, SELENIUM_TIMEOUT, SELENIUM_WAIT_TIME
except ImportError:
    # Fallback values jeśli nie ma wszystkich zmiennych w config
    from config import DEFAULT_DELAY, MAX_RETRIES, TIMEOUT
    SELENIUM_HEADLESS = True
    SELENIUM_TIMEOUT = 20
    SELENIUM_WAIT_TIME = 2

logger = logging.getLogger(__name__)
ua = UserAgent()

def get_soup(url: str, use_selenium: bool = False, retries: int = MAX_RETRIES) -> BeautifulSoup:
    """
    Pobiera i parsuje stronę HTML
    
    Args:
        url: URL do pobrania
        use_selenium: Czy użyć Selenium (dla JS-heavy stron)
        retries: Liczba prób ponowienia
    
    Returns:
        BeautifulSoup: Sparsowana strona
    """
    for attempt in range(retries):
        try:
            if use_selenium:
                return get_soup_selenium(url)
            else:
                return get_soup_requests(url)
        except Exception as e:
            logger.warning(f"Próba {attempt + 1}/{retries} nieudana dla {url}: {e}")
            if attempt < retries - 1:
                time.sleep(random.uniform(2, 5))
            else:
                raise

def get_soup_requests(url: str) -> BeautifulSoup:
    """Pobiera stronę używając requests"""
    headers = {
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "pl-PL,pl;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }
    
    response = requests.get(url, headers=headers, timeout=TIMEOUT)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")

def get_soup_selenium(url: str) -> BeautifulSoup:
    """Pobiera stronę używając Selenium"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        options = Options()
        if SELENIUM_HEADLESS:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument(f"--user-agent={ua.random}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        try:
            driver.set_page_load_timeout(SELENIUM_TIMEOUT)
            driver.get(url)
            
            # Czekaj na załadowanie podstawowej zawartości
            WebDriverWait(driver, SELENIUM_WAIT_TIME).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Dodatkowe oczekiwanie na JavaScript
            time.sleep(SELENIUM_WAIT_TIME)
            
            html = driver.page_source
            return BeautifulSoup(html, "html.parser")
        finally:
            driver.quit()
    except ImportError:
        logger.warning("Selenium nie jest zainstalowany, używam requests")
        return get_soup_requests(url)
    except Exception as e:
        logger.error(f"Błąd Selenium: {e}")
        logger.warning("Przełączam na requests")
        return get_soup_requests(url)

def random_delay():
    """Dodaje losowe opóźnienie między requestami"""
    delay = random.uniform(*DEFAULT_DELAY)
    time.sleep(delay)

def clean_text(text: str) -> str:
    """Czyści tekst z niepotrzebnych znaków"""
    if not text:
        return ""
    return text.strip().replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')

def extract_price(price_text: str) -> dict:
    """
    Ekstraktuje cenę z tekstu
    
    Returns:
        dict: {"price": float, "currency": str, "original": str}
    """
    if not price_text:
        return {"price": None, "currency": None, "original": ""}
    
    # Usuń spacje i znormalizuj
    price_clean = re.sub(r'\s+', ' ', price_text.strip())
    
    # Znajdź liczby i walutę
    price_match = re.search(r'(\d+(?:\s\d{3})*(?:,\d{2})?)', price_clean)
    currency_match = re.search(r'(zł|PLN|€|EUR|\$|USD)', price_clean)
    
    price_value = None
    if price_match:
        price_str = price_match.group(1).replace(' ', '').replace(',', '.')
        try:
            price_value = float(price_str)
        except ValueError:
            pass
    
    currency = currency_match.group(1) if currency_match else "zł"
    
    return {
        "price": price_value,
        "currency": currency,
        "original": price_clean
    }

# =================================================================
# FUNKCJE WYKRYWANIA DUPLIKATÓW OGŁOSZEŃ
# =================================================================

def normalize_text(text: str) -> str:
    """
    Normalizuje tekst do porównywania duplikatów
    
    Args:
        text: Tekst do normalizacji
    
    Returns:
        str: Znormalizowany tekst
    """
    if not text:
        return ""
    
    # Konwertuj na małe litery
    text = text.lower()
    
    # Usuń interpunkcję i nadmiarowe spacje
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    
    # Usuń typowe słowa nieistotne
    stop_words = [
        'mieszkanie', 'pokojowe', 'pokój', 'pokoje', 'm2', 'sprzedam', 
        'na', 'sprzedaż', 'do', 'w', 'z', 'i', 'a', 'o', 'u', 'po'
    ]
    
    words = text.split()
    words = [word for word in words if word not in stop_words and len(word) > 2]
    
    return ' '.join(words).strip()

def extract_area_number(area_text: str) -> Optional[float]:
    """
    Ekstraktuje liczbę metrów kwadratowych z tekstu
    
    Args:
        area_text: Tekst z powierzchnią
    
    Returns:
        float: Powierzchnia w m2 lub None
    """
    if not area_text:
        return None
    
    # Szukaj wzorców typu "65 m2", "65m²", "65.5 m2"
    pattern = r'(\d+(?:[.,]\d+)?)\s*m[2²]?'
    match = re.search(pattern, area_text.lower())
    
    if match:
        try:
            return float(match.group(1).replace(',', '.'))
        except ValueError:
            pass
    
    return None

def extract_rooms_number(rooms_text: str) -> Optional[int]:
    """
    Ekstraktuje liczbę pokoi z tekstu
    
    Args:
        rooms_text: Tekst z liczbą pokoi
    
    Returns:
        int: Liczba pokoi lub None
    """
    if not rooms_text:
        return None
    
    # Szukaj wzorców typu "3 pokoje", "3-pokojowe", "3pok"
    pattern = r'(\d+)[\s\-]?pok'
    match = re.search(pattern, rooms_text.lower())
    
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            pass
    
    # Może być sama liczba
    if rooms_text.strip().isdigit():
        return int(rooms_text.strip())
    
    return None

def calculate_listings_similarity(listing1: Dict, listing2: Dict) -> float:
    """
    Oblicza podobieństwo między dwoma ogłoszeniami
    
    Args:
        listing1: Pierwsze ogłoszenie
        listing2: Drugie ogłoszenie
    
    Returns:
        float: Współczynnik podobieństwa (0-100)
    """
    try:
        from fuzzywuzzy import fuzz
    except ImportError:
        logger.warning("fuzzywuzzy nie jest zainstalowane, używam prostego porównania")
        return simple_similarity(listing1, listing2)
    
    total_score = 0
    weight_sum = 0
    
    # 1. Podobieństwo tytułów (waga: 40%)
    title1 = normalize_text(listing1.get('title', ''))
    title2 = normalize_text(listing2.get('title', ''))
    if title1 and title2:
        title_similarity = fuzz.token_sort_ratio(title1, title2)
        total_score += title_similarity * 0.4
        weight_sum += 0.4
    
    # 2. Dokładność ceny (waga: 25%)
    price1 = listing1.get('price')
    price2 = listing2.get('price')
    if price1 and price2:
        price_diff = abs(price1 - price2) / max(price1, price2)
        price_similarity = max(0, 100 - (price_diff * 100))
        total_score += price_similarity * 0.25
        weight_sum += 0.25
    
    # 3. Powierzchnia (waga: 15%)
    area1 = extract_area_number(listing1.get('area', ''))
    area2 = extract_area_number(listing2.get('area', ''))
    if area1 and area2:
        area_diff = abs(area1 - area2) / max(area1, area2)
        area_similarity = max(0, 100 - (area_diff * 50))  # Większa tolerancja
        total_score += area_similarity * 0.15
        weight_sum += 0.15
    
    # 4. Liczba pokoi (waga: 10%)
    rooms1 = extract_rooms_number(listing1.get('rooms', ''))
    rooms2 = extract_rooms_number(listing2.get('rooms', ''))
    if rooms1 and rooms2:
        if rooms1 == rooms2:
            total_score += 100 * 0.1
        weight_sum += 0.1
    
    # 5. Lokalizacja (waga: 10%)
    location1 = normalize_text(listing1.get('location', ''))
    location2 = normalize_text(listing2.get('location', ''))
    if location1 and location2:
        location_similarity = fuzz.partial_ratio(location1, location2)
        total_score += location_similarity * 0.1
        weight_sum += 0.1
    
    # Oblicz końcowy wynik
    if weight_sum > 0:
        return total_score / weight_sum
    else:
        return 0

def simple_similarity(listing1: Dict, listing2: Dict) -> float:
    """
    Prosta kalkulacja podobieństwa bez fuzzywuzzy
    """
    score = 0
    factors = 0
    
    # Porównaj ceny
    price1 = listing1.get('price')
    price2 = listing2.get('price')
    if price1 and price2:
        price_diff = abs(price1 - price2) / max(price1, price2)
        if price_diff < 0.05:  # 5% różnicy
            score += 80
        elif price_diff < 0.1:  # 10% różnicy
            score += 60
        factors += 1
    
    # Porównaj powierzchnie
    area1 = extract_area_number(listing1.get('area', ''))
    area2 = extract_area_number(listing2.get('area', ''))
    if area1 and area2:
        area_diff = abs(area1 - area2) / max(area1, area2)
        if area_diff < 0.1:  # 10% różnicy
            score += 70
        factors += 1
    
    # Porównaj pokoje
    rooms1 = extract_rooms_number(listing1.get('rooms', ''))
    rooms2 = extract_rooms_number(listing2.get('rooms', ''))
    if rooms1 and rooms2 and rooms1 == rooms2:
        score += 60
        factors += 1
    
    return score / factors if factors > 0 else 0

def find_duplicates(listings: List[Dict], similarity_threshold: float = 75.0) -> Tuple[List[Dict], List[Dict]]:
    """
    Znajduje duplikaty w liście ogłoszeń
    
    Args:
        listings: Lista ogłoszeń do sprawdzenia
        similarity_threshold: Próg podobieństwa (0-100)
    
    Returns:
        Tuple[List[Dict], List[Dict]]: (unikalne_ogłoszenia, duplikaty)
    """
    unique_listings = []
    duplicates = []
    
    logger.info(f"🔍 Sprawdzam {len(listings)} ogłoszeń pod kątem duplikatów (próg: {similarity_threshold}%)")
    
    for i, listing in enumerate(listings):
        is_duplicate = False
        
        # Porównaj z już zaakceptowanymi unikalnymi ogłoszeniami
        for unique_listing in unique_listings:
            similarity = calculate_listings_similarity(listing, unique_listing)
            
            if similarity >= similarity_threshold:
                logger.debug(f"Znaleziono duplikat: {similarity:.1f}% podobieństwa")
                logger.debug(f"  Original: {unique_listing.get('title', '')[:50]}... ({unique_listing.get('source')})")
                logger.debug(f"  Duplikat: {listing.get('title', '')[:50]}... ({listing.get('source')})")
                
                # Dodaj informację o duplikacie
                duplicate_info = listing.copy()
                duplicate_info['duplicate_of'] = unique_listing.get('url', '')
                duplicate_info['similarity_score'] = similarity
                duplicates.append(duplicate_info)
                
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique_listings.append(listing)
    
    logger.info(f"✅ Wyniki deduplikacji:")
    logger.info(f"   📋 Unikalne ogłoszenia: {len(unique_listings)}")
    logger.info(f"   🔄 Duplikaty: {len(duplicates)}")
    
    return unique_listings, duplicates

def deduplicate_listings(listings: List[Dict], similarity_threshold: float = 75.0, 
                        keep_best_source: bool = True) -> List[Dict]:
    """
    Usuwa duplikaty z listy ogłoszeń
    
    Args:
        listings: Lista ogłoszeń
        similarity_threshold: Próg podobieństwa (0-100)
        keep_best_source: Czy zachować najlepsze źródło przy duplikatach
    
    Returns:
        List[Dict]: Lista bez duplikatów
    """
    if not listings:
        return []
    
    # Ranking portali (najlepsze źródła mają priorytet)
    source_priority = {
        'otodom.pl': 1,
        'olx.pl': 2,
        'domiporta.pl': 3,
        'gratka.pl': 4,
        'metrohouse.pl': 5,
        'freedom.pl': 6
    }
    
    # Sortuj według priorytetu źródła jeśli włączone
    if keep_best_source:
        listings_sorted = sorted(listings, 
                               key=lambda x: source_priority.get(x.get('source', ''), 999))
    else:
        listings_sorted = listings.copy()
    
    unique_listings, duplicates = find_duplicates(listings_sorted, similarity_threshold)
    
    # Wyświetl statystyki duplikatów per portal
    if duplicates:
        duplicate_stats = {}
        for dup in duplicates:
            source = dup.get('source', 'nieznany')
            duplicate_stats[source] = duplicate_stats.get(source, 0) + 1
        
        logger.info("📊 Duplikaty per portal:")
        for source, count in sorted(duplicate_stats.items()):
            logger.info(f"   • {source}: {count} duplikatów")
    
    return unique_listings

def generate_duplicate_report(duplicates: List[Dict]) -> str:
    """
    Generuje raport o duplikatach
    
    Args:
        duplicates: Lista duplikatów
    
    Returns:
        str: Raport tekstowy
    """
    if not duplicates:
        return "🎉 Nie znaleziono duplikatów!"
    
    report = [
        "🔄 RAPORT DUPLIKATÓW OGŁOSZEŃ",
        "="*50,
        f"Łączna liczba duplikatów: {len(duplicates)}",
        ""
    ]
    
    # Grupuj według podobieństwa
    high_similarity = [d for d in duplicates if d.get('similarity_score', 0) >= 90]
    medium_similarity = [d for d in duplicates if 75 <= d.get('similarity_score', 0) < 90]
    
    if high_similarity:
        report.extend([
            f"🔴 Bardzo podobne (90%+): {len(high_similarity)}",
            ""
        ])
        for dup in high_similarity[:5]:  # Pokaż tylko pierwsze 5
            title = dup.get('title', 'Brak tytułu')[:60]
            source = dup.get('source', 'nieznany')
            similarity = dup.get('similarity_score', 0)
            report.append(f"  • {title}... ({source}) - {similarity:.1f}%")
    
    if medium_similarity:
        report.extend([
            "",
            f"🟡 Średnio podobne (75-89%): {len(medium_similarity)}",
            ""
        ])
        for dup in medium_similarity[:3]:  # Pokaż tylko pierwsze 3
            title = dup.get('title', 'Brak tytułu')[:60]
            source = dup.get('source', 'nieznany')
            similarity = dup.get('similarity_score', 0)
            report.append(f"  • {title}... ({source}) - {similarity:.1f}%")
    
    return "\n".join(report) 