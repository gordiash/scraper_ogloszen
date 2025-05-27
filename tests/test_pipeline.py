#!/usr/bin/env python3
"""
TESTY PIPELINE SCRAPERA NIERUCHOMOŚCI
Testy jednostkowe i integracyjne dla całego systemu
"""
import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Dodaj główny katalog do ścieżki
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestOtodomScraper(unittest.TestCase):
    """Testy scrapera Otodom.pl"""
    
    def setUp(self):
        """Przygotowanie testów"""
        from src.scrapers.otodom_scraper import parse_otodom_listing
        self.parse_function = parse_otodom_listing
    
    def test_parse_otodom_listing_valid(self):
        """Test parsowania prawidłowego ogłoszenia"""
        # Mock element HTML
        mock_element = MagicMock()
        
        # Mock title
        mock_title = MagicMock()
        mock_title.get_text.return_value = "Mieszkanie 3 pokoje, 60 m²"
        mock_element.select_one.side_effect = lambda selector: {
            "[data-cy='listing-item-title']": mock_title,
            "span.css-2bt9f1": None,
            "p.css-42r2ms": None,
            "[data-cy='listing-item-link']": None,
            "dl.css-9q2yy4": None
        }.get(selector)
        
        result = self.parse_function(mock_element)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['title'], "Mieszkanie 3 pokoje, 60 m²")
        self.assertEqual(result['source'], "otodom.pl")
    
    def test_parse_otodom_listing_empty(self):
        """Test parsowania pustego elementu"""
        mock_element = MagicMock()
        mock_element.select_one.return_value = None
        
        result = self.parse_function(mock_element)
        
        self.assertIsNone(result)

class TestAddressParser(unittest.TestCase):
    """Testy parsera adresów"""
    
    def setUp(self):
        """Przygotowanie testów"""
        from src.parsers.address_parser import parse_location_string
        self.parse_function = parse_location_string
    
    def test_parse_full_address(self):
        """Test parsowania pełnego adresu"""
        location = "Warszawa, Mokotów, ul. Puławska 123"
        result = self.parse_function(location)
        
        self.assertEqual(result['city'], "Warszawa")
        self.assertEqual(result['district'], "Mokotów")
        self.assertEqual(result['street_name'], "Ul. Puławska 123")
    
    def test_parse_city_only(self):
        """Test parsowania tylko miasta"""
        location = "Kraków"
        result = self.parse_function(location)
        
        self.assertEqual(result['city'], "Kraków")
        self.assertIsNone(result['district'])
        self.assertIsNone(result['street_name'])
    
    def test_parse_empty_location(self):
        """Test parsowania pustej lokalizacji"""
        location = ""
        result = self.parse_function(location)
        
        self.assertIsNone(result['city'])
        self.assertIsNone(result['district'])
        self.assertIsNone(result['street_name'])
    
    def test_parse_major_city(self):
        """Test rozpoznawania głównych miast"""
        location = "Gdańsk, Wrzeszcz"
        result = self.parse_function(location)
        
        self.assertEqual(result['city'], "Gdańsk")
        self.assertEqual(result['district'], "Wrzeszcz")

class TestGeocoder(unittest.TestCase):
    """Testy geocodera"""
    
    def setUp(self):
        """Przygotowanie testów"""
        from src.geocoding.geocoder import build_simple_search_query, build_fallback_query
        self.build_query = build_simple_search_query
        self.build_fallback = build_fallback_query
    
    def test_build_simple_query(self):
        """Test budowania uproszczonego zapytania"""
        address_data = {
            'city': 'Warszawa',
            'street_name': 'ul. Puławska',
            'district': 'Mokotów'
        }
        
        result = self.build_query(address_data)
        
        # Sprawdź czy zapytanie zawiera miasto i Polskę
        self.assertIn("Warszawa", result)
        self.assertIn("Polska", result)
        # Sprawdź czy usunięto prefiks "ul."
        self.assertIn("Puławska", result)
        self.assertNotIn("ul.", result)
    
    def test_build_fallback_query(self):
        """Test budowania zapytania fallback"""
        address_data = {
            'city': 'Kraków',
            'district': 'Stare Miasto'
        }
        
        result = self.build_fallback(address_data)
        
        self.assertEqual(result, "Kraków, Polska")
    
    def test_city_fixes(self):
        """Test poprawek nazw miast"""
        address_data = {
            'city': 'Gdański'  # Błędna nazwa
        }
        
        result = self.build_query(address_data)
        
        # Sprawdź czy nazwa została poprawiona
        self.assertIn("Pruszcz Gdański", result)
        self.assertNotIn("Gdański,", result)

class TestSupabaseUtils(unittest.TestCase):
    """Testy funkcji Supabase"""
    
    @patch('supabase_utils.get_supabase_client')
    def test_save_listing_valid(self, mock_client):
        """Test zapisu prawidłowego ogłoszenia"""
        from supabase_utils import save_listing
        
        # Mock Supabase client
        mock_supabase = MagicMock()
        mock_client.return_value = mock_supabase
        
        # Mock successful insert
        mock_result = MagicMock()
        mock_result.data = [{'id': 1}]
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_result
        
        # Mock get_table_columns
        with patch('supabase_utils.get_table_columns', return_value=['title', 'price', 'location', 'url']):
            listing = {
                'title': 'Test Mieszkanie',
                'price': 500000,
                'location': 'Warszawa',
                'url': 'https://test.com/1'
            }
            
            result = save_listing(listing)
            
            self.assertTrue(result)
    
    @patch('supabase_utils.get_supabase_client')
    def test_save_listing_incomplete(self, mock_client):
        """Test zapisu niekompletnego ogłoszenia"""
        from supabase_utils import save_listing
        
        listing = {
            'title': 'Test Mieszkanie'
            # Brak price, location, url
        }
        
        result = save_listing(listing, require_complete=True)
        
        self.assertFalse(result)

class TestPipelineIntegration(unittest.TestCase):
    """Testy integracyjne całego pipeline"""
    
    @patch('src.scrapers.otodom_scraper.get_soup')
    @patch('supabase_utils.save_listings_to_supabase')
    def test_complete_pipeline_mock(self, mock_save, mock_soup):
        """Test kompletnego pipeline z mockami"""
        from scripts.scraper_main import run_complete_pipeline
        
        # Mock HTML response
        mock_soup_obj = MagicMock()
        mock_soup.return_value = mock_soup_obj
        
        # Mock ogłoszenia
        mock_offers = []
        for i in range(3):
            mock_offer = MagicMock()
            mock_title = MagicMock()
            mock_title.get_text.return_value = f"Test Mieszkanie {i+1}"
            mock_offer.select_one.side_effect = lambda selector: {
                "[data-cy='listing-item-title']": mock_title
            }.get(selector, None)
            mock_offers.append(mock_offer)
        
        mock_soup_obj.select.return_value = mock_offers
        
        # Mock save function
        mock_save.return_value = 3
        
        # Mock Supabase dla statystyk
        with patch('supabase_utils.get_supabase_client') as mock_client:
            mock_supabase = MagicMock()
            mock_client.return_value = mock_supabase
            
            # Mock statystyki
            mock_result = MagicMock()
            mock_result.count = 10
            mock_supabase.table.return_value.select.return_value.execute.return_value = mock_result
            
            # Uruchom pipeline
            result = run_complete_pipeline(max_pages=1, max_geocoding_addresses=5)
            
            self.assertTrue(result)

class TestUtilsFunctions(unittest.TestCase):
    """Testy funkcji pomocniczych"""
    
    def test_clean_text(self):
        """Test czyszczenia tekstu"""
        from utils import clean_text
        
        dirty_text = "  Test   text\n\t  "
        clean = clean_text(dirty_text)
        
        self.assertEqual(clean, "Test text")
    
    def test_extract_price(self):
        """Test ekstraktowania ceny"""
        from utils import extract_price
        
        price_text = "500 000 zł"
        result = extract_price(price_text)
        
        self.assertEqual(result['price'], 500000)
        self.assertEqual(result['currency'], 'zł')
        self.assertEqual(result['original'], "500 000 zł")
    
    def test_extract_price_invalid(self):
        """Test ekstraktowania nieprawidłowej ceny"""
        from utils import extract_price
        
        price_text = "Cena do uzgodnienia"
        result = extract_price(price_text)
        
        self.assertIsNone(result['price'])
        self.assertEqual(result['original'], "Cena do uzgodnienia")

def run_tests():
    """Uruchom wszystkie testy"""
    print("🧪 URUCHAMIANIE TESTÓW PIPELINE SCRAPERA")
    print("="*60)
    
    # Utwórz test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Dodaj wszystkie klasy testowe
    test_classes = [
        TestOtodomScraper,
        TestAddressParser,
        TestGeocoder,
        TestSupabaseUtils,
        TestPipelineIntegration,
        TestUtilsFunctions
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Uruchom testy
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Podsumowanie
    print("\n" + "="*60)
    print("📊 PODSUMOWANIE TESTÓW")
    print("="*60)
    print(f"✅ Testy zakończone sukcesem: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Testy nieudane: {len(result.failures)}")
    print(f"💥 Błędy: {len(result.errors)}")
    print(f"📈 Skuteczność: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\n❌ NIEUDANE TESTY:")
        for test, traceback in result.failures:
            print(f"   • {test}")
    
    if result.errors:
        print(f"\n💥 BŁĘDY:")
        for test, traceback in result.errors:
            print(f"   • {test}")
    
    print("="*60)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 