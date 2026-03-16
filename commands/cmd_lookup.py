import phonenumbers
from phonenumbers import geocoder, carrier, timezone
from colorama import Fore, Style, init

init(autoreset=True)

def run(args):
    if len(args) == 0:
        print(Fore.LIGHTRED_EX + "[!] You must provide a phone number to lookup.")
        return

    raw_number = args[0].strip()

    try:
        number = phonenumbers.parse(raw_number, None)

        if not phonenumbers.is_valid_number(number):
            print(Fore.LIGHTRED_EX + "[!] The phone number is not valid.")
            return

        country = geocoder.description_for_number(number, "en")
        operator = carrier.name_for_number(number, "en")
        time_zones = timezone.time_zones_for_number(number)
        e164 = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)
        international = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        national = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.NATIONAL)

        print(Fore.LIGHTCYAN_EX + f"\n📞 Phone Number Lookup for: {raw_number}")
        print(Fore.LIGHTGREEN_EX + f"├─ Formatted (E164): {Fore.WHITE}{e164}")
        print(Fore.LIGHTGREEN_EX + f"├─ International Format: {Fore.WHITE}{international}")
        print(Fore.LIGHTGREEN_EX + f"├─ National Format: {Fore.WHITE}{national}")
        print(Fore.LIGHTGREEN_EX + f"├─ Country: {Fore.WHITE}{country}")
        print(Fore.LIGHTGREEN_EX + f"├─ Carrier / Operator: {Fore.WHITE}{operator if operator else 'Unknown'}")
        print(Fore.LIGHTGREEN_EX + f"└─ Time Zones: {Fore.WHITE}{', '.join(time_zones)}\n")

    except phonenumbers.NumberParseException as e:
        print(Fore.LIGHTRED_EX + f"[!] Error parsing number: {str(e)}")
