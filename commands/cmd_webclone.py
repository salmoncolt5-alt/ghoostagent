import os
import re
import time
import mimetypes
from urllib.parse import urljoin, urlparse, unquote
from colorama import Fore

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print(Fore.RED + "[!] Dependencias faltantes. Ejecuta:")
    print(Fore.WHITE + "    pip install requests beautifulsoup4")
    exit(1)

COMMAND_NAME = "webclone"
DESCRIPTION  = "Clona una web completa: HTML, CSS, JS, imágenes, fuentes y más"
USAGE        = "webclone <url> [-o <carpeta>] [-d <profundidad>]"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

ASSETS_TAGS = {
    "img":    ["src", "data-src", "data-lazy"],
    "script": ["src"],
    "link":   ["href"],
    "source": ["src", "srcset"],
    "video":  ["src", "poster"],
    "audio":  ["src"],
    "input":  ["src"],
}

# ──────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────

def run(args: list):
    if not args or args[0] in ("-h", "--help"):
        _show_help()
        return

    url       = None
    output    = None
    depth     = 1

    i = 0
    while i < len(args):
        if args[i] == "-o" and i + 1 < len(args):
            output = args[i + 1]
            i += 2
        elif args[i] == "-d" and i + 1 < len(args):
            try:
                depth = int(args[i + 1])
                if depth < 1 or depth > 3:
                    print(Fore.RED + "[!] -d debe ser entre 1 y 3.")
                    return
            except ValueError:
                print(Fore.RED + "[!] Valor inválido para -d.")
                return
            i += 2
        else:
            url = args[i]
            i += 1

    if not url:
        print(Fore.RED + "[!] Debes especificar una URL.")
        _show_help()
        return

    # Asegurar esquema
    if not url.startswith("http"):
        url = "https://" + url

    dominio = urlparse(url).netloc.replace("www.", "")
    output  = output or f"clone_{dominio}"

    print(Fore.RED + "\n  [webclone] " + Fore.WHITE + f"Target   : {url}")
    print(Fore.RED + "  [webclone] " + Fore.WHITE + f"Carpeta  : {output}/")
    print(Fore.RED + "  [webclone] " + Fore.WHITE + f"Profund. : {depth} nivel(es)\n")

    cloner = WebCloner(url, output, depth)
    cloner.clone()

# ──────────────────────────────────────────────────────────────
# Cloner class
# ──────────────────────────────────────────────────────────────

class WebCloner:
    def __init__(self, base_url: str, output_dir: str, depth: int):
        self.base_url   = base_url.rstrip("/")
        self.base_host  = urlparse(base_url).netloc
        self.output_dir = output_dir
        self.depth      = depth
        self.visitados  = set()
        self.assets_ok  = 0
        self.assets_err = 0
        self.session    = requests.Session()
        self.session.headers.update(HEADERS)

    def clone(self):
        os.makedirs(self.output_dir, exist_ok=True)
        self._clonar_pagina(self.base_url, nivel=0)
        self._resumen()

    # ── Página HTML ──────────────────────────────────────────

    def _clonar_pagina(self, url: str, nivel: int):
        if url in self.visitados or nivel > self.depth:
            return
        self.visitados.add(url)

        print(Fore.RED + f"  [HTML] " + Fore.WHITE + url)

        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            print(Fore.RED + f"  [!] Error descargando página: {e}")
            return

        soup = BeautifulSoup(resp.text, "html.parser")

        # Descargar todos los assets y reescribir rutas en el HTML
        self._procesar_assets(soup, url)

        # Reescribir links internos para que funcionen offline
        self._reescribir_links(soup, url)

        # Guardar HTML modificado
        ruta_local = self._ruta_local_html(url)
        os.makedirs(os.path.dirname(ruta_local), exist_ok=True)
        with open(ruta_local, "w", encoding="utf-8", errors="ignore") as f:
            f.write(str(soup))

        # Si depth > 1, seguir links internos
        if nivel < self.depth:
            for a in soup.find_all("a", href=True):
                href = urljoin(url, a["href"])
                parsed = urlparse(href)
                if parsed.netloc == self.base_host and href not in self.visitados:
                    # Solo páginas HTML, no archivos
                    ext = os.path.splitext(parsed.path)[1].lower()
                    if ext in ("", ".html", ".htm", ".php", ".asp", ".aspx"):
                        time.sleep(0.2)
                        self._clonar_pagina(href, nivel + 1)

    # ── Assets ───────────────────────────────────────────────

    def _procesar_assets(self, soup: BeautifulSoup, page_url: str):
        for tag, attrs in ASSETS_TAGS.items():
            for elemento in soup.find_all(tag):
                for attr in attrs:
                    val = elemento.get(attr, "")
                    if not val or val.startswith("data:"):
                        continue

                    # srcset puede tener múltiples URLs
                    if attr == "srcset":
                        nuevas = []
                        for parte in val.split(","):
                            partes = parte.strip().split()
                            if partes:
                                asset_url = urljoin(page_url, partes[0])
                                local = self._descargar_asset(asset_url)
                                if local:
                                    partes[0] = local
                                nuevas.append(" ".join(partes))
                        elemento[attr] = ", ".join(nuevas)
                    else:
                        asset_url = urljoin(page_url, val)
                        local = self._descargar_asset(asset_url)
                        if local:
                            elemento[attr] = local

        # CSS inline con url()
        for style_tag in soup.find_all("style"):
            if style_tag.string:
                style_tag.string = self._procesar_css(style_tag.string, page_url)

        # Atributos style inline
        for elem in soup.find_all(style=True):
            elem["style"] = self._procesar_css(elem["style"], page_url)

    def _procesar_css(self, css: str, base: str) -> str:
        def reemplazar(m):
            raw = m.group(1).strip("'\"")
            if raw.startswith("data:") or raw.startswith("http"):
                asset_url = raw if raw.startswith("http") else urljoin(base, raw)
            else:
                asset_url = urljoin(base, raw)
            local = self._descargar_asset(asset_url)
            return f"url('{local}')" if local else m.group(0)

        return re.sub(r'url\(([^)]+)\)', reemplazar, css)

    def _descargar_asset(self, url: str) -> str | None:
        if not url or not url.startswith("http"):
            return None
        if url in self.visitados:
            return self._ruta_relativa_asset(url)
        self.visitados.add(url)

        ruta_local = self._ruta_local_asset(url)
        if os.path.exists(ruta_local):
            return self._ruta_relativa_asset(url)

        try:
            resp = self.session.get(url, timeout=15, stream=True)
            resp.raise_for_status()

            os.makedirs(os.path.dirname(ruta_local), exist_ok=True)
            with open(ruta_local, "wb") as f:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)

            tipo = resp.headers.get("Content-Type", "").split(";")[0].strip()
            ext  = mimetypes.guess_extension(tipo) or ""
            icono = _icono_tipo(tipo)

            print(Fore.RED + f"  {icono} " + Fore.WHITE + f"{_nombre_corto(url)}" +
                  Fore.RED + f" [{_human_size(os.path.getsize(ruta_local))}]")
            self.assets_ok += 1

            # Si es CSS, también procesar sus url() internos
            if "css" in tipo:
                with open(ruta_local, "r", encoding="utf-8", errors="ignore") as f:
                    css = f.read()
                css = self._procesar_css(css, url)
                with open(ruta_local, "w", encoding="utf-8") as f:
                    f.write(css)

            return self._ruta_relativa_asset(url)

        except Exception as e:
            print(Fore.YELLOW + f"  [~] No descargado: {_nombre_corto(url)} ({e})")
            self.assets_err += 1
            return None

    # ── Links ─────────────────────────────────────────────────

    def _reescribir_links(self, soup: BeautifulSoup, page_url: str):
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:"):
                continue
            abs_url = urljoin(page_url, href)
            if urlparse(abs_url).netloc == self.base_host:
                a["href"] = self._ruta_relativa_html(abs_url)

    # ── Rutas locales ─────────────────────────────────────────

    def _ruta_local_html(self, url: str) -> str:
        path = urlparse(url).path.rstrip("/") or "/index"
        if not os.path.splitext(path)[1]:
            path += "/index.html"
        return os.path.join(self.output_dir, path.lstrip("/"))

    def _ruta_local_asset(self, url: str) -> str:
        parsed = urlparse(url)
        path   = unquote(parsed.path).lstrip("/")
        if not path:
            path = "index"
        # Assets externos van a carpeta assets/host/
        if parsed.netloc != self.base_host:
            path = os.path.join("assets", parsed.netloc, path)
        return os.path.join(self.output_dir, path)

    def _ruta_relativa_asset(self, url: str) -> str:
        local = self._ruta_local_asset(url)
        return os.path.relpath(local, self.output_dir).replace("\\", "/")

    def _ruta_relativa_html(self, url: str) -> str:
        local = self._ruta_local_html(url)
        return os.path.relpath(local, self.output_dir).replace("\\", "/")

    # ── Resumen ───────────────────────────────────────────────

    def _resumen(self):
        print(Fore.RED + f"\n  ╔══ Clonación completada ══════════════")
        print(Fore.RED + f"  ║ " + Fore.WHITE + f"Páginas  : {len(self.visitados)}")
        print(Fore.RED + f"  ║ " + Fore.GREEN + f"Assets OK: {self.assets_ok}")
        if self.assets_err:
            print(Fore.RED + f"  ║ " + Fore.YELLOW + f"Errores  : {self.assets_err}")
        print(Fore.RED + f"  ║ " + Fore.WHITE + f"Guardado : {self.output_dir}/")
        print(Fore.RED + f"  ╚══════════════════════════════════════\n")

# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────

def _icono_tipo(content_type: str) -> str:
    if "image"      in content_type: return "[IMG]"
    if "javascript" in content_type: return "[JS] "
    if "css"        in content_type: return "[CSS]"
    if "font"       in content_type: return "[FNT]"
    if "video"      in content_type: return "[VID]"
    if "audio"      in content_type: return "[AUD]"
    return "[AST]"

def _nombre_corto(url: str, max_len: int = 60) -> str:
    nombre = urlparse(url).path.split("/")[-1] or urlparse(url).netloc
    return (nombre[:max_len] + "...") if len(nombre) > max_len else nombre

def _human_size(n: int) -> str:
    for u in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.1f}{u}"
        n /= 1024
    return f"{n:.1f}TB"

def _show_help():
    print(Fore.RED   + "\n  webclone — " + Fore.WHITE + DESCRIPTION)
    print(Fore.WHITE + f"\n  Uso: {USAGE}\n")
    print(Fore.YELLOW + "  Opciones:")
    print(Fore.WHITE  + "    -o <carpeta>      Carpeta de salida (default: clone_dominio)")
    print(Fore.WHITE  + "    -d <profundidad>  Seguir links internos, 1-3 (default: 1)\n")
    print(Fore.YELLOW + "  Ejemplos:")
    print(Fore.WHITE  + "    webclone example.com")
    print(Fore.WHITE  + "    webclone https://example.com -o mi_clon")
    print(Fore.WHITE  + "    webclone example.com -d 2 -o sitio_completo\n")