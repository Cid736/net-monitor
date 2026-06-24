from flask import Flask, render_template_string
from db import init, get_targets, get_history, uptime_pct
from checks import ping, port, http
from db import record
import threading, time, os

app = Flask(__name__)
CHECK_INTERVAL = 60  # seconds

TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8"/>
  <meta http-equiv="refresh" content="30"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>net-monitor</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Segoe UI', sans-serif; background: #0d1117; color: #c9d1d9; min-height: 100vh; }
    header { padding: 24px 32px; border-bottom: 1px solid #21262d; display: flex; align-items: center; gap: 12px; }
    header h1 { font-size: 1.2rem; font-weight: 600; color: #e6edf3; }
    header span { font-size: 0.8rem; color: #8b949e; margin-left: auto; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; padding: 24px 32px; }
    .card { background: #161b22; border: 1px solid #21262d; border-radius: 10px; padding: 20px; position: relative; }
    .card.up   { border-left: 4px solid #3fb950; }
    .card.down { border-left: 4px solid #f85149; }
    .card.unknown { border-left: 4px solid #8b949e; }
    .badge { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 0.72rem; font-weight: 600; letter-spacing: .5px; text-transform: uppercase; }
    .badge.up   { background: #1a3a1f; color: #3fb950; }
    .badge.down { background: #3a1a1a; color: #f85149; }
    .badge.unknown { background: #21262d; color: #8b949e; }
    .card h2 { font-size: 1rem; margin: 10px 0 4px; color: #e6edf3; }
    .card .target { font-size: 0.78rem; color: #8b949e; word-break: break-all; margin-bottom: 12px; }
    .meta { display: flex; justify-content: space-between; font-size: 0.75rem; color: #8b949e; border-top: 1px solid #21262d; padding-top: 10px; margin-top: 4px; }
    .meta .uptime { color: {% if up %} #3fb950 {% else %} #8b949e {% endif %}; font-weight: 600; }
    .summary { padding: 0 32px 8px; display: flex; gap: 24px; font-size: 0.85rem; color: #8b949e; }
    .summary b { color: #e6edf3; }
    table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
    th { text-align: left; padding: 8px 12px; color: #8b949e; border-bottom: 1px solid #21262d; font-weight: 500; }
    td { padding: 8px 12px; border-bottom: 1px solid #161b22; }
    .section { padding: 0 32px 32px; }
    .section h2 { font-size: 0.9rem; color: #8b949e; margin-bottom: 12px; text-transform: uppercase; letter-spacing: .5px; }
    .dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
    .dot.up   { background: #3fb950; }
    .dot.down { background: #f85149; }
    .type-badge { background: #21262d; color: #8b949e; padding: 2px 8px; border-radius: 4px; font-size: 0.72rem; }
    footer { text-align: center; padding: 16px; font-size: 0.75rem; color: #484f58; }
  </style>
</head>
<body>
<header>
  <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="#3fb950" stroke-width="2">
    <path stroke-linecap="round" stroke-linejoin="round" d="M9 3H5a2 2 0 00-2 2v4m6-6h10a2 2 0 012 2v4M9 3v18m0 0h10a2 2 0 002-2V9M9 21H5a2 2 0 01-2-2V9m0 0h18"/>
  </svg>
  <h1>net-monitor</h1>
  <span>Auto-refresh 30s &nbsp;|&nbsp; {{ now }}</span>
</header>

<div class="summary">
  <div><b>{{ total }}</b> targets</div>
  <div style="color:#3fb950"><b>{{ up_count }}</b> UP</div>
  <div style="color:#f85149"><b>{{ down_count }}</b> DOWN</div>
</div>

<div class="grid">
{% for t in targets %}
  {% set pct = uptime_pct(t['id']) %}
  <div class="card {{ t['status'] }}">
    <span class="badge {{ t['status'] }}">{{ t['status'] }}</span>
    <h2>{{ t['name'] }}</h2>
    <div class="target">
      {% if t['type'] == 'http' %}{{ t['url'] }}
      {% elif t['type'] == 'port' %}{{ t['host'] }}:{{ t['port'] }}
      {% else %}{{ t['host'] }}{% endif %}
    </div>
    <div class="meta">
      <span class="type-badge">{{ t['type'] }}</span>
      <span class="uptime">{{ pct }}% uptime</span>
    </div>
  </div>
{% endfor %}
</div>

<div class="section">
  <h2>Recent checks</h2>
  <table>
    <tr><th>Time (UTC)</th><th>Target</th><th>Status</th><th>Latency</th><th>HTTP</th></tr>
    {% for r in history %}
    <tr>
      <td>{{ r['checked'] }}</td>
      <td>{{ r['name'] }}</td>
      <td><span class="dot {{ r['status'] }}"></span>{{ r['status'] }}</td>
      <td>{{ r['latency'] }}ms</td>
      <td>{{ r['http_code'] or '-' }}</td>
    </tr>
    {% endfor %}
  </table>
</div>

<footer>net-monitor &mdash; github.com/Cid736/net-monitor</footer>
</body>
</html>"""


def run_checks():
    while True:
        targets = get_targets()
        for t in targets:
            try:
                if t["type"] == "ping":
                    ok, ms = ping(t["host"]); code = None
                elif t["type"] == "port":
                    ok, ms = port(t["host"], t["port"]); code = None
                else:
                    ok, ms, code = http(t["url"])
                record(t["id"], "up" if ok else "down", ms, code)
            except Exception:
                pass
        time.sleep(CHECK_INTERVAL)


@app.route("/")
def index():
    from datetime import datetime
    targets = get_targets()
    history = get_history(limit=30)
    up_count   = sum(1 for t in targets if t["status"] == "up")
    down_count = sum(1 for t in targets if t["status"] == "down")
    return render_template_string(
        TEMPLATE,
        targets=targets,
        history=history,
        uptime_pct=uptime_pct,
        total=len(targets),
        up_count=up_count,
        down_count=down_count,
        now=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
    )


if __name__ == "__main__":
    init()
    # Seed some targets if DB is empty
    if not get_targets():
        from db import add_target
        add_target("GitHub Web",  "http", "",           url="https://github.com")
        add_target("GitHub SSH",  "port", "github.com", port=22)
        add_target("Google DNS",  "ping", "8.8.8.8")
        add_target("Cloudflare",  "ping", "1.1.1.1")
        add_target("Google Web",  "http", "",           url="https://google.com")

    t = threading.Thread(target=run_checks, daemon=True)
    t.start()

    PORT = int(os.environ.get("PORT", 8080))
    print(f"[net-monitor] dashboard -> http://localhost:{PORT}")
    app.run(host="0.0.0.0", port=PORT)
