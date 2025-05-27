#!/usr/bin/env python3
"""
AKTUALIZACJA ADRESÓW BEZ MIASTA W BAZIE
Uzupełnia city z district dla adresów gdzie city jest null
"""
from address_parser import get_supabase_client, parse_location_string
import logging

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def update_null_cities(dry_run: bool = True, batch_size: int = 50):
    """
    Aktualizuje adresy bez miasta w bazie
    
    Args:
        dry_run: Jeśli True, tylko pokazuje co by zostało zaktualizowane
        batch_size: Liczba adresów do przetworzenia na raz
    """
    
    print('🔧 AKTUALIZACJA ADRESÓW BEZ MIASTA W BAZIE')
    print('='*60)
    print(f'📊 Tryb: {"DRY RUN (tylko podgląd)" if dry_run else "RZECZYWISTA AKTUALIZACJA"}')
    print(f'📦 Rozmiar batch: {batch_size}')
    print('='*60)
    
    try:
        client = get_supabase_client()
        
        # Pobierz wszystkie adresy bez miasta
        result = client.table('addresses').select('id, full_address, city, district').is_('city', 'null').execute()
        
        if not result.data:
            print('✅ Wszystkie adresy mają wypełnione miasto!')
            return
        
        total_addresses = len(result.data)
        print(f'📊 Znaleziono {total_addresses} adresów bez miasta')
        
        updated_count = 0
        skipped_count = 0
        error_count = 0
        
        # Przetwarzaj w batch'ach
        for i in range(0, total_addresses, batch_size):
            batch = result.data[i:i+batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_addresses + batch_size - 1) // batch_size
            
            print(f'\n📦 BATCH {batch_num}/{total_batches} ({len(batch)} adresów):')
            print('-' * 50)
            
            for j, addr in enumerate(batch, 1):
                addr_id = addr['id']
                full_address = addr['full_address']
                old_city = addr['city']
                old_district = addr['district']
                
                try:
                    # Parsuj z nową logiką
                    parsed = parse_location_string(full_address)
                    new_city = parsed.get('city')
                    new_district = parsed.get('district')
                    
                    # Sprawdź czy można zaktualizować
                    if new_city and not old_city:
                        print(f'  {j:2d}. ID {addr_id}: "{old_district}" → "{new_city}"')
                        
                        if not dry_run:
                            # Rzeczywista aktualizacja
                            update_data = {
                                'city': new_city,
                                'district': new_district  # Może być None
                            }
                            
                            client.table('addresses').update(update_data).eq('id', addr_id).execute()
                            logger.debug(f'Zaktualizowano adres ID {addr_id}')
                        
                        updated_count += 1
                    else:
                        print(f'  {j:2d}. ID {addr_id}: POMINIĘTO (brak poprawy)')
                        skipped_count += 1
                        
                except Exception as e:
                    print(f'  {j:2d}. ID {addr_id}: BŁĄD - {e}')
                    error_count += 1
                    logger.error(f'Błąd aktualizacji adresu ID {addr_id}: {e}')
            
            # Progress info
            processed = min(i + batch_size, total_addresses)
            print(f'📊 Postęp: {processed}/{total_addresses} - zaktualizowane: {updated_count}, pominięte: {skipped_count}, błędy: {error_count}')
        
        # Podsumowanie końcowe
        print(f'\n📈 PODSUMOWANIE KOŃCOWE:')
        print('='*60)
        print(f'📊 Łącznie adresów: {total_addresses}')
        print(f'✅ Zaktualizowane: {updated_count}')
        print(f'⏭️ Pominięte: {skipped_count}')
        print(f'❌ Błędy: {error_count}')
        
        if updated_count > 0:
            success_rate = (updated_count / total_addresses) * 100
            print(f'📈 Skuteczność: {success_rate:.1f}%')
        
        if dry_run and updated_count > 0:
            print(f'\n💡 Aby wykonać rzeczywistą aktualizację:')
            print(f'   python update_null_cities.py --real')
        
    except Exception as e:
        print(f'❌ Błąd krytyczny: {e}')
        logger.error(f'Błąd w update_null_cities: {e}', exc_info=True)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Aktualizacja adresów bez miasta')
    parser.add_argument('--real', action='store_true', help='Wykonaj rzeczywistą aktualizację (domyślnie: dry run)')
    parser.add_argument('--batch-size', type=int, default=50, help='Rozmiar batch (domyślnie: 50)')
    
    args = parser.parse_args()
    
    try:
        update_null_cities(dry_run=not args.real, batch_size=args.batch_size)
    except KeyboardInterrupt:
        print('\n⚠️ Przerwano przez użytkownika')
    except Exception as e:
        print(f'\n❌ Błąd krytyczny: {e}') 