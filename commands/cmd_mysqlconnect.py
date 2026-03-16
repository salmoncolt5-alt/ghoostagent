# Command New Update

import subprocess
from colorama import Fore

def run(args):
    if len(args) < 2:
        print(Fore.LIGHTWHITE_EX + "Usage: mysqlconnect <ip> <username>")
        print(Fore.LIGHTWHITE_EX + "Example: mysqlconnect 23.95.79.90 pterodactyl")
        return

    ip = args[0]
    username = args[1]

    try:
        password = input(Fore.LIGHTWHITE_EX + "Enter Password: ")
        print(Fore.LIGHTYELLOW_EX + "[•] Connecting to MySQL...")
        subprocess.run(["mysql", "-h", ip, "-u", username, f"-p{password}"])
    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] Connection aborted")
    except Exception as e:
        print(Fore.RED + f"[!] Error: {e}")