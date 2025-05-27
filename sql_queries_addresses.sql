-- PRZYDATNE ZAPYTANIA SQL DLA TABELI ADDRESSES
-- Wykonaj te zapytania w SQL Editor w Supabase

-- 1. PODSTAWOWE STATYSTYKI
SELECT 
    COUNT(*) as total_addresses,
    COUNT(DISTINCT city) as unique_cities,
    COUNT(DISTINCT district) as unique_districts,
    COUNT(DISTINCT province) as unique_provinces
FROM addresses;

-- 2. TOP 10 MIAST Z NAJWIĘKSZĄ LICZBĄ OGŁOSZEŃ
SELECT 
    city,
    COUNT(*) as listings_count
FROM addresses 
WHERE city IS NOT NULL
GROUP BY city 
ORDER BY listings_count DESC 
LIMIT 10;

-- 3. TOP 10 DZIELNIC Z NAJWIĘKSZĄ LICZBĄ OGŁOSZEŃ
SELECT 
    city,
    district,
    COUNT(*) as listings_count
FROM addresses 
WHERE district IS NOT NULL
GROUP BY city, district 
ORDER BY listings_count DESC 
LIMIT 10;

-- 4. ROZKŁAD OGŁOSZEŃ PO WOJEWÓDZTWACH
SELECT 
    province,
    COUNT(*) as listings_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM addresses), 2) as percentage
FROM addresses 
WHERE province IS NOT NULL
GROUP BY province 
ORDER BY listings_count DESC;

-- 5. ADRESY Z PEŁNĄ INFORMACJĄ (wszystkie pola wypełnione)
SELECT 
    full_address,
    street_name,
    district,
    sub_district,
    city,
    province
FROM addresses 
WHERE street_name IS NOT NULL 
    AND district IS NOT NULL 
    AND sub_district IS NOT NULL 
    AND city IS NOT NULL 
    AND province IS NOT NULL
LIMIT 20;

-- 6. ADRESY TYLKO Z MIASTEM (bez szczegółów)
SELECT 
    full_address,
    city,
    province
FROM addresses 
WHERE street_name IS NULL 
    AND district IS NULL 
    AND sub_district IS NULL 
    AND city IS NOT NULL
LIMIT 20;

-- 7. STATYSTYKI KOMPLETNOŚCI DANYCH
SELECT 
    'street_name' as field_name,
    COUNT(CASE WHEN street_name IS NOT NULL THEN 1 END) as filled_count,
    COUNT(*) as total_count,
    ROUND(COUNT(CASE WHEN street_name IS NOT NULL THEN 1 END) * 100.0 / COUNT(*), 2) as fill_percentage
FROM addresses
UNION ALL
SELECT 
    'district',
    COUNT(CASE WHEN district IS NOT NULL THEN 1 END),
    COUNT(*),
    ROUND(COUNT(CASE WHEN district IS NOT NULL THEN 1 END) * 100.0 / COUNT(*), 2)
FROM addresses
UNION ALL
SELECT 
    'sub_district',
    COUNT(CASE WHEN sub_district IS NOT NULL THEN 1 END),
    COUNT(*),
    ROUND(COUNT(CASE WHEN sub_district IS NOT NULL THEN 1 END) * 100.0 / COUNT(*), 2)
FROM addresses
UNION ALL
SELECT 
    'city',
    COUNT(CASE WHEN city IS NOT NULL THEN 1 END),
    COUNT(*),
    ROUND(COUNT(CASE WHEN city IS NOT NULL THEN 1 END) * 100.0 / COUNT(*), 2)
FROM addresses
UNION ALL
SELECT 
    'province',
    COUNT(CASE WHEN province IS NOT NULL THEN 1 END),
    COUNT(*),
    ROUND(COUNT(CASE WHEN province IS NOT NULL THEN 1 END) * 100.0 / COUNT(*), 2)
FROM addresses;

-- 8. POŁĄCZENIE Z TABELĄ LISTINGS (przykład JOIN)
SELECT 
    l.title,
    l.price,
    l.location as original_location,
    a.city,
    a.district,
    a.street_name,
    a.province
FROM listings l
JOIN addresses a ON l.id = a.foreign_key
WHERE a.city = 'Warszawa'
LIMIT 10;

-- 9. WYSZUKIWANIE PO DZIELNICY
SELECT 
    full_address,
    city,
    district,
    street_name
FROM addresses 
WHERE district ILIKE '%Mokotów%'
    OR district ILIKE '%Śródmieście%'
    OR district ILIKE '%Wola%'
ORDER BY city, district;

-- 10. ADRESY Z KONKRETNYMI ULICAMI
SELECT 
    full_address,
    city,
    district,
    street_name
FROM addresses 
WHERE street_name ILIKE '%Marszałkowska%'
    OR street_name ILIKE '%Puławska%'
    OR street_name ILIKE '%Grunwaldzka%'
ORDER BY city, street_name; 