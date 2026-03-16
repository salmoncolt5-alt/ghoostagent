import nmap
from colorama import Fore

def run(args):
    if not args:
        print(Fore.WHITE + "[!] You must provide an IP address to scan.\n")
        return

    target_ip = args[0]
    scanner = nmap.PortScanner()

    print(Fore.WHITE + f"[*] Starting fast port scan on {target_ip}...\n")

    try:
        scanner.scan(hosts=target_ip, arguments='-p 1-2590 -T5 --min-rate 500')
    except Exception as e:
        print(Fore.RED + f"[!] Failed to scan {target_ip}: {e}\n")
        return

    if target_ip not in scanner.all_hosts():
        print(Fore.RED + f"[!] No response from {target_ip}. Host may be offline or filtered.\n")
        return

    has_ports = False
    for proto in scanner[target_ip].all_protocols():
        ports = scanner[target_ip][proto].keys()
        if ports:
            has_ports = True
            for port in sorted(ports):
                state = scanner[target_ip][proto][port]['state']
                name = scanner[target_ip][proto][port]['name']
                print(Fore.WHITE + f"[{proto.upper()}] Port {port}: {state.upper()} ({name})")

    if not has_ports:
        print(Fore.YELLOW + f"[!] No open ports found on {target_ip}.\n")

    print(Fore.WHITE + "\n[*] Scan complete.\n")
