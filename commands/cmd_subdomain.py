import socket
from colorama import Fore, init
import threading

init(autoreset=True)

COMMON_SUBDOMAINS = [
    "www", "mail", "ftp", "cpanel", "webmail", "ns1", "ns2",
    "blog", "dev", "web", "shop", "api", "portal", "beta",
    "admin", "server", "vpn", "m", "mobile", "static", "support",
    "play", "mc", "store", "tienda", "panel", "phpyadmin", "dash",
    "dashboard", "app", "apps", "cdn", "cdn1", "cdn2", "cdn3",
    "test", "demo", "docs", "doc", "wiki", "forum", "community"
]

def check_subdomain(domain, subdomain, results):
    full_domain = f"{subdomain}.{domain}"
    try:
        socket.gethostbyname(full_domain)
        results.append(full_domain)
    except socket.gaierror:
        pass

def run(args):
    if len(args) == 0:
        print(Fore.RED + "[!] You must provide a domain to scan for subdomains.")
        return

    domain = args[0].strip()
    print(Fore.LIGHTCYAN_EX + f"Scanning common subdomains for: {domain}\n")

    results = []
    threads = []

    for sub in COMMON_SUBDOMAINS:
        t = threading.Thread(target=check_subdomain, args=(domain, sub, results))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    if results:
        print(Fore.WHITE + f"Found subdomains for {domain}:")
        for r in sorted(results):
            print(Fore.LIGHTGREEN_EX + f"- {r}")
    else:
        print(Fore.LIGHTYELLOW_EX + "No common subdomains found.")

