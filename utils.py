import requests
from bs4 import BeautifulSoup
import time
import random
import logging
from fake_useragent import UserAgent
from config import DEFAULT_DELAY, MAX_RETRIES, TIMEOUT

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
        
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(f"--user-agent={ua.random}")
        
        driver = webdriver.Chrome(options=options)
        try:
            driver.get(url)
            time.sleep(2)  # Czekaj na załadowanie JS
            html = driver.page_source
            return BeautifulSoup(html, "html.parser")
        finally:
            driver.quit()
    except ImportError:
        logger.warning("Selenium nie jest zainstalowany, używam requests")
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
    import re
    
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