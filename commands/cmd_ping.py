import platform
import subprocess
from colorama import Fore

def run(args):
    if len(args) != 1:
        print(Fore.LIGHTRED_EX + "Usage: ping <host>")
        return

    host = args[0]
    system = platform.system()

    if system == "Windows":
        command = ["ping", "-n", "4", host]
    else:
        command = ["ping", "-c", "4", host]

    print(Fore.LIGHTCYAN_EX + f"Pinging {host}...\n")

    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(Fore.LIGHTGREEN_EX + result.stdout)
        else:
            print(Fore.RED + f"Ping to {host} failed")
            print(Fore.LIGHTBLACK_EX + result.stderr)
    except subprocess.TimeoutExpired:
        print(Fore.RED + "Ping request timed out.")
    except Exception as e:
        print(Fore.RED + f"Unexpected error: {e}")
