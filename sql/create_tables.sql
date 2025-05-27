-- SKRYPT TWORZENIA TABEL DLA SCRAPERA NIERUCHOMOŚCI
-- Wykonaj ten kod w SQL Editor w Supabase

-- =====================================================
-- TABELA LISTINGS - GŁÓWNE OGŁOSZENIA
-- =====================================================

CREATE TABLE IF NOT EXISTS listings (
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
    scraped_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indeksy dla lepszej wydajności
CREATE INDEX IF NOT EXISTS idx_listings_source ON listings(source);
CREATE INDEX IF NOT EXISTS idx_listings_price ON listings(price);
CREATE INDEX IF NOT EXISTS idx_listings_scraped_at ON listings(scraped_at);
CREATE INDEX IF NOT EXISTS idx_listings_location ON listings(location);
CREATE INDEX IF NOT EXISTS idx_listings_url ON listings(url);

-- Komentarze do kolumn
COMMENT ON TABLE listings IS 'Główna tabela z ogłoszeniami nieruchomości';
COMMENT ON COLUMN listings.title IS 'Tytuł ogłoszenia';
COMMENT ON COLUMN listings.price IS 'Cena w liczbach całkowitych (grosze)';
COMMENT ON COLUMN listings.price_currency IS 'Waluta ceny (domyślnie zł)';
COMMENT ON COLUMN listings.price_original IS 'Oryginalny tekst ceny ze strony';
COMMENT ON COLUMN listings.location IS 'Lokalizacja tekstowa ze strony';
COMMENT ON COLUMN listings.url IS 'Unikalny URL ogłoszenia';
COMMENT ON COLUMN listings.area IS 'Powierzchnia tekstowa';
COMMENT ON COLUMN listings.rooms IS 'Liczba pokoi tekstowa';
COMMENT ON COLUMN listings.description IS 'Opis ogłoszenia';
COMMENT ON COLUMN listings.source IS 'Źródło danych (portal)';
COMMENT ON COLUMN listings.scraped_at IS 'Czas scrapowania';

-- =====================================================
-- TABELA ADDRESSES - SPARSOWANE ADRESY
-- =====================================================

CREATE TABLE IF NOT EXISTS addresses (
    id SERIAL PRIMARY KEY,
    full_address TEXT NOT NULL,
    street_name TEXT,
    district TEXT,
    sub_district TEXT,
    city TEXT,
    province TEXT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    foreign_key INTEGER REFERENCES listings(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indeksy dla lepszej wydajności
CREATE INDEX IF NOT EXISTS idx_addresses_foreign_key ON addresses(foreign_key);
CREATE INDEX IF NOT EXISTS idx_addresses_city ON addresses(city);
CREATE INDEX IF NOT EXISTS idx_addresses_district ON addresses(district);
CREATE INDEX IF NOT EXISTS idx_addresses_province ON addresses(province);
CREATE INDEX IF NOT EXISTS idx_addresses_latitude ON addresses(latitude);
CREATE INDEX IF NOT EXISTS idx_addresses_longitude ON addresses(longitude);
CREATE INDEX IF NOT EXISTS idx_addresses_coordinates ON addresses(latitude, longitude);

-- Constrainty sprawdzające współrzędne dla Polski
ALTER TABLE addresses 
ADD CONSTRAINT IF NOT EXISTS check_latitude_range 
CHECK (latitude IS NULL OR (latitude >= 49.0 AND latitude <= 54.9));

ALTER TABLE addresses 
ADD CONSTRAINT IF NOT EXISTS check_longitude_range 
CHECK (longitude IS NULL OR (longitude >= 14.1 AND longitude <= 24.2));

-- Komentarze do kolumn
COMMENT ON TABLE addresses IS 'Sparsowane komponenty adresów z tabeli listings';
COMMENT ON COLUMN addresses.full_address IS 'Pełny oryginalny adres z kolumny location';
COMMENT ON COLUMN addresses.street_name IS 'Nazwa ulicy (ul., al., pl., os.)';
COMMENT ON COLUMN addresses.district IS 'Dzielnica/rejon miasta';
COMMENT ON COLUMN addresses.sub_district IS 'Pod-dzielnica/osiedle/obszar';
COMMENT ON COLUMN addresses.city IS 'Miasto';
COMMENT ON COLUMN addresses.province IS 'Województwo';
COMMENT ON COLUMN addresses.latitude IS 'Szerokość geograficzna (decimal degrees)';
COMMENT ON COLUMN addresses.longitude IS 'Długość geograficzna (decimal degrees)';
COMMENT ON COLUMN addresses.foreign_key IS 'Klucz obcy do tabeli listings';

-- =====================================================
-- TRIGGERY DO AUTOMATYCZNEGO USTAWIANIA updated_at
-- =====================================================

-- Funkcja do ustawiania updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger dla tabeli listings
DROP TRIGGER IF EXISTS update_listings_updated_at ON listings;
CREATE TRIGGER update_listings_updated_at 
    BEFORE UPDATE ON listings 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger dla tabeli addresses
DROP TRIGGER IF EXISTS update_addresses_updated_at ON addresses;
CREATE TRIGGER update_addresses_updated_at 
    BEFORE UPDATE ON addresses 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- WIDOKI DLA UŁATWIENIA ZAPYTAŃ
-- =====================================================

-- Widok łączący listings z addresses
CREATE OR REPLACE VIEW listings_with_addresses AS
SELECT 
    l.*,
    a.street_name,
    a.district,
    a.sub_district,
    a.city,
    a.province,
    a.latitude,
    a.longitude
FROM listings l
LEFT JOIN addresses a ON l.id = a.foreign_key;

-- Widok tylko z geocodowanymi adresami
CREATE OR REPLACE VIEW geocoded_listings AS
SELECT 
    l.*,
    a.street_name,
    a.district,
    a.city,
    a.latitude,
    a.longitude
FROM listings l
INNER JOIN addresses a ON l.id = a.foreign_key
WHERE a.latitude IS NOT NULL AND a.longitude IS NOT NULL;

-- =====================================================
-- FUNKCJE POMOCNICZE
-- =====================================================

-- Funkcja do sprawdzania kompletności danych
CREATE OR REPLACE FUNCTION check_listing_completeness(listing_id INTEGER)
RETURNS TABLE(
    id INTEGER,
    has_title BOOLEAN,
    has_price BOOLEAN,
    has_location BOOLEAN,
    has_area BOOLEAN,
    has_rooms BOOLEAN,
    has_coordinates BOOLEAN,
    completeness_score DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        l.id,
        (l.title IS NOT NULL AND l.title != '') as has_title,
        (l.price IS NOT NULL AND l.price > 0) as has_price,
        (l.location IS NOT NULL AND l.location != '') as has_location,
        (l.area IS NOT NULL AND l.area != '') as has_area,
        (l.rooms IS NOT NULL AND l.rooms != '') as has_rooms,
        (a.latitude IS NOT NULL AND a.longitude IS NOT NULL) as has_coordinates,
        (
            CASE WHEN l.title IS NOT NULL AND l.title != '' THEN 1 ELSE 0 END +
            CASE WHEN l.price IS NOT NULL AND l.price > 0 THEN 1 ELSE 0 END +
            CASE WHEN l.location IS NOT NULL AND l.location != '' THEN 1 ELSE 0 END +
            CASE WHEN l.area IS NOT NULL AND l.area != '' THEN 1 ELSE 0 END +
            CASE WHEN l.rooms IS NOT NULL AND l.rooms != '' THEN 1 ELSE 0 END +
            CASE WHEN a.latitude IS NOT NULL AND a.longitude IS NOT NULL THEN 1 ELSE 0 END
        )::DECIMAL / 6 * 100 as completeness_score
    FROM listings l
    LEFT JOIN addresses a ON l.id = a.foreign_key
    WHERE l.id = listing_id;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- SPRAWDZENIE UTWORZONYCH TABEL
-- =====================================================

-- Sprawdź strukturę tabeli listings
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'listings' 
ORDER BY ordinal_position;

-- Sprawdź strukturę tabeli addresses
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'addresses' 
ORDER BY ordinal_position;

-- Sprawdź czy tabele zostały utworzone
SELECT 
    table_name,
    table_type
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('listings', 'addresses')
ORDER BY table_name;

-- Sprawdź indeksy
SELECT 
    indexname,
    tablename,
    indexdef
FROM pg_indexes 
WHERE tablename IN ('listings', 'addresses')
ORDER BY tablename, indexname;

-- =====================================================
-- PRZYKŁADOWE ZAPYTANIA TESTOWE
-- =====================================================

-- Sprawdź czy tabele są puste
SELECT 
    'listings' as table_name,
    COUNT(*) as row_count
FROM listings
UNION ALL
SELECT 
    'addresses' as table_name,
    COUNT(*) as row_count
FROM addresses;

-- Test funkcji kompletności (po dodaniu danych)
-- SELECT * FROM check_listing_completeness(1);

-- =====================================================
-- KOMUNIKAT KOŃCOWY
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '✅ TABELE UTWORZONE POMYŚLNIE!';
    RAISE NOTICE '📋 Utworzono tabele: listings, addresses';
    RAISE NOTICE '🔍 Utworzono widoki: listings_with_addresses, geocoded_listings';
    RAISE NOTICE '⚙️ Utworzono funkcje: check_listing_completeness';
    RAISE NOTICE '🚀 Scraper może teraz zapisywać dane do bazy!';
END $$; 