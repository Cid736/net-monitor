#!/usr/bin/env python3
"""
net-monitor — network availability monitor
Checks hosts (ping), TCP ports and HTTP/HTTPS endpoints.
Logs history in SQLite and sends Telegram alerts on status changes.
"""

import argparse
import time
import sys
from dotenv import load_dotenv
from db import init, add_target, get_targets, remove_target, record, get_history, uptime_pct
from checks import ping, port, http
from notifier import alert_down, alert_up

load_dotenv()


# ── helpers ──────────────────────────────────────────────────────────────────

def _target_detail(t) -> str:
    if t["type"] == "http":
        return t["url"]
    if t["type"] == "port":
        return f"{t['host']}:{t['port']}"
    return t["host"]


def run_check(t, verbose=True) -> str:
    prev = t["status"]
    name = t["name"]
    typ  = t["type"]

    if typ == "ping":
        ok, ms = ping(t["host"])
        detail = t["host"]
        code   = None
    elif typ == "port":
        ok, ms = port(t["host"], t["port"])
        detail = f"{t['host']}:{t['port']}"
        code   = None
    else:
        ok, ms, code = http(t["url"])
        detail = t["url"]

    status = "up" if ok else "down"
    record(t["id"], status, ms, code)

    symbol = "[UP]" if ok else "[DOWN]"
    lat    = f"{ms}ms" if ok else "timeout"
    extra  = f" (HTTP {code})" if code else ""
    if verbose:
        print(f"  {symbol:8} {name:30} {detail:40} {lat}{extra}")

    if prev != "unknown" and prev != status:
        if status == "down":
            alert_down(name, typ, detail)
        else:
            alert_up(name, typ, detail)

    return status


# ── commands ─────────────────────────────────────────────────────────────────

def cmd_add(args):
    if args.type == "port" and not args.port:
        print("Error: --port required for type 'port'")
        sys.exit(1)
    if args.type == "http" and not args.url:
        print("Error: --url required for type 'http'")
        sys.exit(1)
    add_target(
        name=args.name,
        check_type=args.type,
        host=args.host or "",
        port=args.port,
        url=args.url,
    )
    print(f"Added: {args.name} ({args.type})")


def cmd_remove(args):
    remove_target(args.id)
    print(f"Removed target ID {args.id}")


def cmd_list(_args):
    targets = get_targets()
    if not targets:
        print("No targets. Use: net-monitor add --help")
        return
    print(f"\n{'ID':<4} {'Name':<25} {'Type':<6} {'Target':<40} {'Status':<8} {'Uptime'}")
    print("-" * 100)
    for t in targets:
        pct = uptime_pct(t["id"])
        up  = f"{pct}%" if pct is not None else "-"
        print(f"{t['id']:<4} {t['name']:<25} {t['type']:<6} {_target_detail(t):<40} {t['status']:<8} {up}")
    print()


def cmd_check(_args):
    targets = get_targets()
    if not targets:
        print("No targets configured.")
        return
    print(f"\nChecking {len(targets)} target(s)...\n")
    for t in targets:
        run_check(t)
    print()


def cmd_history(args):
    rows = get_history(args.id, args.limit)
    if not rows:
        print("No history yet.")
        return
    print(f"\n{'Time (UTC)':<22} {'Name':<25} {'Status':<6} {'Latency':<10} {'HTTP'}")
    print("-" * 80)
    for r in rows:
        lat  = f"{r['latency']}ms" if r["latency"] else "-"
        code = str(r["http_code"]) if r["http_code"] else "-"
        print(f"{r['checked']:<22} {r['name']:<25} {r['status']:<6} {lat:<10} {code}")
    print()


def cmd_run(args):
    interval = args.interval * 60
    targets  = get_targets()
    if not targets:
        print("No targets configured.")
        return
    print(f"Running every {args.interval} min. Ctrl+C to stop.\n")
    while True:
        targets = get_targets()
        for t in targets:
            run_check(t, verbose=True)
        print(f"  -- next check in {args.interval} min --\n")
        time.sleep(interval)


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    init()

    p = argparse.ArgumentParser(
        prog="net-monitor",
        description="Network availability monitor — ping, port and HTTP checks with Telegram alerts",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # add
    a = sub.add_parser("add", help="Add a target to monitor")
    a.add_argument("--name",  required=True, help="Display name")
    a.add_argument("--type",  required=True, choices=["ping", "port", "http"])
    a.add_argument("--host",  help="Hostname or IP (ping and port checks)")
    a.add_argument("--port",  type=int, help="TCP port (port check)")
    a.add_argument("--url",   help="Full URL (http check)")

    # remove
    r = sub.add_parser("remove", help="Remove a target by ID")
    r.add_argument("id", type=int)

    # list
    sub.add_parser("list", help="List all targets and current status")

    # check
    sub.add_parser("check", help="Run one check pass now")

    # history
    h = sub.add_parser("history", help="Show check history")
    h.add_argument("--id",    type=int, help="Filter by target ID")
    h.add_argument("--limit", type=int, default=20)

    # run
    d = sub.add_parser("run", help="Run checks continuously (daemon mode)")
    d.add_argument("--interval", type=int, default=5, help="Minutes between checks (default: 5)")

    args = p.parse_args()
    {
        "add":     cmd_add,
        "remove":  cmd_remove,
        "list":    cmd_list,
        "check":   cmd_check,
        "history": cmd_history,
        "run":     cmd_run,
    }[args.cmd](args)


if __name__ == "__main__":
    main()
