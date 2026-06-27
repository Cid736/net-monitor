<p align="center">
  <a href="#english">🇬🇧 English</a> &nbsp;·&nbsp; <a href="#español">🇪🇸 Español</a>
</p>

---

<a name="english"></a>

# net-monitor

Network availability monitor — checks hosts (ICMP ping), TCP ports and HTTP/HTTPS endpoints. Logs uptime history in SQLite and sends Telegram alerts when a target goes down or comes back up.

## Stack
Python · Flask · socket · requests · SQLite · Telegram Bot API

## Demo

```
$ python main.py check

Checking 4 target(s)...

  [UP]     Router                         192.168.1.1                              2.1ms
  [UP]     Main server (SSH)              192.168.1.10:22                          3.4ms
  [DOWN]   Web app                        https://myapp.example.com                timeout
  [UP]     DNS                            8.8.8.8                                  12.3ms

$ python main.py list

ID   Name                      Type   Target                                   Status   Uptime
----------------------------------------------------------------------------------------------------
1    Router                    ping   192.168.1.1                              up       100.0%
2    Main server (SSH)         port   192.168.1.10:22                          up       98.5%
3    Web app                   http   https://myapp.example.com                down     91.2%
4    DNS                       ping   8.8.8.8                                  up       100.0%
```

When status changes, a Telegram message is sent:
```
🔴 DOWN — Web app
Type: http
Target: https://myapp.example.com
```

## Web dashboard

```bash
python web.py
# Open http://localhost:8080
```

Dark dashboard with status cards (UP/DOWN), uptime %, latency and recent check history. Auto-refreshes every 30 seconds. Background checker runs every 60s.

## CLI

```bash
python main.py check    # one-shot check
python main.py list     # status + uptime table
python main.py run      # daemon mode
```

## Setup

```bash
git clone https://github.com/Cid736/net-monitor.git
cd net-monitor
pip install -r requirements.txt
cp .env.example .env
# Add your Telegram bot token and chat ID (optional — alerts won't fire without them)
```

## Usage

```bash
# Add targets
python main.py add --name "Router"          --type ping --host 192.168.1.1
python main.py add --name "SSH server"      --type port --host 192.168.1.10 --port 22
python main.py add --name "Web app"         --type http --url https://myapp.example.com
python main.py add --name "DNS"             --type ping --host 8.8.8.8

# One-shot check
python main.py check

# List all targets with status and uptime %
python main.py list

# Check history (last 20 entries)
python main.py history
python main.py history --id 3 --limit 50

# Daemon mode — checks every 5 minutes, alerts on change
python main.py run --interval 5

# Remove a target
python main.py remove 3
```

## Telegram setup

1. Create a bot with [@BotFather](https://t.me/BotFather) — get `TELEGRAM_TOKEN`
2. Message your bot, then visit `https://api.telegram.org/bot<TOKEN>/getUpdates` to get `TELEGRAM_CHAT_ID`
3. Add both to `.env`

## How it works

| Check type | Method | What it detects |
|---|---|---|
| `ping` | ICMP via `ping` subprocess | Host reachability |
| `port` | TCP `socket.create_connection` | Service availability on a specific port |
| `http` | HTTP GET via `requests` | Web app / API availability (HTTP 5xx = down) |

All results are stored in `monitor.db` (SQLite). Alerts only fire on **status change** — no spam if something stays down.

## Changelog

**v0.1.1** — 2026-06-24
- Fix: check errors are now logged instead of silently discarded
- Fix: replace em-dash in CLI list output that caused encoding crash on Windows (CP1252)

**v0.1.0** — 2026-06-23
- Initial release: ping, port and HTTP checks, SQLite history, Telegram alerts

## Security

Automated security reviews are powered by [Claude](https://claude.ai) (Anthropic AI) and run on every significant change. Findings are tracked in [`BUGLOG.md`](BUGLOG.md).

**Last review:** 2026-06-28 — 5 new issues found (1 high, 2 medium, 2 low) — all patched.

### Model

| Control | Implementation |
|---|---|
| Command injection (ping) | `_valid_host()` — strict regex + `ipaddress`; no shell=True |
| SSRF (HTTP checks) | `_safe_url()` resolves DNS and blocks all RFC-1918/loopback/link-local ranges; redirects disabled (`allow_redirects=False`) |
| SSRF (TCP port checks) | `_valid_host()` + DNS resolution with private-IP check before `create_connection` |
| Host validation on add | `cmd_add` calls `_valid_host()` / `_safe_url()` before persisting to DB |
| SQL injection | All queries use parameterized statements (`?` placeholders) |
| Dashboard authentication | Session-based login at `/login`; `CONTROL_TOKEN` (required) authenticates the session; `FLASK_SECRET_KEY` signs cookies |
| Secret management | Credentials via `.env` / environment variables only; `.env` is git-ignored |
| Security headers | `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy` on every response |

### Required `.env` variables

```
CONTROL_TOKEN=<random 32+ char string>    # protects the web dashboard
FLASK_SECRET_KEY=<random 32+ char string> # signs Flask session cookies
TELEGRAM_TOKEN=<bot token>               # optional — alerts won't fire without it
TELEGRAM_CHAT_ID=<chat id>               # optional
```

Found a vulnerability? Open an issue or contact directly.

---

<a name="español"></a>

# net-monitor

Monitor de disponibilidad de red — comprueba hosts (ping ICMP), puertos TCP y endpoints HTTP/HTTPS. Registra el historial de uptime en SQLite y envía alertas por Telegram cuando un objetivo cae o se recupera.

## Stack
Python · Flask · socket · requests · SQLite · Telegram Bot API

## Instalación

```bash
git clone https://github.com/Cid736/net-monitor.git
cd net-monitor
pip install -r requirements.txt
cp .env.example .env
# Añade tu token de Telegram y chat ID (opcional — sin ellos las alertas no se envían)
```

## Uso

```bash
# Añadir objetivos
python main.py add --name "Router"        --type ping --host 192.168.1.1
python main.py add --name "Servidor SSH"  --type port --host 192.168.1.10 --port 22
python main.py add --name "Web app"       --type http --url https://myapp.example.com

# Comprobación puntual
python main.py check

# Listar todos los objetivos con estado y uptime %
python main.py list

# Historial de comprobaciones
python main.py history

# Modo demonio — comprueba cada 5 minutos, alerta en cambio de estado
python main.py run --interval 5
```

## Cómo funciona

| Tipo | Método | Qué detecta |
|---|---|---|
| `ping` | ICMP via subproceso `ping` | Accesibilidad del host |
| `port` | TCP `socket.create_connection` | Disponibilidad del servicio en un puerto |
| `http` | HTTP GET via `requests` | Disponibilidad de la app/API (HTTP 5xx = caído) |

Los resultados se almacenan en `monitor.db` (SQLite). Las alertas solo se disparan en **cambio de estado** — sin spam si algo sigue caído.

## Configuración de Telegram

1. Crea un bot con [@BotFather](https://t.me/BotFather) — obtén `TELEGRAM_TOKEN`
2. Escríbele al bot y visita `https://api.telegram.org/bot<TOKEN>/getUpdates` para obtener `TELEGRAM_CHAT_ID`
3. Añade ambos al `.env`

## Seguridad

Las revisiones de seguridad automatizadas utilizan [Claude](https://claude.ai) (Anthropic AI) y se ejecutan en cada cambio significativo. Los hallazgos se registran en [`BUGLOG.md`](BUGLOG.md).

**Última revisión:** 2026-06-28 — 5 nuevas vulnerabilidades encontradas (1 alta, 2 medias, 2 bajas) — todas parcheadas.

| Control | Implementación |
|---|---|
| Inyección de comandos (ping) | `_valid_host()` — regex estricta + `ipaddress`; sin `shell=True` |
| SSRF (checks HTTP) | `_safe_url()` resuelve DNS y bloquea RFC-1918/loopback/link-local; redirects desactivados |
| SSRF (checks TCP) | `_valid_host()` + resolución DNS con comprobación de IP privada antes de `create_connection` |
| Validación al añadir objetivo | `cmd_add` llama a `_valid_host()` / `_safe_url()` antes de persistir en la BD |
| Inyección SQL | Todas las queries usan sentencias parametrizadas (placeholders `?`) |
| Autenticación del dashboard | Login de sesión en `/login`; `CONTROL_TOKEN` (obligatorio) autentica la sesión; `FLASK_SECRET_KEY` firma las cookies |
| Gestión de secretos | Credenciales solo via `.env` / variables de entorno; `.env` en `.gitignore` |
| Cabeceras de seguridad | `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy` en cada respuesta |

¿Encontraste una vulnerabilidad? Abre un issue o contacta directamente.
## Licencia

MIT
