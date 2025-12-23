# Guía Rápida: Ejecutar el Bot Standalone

Esta es una guía rápida para ejecutar el bot de Telegram en modo standalone para pruebas.

## Requisitos

- Python 3.10+
- Token de Telegram Bot (obtenerlo de [@BotFather](https://t.me/botfather))

## Instalación Rápida

```bash
# 1. Clonar el repositorio
git clone https://github.com/Geek-MD/CrazyOnes.git
cd CrazyOnes

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar token en config.json
cat > config.json << EOF
{
  "version": "0.9.3",
  "apple_updates_url": "https://support.apple.com/es-cl/100100",
  "telegram_bot_token": "TU_TOKEN_AQUI"
}
EOF
```

## Flujo de Trabajo

### Paso 1: Generar Datos (Solo primera vez)

**IMPORTANTE**: El bot lee datos de archivos JSON. Primero debes generar estos datos.

El sistema usa el token almacenado en `config.json`, así que puedes ejecutar:

```bash
python3 crazyones.py --url https://support.apple.com/es-cl/100100
```

O si prefieres especificar el token explícitamente:

```bash
python3 crazyones.py --token TU_TOKEN --url https://support.apple.com/es-cl/100100
```

Esto creará:
- `data/language_urls.json` - URLs de idiomas
- `data/language_names.json` - Nombres de idiomas  
- `data/updates/es-cl.json` - Actualizaciones para Chile
- Y más archivos para otros idiomas

**Tiempo estimado**: 1-2 minutos

### Paso 2: Ejecutar el Bot

**El bot usa el token de config.json automáticamente:**

```bash
python3 crazyones-bot.py
```

Si quieres usar un token diferente al de config.json:

```bash
python3 crazyones-bot.py -t OTRO_TOKEN
```

Deberías ver:

```
INFO - ============================================================
INFO - CrazyOnes Telegram Bot - Standalone Mode
INFO - ============================================================
INFO - Starting Telegram bot...
INFO - Token: ********************...xyz1234567
INFO - Starting polling...
INFO - ✓ Bot is running and polling for updates
INFO - 
INFO - Bot commands:
INFO -   /start - Subscribe to Apple Updates notifications
INFO -   /stop  - Unsubscribe from notifications
INFO - 
INFO - Press Ctrl+C to stop the bot
INFO - ============================================================
```

### Paso 3: Usar el Bot en Telegram

1. Abre Telegram en tu teléfono o computadora
2. Busca tu bot por el nombre que le diste en @BotFather
3. Inicia una conversación
4. Envía el comando: `/start`
5. El bot responderá automáticamente con las 10 actualizaciones más recientes de Apple para Chile

**Ejemplo de respuesta:**

```
🍎 ¡Bienvenido al Bot de Actualizaciones de Apple!

Aquí están las 10 actualizaciones más recientes de Apple para Chile:

1. 2024-12-19 - iOS 17.2.1 - iPhone XS y posterior
2. 2024-12-11 - iOS 17.2 - iPhone XS y posterior
3. 2024-12-11 - macOS Sonoma 14.2 - Mac
4. 2024-12-11 - watchOS 10.2 - Apple Watch
5. 2024-12-11 - tvOS 17.2 - Apple TV
6. 2024-11-30 - iOS 17.1.2 - iPhone XS y posterior
7. 2024-11-07 - iOS 17.1.1 - iPhone XS y posterior
8. 2024-11-07 - macOS Sonoma 14.1.1 - Mac
9. 2024-10-25 - iOS 17.1 - iPhone XS y posterior
10. 2024-10-25 - macOS Sonoma 14.1 - Mac
```

### Paso 4: Detener el Bot

Presiona `Ctrl+C` en la terminal donde está corriendo el bot.

## Actualizar Datos

Para obtener las actualizaciones más recientes (usa el token de config.json):

```bash
# 1. Detener el bot (Ctrl+C)
# 2. Ejecutar el monitor para actualizar datos
python3 crazyones.py --url https://support.apple.com/es-cl/100100
# 3. Reiniciar el bot
python3 crazyones-bot.py
```

## Solución de Problemas

### El bot no responde

1. **Verifica que el bot esté corriendo**: Deberías ver "✓ Bot is running and polling for updates"
2. **Verifica el token**: Asegúrate de usar el token correcto de @BotFather
3. **Verifica los datos**: Asegúrate de haber ejecutado el Paso 1 (generar datos)

### Error: "No module named 'telegram'"

```bash
pip install -r requirements.txt
```

### Error: "Language URLs file not found"

Debes generar los datos primero (usa el token de config.json):

```bash
python3 crazyones.py --url https://support.apple.com/es-cl/100100
```

### Error: "Configuration file not found"

Crea `config.json` con tu token:

```json
{
  "version": "0.9.3",
  "apple_updates_url": "https://support.apple.com/es-cl/100100",
  "telegram_bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890"
}
```

## Características de esta Versión (Prueba de Concepto)

✅ **Implementado:**
- Bot standalone que se puede ejecutar independientemente
- Responde al comando `/start`
- Muestra automáticamente las 10 actualizaciones más recientes de es-cl
- Sin selección de idioma (fijo a es-cl para pruebas)

🔄 **Por implementar:**
- Selección de idioma por el usuario
- Sistema de suscripciones
- Comando `/stop` funcional
- Notificaciones automáticas de nuevas actualizaciones

## Documentación Completa

Para más detalles, consulta:
- `BOT_STANDALONE.md` - Documentación completa del bot standalone
- `README.md` - Documentación del sistema completo CrazyOnes

## Nota sobre Datos de Prueba

Esta versión es una **prueba de concepto** que usa datos de ejemplo. Para uso en producción:

1. Configura el sistema completo siguiendo `README.md`
2. Usa el modo daemon para monitoreo continuo
3. Integra el bot con el sistema de monitoreo

## Soporte

Si encuentras problemas, revisa los logs en la consola o consulta la documentación completa.
