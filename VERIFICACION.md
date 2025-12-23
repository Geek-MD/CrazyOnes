# ✅ Lista de Verificación - Bot Standalone

Usa esta lista para verificar que todo está configurado correctamente antes de ejecutar el bot.

## 📋 Pre-requisitos

### 1. Python y Dependencias
```bash
# Verificar Python
python3 --version
# Debe ser 3.10 o superior

# Instalar dependencias
pip install -r requirements.txt
```

- [ ] Python 3.10+ instalado
- [ ] Dependencias instaladas (requests, beautifulsoup4, lxml, python-telegram-bot)

### 2. Token de Telegram
```bash
# Verificar que el token está en config.json
cat config.json | grep telegram_bot_token
```

- [ ] Token obtenido de @BotFather
- [ ] Token guardado en config.json
- [ ] Token NO es "YOUR_TELEGRAM_BOT_TOKEN_HERE"

### 3. Archivos de Datos

**IMPORTANTE**: Ejecutar primero el monitor para generar datos:

```bash
python3 crazyones.py --url https://support.apple.com/es-cl/100100
```

Verificar que se crearon:
```bash
ls -la data/
ls -la data/updates/
```

- [ ] Archivo `data/language_urls.json` existe
- [ ] Archivo `data/language_names.json` existe
- [ ] Archivo `data/updates/es-cl.json` existe
- [ ] El archivo es-cl.json tiene actualizaciones (no está vacío)

## 🧪 Tests

### Ejecutar Tests Automatizados
```bash
python3 test-bot.py
```

Deberías ver:
```
✓ PASS - Configuración
✓ PASS - Carga de Datos
✓ PASS - Formateo de Mensajes
✓ Todos los tests pasaron!
```

- [ ] Test de Configuración: PASS
- [ ] Test de Carga de Datos: PASS
- [ ] Test de Formateo: PASS

## 🚀 Ejecutar el Bot

### 1. Iniciar el Bot
```bash
python3 crazyones-bot.py
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
```

- [ ] Bot inicia sin errores
- [ ] Mensaje "✓ Bot is running and polling for updates" aparece
- [ ] No hay mensajes de error en la consola

### 2. Probar en Telegram

1. Abrir Telegram (app móvil o desktop)
2. Buscar el bot por su nombre
3. Iniciar conversación
4. Enviar: `/start`

**Resultado Esperado:**
```
🍎 ¡Bienvenido al Bot de Actualizaciones de Apple!

Aquí están las 10 actualizaciones más recientes de Apple para Chile:

1. 2024-12-19 - iOS 17.2.1 - iPhone XS y posterior
2. 2024-12-11 - iOS 17.2 - iPhone XS y posterior
...
```

- [ ] Bot responde al comando `/start`
- [ ] Bot muestra mensaje de bienvenida
- [ ] Bot muestra 10 actualizaciones
- [ ] Las actualizaciones tienen formato: fecha - nombre - target
- [ ] Los nombres son enlaces clickeables

## ❌ Solución de Problemas

### Bot no responde en Telegram

**Verificar:**
1. Bot está corriendo (ver logs en consola)
2. Token es correcto
3. Bot no está bloqueado por el usuario
4. Conexión a internet funciona

**Reintentar:**
```bash
# Detener bot: Ctrl+C
# Reiniciar bot:
python3 crazyones-bot.py
```

### Error: "Language URLs file not found"

**Solución:**
```bash
# Generar datos primero
python3 crazyones.py --url https://support.apple.com/es-cl/100100
# Luego ejecutar bot
python3 crazyones-bot.py
```

### Error: "No module named 'telegram'"

**Solución:**
```bash
pip install -r requirements.txt
```

### Bot muestra actualizaciones vacías

**Verificar:**
```bash
# Ver contenido del archivo
cat data/updates/es-cl.json
```

Si está vacío, regenerar datos:
```bash
python3 crazyones.py --url https://support.apple.com/es-cl/100100
```

## 📊 Estado Final

Una vez completada la verificación:

- [ ] ✅ Todos los pre-requisitos cumplidos
- [ ] ✅ Tests pasados
- [ ] ✅ Bot ejecutándose correctamente
- [ ] ✅ Bot responde en Telegram
- [ ] ✅ Actualizaciones se muestran correctamente

## 📝 Notas

- Esta es una versión de **prueba de concepto**
- El idioma está **fijo a es-cl** (Chile)
- **No hay selección de idioma** en esta versión
- El bot muestra automáticamente las actualizaciones al enviar `/start`

## 🎯 Siguiente Paso

Una vez que confirmes que todo funciona:

1. Notificar que el bot responde correctamente
2. Discutir próximas funcionalidades:
   - Selección de idioma
   - Sistema de suscripciones
   - Notificaciones automáticas
   - Integración con systemd

---

**¿Todo funcionando?** 🎉

Si todos los checks están marcados, ¡el bot está listo para usar!

**¿Problemas?** 🔧

Revisa la sección de "Solución de Problemas" o consulta `BOT_STANDALONE.md` para más detalles.
