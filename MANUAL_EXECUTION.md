# Manual de Ejecución Manual de Scripts

Este documento explica cómo ejecutar cada script individualmente para propósitos de depuración y desarrollo.

## ⚠️ Importante

**En producción, NO necesitas ejecutar estos scripts manualmente.** Simplemente ejecuta:
```bash
python3 crazyones.py --token YOUR_TOKEN
```

Este documento es **solo para desarrollo y depuración** cuando quieres entender o probar cada componente por separado.

## Orden de Ejecución Lógico

Los scripts deben ejecutarse en el siguiente orden:

### 1. `scrape_apple_updates.py` (PRIMERO)
**Propósito**: Obtiene todas las URLs de los diferentes idiomas disponibles en Apple Updates.

```bash
cd scripts
python3 scrape_apple_updates.py
```

**Qué hace**:
- Descarga la página de Apple Updates (por defecto: https://support.apple.com/en-us/100100)
- Extrae todos los enlaces a versiones en diferentes idiomas
- Guarda las URLs en `data/language_urls.json`
- Genera automáticamente `data/language_names.json` con los nombres de los idiomas

**Archivos que crea**:
- `data/language_urls.json` - Mapeo de códigos de idioma a URLs
- `data/language_names.json` - Nombres legibles de los idiomas

**Ejemplo de salida**:
```
Fetching Apple Updates page: https://support.apple.com/en-us/100100
Extracting language-specific URLs...

Language URLs saved to data/language_urls.json
First time: Found 45 language versions:
  ar-ae: https://support.apple.com/ar-ae/100100
  de-de: https://support.apple.com/de-de/100100
  en-us: https://support.apple.com/en-us/100100
  es-es: https://support.apple.com/es-es/100100
  ...
```

---

### 2. `monitor_apple_updates.py` (SEGUNDO)
**Propósito**: Monitorea y descarga las actualizaciones de seguridad de cada URL de idioma.

```bash
cd scripts
python3 monitor_apple_updates.py
```

**Qué hace**:
- Lee `data/language_urls.json` (creado por el script anterior)
- Para cada idioma, descarga la página y extrae la tabla de actualizaciones de seguridad
- Guarda cada idioma en un archivo JSON separado
- Utiliza hashes SHA256 para detectar cambios en el contenido
- Solo reprocesa páginas que han cambiado

**Archivos que lee**:
- `data/language_urls.json` (REQUERIDO - debe existir)

**Archivos que crea**:
- `data/updates/en-us.json` - Actualizaciones en inglés (USA)
- `data/updates/es-es.json` - Actualizaciones en español (España)
- `data/updates/*.json` - Un archivo por cada idioma
- `data/updates_tracking.json` - Seguimiento de cambios (hashes de contenido)

**Ejemplo de salida**:
```
=== Apple Security Updates Monitor ===

Loaded 45 language URLs

Processing en-us: https://support.apple.com/en-us/100100
  ✓ Saved 156 updates for en-us
Processing es-es: https://support.apple.com/es-es/100100
  ✓ Saved 156 updates for es-es
...

=== Summary ===
Processed: 45 languages
Successful: 45 languages
Updates saved to 'data/updates/' directory
```

---

### 3. `generate_language_names.py` (OPCIONAL)
**Propósito**: Regenera el mapeo de códigos de idioma a nombres legibles.

```bash
cd scripts
python3 generate_language_names.py
```

**Nota**: Este script **YA se ejecuta automáticamente** al final de `scrape_apple_updates.py`, así que normalmente NO necesitas ejecutarlo manualmente.

**Cuándo ejecutarlo manualmente**:
- Si borraste accidentalmente `data/language_names.json`
- Si agregaste nuevos códigos de idioma al mapeo `LANGUAGE_NAME_MAP` en el código

**Archivos que lee**:
- `data/language_urls.json` (REQUERIDO)

**Archivos que crea**:
- `data/language_names.json`

---

### 4. `telegram_bot.py` (NO EJECUTAR DIRECTAMENTE)
**Propósito**: Bot de Telegram que notifica a usuarios sobre actualizaciones.

⚠️ **Este script NO está diseñado para ejecutarse de forma independiente.** 

Solo debe usarse con:
```bash
python3 crazyones.py --token YOUR_TOKEN --daemon --bot
```

---

## Resumen del Flujo de Datos

```
┌─────────────────────────────────┐
│ 1. scrape_apple_updates.py      │
│    Descarga página de Apple     │
│    Extrae URLs de idiomas       │
└───────────┬─────────────────────┘
            │
            │ Crea: data/language_urls.json
            │       data/language_names.json
            ↓
┌─────────────────────────────────┐
│ 2. monitor_apple_updates.py     │
│    Lee URLs de idiomas          │
│    Descarga actualizaciones     │
│    Detecta cambios              │
└───────────┬─────────────────────┘
            │
            │ Crea: data/updates/*.json
            │       data/updates_tracking.json
            ↓
┌─────────────────────────────────┐
│ Datos listos para usar          │
│ - Bot de Telegram               │
│ - APIs personalizadas           │
│ - Análisis de datos             │
└─────────────────────────────────┘
```

## Errores Comunes

### Error: "Language URLs file not found"
```
Error: Language URLs file not found: data/language_urls.json
Please run scrape_apple_updates.py first
```

**Solución**: Ejecuta primero `scrape_apple_updates.py`:
```bash
cd scripts
python3 scrape_apple_updates.py
```

### Error: "ImportError: attempted relative import"
```
ImportError: attempted relative import with no known parent package
```

**Solución**: Este error ya está corregido en la versión actual. Asegúrate de tener la última versión del código.

### Error de conexión de red
```
requests.exceptions.ConnectionError: Failed to establish a new connection
```

**Solución**: Verifica tu conexión a internet. Los scripts necesitan acceso a `support.apple.com`.

## Modo de Ejecución Normal (Recomendado)

En lugar de ejecutar scripts individuales, usa el coordinador principal:

```bash
# Ejecución única (hace todo automáticamente)
python3 crazyones.py --token YOUR_TOKEN

# Modo daemon (ejecución continua cada 12 horas)
python3 crazyones.py --token YOUR_TOKEN --daemon

# Con bot de Telegram
python3 crazyones.py --token YOUR_TOKEN --daemon --bot
```

El script `crazyones.py` ejecuta todos los pasos en el orden correcto automáticamente.

## Para Desarrolladores

Si estás desarrollando o depurando:

1. **Primera vez**: Ejecuta `scrape_apple_updates.py` para obtener las URLs
2. **Después**: Ejecuta `monitor_apple_updates.py` para obtener las actualizaciones
3. **Para probar cambios**: Ejecuta el script específico que modificaste
4. **Para probar el flujo completo**: Usa `python3 crazyones.py`

## Verificar que los Scripts Funcionan

Puedes verificar que cada script se importa correctamente:

```bash
# Desde el directorio raíz del proyecto
python3 -c "from scripts.scrape_apple_updates import fetch_apple_updates_page; print('✓ OK')"
python3 -c "from scripts.monitor_apple_updates import load_language_urls; print('✓ OK')"
python3 -c "from scripts.generate_language_names import update_language_names; print('✓ OK')"
```

## Soporte

Si tienes problemas:
1. Verifica que todas las dependencias estén instaladas: `pip install -r requirements.txt`
2. Asegúrate de ejecutar los scripts en el orden correcto
3. Revisa los logs en `crazyones.log`
4. Consulta el README principal para más información
