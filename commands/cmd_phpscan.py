# cmd_phpscan.py
# Escanea una URL buscando paneles admin, endpoints PHP sensibles y extrae datos
# Uso: phpscan <url> [-t <threads>] [-o <archivo>]

import os
import re
import json
import threading
from queue import Queue
from urllib.parse import urljoin, urlparse
from colorama import Fore

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print(Fore.RED + "[!] Ejecuta: pip install requests beautifulsoup4")
    exit(1)

COMMAND_NAME = "phpscan"
DESCRIPTION  = "Busca paneles admin, endpoints PHP sensibles y extrae datos expuestos"
USAGE        = "phpscan <url> [-t <threads>] [-o <archivo>]"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# ── Wordlist integrada ────────────────────────────────────────

PATHS = [
    # Paneles admin
    "admin/", "admin/index.php", "admin/login.php", "admin/panel.php",
    "administrator/", "administrator/index.php", "administrator/login.php",
    "adminpanel/", "adminpanel/index.php", "backend/", "backend/login.php",
    "panel/", "panel/index.php", "cpanel/", "controlpanel/", "manage/",
    "management/", "webadmin/", "wp-admin/", "wp-login.php",
    "phpmyadmin/", "phpmyadmin/index.php", "pma/", "mysql/", "db/",
    "dbadmin/", "myadmin/", "sqlmanager/",

    # Endpoints PHP sensibles
    "php/", "api/", "api/index.php", "api/v1/", "api/v2/",
    "ajax/", "ajax/index.php", "php/ajax.php",
    "php/phpAjaxEmpleados.php", "php/phpAjax.php",
    "php/empleados.php", "php/usuarios.php", "php/users.php",
    "php/datos.php", "php/data.php", "php/api.php",
    "php/config.php", "php/database.php", "php/db.php",
    "php/login.php", "php/auth.php", "php/register.php",
    "php/upload.php", "php/file.php", "php/files.php",
    "includes/", "includes/config.php", "includes/db.php",
    "includes/database.php", "includes/functions.php",
    "config/", "config/config.php", "config/database.php",
    "config/settings.php", "config/app.php", "conf/",
    "lib/", "libs/", "library/", "libraries/",
    "src/", "app/", "application/", "core/",
    "system/", "modules/", "module/",

    # Archivos de info / debug
    "info.php", "phpinfo.php", "test.php", "debug.php",
    "status.php", "server-status", "server-info",
    ".env", ".env.local", ".env.production",
    "config.php", "configuration.php", "settings.php",
    "web.config", "app.config",

    # Backup / logs expuestos
    "backup/", "backups/", "bak/", "old/", "temp/", "tmp/",
    "log/", "logs/", "error.log", "access.log", "debug.log",
    "dump.sql", "backup.sql", "database.sql", "db.sql",
    "backup.zip", "backup.tar.gz", "www.zip", "site.zip",

    # Upload / archivos
    "upload/", "uploads/", "files/", "images/", "img/",
    "media/", "static/", "assets/",

    # Git / svn expuesto
    ".git/HEAD", ".git/config", ".svn/entries",
    ".gitignore", "README.md", "composer.json",
    "package.json", "Makefile", "Dockerfile",
]

# Params comunes para probar extracción de datos
AJAX_PARAMS = [
    {"action": "get_users"},
    {"action": "getUsers"},
    {"action": "list"},
    {"action": "getAll"},
    {"action": "fetch"},
    {"action": "load"},
    {"op": "list"},
    {"op": "get"},
    {"cmd": "list"},
    {"type": "users"},
    {"type": "empleados"},
    {"method": "get"},
]

# ── Entry point ───────────────────────────────────────────────

def run(args: list):
    if not args or args[0] in ("-h", "--help"):
        _show_help()
        return

    url     = None
    threads = 10
    output  = None

    i = 0
    while i < len(args):
        if args[i] == "-t" and i + 1 < len(args):
            try:
                threads = int(args[i + 1])
            except ValueError:
                print(Fore.RED + "[!] Valor inválido para -t.")
                return
            i += 2
        elif args[i] == "-o" and i + 1 < len(args):
            output = args[i + 1]
            i += 2
        else:
            url = args[i]
            i += 1

    if not url:
        print(Fore.RED + "[!] Debes especificar una URL.")
        _show_help()
        return

    if not url.startswith("http"):
        url = "http://" + url
    if not url.endswith("/"):
        url += "/"

    print(Fore.RED + f"\n  [phpscan] " + Fore.WHITE + f"Target  : {url}")
    print(Fore.RED + f"  [phpscan] " + Fore.WHITE + f"Threads : {threads}")
    print(Fore.RED + f"  [phpscan] " + Fore.WHITE + f"Paths   : {len(PATHS)}\n")

    encontrados = _escanear(url, threads)

    if encontrados:
        _extraer_datos(url, encontrados)

    if output and encontrados:
        _exportar(encontrados, output)

    _resumen(encontrados)

# ── Scanner ───────────────────────────────────────────────────

def _escanear(base_url: str, num_threads: int) -> list:
    encontrados = []
    lock = threading.Lock()
    queue = Queue()

    for path in PATHS:
        queue.put(path)

    def worker():
        session = requests.Session()
        session.headers.update(HEADERS)
        while not queue.empty():
            try:
                path = queue.get_nowait()
            except Exception:
                break

            full_url = urljoin(base_url, path)
            try:
                resp = session.get(full_url, timeout=6, allow_redirects=True)
                code = resp.status_code
                size = len(resp.content)

                if code in (200, 301, 302, 403) and size > 0:
                    tipo = _clasificar(path, resp)
                    with lock:
                        encontrados.append({
                            "url":    full_url,
                            "code":   code,
                            "size":   size,
                            "type":   tipo,
                            "resp":   resp,
                        })
                        _imprimir_hallazgo(full_url, code, size, tipo)
            except requests.exceptions.ConnectionError:
                pass
            except requests.exceptions.Timeout:
                pass
            except Exception:
                pass
            finally:
                queue.task_done()

    hilos = []
    for _ in range(num_threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        hilos.append(t)
    for t in hilos:
        t.join()

    return encontrados

def _clasificar(path: str, resp) -> str:
    ct = resp.headers.get("Content-Type", "").lower()
    if any(x in path for x in ["admin", "panel", "login", "wp-admin", "phpmyadmin", "pma"]):
        return "PANEL"
    if any(x in path for x in ["ajax", "api", "php/"]):
        return "ENDPOINT"
    if any(x in path for x in [".env", "config", "database", "settings"]):
        return "CONFIG"
    if any(x in path for x in [".git", ".svn", "README", "composer", "package.json"]):
        return "EXPOSED"
    if any(x in path for x in ["backup", "dump", ".sql", ".zip", "log"]):
        return "BACKUP"
    if "phpinfo" in path or ("application/json" in ct and "php" in path):
        return "INFO"
    return "FILE"

def _imprimir_hallazgo(url: str, code: int, size: int, tipo: str):
    color_code = Fore.GREEN if code == 200 else Fore.YELLOW if code in (301, 302) else Fore.RED
    color_tipo = {
        "PANEL":    Fore.RED,
        "ENDPOINT": Fore.YELLOW,
        "CONFIG":   Fore.RED,
        "EXPOSED":  Fore.YELLOW,
        "BACKUP":   Fore.RED,
        "INFO":     Fore.YELLOW,
        "FILE":     Fore.WHITE,
    }.get(tipo, Fore.WHITE)

    print(
        color_tipo  + f"  [{tipo:<8}] " +
        color_code  + f"[{code}] " +
        Fore.WHITE  + f"{url} " +
        Fore.RED    + f"({_human_size(size)})"
    )

# ── Extracción de datos ───────────────────────────────────────

def _extraer_datos(base_url: str, encontrados: list):
    endpoints = [e for e in encontrados if e["type"] in ("ENDPOINT", "FILE") and e["code"] == 200]
    if not endpoints:
        return

    print(Fore.RED + "\n  ╔══ Extracción de datos ═══════════════")

    session = requests.Session()
    session.headers.update(HEADERS)

    for item in endpoints:
        url  = item["url"]
        resp = item["resp"]
        ct   = resp.headers.get("Content-Type", "").lower()

        # Si ya responde JSON directo
        if "json" in ct or _es_json(resp.text):
            print(Fore.RED + f"  ║ " + Fore.GREEN + f"[JSON] " + Fore.WHITE + url)
            _mostrar_json(resp.text)
            continue

        # Intentar con parámetros AJAX comunes (GET)
        for params in AJAX_PARAMS:
            try:
                r = session.get(url, params=params, timeout=6)
                if r.status_code == 200 and _es_json(r.text):
                    param_str = "&".join(f"{k}={v}" for k, v in params.items())
                    print(Fore.RED + f"  ║ " + Fore.YELLOW + f"[AJAX GET] " +
                          Fore.WHITE + f"{url}?{param_str}")
                    _mostrar_json(r.text)
                    break
            except Exception:
                pass

        # Intentar con POST
        for params in AJAX_PARAMS:
            try:
                r = session.post(url, data=params, timeout=6)
                if r.status_code == 200 and _es_json(r.text):
                    param_str = "&".join(f"{k}={v}" for k, v in params.items())
                    print(Fore.RED + f"  ║ " + Fore.YELLOW + f"[AJAX POST] " +
                          Fore.WHITE + f"{url} data={param_str}")
                    _mostrar_json(r.text)
                    break
            except Exception:
                pass

        # Extraer emails/usuarios del HTML
        if "html" in ct:
            _extraer_html(resp.text, url)

    print(Fore.RED + "  ╚═══════════════════════════════════════\n")

def _es_json(texto: str) -> bool:
    texto = texto.strip()
    if not texto or texto[0] not in ("{", "["):
        return False
    try:
        json.loads(texto)
        return True
    except Exception:
        return False

def _mostrar_json(texto: str):
    try:
        data = json.loads(texto)
        # Mostrar primeros 5 registros si es lista
        if isinstance(data, list):
            print(Fore.WHITE + f"     → {len(data)} registros encontrados")
            for item in data[:5]:
                print(Fore.YELLOW + f"     · {json.dumps(item, ensure_ascii=False)}")
            if len(data) > 5:
                print(Fore.WHITE + f"     ... y {len(data) - 5} más")
        elif isinstance(data, dict):
            for k, v in list(data.items())[:10]:
                print(Fore.YELLOW + f"     · {k}: {v}")
    except Exception:
        print(Fore.WHITE + f"     → {texto[:200]}")

def _extraer_html(html: str, url: str):
    emails = set(re.findall(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", html))
    users  = set(re.findall(r'"(?:user|usuario|username|email|correo|nombre)":\s*"([^"]+)"', html, re.I))
    tokens = set(re.findall(r'(?:token|api_key|apikey|secret|password|passwd)\s*[=:]\s*["\']([^"\']{6,})["\']', html, re.I))

    if emails:
        print(Fore.RED + f"  ║ " + Fore.CYAN + f"[EMAILS] " + Fore.WHITE + url)
        for e in list(emails)[:10]:
            print(Fore.YELLOW + f"     · {e}")
    if users:
        print(Fore.RED + f"  ║ " + Fore.CYAN + f"[USERS] " + Fore.WHITE + url)
        for u in list(users)[:10]:
            print(Fore.YELLOW + f"     · {u}")
    if tokens:
        print(Fore.RED + f"  ║ " + Fore.RED + f"[TOKENS/KEYS] " + Fore.WHITE + url)
        for t in list(tokens)[:5]:
            print(Fore.RED + f"     · {t}")

# ── Export ────────────────────────────────────────────────────

def _exportar(encontrados: list, archivo: str):
    try:
        with open(archivo, "w", encoding="utf-8") as f:
            for item in encontrados:
                f.write(f"[{item['type']}] [{item['code']}] {item['url']} ({_human_size(item['size'])})\n")
        print(Fore.GREEN + f"  [+] Guardado en: {archivo}\n")
    except Exception as e:
        print(Fore.RED + f"  [!] Error al guardar: {e}\n")

# ── Resumen ───────────────────────────────────────────────────

def _resumen(encontrados: list):
    if not encontrados:
        print(Fore.YELLOW + "\n  [~] No se encontró nada.\n")
        return

    tipos = {}
    for item in encontrados:
        tipos[item["type"]] = tipos.get(item["type"], 0) + 1

    print(Fore.RED + "\n  ╔══ Resumen ════════════════════════════")
    print(Fore.RED + "  ║ " + Fore.WHITE + f"Total encontrados : {len(encontrados)}")
    for tipo, count in sorted(tipos.items(), key=lambda x: -x[1]):
        print(Fore.RED + "  ║ " + Fore.YELLOW + f"  {tipo:<10} : {count}")
    print(Fore.RED + "  ╚═══════════════════════════════════════\n")

# ── Helpers ───────────────────────────────────────────────────

def _human_size(n: int) -> str:
    for u in ["B", "KB", "MB"]:
        if n < 1024:
            return f"{n:.0f}{u}"
        n /= 1024
    return f"{n:.1f}GB"

def _show_help():
    print(Fore.RED   + "\n  phpscan — " + Fore.WHITE + DESCRIPTION)
    print(Fore.WHITE + f"\n  Uso: {USAGE}\n")
    print(Fore.YELLOW + "  Opciones:")
    print(Fore.WHITE  + "    -t <threads>    Hilos simultáneos (default: 10)")
    print(Fore.WHITE  + "    -o <archivo>    Exportar resultados a .txt\n")
    print(Fore.YELLOW + "  Ejemplos:")
    print(Fore.WHITE  + "    phpscan http://target.com")
    print(Fore.WHITE  + "    phpscan target.com -t 20")
    print(Fore.WHITE  + "    phpscan target.com -t 15 -o resultados.txt\n")