import requests
from colorama import Fore, init

init(autoreset=True)

def run(args):
    if len(args) == 0:
        print(Fore.RED + "[!] You must provide a URL to scan.")
        return

    url = args[0].strip()

    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'http://' + url 

    print(Fore.CYAN + f"[*] Scanning {url} for common vulnerabilities..." + Fore.LIGHTGREEN_EX)

    try:
        resp = requests.get(url, timeout=10, allow_redirects=True)
    except requests.RequestException as e:
        print(Fore.RED + f"[!] Request error: {e}")
        return

    headers = resp.headers

    if url.startswith('https://'):
        print(Fore.LIGHTGREEN_EX + "[+] HTTPS is used.")
    else:
        print(Fore.YELLOW + "[!] Not using HTTPS, traffic is unencrypted.")

    def check_header(name, expected_value=None):
        val = headers.get(name)
        if val:
            if expected_value:
                if expected_value.lower() in val.lower():
                    print(Fore.LIGHTGREEN_EX + f"[+] {name}: {val}")
                else:
                    print(Fore.YELLOW + f"[!] {name} header is present but may be misconfigured: {val}")
            else:
                print(Fore.LIGHTGREEN_EX + f"[+] {name}: {val}")
        else:
            print(Fore.RED + f"[!] {name} header is missing.")

    print()
    print(Fore.BLUE + "Header Security Checks:")
    check_header("X-Content-Type-Options", "nosniff")
    check_header("X-Frame-Options")
    check_header("Strict-Transport-Security")
    check_header("Content-Security-Policy")
    check_header("Referrer-Policy")

    cookies = resp.cookies
    if cookies:
        print()
        print(Fore.BLUE + "Cookies Security Check:")
        for c in cookies:
            secure = "Secure" if c.secure else "Not Secure"
            httponly = "HttpOnly" if c.has_nonstandard_attr('HttpOnly') or c._rest.get('HttpOnly') else "Not HttpOnly"
            print(f" - {c.name}: {secure}, {httponly}")
    else:
        print()
        print(Fore.LIGHTGREEN_EX + "No cookies received.")

    print()
    print(Fore.CYAN + "[*] Scan completed.")
