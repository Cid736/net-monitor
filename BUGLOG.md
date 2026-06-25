# Bug Log — net-monitor

## 2026-06-25

### [HIGH] Flag de timeout incorrecto en ping en Windows
- **Archivo:** `checks.py`
- **Fix:** En Windows el flag es `-w` (minúscula, milisegundos); en Linux `-W` (mayúscula, segundos). Corregida la construcción del comando.

### [HIGH] Sin validación del host antes de pasarlo a ping/subprocess
- **Archivo:** `checks.py`
- **Fix:** Añadida función `_valid_host()` que valida que el host sea una IP válida o un hostname conforme a RFC 1123 antes de pasarlo al subprocess.

### [HIGH] Endpoints `/control/*` sin autenticación
- **Archivo:** `web.py`
- **Fix:** Añadida función `_check_control()` que restringe los endpoints de control a localhost (127.0.0.1/::1) si no hay `CONTROL_TOKEN` configurado, o verifica el token en el cuerpo del formulario si está configurado.

### [MEDIUM] SSRF: URL en checks HTTP sin validar esquema
- **Archivo:** `checks.py`
- **Fix:** Añadida función `_safe_url()` que valida que la URL tenga esquema `http` o `https` y hostname no vacío antes de realizar la petición.
