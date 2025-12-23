#!/bin/bash
# Script de ejemplo para demostrar el flujo completo de CrazyOnes Bot

echo "=========================================="
echo "CrazyOnes Bot - Flujo de Trabajo Completo"
echo "=========================================="
echo ""

# Verificar que Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "✗ Error: Python 3 no está instalado"
    exit 1
fi

echo "✓ Python 3 encontrado: $(python3 --version)"
echo ""

# Verificar dependencias
echo "Paso 1: Verificando dependencias..."
if python3 -c "import telegram" 2>/dev/null; then
    echo "✓ python-telegram-bot instalado"
else
    echo "⚠ python-telegram-bot no instalado"
    echo "  Instalando dependencias..."
    pip install -r requirements.txt
fi
echo ""

# Verificar token
echo "Paso 2: Verificando configuración..."
if [ -f "config.json" ]; then
    echo "✓ config.json encontrado"
    TOKEN=$(python3 -c "import json; print(json.load(open('config.json')).get('telegram_bot_token', ''))" 2>/dev/null)
    if [ ! -z "$TOKEN" ] && [ "$TOKEN" != "YOUR_TELEGRAM_BOT_TOKEN_HERE" ]; then
        echo "✓ Token configurado en config.json"
        USE_CONFIG=1
    else
        echo "⚠ Token no válido en config.json"
        echo "  Por favor, edita config.json con tu token de @BotFather"
        USE_CONFIG=0
    fi
else
    echo "⚠ config.json no encontrado"
    echo "  Por favor, crea config.json con tu token"
    USE_CONFIG=0
fi
echo ""

# Generar datos (si no existen)
echo "Paso 3: Verificando archivos de datos..."
if [ -f "data/updates/es-cl.json" ]; then
    echo "✓ Datos de es-cl ya existen"
    NUM_UPDATES=$(python3 -c "import json; print(len(json.load(open('data/updates/es-cl.json'))))" 2>/dev/null || echo "0")
    echo "  Actualizaciones disponibles: $NUM_UPDATES"
else
    echo "⚠ Datos no encontrados"
    echo ""
    echo "IMPORTANTE: Debes generar los datos primero ejecutando:"
    echo "  python3 crazyones.py --token TU_TOKEN --url https://support.apple.com/es-cl/100100"
    echo ""
    echo "Esto descargará las actualizaciones de Apple y las guardará en data/"
    exit 1
fi
echo ""

# Mostrar instrucciones para ejecutar el bot
echo "=========================================="
echo "Todo listo para ejecutar el bot!"
echo "=========================================="
echo ""
echo "Para ejecutar el bot en modo standalone:"
echo ""

if [ $USE_CONFIG -eq 1 ]; then
    echo "  python3 crazyones-bot.py"
    echo ""
    echo "O si quieres especificar un token diferente:"
    echo "  python3 crazyones-bot.py -t TU_TOKEN"
else
    echo "  python3 crazyones-bot.py -t TU_TOKEN"
fi

echo ""
echo "Una vez iniciado el bot:"
echo "  1. Abre Telegram"
echo "  2. Busca tu bot (nombre configurado en @BotFather)"
echo "  3. Envía /start"
echo "  4. El bot mostrará las 10 actualizaciones más recientes de Apple para Chile"
echo ""
echo "Para detener el bot: Presiona Ctrl+C"
echo ""
