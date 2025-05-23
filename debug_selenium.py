"""
Debug narzędzie do analizy struktury HTML portali z Selenium
"""
import logging
from utils import get_soup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_portal_structure(url: str, portal_name: str):
    """Analizuje strukturę HTML portalu"""
    print(f"\n{'='*60}")
    print(f"ANALIZA STRUKTURY: {portal_name}")
    print(f"URL: {url}")
    print(f"{'='*60}")
    
    try:
        soup = get_soup(url, use_selenium=True)
        
        # Podstawowe informacje
        print(f"Tytuł strony: {soup.title.get_text() if soup.title else 'Brak'}")
        print(f"Liczba elementów article: {len(soup.select('article'))}")
        print(f"Liczba elementów div: {len(soup.select('div'))}")
        
        # Szukaj elementów z kluczowymi słowami
        keywords = ['property', 'listing', 'offer', 'card', 'item', 'teaser', 'sneakpeak']
        
        print("\n--- KLASY ZAWIERAJĄCE KLUCZOWE SŁOWA ---")
        for keyword in keywords:
            elements = soup.select(f"[class*='{keyword}']")
            if elements:
                print(f"{keyword}: {len(elements)} elementów")
                # Pokaż pierwszych kilka unikalnych klas
                classes = set()
                for elem in elements[:10]:
                    if elem.get('class'):
                        classes.update(elem.get('class'))
                unique_classes = [cls for cls in classes if keyword in cls.lower()][:5]
                if unique_classes:
                    print(f"  Przykładowe klasy: {', '.join(unique_classes)}")
        
        # Szukaj data-testid
        print("\n--- DATA-TESTID ---")
        testids = soup.select("[data-testid]")
        if testids:
            testid_values = set()
            for elem in testids[:20]:
                testid_values.add(elem.get('data-testid'))
            print(f"Znaleziono {len(testids)} elementów z data-testid")
            print(f"Przykłady: {', '.join(list(testid_values)[:10])}")
        else:
            print("Brak elementów z data-testid")
        
        # Struktura nagłówków
        print("\n--- NAGŁÓWKI ---")
        for tag in ['h1', 'h2', 'h3', 'h4']:
            headers = soup.select(tag)
            if headers:
                print(f"{tag}: {len(headers)} elementów")
                # Pokaż pierwsze 3 nagłówki
                for i, h in enumerate(headers[:3]):
                    text = h.get_text().strip()[:50]
                    print(f"  {i+1}. {text}...")
        
        # Linki z href
        print("\n--- LINKI ---")
        links = soup.select("a[href]")
        print(f"Łącznie linków: {len(links)}")
        
        # Linki zawierające kluczowe słowa
        property_links = [a for a in links if any(word in a.get('href', '').lower() 
                         for word in ['mieszkanie', 'oferta', 'nieruchomosc', 'property'])]
        if property_links:
            print(f"Linki do nieruchomości: {len(property_links)}")
            for i, link in enumerate(property_links[:3]):
                href = link.get('href')[:60]
                text = link.get_text().strip()[:40]
                print(f"  {i+1}. {text} -> {href}")
        
        # Ceny
        print("\n--- POTENCJALNE CENY ---")
        price_patterns = ['price', 'amount', 'cost', 'cena', 'kwota']
        for pattern in price_patterns:
            price_elems = soup.select(f"[class*='{pattern}']")
            if price_elems:
                print(f"{pattern}: {len(price_elems)} elementów")
                # Pokaż teksty z liczbami
                for elem in price_elems[:3]:
                    text = elem.get_text().strip()
                    if any(char.isdigit() for char in text):
                        print(f"  {text[:50]}")
        
        # Zapisz HTML do pliku (pierwsze 10000 znaków)
        filename = f"debug_{portal_name.lower().replace('.', '_')}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(str(soup)[:10000])
        print(f"\nPierwsze 10k znaków HTML zapisane do: {filename}")
        
    except Exception as e:
        print(f"BŁĄD podczas analizy {portal_name}: {e}")

def main():
    """Debuguje wszystkie portale"""
    portals = [
        ("https://freedom.pl/mieszkania-sprzedaz", "Freedom.pl"),
        ("https://gratka.pl/nieruchomosci/mieszkania/sprzedaz", "Gratka.pl"),
        ("https://metrohouse.pl/sprzedaz/mieszkanie", "Metrohouse.pl"),
        ("https://www.domiporta.pl/mieszkanie/sprzedam", "Domiporta.pl"),
    ]
    
    print("DEBUGOWANIE STRUKTURY HTML PORTALI")
    print("Używamy Selenium do pobrania zawartości")
    
    for url, name in portals:
        try:
            debug_portal_structure(url, name)
        except KeyboardInterrupt:
            print("\nPrzerwano przez użytkownika")
            break
        except Exception as e:
            print(f"Błąd z {name}: {e}")
    
    print(f"\n{'='*60}")
    print("DEBUGGING ZAKOŃCZONY")
    print(f"{'='*60}")
    print("Sprawdź pliki debug_*.html żeby zobaczyć strukturę HTML")
    print("Użyj tych informacji do aktualizacji selektorów CSS w scraperach")

if __name__ == "__main__":
    main() 