import socket
import subprocess
import platform
import requests
import time

TIMEOUT = 5


def ping(host: str) -> tuple[bool, float]:
    flag = "-n" if platform.system() == "Windows" else "-c"
    cmd = ["ping", flag, "1", "-W", "1000" if platform.system() == "Windows" else "1", host]
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
    start = time.time()
    try:
        r = requests.get(url, timeout=TIMEOUT, allow_redirects=True)
        ok = r.status_code < 500
        code = r.status_code
    except Exception:
        ok, code = False, 0
    return ok, round((time.time() - start) * 1000, 1), code
