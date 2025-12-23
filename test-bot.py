#!/usr/bin/env python3
"""
Test script para verificar que el bot puede cargar datos y formatear mensajes.
No se conecta a Telegram, solo verifica la funcionalidad local.
"""

import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

def test_data_loading():
    """Test que los archivos de datos se pueden cargar."""
    print("=" * 60)
    print("Test 1: Carga de Archivos de Datos")
    print("=" * 60)
    print()
    
    from telegram_bot import (
        load_language_urls,
        load_updates_for_language,
    )
    
    # Test language URLs
    try:
        language_urls = load_language_urls()
        print(f"✓ language_urls.json cargado: {len(language_urls)} idiomas")
        if "es-cl" in language_urls:
            print(f"✓ es-cl encontrado: {language_urls['es-cl']}")
        else:
            print("✗ es-cl no encontrado en language_urls.json")
            return False
    except Exception as e:
        print(f"✗ Error cargando language_urls.json: {e}")
        return False
    
    print()
    
    # Test updates for es-cl
    try:
        updates = load_updates_for_language("es-cl")
        print(f"✓ Updates para es-cl cargados: {len(updates)} actualizaciones")
        
        if updates:
            print()
            print("Las 3 actualizaciones más recientes:")
            for i, update in enumerate(updates[:3], 1):
                name = update.get("name", "Unknown")
                date = update.get("date", "N/A")
                target = update.get("target", "N/A")
                print(f"  {i}. {date} - {name} - {target}")
    except Exception as e:
        print(f"✗ Error cargando updates: {e}")
        return False
    
    print()
    return True


def test_message_formatting():
    """Test que los mensajes se formatean correctamente."""
    print("=" * 60)
    print("Test 2: Formateo de Mensajes")
    print("=" * 60)
    print()
    
    from telegram_bot import load_updates_for_language
    
    try:
        updates = load_updates_for_language("es-cl")
        
        if not updates:
            print("✗ No hay updates para formatear")
            return False
        
        recent_updates = updates[:10]
        
        # Simulate message formatting
        message = "🍎 *¡Bienvenido al Bot de Actualizaciones de Apple!*\n\n"
        message += "Aquí están las 10 actualizaciones más recientes de Apple para Chile:\n\n"
        
        for idx, update_item in enumerate(recent_updates, 1):
            date = update_item.get("date", "N/A")
            name = update_item.get("name", "Unknown")
            target = update_item.get("target", "N/A")
            url = update_item.get("url")
            
            if url:
                update_line = f"{idx}. {date} - [{name}]({url}) - {target}\n"
            else:
                update_line = f"{idx}. {date} - {name} - {target}\n"
            
            message += update_line
        
        print("Mensaje de ejemplo que enviará el bot:")
        print()
        print(message)
        
        return True
        
    except Exception as e:
        print(f"✗ Error formateando mensaje: {e}")
        return False


def test_config_loading():
    """Test que el config.json se puede cargar."""
    print("=" * 60)
    print("Test 3: Carga de Configuración")
    print("=" * 60)
    print()
    
    import json
    
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        
        token = config.get("telegram_bot_token", "")
        
        if token and token != "YOUR_TELEGRAM_BOT_TOKEN_HERE":
            print(f"✓ Token encontrado en config.json")
            print(f"  Token: {token[:15]}...{token[-10:]}")
        else:
            print("⚠ Token no configurado en config.json")
            print("  El bot no podrá conectarse a Telegram")
            return False
        
        print()
        return True
        
    except FileNotFoundError:
        print("✗ config.json no encontrado")
        return False
    except Exception as e:
        print(f"✗ Error leyendo config.json: {e}")
        return False


def main():
    """Ejecutar todos los tests."""
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "CrazyOnes Bot - Test de Funcionalidad" + " " * 10 + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    results = []
    
    # Test 1: Config
    results.append(("Configuración", test_config_loading()))
    print()
    
    # Test 2: Data Loading
    results.append(("Carga de Datos", test_data_loading()))
    print()
    
    # Test 3: Message Formatting
    results.append(("Formateo de Mensajes", test_message_formatting()))
    print()
    
    # Summary
    print("=" * 60)
    print("Resumen de Tests")
    print("=" * 60)
    print()
    
    all_passed = True
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status} - {test_name}")
        if not result:
            all_passed = False
    
    print()
    
    if all_passed:
        print("✓ Todos los tests pasaron!")
        print()
        print("El bot está listo para ejecutarse:")
        print("  python3 crazyones-bot.py")
        print()
        return 0
    else:
        print("✗ Algunos tests fallaron")
        print()
        print("Por favor, revisa los errores antes de ejecutar el bot")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
