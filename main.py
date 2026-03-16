import os
import sys
import time
import importlib
import subprocess
from colorama import Fore, init
from rich.console import Console
from rich.text import Text
from rich.align import Align
from rich.columns import Columns

init(autoreset=True)
console = Console()

# ── Auto-install dependencias ─────────────────────────────────

required = [
    "requests", "phonenumbers", "mcstatus", "python-nmap",
    "colorama", "rich", "pypresence"
]

for pkg in required:
    try:
        __import__(pkg.replace("-", "_").split("==")[0])
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

COMMANDS_PATH = "commands"
DISCORD_CLIENT_ID = "1478826895989538827"

# ── Utilidades ────────────────────────────────────────────────

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# ── Banner ────────────────────────────────────────────────────

def print_banner():
    clear_screen()

    left_banner = Text.from_markup(
        "[red]╔═╗╦ ╦╔═╗╔═╗╔═╗╔╦╗\n"
        "║ ╦╠═╣║ ║║ ║╚═╗ ║ \n"
        "╚═╝╩ ╩╚═╝╚═╝╚═╝ ╩ [/red]\n"
        "[red]╔═══════════════════════╗\n"
        "║[/red][white] Advanced Tool        [/white][red]║\n"
        "╚═══════════════════════╝[/red]\n"
        "[red]    [By @SalmonColt][/red]"
    )

    right_banner = Text.from_markup(
        "[red]╔══════════════╗\n"
        "║[/red][white].gg/SRbU2hsmBk[/white][red]║\n"
        "║[/red][bright_red]    v1.2      [/bright_red][red]║\n"
        "╚══════════════╝[/red]"
    )

    columns = Columns([Align(left_banner, "left"), Align(right_banner, "right")], expand=True)
    console.print(columns)
    console.print()
    console.print("[white]Hello User. Welcome to [red]Ghoost[/red]")
    console.print("To view the list of commands, type [green]help[/green]\n")

# ── Menú ──────────────────────────────────────────────────────

def show_menu():
    print(Fore.WHITE + "Available commands:\n")
    for cmd in listar_comandos():
        print(Fore.RED + "» [CMD] " + Fore.WHITE + f" > {cmd}")
    print(Fore.RED + "» [CMD] " + Fore.WHITE + " > pterodactyl")
    print(Fore.RED + "» [CMD] " + Fore.WHITE + " > serverinfo")
    print(Fore.RED + "» [CMD] " + Fore.WHITE + " > scanports")
    print(Fore.RED + "» [CMD] " + Fore.WHITE + " > geoip")
    print(Fore.RED + "» [CMD] " + Fore.WHITE + " > vulnscan")
    print(Fore.RED + "» [CMD] " + Fore.WHITE + " > botattack")
    print(Fore.RED + "» [CMD] " + Fore.WHITE + " > webhook")
    print(Fore.RED + "» [CMD] " + Fore.WHITE + " > webattack")
    print(Fore.RED + "» [CMD] " + Fore.WHITE + " > mc_query_flood")
    print(Fore.RED + "» [CMD] " + Fore.WHITE + " > ping")
    print(Fore.RED + "» [CMD] " + Fore.WHITE + " > servercrash")
    print(Fore.RED + "» [CMD] " + Fore.WHITE + " > mysqlconnect")
    print(Fore.RED + "» [CMD] " + Fore.WHITE + " > masscanhost")
    print(Fore.RED + "» [CMD] " + Fore.WHITE + " > dnslookup")
    print(Fore.RED + "» [CMD] " + Fore.WHITE + " > subdomain")
    print(Fore.RED + "» [CMD] " + Fore.WHITE + " > lookup")
    print(Fore.RED + "» [CMD] " + Fore.WHITE + " > dehash")
    print(Fore.RED + "» [CMD] " + Fore.WHITE + " > webclone")
    print()
    print()
    print(Fore.WHITE + "» [INFO]  > help    (Show this message)")
    print(Fore.WHITE + "» [INFO]  > clear   (Clear screen)")
    print(Fore.WHITE + "» [INFO]  > exit    (Exit the tool)")
    print()

# ── Comandos ──────────────────────────────────────────────────

def listar_comandos():
    comandos = []
    if not os.path.exists(COMMANDS_PATH):
        return comandos
    for f in os.listdir(COMMANDS_PATH):
        if f.startswith('cmd_') and f.endswith('.py'):
            comandos.append(f[4:-3])
    return sorted(comandos)

def ejecutar_comando(nombre_comando, args=None):
    try:
        modulo = importlib.import_module(f'{COMMANDS_PATH}.cmd_{nombre_comando}')
        if hasattr(modulo, 'run'):
            modulo.run(args or [])
        else:
            print(Fore.WHITE + f"Error: Command '{nombre_comando}' does not have a run() function.")
    except ModuleNotFoundError:
        print(Fore.RED + f"Command '{nombre_comando}' not found.")
    except Exception as e:
        print(Fore.RED + f"Error executing command '{nombre_comando}': {e}")

# ── Discord RPC ───────────────────────────────────────────────

def init_discord():
    try:
        from pypresence import Presence
        rpc = Presence(DISCORD_CLIENT_ID)
        rpc.connect()
        rpc.update(
            state="Awaiting Commands...",
            details="😈 The Best Attack Tool",
            start=time.time(),
            large_image="logo",
            large_text=".gg/SRbU2hsmBk",
            small_image="user",
            small_text="Free Version",
            buttons=[
                {"label": "GitHub", "url": "https://github.com/salmoncolt5-alt"},
                {"label": "Telegram", "url": "https://t.me/salmoncolt"}
            ]
        )
    except Exception as e:
        print(f"[!] Discord RPC error: {e}")

# ── Main ──────────────────────────────────────────────────────

def main():
    init_discord()
    print_banner()

    comandos_disponibles = listar_comandos()

    while True:
        try:
            entrada = input(
                Fore.RED + "ghoostagent" +
                Fore.YELLOW + "@user" +
                Fore.WHITE + ":~$ "
            ).strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

        if entrada.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break
        elif entrada.lower() == 'help':
            show_menu()
        elif entrada.lower() == 'clear':
            clear_screen()
            print_banner()
        elif entrada == '':
            continue
        else:
            partes = entrada.split()
            comando = partes[0]
            args = partes[1:]

            if comando in comandos_disponibles:
                ejecutar_comando(comando, args)
            else:
                print(Fore.WHITE + f"Command '{entrada}' is not recognized. Type 'help' to view commands.\n")

if __name__ == "__main__":
    main()