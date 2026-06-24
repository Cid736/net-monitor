import sqlite3
from pathlib import Path

DB = Path(__file__).parent / "monitor.db"


def conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c


def init():
    with conn() as c:
        c.executescript("""
            CREATE TABLE IF NOT EXISTS targets (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                name    TEXT NOT NULL,
                type    TEXT NOT NULL,      -- ping | port | http
                host    TEXT NOT NULL,
                port    INTEGER,
                url     TEXT,
                status  TEXT DEFAULT 'unknown',
                added   TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS history (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                target_id INTEGER REFERENCES targets(id),
                status    TEXT NOT NULL,    -- up | down
                latency   REAL,
                http_code INTEGER,
                checked   TEXT DEFAULT (datetime('now'))
            );
        """)


def add_target(name, check_type, host, port=None, url=None):
    with conn() as c:
        c.execute(
            "INSERT INTO targets (name, type, host, port, url) VALUES (?,?,?,?,?)",
            (name, check_type, host, port, url),
        )


def get_targets():
    with conn() as c:
        return c.execute("SELECT * FROM targets ORDER BY id").fetchall()


def remove_target(target_id):
    with conn() as c:
        c.execute("DELETE FROM history WHERE target_id=?", (target_id,))
        c.execute("DELETE FROM targets WHERE id=?", (target_id,))


def record(target_id, status, latency=None, http_code=None):
    with conn() as c:
        c.execute(
            "INSERT INTO history (target_id, status, latency, http_code) VALUES (?,?,?,?)",
            (target_id, status, latency, http_code),
        )
        c.execute("UPDATE targets SET status=? WHERE id=?", (status, target_id))


def get_history(target_id=None, limit=20):
    with conn() as c:
        if target_id:
            return c.execute(
                "SELECT h.*, t.name FROM history h JOIN targets t ON h.target_id=t.id "
                "WHERE h.target_id=? ORDER BY h.id DESC LIMIT ?",
                (target_id, limit),
            ).fetchall()
        return c.execute(
            "SELECT h.*, t.name FROM history h JOIN targets t ON h.target_id=t.id "
            "ORDER BY h.id DESC LIMIT ?",
            (limit,),
        ).fetchall()


def uptime_pct(target_id, last=100):
    with conn() as c:
        rows = c.execute(
            "SELECT status FROM history WHERE target_id=? ORDER BY id DESC LIMIT ?",
            (target_id, last),
        ).fetchall()
    if not rows:
        return None
    up = sum(1 for r in rows if r["status"] == "up")
    return round(up / len(rows) * 100, 1)
