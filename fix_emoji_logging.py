#!/usr/bin/env python3
"""
Naprawa emoji w logowaniu dla Windows PowerShell
"""
import logging
import sys
import io

def setup_unicode_logging():
    """Ustaw kodowanie dla emoji w Windows"""
    # Wymuszenie UTF-8 dla stdout/stderr
    if sys.platform == "win32":
        try:
            # Spróbuj ustawić UTF-8
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, 
                encoding='utf-8', 
                errors='replace'
            )
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer, 
                encoding='utf-8', 
                errors='replace'
            )
            print("🔧 Kodowanie UTF-8 ustawione dla emoji")
        except Exception as e:
            print(f"⚠️ Nie udało się ustawić UTF-8: {e}")
            print("💡 Emoji mogą nie wyświetlać się poprawnie")

def create_ascii_logging():
    """Stwórz wersję logowania bez emoji"""
    # Słownik konwersji emoji na ASCII
    EMOJI_REPLACEMENTS = {
        '🎯': '>>>',
        '📋': '[INFO]',
        '🔍': '[SEARCH]',
        '✅': '[OK]',
        '❌': '[ERROR]',
        '⚠️': '[WARN]',
        '📊': '[STATS]',
        '🎉': '[SUCCESS]',
        '⏭️': '[SKIP]',
        '📝': '[NOTE]',
        '📈': '[PERF]',
        '💰': '[PRICE]',
        '📍': '[LOC]',
        '📐': '[AREA]',
        '🚪': '[ROOMS]',
        '🌐': '[SOURCE]',
        '🔗': '[URL]',
        '🏠': '[PROPERTY]',
        '💾': '[SAVE]',
        '🔄': '[PROCESS]',
        '🚀': '[START]',
        '💡': '[TIP]',
        '🔧': '[FIX]',
        '📄': '[TITLE]'
    }
    
    class NoEmojiFormatter(logging.Formatter):
        def format(self, record):
            # Usuń emoji z wiadomości
            msg = super().format(record)
            for emoji, replacement in EMOJI_REPLACEMENTS.items():
                msg = msg.replace(emoji, replacement)
            return msg
    
    # Skonfiguruj formatter bez emoji
    formatter = NoEmojiFormatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Zastąp wszystkie handlery
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Dodaj nowy handler bez emoji
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
    
    print("[FIX] Logging bez emoji skonfigurowany dla Windows")

if __name__ == "__main__":
    print("🧪 TEST NAPRAWY EMOJI")
    print("=" * 50)
    
    print("1. Próba UTF-8...")
    setup_unicode_logging()
    
    print("\n2. Fallback do ASCII...")
    create_ascii_logging()
    
    print("\n3. Test logowania...")
    logger = logging.getLogger(__name__)
    logger.info("✅ Test emoji w logach")
    logger.warning("⚠️ Test ostrzeżenia")
    logger.error("❌ Test błędu")
    
    print("\n[SUCCESS] Test zakończony!") 