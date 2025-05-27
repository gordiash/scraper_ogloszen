-- TABELA ADDRESSES - ROZDZIELONE ADRESY Z LISTINGS
-- Wykonaj ten kod w SQL Editor w Supabase

CREATE TABLE addresses (
    id SERIAL PRIMARY KEY,
    full_address TEXT NOT NULL,
    street_name TEXT,
    district TEXT,
    sub_district TEXT, -- Można nazwać 'area' lub 'neighborhood'
    city TEXT,
    province TEXT,
    foreign_key INTEGER REFERENCES listings(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indeksy dla lepszej wydajności
CREATE INDEX idx_addresses_foreign_key ON addresses(foreign_key);
CREATE INDEX idx_addresses_city ON addresses(city);
CREATE INDEX idx_addresses_district ON addresses(district);
CREATE INDEX idx_addresses_province ON addresses(province);

-- Trigger do automatycznego ustawiania updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_addresses_updated_at 
    BEFORE UPDATE ON addresses 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Komentarze do kolumn
COMMENT ON TABLE addresses IS 'Rozdzielone komponenty adresów z tabeli listings';
COMMENT ON COLUMN addresses.full_address IS 'Pełny oryginalny adres z kolumny location';
COMMENT ON COLUMN addresses.street_name IS 'Nazwa ulicy (ul., al., pl., os.)';
COMMENT ON COLUMN addresses.district IS 'Dzielnica/rejon miasta';
COMMENT ON COLUMN addresses.sub_district IS 'Pod-dzielnica/osiedle/obszar';
COMMENT ON COLUMN addresses.city IS 'Miasto';
COMMENT ON COLUMN addresses.province IS 'Województwo';
COMMENT ON COLUMN addresses.foreign_key IS 'Klucz obcy do tabeli listings';

-- Sprawdź czy tabela została utworzona
SELECT 
    table_name, 
    column_name, 
    data_type, 
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'addresses' 
ORDER BY ordinal_position; 