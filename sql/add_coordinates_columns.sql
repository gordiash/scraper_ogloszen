-- DODANIE KOLUMN LONGITUDE I LATITUDE DO TABELI ADDRESSES
-- Wykonaj ten kod w SQL Editor w Supabase

-- Dodaj kolumny współrzędnych geograficznych
ALTER TABLE addresses 
ADD COLUMN IF NOT EXISTS latitude DECIMAL(10, 8),
ADD COLUMN IF NOT EXISTS longitude DECIMAL(11, 8);

-- Dodaj komentarze do nowych kolumn
COMMENT ON COLUMN addresses.latitude IS 'Szerokość geograficzna (decimal degrees)';
COMMENT ON COLUMN addresses.longitude IS 'Długość geograficzna (decimal degrees)';

-- Dodaj indeksy dla lepszej wydajności zapytań geograficznych
CREATE INDEX IF NOT EXISTS idx_addresses_latitude ON addresses(latitude);
CREATE INDEX IF NOT EXISTS idx_addresses_longitude ON addresses(longitude);
CREATE INDEX IF NOT EXISTS idx_addresses_coordinates ON addresses(latitude, longitude);

-- Dodaj constraint sprawdzający czy współrzędne są w rozsądnych granicach dla Polski
ALTER TABLE addresses 
ADD CONSTRAINT check_latitude_range 
CHECK (latitude IS NULL OR (latitude >= 49.0 AND latitude <= 54.9));

ALTER TABLE addresses 
ADD CONSTRAINT check_longitude_range 
CHECK (longitude IS NULL OR (longitude >= 14.1 AND longitude <= 24.2));

-- Sprawdź strukturę tabeli po dodaniu kolumn
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'addresses' 
ORDER BY ordinal_position;

-- Sprawdź czy kolumny zostały dodane
SELECT COUNT(*) as total_addresses,
       COUNT(latitude) as with_latitude,
       COUNT(longitude) as with_longitude
FROM addresses; 