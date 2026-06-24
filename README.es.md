# net-monitor

Monitor de disponibilidad de red — comprueba hosts (ping ICMP), puertos TCP y endpoints HTTP/HTTPS. Guarda historial de uptime en SQLite y envía alertas por Telegram cuando un objetivo cae o vuelve a estar disponible.

## Stack
Python · Flask · socket · requests · SQLite · Telegram Bot API

## Demo

```
$ python main.py check

Comprobando 4 objetivo(s)...

  [UP]     Router                         192.168.1.1                              2.1ms
  [UP]     Servidor principal (SSH)       192.168.1.10:22                          3.4ms
  [DOWN]   App web                        https://myapp.example.com                timeout
  [UP]     DNS                            8.8.8.8                                  12.3ms

$ python main.py list

ID   Nombre                    Tipo   Objetivo                                 Estado   Uptime
----------------------------------------------------------------------------------------------------
1    Router                    ping   192.168.1.1                              up       100.0%
2    Servidor principal (SSH)  port   192.168.1.10:22                          up       98.5%
3    App web                   http   https://myapp.example.com                down     91.2%
4    DNS                       ping   8.8.8.8                                  up       100.0%
```

Cuando el estado cambia, se envía un mensaje de Telegram:
```
🔴 DOWN — App web
Type: http
Target: https://myapp.example.com
```

## Dashboard web

```bash
python web.py
# Abre http://localhost:8080
```

Dashboard oscuro con tarjetas de estado (UP/DOWN), uptime %, latencia e historial de comprobaciones recientes. Se refresca automáticamente cada 30 segundos. El checker corre en background cada 60s.

## CLI

```bash
python main.py check    # comprobación puntual
python main.py list     # tabla de estado y uptime
python main.py run      # modo demonio
```

## Instalación

```bash
git clone https://github.com/Cid736/net-monitor.git
cd net-monitor
pip install -r requirements.txt
cp .env.example .env
# Añade tu token de bot de Telegram y chat ID (opcional — las alertas no funcionan sin ellos)
```

## Uso

```bash
# Añadir objetivos
python main.py add --name "Router"              --type ping --host 192.168.1.1
python main.py add --name "Servidor SSH"        --type port --host 192.168.1.10 --port 22
python main.py add --name "App web"             --type http --url https://myapp.example.com
python main.py add --name "DNS"                 --type ping --host 8.8.8.8

# Comprobación única
python main.py check

# Listar todos los objetivos con estado y uptime %
python main.py list

# Historial de comprobaciones (últimas 20 entradas)
python main.py history
python main.py history --id 3 --limit 50

# Modo demonio — comprueba cada 5 minutos, alerta en cambio de estado
python main.py run --interval 5

# Eliminar un objetivo
python main.py remove 3
```

## Configurar Telegram

1. Crea un bot con [@BotFather](https://t.me/BotFather) — obtén `TELEGRAM_TOKEN`
2. Escribe a tu bot, luego visita `https://api.telegram.org/bot<TOKEN>/getUpdates` para obtener `TELEGRAM_CHAT_ID`
3. Añade ambos al archivo `.env`

## Cómo funciona

| Tipo de comprobación | Método | Qué detecta |
|---|---|---|
| `ping` | ICMP via subprocess `ping` | Alcanzabilidad del host |
| `port` | TCP `socket.create_connection` | Disponibilidad de un servicio en un puerto concreto |
| `http` | HTTP GET via `requests` | Disponibilidad de app web / API (HTTP 5xx = caído) |

Todos los resultados se almacenan en `monitor.db` (SQLite). Las alertas solo se disparan en **cambio de estado** — sin spam si algo sigue caído.

## Historial de versiones

**v0.1.1** — 2026-06-24
- Fix: reemplazado guion largo en la salida CLI que causaba error de encoding en Windows (CP1252)

**v0.1.0** — 2026-06-23
- Publicación inicial: comprobaciones ping, puerto y HTTP, historial SQLite, alertas Telegram
- Dashboard web con controles Iniciar/Parar/Reiniciar y banner alfa
