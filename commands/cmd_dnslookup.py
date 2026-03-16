# cmd_dnslookup.py

import dns.resolver
from colorama import Fore

def run(args):
    if len(args) < 1:
        print(Fore.LIGHTWHITE_EX + "Usage: dnslookup <domain>")
        print(Fore.LIGHTWHITE_EX + "Example: dnslookup hypixel.net")
        return

    domain = args[0]

    dns_records = [
        'A', 'AAAA', 'CNAME', 'MX', 'NS', 'PTR', 'SOA', 'SRV', 'TXT',
        'CAA', 'SPF', 'NAPTR'
    ]

    print(Fore.LIGHTYELLOW_EX + f"[•] DNS records for {domain}:\n")

    for rtype in dns_records:
        try:
            answers = dns.resolver.resolve(domain, rtype)
            print(Fore.LIGHTCYAN_EX + f"{rtype} Records:")
            for rdata in answers:
                print(Fore.GREEN + f"  - {rdata.to_text()}")
            print("")
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
            print(Fore.YELLOW + f"{rtype} Records: None found\n")
        except Exception as e:
            print(Fore.RED + f"Error retrieving {rtype} records: {e}\n")
