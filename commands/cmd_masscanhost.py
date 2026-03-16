# cmd_masscanhost.py

import nmap
from colorama import Fore

def scan(ip, ports):
    scanner = nmap.PortScanner()
    try:
        scanner.scan(ip, ports, arguments='-Pn')
    except Exception as e:
        print(Fore.RED + f"[!] Error scanning {ip}: {e}")
        return

    print(Fore.LIGHTCYAN_EX + f"\n[+] Scan result for {ip}:")

    if ip not in scanner.all_hosts():
        print(Fore.RED + f"[!] No response from {ip}")
        return

    open_ports = []
    for proto in scanner[ip].all_protocols():
        lport = scanner[ip][proto].keys()
        for port in sorted(lport):
            state = scanner[ip][proto][port]['state']
            if state == 'open':
                open_ports.append(port)

    if open_ports:
        for port in open_ports:
            print(Fore.GREEN + f"  [✓] Port {port} is OPEN")
    else:
        print(Fore.YELLOW + "  [•] No open ports found.")

def run(args):
    if len(args) < 2:
        print(Fore.LIGHTWHITE_EX + "Usage: masscanhost <ip1,ip2,...> <port-range>")
        print(Fore.LIGHTWHITE_EX + "Example: masscanhost 192.168.1.1,192.168.1.2 20-80")
        return

    targets = args[0].split(",")
    ports = args[1]

    print(Fore.LIGHTYELLOW_EX + f"[•] Scanning {len(targets)} target(s) on ports: {ports}\n")

    for ip in targets:
        scan(ip.strip(), ports)

    print(Fore.LIGHTGREEN_EX + "\n[✓] Scan completed.")
