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

Automated security reviews are powered by [Claude](https://claude.ai) (Anthropic AI) and run on every significant change to detect vulnerabilities, insecure patterns and dependency risks. Findings are tracked in [`BUGLOG.md`](BUGLOG.md).

**Last review:** 2026-06-25 — 4 issues found (2 high, 1 medium, 1 low) — all patched. Set CONTROL_TOKEN in .env to protect the dashboard.

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

Las revisiones de seguridad automatizadas utilizan [Claude](https://claude.ai) (Anthropic AI) y se ejecutan en cada cambio significativo para detectar vulnerabilidades, patrones inseguros y riesgos en dependencias. Los hallazgos se registran en [`BUGLOG.md`](BUGLOG.md).

**Última revisión:** 2026-06-25 — 4 vulnerabilidades encontradas (2 altas, 1 media, 1 baja) — todas parcheadas. Configurar CONTROL_TOKEN en .env para proteger el panel.

¿Encontraste una vulnerabilidad? Abre un issue o contacta directamente.
## Licencia

MIT
