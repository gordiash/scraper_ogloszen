#!/usr/bin/env python3
"""
TEST POPRAWKI: uzupełnianie city z district
"""
from address_parser import parse_location_string
import logging

# Włącz debug logi
logging.basicConfig(level=logging.DEBUG)

def test_city_district_fix():
    """Test przypadków gdzie city może być null ale district ma wartość"""
    
    test_cases = [
        'Mokotów, ul. Puławska 123',  # Brak miasta, ale Mokotów to dzielnica Warszawy
        'Stare Miasto, Kraków',       # Odwrócona kolejność
        'Wrzeszcz, Gdańsk',          # Dzielnica przed miastem
        'Śródmieście, ul. Marszałkowska',  # Dzielnica bez miasta
        'Krzyki, os. Powstańców Śląskich',  # Dzielnica z osiedlem
        'Praga-Północ, ul. Targowa',  # Dzielnica Warszawy
        'Kazimierz, ul. Szeroka',     # Dzielnica Krakowa
        'Jeżyce, Poznań',            # Dzielnica przed miastem
    ]

    print('🧪 TEST POPRAWKI: city z district')
    print('='*60)
    print('Sprawdzam czy gdy city jest null, uzupełnia się z district')
    print('='*60)

    for i, location in enumerate(test_cases, 1):
        print(f'\n{i}. "{location}"')
        parsed = parse_location_string(location)
        
        print(f'   🏙️ Miasto: {parsed.get("city", "brak")}')
        print(f'   🏘️ Dzielnica: {parsed.get("district", "brak")}')
        print(f'   🏠 Pod-dzielnica: {parsed.get("sub_district", "brak")}')
        print(f'   🛣️ Ulica: {parsed.get("street_name", "brak")}')
        
        # Sprawdź czy poprawka zadziałała
        if parsed.get("city") and not parsed.get("district"):
            print(f'   ✅ POPRAWKA: Przeniesiono do city')
        elif parsed.get("city") and parsed.get("district"):
            print(f'   ℹ️ Oba pola wypełnione')
        elif not parsed.get("city"):
            print(f'   ⚠️ Brak miasta')

if __name__ == "__main__":
    test_city_district_fix() 