#!/usr/bin/env python3
import os
import pyotp
import base64
import datetime

SEED_FILE = "/data/seed.txt"

def log_code():
    if not os.path.exists(SEED_FILE):
        return

    try:
        with open(SEED_FILE, "r") as f:
            seed = f.read().strip()
        
        # Convert hex seed to base32
        seed_bytes = bytes.fromhex(seed)
        base32_seed = base64.b32encode(seed_bytes).decode('utf-8')
        
        totp = pyotp.TOTP(base32_seed)
        now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        
        # The output format required by the task
        print(f"{now} - 2FA Code: {totp.now()}")
    except Exception as e:
        print(f"Error in cron: {e}", file=sys.stderr)

if __name__ == "__main__":
    log_code()