import sys
import socket
import struct
from mcstatus import JavaServer
import requests
from colorama import Fore

def ip_to_decimal(ip):
    packed_ip = socket.inet_aton(ip)
    return struct.unpack("!I", packed_ip)[0]

def run(args):
    if len(args) == 0:
        print(Fore.RED + "[!] You must provide the server IP or domain.")
        return
    
    host = args[0]

    try:
        ip = socket.gethostbyname(host)
    except Exception:
        print(Fore.RED + f"[!] Could not resolve domain '{host}'.")
        return

    print(Fore.CYAN + f"[*] Getting server info for {host} ({ip})\n" + Fore.WHITE)
    try:
        server = JavaServer.lookup(host)
        status = server.status()
        players = status.players
        version = status.version
        motd = status.description if hasattr(status, 'description') else "N/A"
        software = "Unknown"

        if hasattr(status, 'modinfo') and status.modinfo is not None:
            software = status.modinfo.name if hasattr(status.modinfo, 'name') else software

        print(Fore.RED + "[Server Info]")
        print(Fore.WHITE + f"  > MOTD: {motd}")
        print(f"  > Version: {version.name}")
        print(f"  > Players online: {players.online} / {players.max}")
        print(f"  > Software: {software}")

    except Exception as e:
        print(Fore.YELLOW + "[!] Could not get Minecraft server status. Server may be offline or unreachable.")
        print(Fore.RED + f"Error: {e}")

    try:
        ip_decimal = ip_to_decimal(ip)
        print()
        print(Fore.RED + "[IP Info]")
        print(Fore.WHITE + f"  > IP Address: {ip}")
        print(f"  > Decimal IP: {ip_decimal}")
    except Exception as e:
        print(Fore.RED + f"[!] Error converting IP to decimal: {e}")

    try:
        print()
        print(Fore.RED + "[Related Domains]")
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            print(Fore.WHITE + f"  > Reverse DNS: {hostname}")
        except Exception:
            print(Fore.YELLOW + "  > No reverse DNS found.")

        for record_type in ['MX', 'NS']:
            try:
                import dns.resolver
                answers = dns.resolver.resolve(host, record_type)
                print(f"  > {record_type} records:")
                for rdata in answers:
                    print(f"    - {rdata.to_text()}")
            except Exception:
                print(f"  > No {record_type} records found or dns.resolver not installed.")
                break  
    except Exception as e:
        print(Fore.RED + f"[!] Error fetching related domains: {e}")
