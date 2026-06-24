# net-monitor

Network availability monitor — checks hosts (ICMP ping), TCP ports and HTTP/HTTPS endpoints. Logs uptime history in SQLite and sends Telegram alerts when a target goes down or comes back up.

## Stack
Python · socket · requests · SQLite · Telegram Bot API

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
