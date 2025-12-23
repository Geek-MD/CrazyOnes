# 🤖 Cómo Usar el Bot de Telegram - Guía Simplificada

## 🎯 Objetivo

Tienes un bot de Telegram que muestra automáticamente las 10 actualizaciones más recientes de Apple para Chile cuando un usuario envía `/start`.

## 📦 Lo que se Implementó

1. **Bot standalone** (`crazyones-bot.py`) que corre independientemente
2. **Lectura automática** del token desde `config.json`
3. **Respuesta automática** con actualizaciones de es-cl (Chile)
4. **Sin selección de idioma** - versión simplificada para pruebas

## 🚀 Pasos para Ejecutar

### 1️⃣ Generar Datos (Solo Primera Vez)

El bot necesita datos. Genera los archivos JSON ejecutando:

```bash
python3 crazyones.py --url https://support.apple.com/es-cl/100100
```

Esto descarga las actualizaciones de Apple y las guarda en `data/`

**Tiempo estimado:** 1-2 minutos

### 2️⃣ Probar que Todo Funciona

```bash
python3 test-bot.py
```

Si ves `✓ Todos los tests pasaron!`, continúa al siguiente paso.

### 3️⃣ Ejecutar el Bot

```bash
python3 crazyones-bot.py
```

Deberías ver:
```
INFO - ✓ Bot is running and polling for updates
```

### 4️⃣ Probar en Telegram

1. Abre Telegram
2. Busca tu bot
3. Envía: `/start`
4. El bot responderá con las 10 actualizaciones más recientes

## 📱 Ejemplo de Uso

**Usuario envía:**
```
/start
```

**Bot responde:**
```
🍎 ¡Bienvenido al Bot de Actualizaciones de Apple!

Aquí están las 10 actualizaciones más recientes de Apple para Chile:

1. 2024-12-19 - iOS 17.2.1 - iPhone XS y posterior
2. 2024-12-11 - iOS 17.2 - iPhone XS y posterior
3. 2024-12-11 - macOS Sonoma 14.2 - Mac
...
```

## 🛑 Detener el Bot

Presiona `Ctrl+C` en la terminal donde está corriendo.

## 🔄 Actualizar Datos

Para obtener actualizaciones más recientes:

```bash
# 1. Detener bot (Ctrl+C)
# 2. Regenerar datos
python3 crazyones.py --url https://support.apple.com/es-cl/100100
# 3. Reiniciar bot
python3 crazyones-bot.py
```

## ⚠️ Notas Importantes

- **Token:** Se lee automáticamente desde `config.json`
- **Idioma:** Fijo a es-cl (Chile) para esta versión de prueba
- **Sin selección:** El bot muestra las actualizaciones directamente, sin preguntar idioma
- **Datos:** El bot lee archivos JSON generados por `crazyones.py`

## 📚 Documentación Adicional

- `VERIFICACION.md` - Lista de verificación completa
- `QUICKSTART.md` - Guía de inicio rápido
- `BOT_STANDALONE.md` - Documentación detallada
- `RESUMEN_BOT.md` - Resumen técnico

## 🐛 Problemas Comunes

### El bot no responde

**Solución:**
1. Verifica que el bot esté corriendo (`✓ Bot is running...`)
2. Verifica el token en `config.json`
3. Reinicia el bot

### No hay actualizaciones

**Solución:**
```bash
python3 crazyones.py --url https://support.apple.com/es-cl/100100
```

### Error de módulos

**Solución:**
```bash
pip install -r requirements.txt
```

## ✅ Resumen Rápido

```bash
# Instalación
pip install -r requirements.txt

# Generar datos
python3 crazyones.py --url https://support.apple.com/es-cl/100100

# Ejecutar bot
python3 crazyones-bot.py

# Usar en Telegram
/start
```

## 🎉 ¡Listo!

Si seguiste estos pasos, tu bot debería estar funcionando correctamente.

**¿Dudas?** Consulta `VERIFICACION.md` para una lista de verificación detallada.

**¿Todo OK?** Cuando esté funcionando, podemos agregar más funcionalidades:
- Selección de idioma
- Suscripciones
- Notificaciones automáticas
- Integración con systemd
