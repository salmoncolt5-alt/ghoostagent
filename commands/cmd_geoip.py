import requests
import socket
from colorama import Fore, Style
import sys
import subprocess

def run(args):
    if len(args) == 0:
        print(Fore.RED + "[!] You must provide an IP to scan.")
        return
    
    ip = args[0]
    print(Fore.WHITE + f"[*] Collecting GeoIP info for: {ip}\n" + Fore.WHITE)

    try:
        response = requests.get(f"http://ip-api.com/json/{ip}").json()
        if response['status'] == 'success':
            print(Fore.RED + "[GeoIP Info]")
            print(Fore.WHITE + f"  > Country: {response.get('country')}")
            print(f"  > Region: {response.get('regionName')}")
            print(f"  > City: {response.get('city')}")
            print(f"  > ISP: {response.get('isp')}")
            print(f"  > Org: {response.get('org')}")
            print(f"  > ASN: {response.get('as')}")
            print(f"  > Timezone: {response.get('timezone')}")
            print(f"  > Coordinates: {response.get('lat')}, {response.get('lon')}")
            print(f"  > ZIP Code: {response.get('zip')}")
        else:
            print(Fore.RED + "[!] Failed to retrieve GeoIP info.")
    except Exception as e:
        print(Fore.RED + f"[!] Error getting GeoIP info: {e}")

    print()

    try:
        domain = socket.gethostbyaddr(ip)[0]
        print(Fore.RED + "[Reverse DNS]")
        print(Fore.WHITE + f"  > Hostname: {domain}")
    except Exception:
        print(Fore.YELLOW + "[!] No reverse DNS found.")

    print()

    try:
        print(Fore.RED + "[Port Scan]")
        print(Fore.WHITE + "  > Running scan... This may take a moment.")
        nmap_result = subprocess.check_output(['nmap', '-Pn', '--top-ports', '1000', ip], stderr=subprocess.DEVNULL).decode()
        print(Fore.GREEN + nmap_result)
    except Exception as e:
        print(Fore.RED + f"[!] Nmap error: {e}")

    print()

    try:
        print(Fore.RED + "[Associated Domains]")
        crt_url = f"https://crt.sh/?q={ip}&output=json"
        crt_response = requests.get(crt_url, timeout=10)
        if crt_response.status_code == 200:
            domains = {entry["name_value"] for entry in crt_response.json()}
            if domains:
                for d in sorted(domains):
                    print(Fore.WHITE + f"  > {d}")
            else:
                print(Fore.YELLOW + "  > No domains found.")
        else:
            print(Fore.RED + "[!] Error fetching domains from crt.sh")
    except Exception as e:
        print(Fore.RED + f"[!] crt.sh error: {e}")
