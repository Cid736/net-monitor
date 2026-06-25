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


def _is_private_ip(ip_str: str) -> bool:
    try:
        addr = ipaddress.ip_address(ip_str)
        return addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_reserved
    except ValueError:
        return False


def _safe_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https') or not parsed.hostname:
            return False
        host = parsed.hostname
        # Direct IP — block if private
        try:
            if _is_private_ip(host):
                return False
            return True  # public IP literal
        except ValueError:
            pass
        # Hostname — resolve and check every returned address
        try:
            infos = socket.getaddrinfo(host, None)
            for info in infos:
                if _is_private_ip(info[4][0]):
                    return False
        except socket.gaierror:
            pass  # resolution failure — allow; will fail at request time
        return True
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
