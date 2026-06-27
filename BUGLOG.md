# Bug Log — net-monitor

## 2026-06-25 — Revisión 1

### [HIGH] Flag de timeout incorrecto en ping en Windows
- **Fix:** Corregido `-W` → `-w` en Windows.

### [HIGH] Sin validación del host antes de pasarlo a subprocess
- **Fix:** Añadida `_valid_host()`.

### [HIGH] Endpoints `/control/*` sin autenticación
- **Fix:** Añadida `_check_control()` con token o restricción a localhost.

### [MEDIUM] URL en checks HTTP sin validar esquema
- **Fix:** Añadida `_safe_url()`.

---

## 2026-06-25 — Revisión 2

### [LOW] CSRF en endpoints `/control/*` via bypass de localhost
- **Archivo:** `web.py`
- **Fix:** Eliminado el bypass de localhost. `CONTROL_TOKEN` es ahora obligatorio para los endpoints de control; si no está configurado, devuelve 403.

---

## 2026-06-28 — Revisión 3

### [HIGH] Botones Start/Stop/Restart del dashboard siempre devuelven 403
- **Archivo:** `web.py`
- **Descripción:** `_check_control()` verificaba `request.form.get('token')`, pero el HTML del dashboard nunca incluía ese campo en los formularios, haciendo los controles completamente inoperables.
- **Fix:** Sustituido el mecanismo de token-en-formulario por sesiones Flask firmadas. Se añade `/login` (GET/POST) y `/logout`. El usuario se autentica una vez con el `CONTROL_TOKEN`; la sesión firmada por `FLASK_SECRET_KEY` se usa para las llamadas posteriores. El índice redirige a `/login` si no hay sesión activa.

### [MEDIA] SSRF via redirect en checks HTTP (`allow_redirects=True`)
- **Archivo:** `checks.py`, línea 92
- **Descripción:** El check HTTP seguía redirects. Un servidor externo malicioso podía redirigir a `http://169.254.169.254/` u otras IPs privadas, saltándose la validación de `_safe_url()` hecha sobre la URL original.
- **Fix:** `allow_redirects=False`. El check ahora valida solo la URL configurada; los redirects se tratan como respuesta válida (código 3xx).

### [MEDIA] `port()` no validaba el host ni bloqueaba IPs privadas
- **Archivo:** `checks.py`, línea 77
- **Descripción:** El check TCP no llamaba a `_valid_host()` ni resolvía el hostname para comprobar si apuntaba a rangos privados, a diferencia de `http()`.
- **Fix:** Añadida validación de host, rango de puerto (1–65535) y resolución DNS con comprobación de rango privado antes del `create_connection`.

### [MEDIA] Sin validación de host/URL al añadir un objetivo via CLI
- **Archivo:** `main.py`, función `cmd_add`
- **Descripción:** Un operador podía insertar en la BD un host privado o URL interna que luego sería chequeada en cada ciclo, incluso aunque los checks individuales la bloqueen. La validación ahora ocurre antes de persistir.
- **Fix:** Llamada a `_valid_host()` / `_safe_url()` en `cmd_add`; `sys.exit(1)` si no pasa.

### [BAJA] Errores de Telegram silenciados sin traza
- **Archivo:** `notifier.py`
- **Descripción:** `except Exception: pass` ocultaba fallos de red o errores de la API de Telegram.
- **Fix:** Se usan `logging.warning()` para registrar el código de estado y la excepción.

### [BAJA] `/api/status` era POST en lugar de GET
- **Archivo:** `web.py`
- **Fix:** Cambiado a `methods=["GET"]`.
