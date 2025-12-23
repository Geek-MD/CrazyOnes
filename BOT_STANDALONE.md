# CrazyOnes Bot - Modo Standalone

Este documento explica cómo ejecutar el bot de Telegram de forma independiente para pruebas y depuración.

## Descripción

El bot en modo standalone es una versión simplificada (prueba de concepto) que automáticamente muestra las 10 actualizaciones más recientes de Apple Updates para Chile (es-cl) cuando un usuario envía el comando `/start`.

**NOTA IMPORTANTE:** El bot lee los datos de los archivos JSON generados por el proceso de monitoreo (`crazyones.py`). Por lo tanto, **debes ejecutar primero el monitor** para generar los datos antes de poder usar el bot.

## Flujo de Trabajo

1. **Primero**: Ejecutar el monitor para generar los datos
   ```bash
   python3 crazyones.py --token TU_TOKEN --url https://support.apple.com/es-cl/100100
   ```

2. **Segundo**: Ejecutar el bot standalone
   ```bash
   python3 crazyones-bot.py -t TU_TOKEN
   ```

3. **Usar el bot**: Abrir Telegram y enviar `/start` al bot

## Requisitos Previos

1. **Python 3.10 o superior**
2. **Dependencias instaladas:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Token de Telegram Bot:**
   - Obtén un token de [@BotFather](https://t.me/botfather) en Telegram
   - El token tiene el formato: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890`

## Configuración

### Opción 1: Usar config.json (Recomendado)

Crea o edita el archivo `config.json` en el directorio raíz del proyecto:

```json
{
  "version": "0.9.3",
  "apple_updates_url": "https://support.apple.com/en-us/100100",
  "telegram_bot_token": "TU_TOKEN_AQUI"
}
```

### Opción 2: Pasar el token como argumento

Puedes pasar el token directamente al ejecutar el script (ver ejemplos abajo).

## Ejecutar el Bot

### Desde el directorio del proyecto:

**Usando el token de config.json:**
```bash
python3 crazyones-bot.py
```

**Especificando el token directamente:**
```bash
python3 crazyones-bot.py --token TU_TOKEN_AQUI
```

o la versión corta:
```bash
python3 crazyones-bot.py -t TU_TOKEN_AQUI
```

### Haciendo el script ejecutable (Linux/Mac):

```bash
chmod +x crazyones-bot.py
./crazyones-bot.py
```

## Uso del Bot

Una vez que el bot esté corriendo:

1. Abre Telegram y busca tu bot (usando el nombre que le diste en @BotFather)
2. Inicia una conversación con el bot
3. Envía el comando `/start`
4. El bot responderá automáticamente con las 10 actualizaciones más recientes de Apple para Chile

### Comandos Disponibles

- `/start` - Muestra las 10 actualizaciones más recientes de Apple (es-cl)
- `/stop` - Para el bot (actualmente no implementado en esta versión simplificada)

## Detener el Bot

Para detener el bot, presiona `Ctrl+C` en la terminal donde está corriendo.

El bot se detendrá de forma ordenada (graceful shutdown).

## Archivos de Datos Necesarios

**IMPORTANTE:** El bot extrae la información de los archivos JSON que son generados por el proceso `crazyones.py` (monitor).

El bot necesita los siguientes archivos de datos para funcionar:

```
data/
├── language_urls.json      # URLs de idiomas disponibles
├── language_names.json     # Nombres legibles de idiomas
├── updates_tracking.json   # Tracking de URLs procesadas
└── updates/
    └── es-cl.json         # Actualizaciones para Chile
```

### Generar los Archivos de Datos

**ANTES de ejecutar el bot**, debes generar los archivos de datos ejecutando el monitor:

```bash
# Opción 1: Ejecutar una vez con el token
python3 crazyones.py --token TU_TOKEN --url https://support.apple.com/es-cl/100100

# Opción 2: Si ya tienes config.json configurado
python3 crazyones.py --url https://support.apple.com/es-cl/100100
```

Esto hará que `crazyones.py`:
1. Extraiga las URLs de idiomas disponibles en Apple Updates
2. Obtenga las actualizaciones de seguridad para cada idioma
3. Guarde los datos en los archivos JSON en el directorio `data/`

Una vez que estos archivos existan, el bot podrá leerlos y mostrar las actualizaciones a los usuarios.

## Solución de Problemas

### Error: "No module named 'telegram'"

Instala las dependencias:
```bash
pip install -r requirements.txt
```

### Error: "Configuration file not found"

Crea el archivo `config.json` con tu token o pasa el token como argumento:
```bash
python3 crazyones-bot.py -t TU_TOKEN_AQUI
```

### Error: "Language URLs file not found"

El bot necesita que primero ejecutes el proceso de monitoreo para generar los archivos JSON. Ejecuta:

```bash
# Generar los datos necesarios ejecutando el monitor
python3 crazyones.py --token TU_TOKEN --url https://support.apple.com/es-cl/100100
```

Esto creará los archivos:
- `data/language_urls.json`
- `data/language_names.json`
- `data/updates/es-cl.json` (y otros idiomas disponibles)

Una vez generados estos archivos, puedes ejecutar el bot standalone:

```bash
python3 crazyones-bot.py -t TU_TOKEN
```

### El bot no responde a /start

1. Verifica que el bot esté corriendo (deberías ver "✓ Bot is running and polling for updates")
2. Verifica que el token sea correcto
3. Verifica que los archivos de datos existan en el directorio `data/`
4. Revisa los logs en la consola para ver si hay errores

## Logs y Debugging

El bot muestra información de logging en la consola:

- **INFO**: Información general (inicio, comandos recibidos, etc.)
- **ERROR**: Errores que requieren atención
- **DEBUG**: Información detallada para depuración (activar con logging.DEBUG)

Para ver más detalles, edita `crazyones-bot.py` y cambia el nivel de logging:

```python
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG  # Cambiar INFO a DEBUG
)
```

## Próximos Pasos

Esta es una versión de prueba de concepto. Las mejoras planificadas incluyen:

- [ ] Selección de idioma por el usuario
- [ ] Sistema de suscripciones persistente
- [ ] Notificaciones automáticas de nuevas actualizaciones
- [ ] Soporte para múltiples idiomas simultáneos
- [ ] Comando `/stop` funcional
- [ ] Integración completa con el sistema de monitoreo

## Notas Técnicas

- El bot usa `python-telegram-bot` versión 20.0+
- Utiliza polling (no webhooks) para simplicidad
- Los handlers registrados: CommandHandler, CallbackQueryHandler, ChatMemberHandler
- Corre en un solo proceso con asyncio
