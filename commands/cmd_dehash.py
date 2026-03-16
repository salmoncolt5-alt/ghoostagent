import re
from hashlib import sha1, sha256, sha512
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import bcrypt
from colorama import Fore, init
import time

init(autoreset=True)

RESULT = None
wl_passwords = []
lock = Lock()

def load_wordlist(path: str):
    global wl_passwords
    with open(path, 'r', encoding='latin-1') as f:
        wl_passwords = [line.strip() for line in f if line.strip()]

def check_password(password: str, hash_str: str, hash_type: str, salt: str = None):
    hash_type = hash_type.lower()
    pw_bytes = password.encode()
    salt_bytes = salt.encode() if salt else b''

    try:
        if hash_type == "sha1":
            candidates = [
                sha1(pw_bytes).hexdigest(),
                sha1(pw_bytes + salt_bytes).hexdigest(),
                sha1(salt_bytes + pw_bytes).hexdigest(),
                sha1(sha1(pw_bytes).hexdigest().encode() + salt_bytes).hexdigest()
            ]
        elif hash_type == "sha256":
            candidates = [
                sha256(pw_bytes).hexdigest(),
                sha256(pw_bytes + salt_bytes).hexdigest(),
                sha256(salt_bytes + pw_bytes).hexdigest(),
                sha256(sha256(pw_bytes).hexdigest().encode() + salt_bytes).hexdigest()
            ]
        elif hash_type == "sha512":
            candidates = [
                sha512(pw_bytes).hexdigest(),
                sha512(pw_bytes + salt_bytes).hexdigest(),
                sha512(salt_bytes + pw_bytes).hexdigest(),
                sha512(sha512(pw_bytes).hexdigest().encode() + salt_bytes).hexdigest()
            ]
        else:
            return None
    except Exception:
        return None

    if hash_str in candidates:
        return password
    return None

def parse_input(args):
    if len(args) < 1:
        return None, None, None

    raw_input = args[0]

    if raw_input.startswith('$SHA512$') or raw_input.startswith('$SHA256$') or raw_input.startswith('$SHA1$'):
        parts = raw_input.split('$')
        if len(parts) == 4:
            hash_str = parts[2].lower()
            salt = parts[3]
        elif len(parts) == 3:
            hash_str = parts[2].lower()
            salt = None
        else:
            hash_str = raw_input.lower()
            salt = None
    else:
        if '@' in raw_input:
            hash_str, salt = raw_input.split('@', 1)
            hash_str = hash_str.lower()
        else:
            hash_str = raw_input.lower()
            salt = None

    if len(args) >= 2:
        hash_type = args[1].lower()
    else:
        if len(hash_str) == 40:
            hash_type = 'sha1'
        elif len(hash_str) == 64:
            hash_type = 'sha256'
        elif len(hash_str) == 128:
            hash_type = 'sha512'
        else:
            hash_type = None

    return hash_str, salt, hash_type
def run(args):
    global RESULT
    RESULT = None

    hash_str, salt, hash_type = parse_input(args)
    if not hash_str or not hash_type:
        print("[ERROR] Usage: dehash <hash> [hash_type]")
        print("Example: dehash $SHA/256/512$salt$hash sha1/sha256/sha512")
        return

    path = r"CloudList.txt"
    
    start_time = time.time()

    if hash_type == 'bcrypt':
        hash_bytes = hash_str.encode()
        with open(path, 'r', encoding='latin-1') as f:
            for line in f:
                pwd = line.strip()
                if not pwd:
                    continue
                if bcrypt.checkpw(pwd.encode(), hash_bytes):
                    RESULT = pwd
                    break
    else:
        with open(path, 'r', encoding='latin-1') as f:
            for line in f:
                pwd = line.strip()
                if not pwd:
                    continue
                res = check_password(pwd, hash_str, hash_type, salt)
                if res:
                    RESULT = res
                    break

    elapsed = time.time() - start_time

    if RESULT:
        print(f"{Fore.GREEN}[FOUND] → {RESULT}")
    else:
        print(f"{Fore.RED}[FAILED] Password not found.")
    print(f"{Fore.LIGHTCYAN_EX} Time elapsed: {elapsed:.2f} seconds")
