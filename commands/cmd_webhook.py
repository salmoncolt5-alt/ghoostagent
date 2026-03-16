import requests
import time
from colorama import Fore, init

init(autoreset=True)

def run(args):
    if len(args) < 3:
        print(Fore.LIGHTRED_EX + "Usage: webhook <webhook_url> <amount> <message>")
        return
    
    webhook_url = args[0]
    try:
        amount = int(args[1])
        if amount <= 0:
            print(Fore.LIGHTRED_EX + "[!] Amount must be a positive integer.")
            return
    except ValueError:
        print(Fore.LIGHTRED_EX + "[!] Amount must be an integer.")
        return
    
    message = " ".join(args[2:])
    
    print(Fore.LIGHTCYAN_EX + f"Starting to send {amount} messages to webhook: {webhook_url}")
    print(Fore.LIGHTWHITE_EX + f"Message: {message}\n")
    
    sent = 0
    try:
        for i in range(amount):
            data = {
                "content": message
            }
            res = requests.post(webhook_url, json=data)
            
            if res.status_code == 204:
                sent += 1
                print(Fore.LIGHTGREEN_EX + f"[+] Sent message {sent}/{amount}", end='\r')
            else:
                print(Fore.RED + f"\n[!] Failed to send message at count {sent+1}. Status code: {res.status_code}")
                break
            
            time.sleep(1) 
        print("\n" + Fore.CYAN + f"Finished sending messages. Total sent: {sent}")
    except KeyboardInterrupt:
        print("\n" + Fore.CYAN + f"Stopped early. Total messages sent: {sent}")
    except Exception as e:
        print(Fore.RED + f"Error: {e}")
