import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except (ImportError, FileNotFoundError):
    # Jeśli dotenv nie jest dostępny lub plik .env nie istnieje, kontynuuj
    pass

# Konfiguracja Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://twoj-projekt.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "twój_anon_key")

# Ustawienia scrapera
DEFAULT_DELAY = (1, 3)  # Random delay między requestami (min, max)
MAX_RETRIES = 3
TIMEOUT = 10

# Konfiguracja Selenium
SELENIUM_ENABLED = True
SELENIUM_HEADLESS = True
SELENIUM_TIMEOUT = 20
SELENIUM_WAIT_TIME = 2  # Czas oczekiwania na JS (sekundy)

# User-Agent headers
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
] 