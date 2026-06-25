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
