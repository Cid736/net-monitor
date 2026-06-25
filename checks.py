import socket
import subprocess
import platform
import requests
import time
import ipaddress
import re
from urllib.parse import urlparse

TIMEOUT = 5

_HOSTNAME_RE = re.compile(
    r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?'
    r'(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
)


def _valid_host(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        pass
    return bool(_HOSTNAME_RE.match(host)) and len(host) <= 253


def _safe_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme in ('http', 'https') and bool(parsed.hostname)
    except Exception:
        return False


def ping(host: str) -> tuple[bool, float]:
    if not _valid_host(host):
        return False, 0.0
    is_windows = platform.system() == "Windows"
    flag = "-n" if is_windows else "-c"
    timeout_args = ["-w", "1000"] if is_windows else ["-W", "1"]
    cmd = ["ping", flag, "1"] + timeout_args + [host]
    start = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=TIMEOUT)
        ok = result.returncode == 0
    except Exception:
        ok = False
    return ok, round((time.time() - start) * 1000, 1)


def port(host: str, p: int) -> tuple[bool, float]:
    start = time.time()
    try:
        with socket.create_connection((host, p), timeout=TIMEOUT):
            ok = True
    except Exception:
        ok = False
    return ok, round((time.time() - start) * 1000, 1)


def http(url: str) -> tuple[bool, float, int]:
    if not _safe_url(url):
        return False, 0.0, 0
    start = time.time()
    try:
        r = requests.get(url, timeout=TIMEOUT, allow_redirects=True)
        ok = r.status_code < 500
        code = r.status_code
    except Exception:
        ok, code = False, 0
    return ok, round((time.time() - start) * 1000, 1), code
