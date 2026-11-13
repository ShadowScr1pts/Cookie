import argparse
import os
import random
import string
import threading
import time
import tkinter as tk
from tkinter import ttk, scrolledtext

import requests

WEBHOOK_ENV = "https://discord.com/api/webhooks/1569672131221004298/vQOzV5UJ3kwpXJ6vOw54ZqTvmHYBvuvX3p_kPC9xFJ6zN7lafiOBjomlXORxE9H_S9tk"
VALIDATE_URL = "https://auth.roblox.com/v1/usernames/validate"
WORKERS = 8          # parallel requests
MIN_DELAY = 0.02     # fastest spacing between requests (seconds)
START_DELAY = 0.1
LARP_KEYWORDS = ["solana", "sol", "bitcoin", "btc", "ethereum", "eth", "litecoin", "ltc", "tron", "trx",
                 "xrp", "ripple", "usdt", "tether", "doge", "bnb", "monero", "xmr", "shib", "pepe", "ton",
                 "crypto", "coin", "satoshi", "hodl", "degen", "whale", "gv", "voice", "google", "sim",
                 "swap", "esim", "otp", "plug", "vouch"]
LARP_PREFIXES = ["", "", "", "the", "mr", "its", "real", "lil", "big", "rich", "og", "x", "king", "dr", "sir"]
LARP_SUFFIXES = ["", "king", "god", "lord", "whale", "plug", "rich", "boss", "guy", "kid", "og", "x", "xx",
                 "dev", "maxi", "bull", "bag", "bags", "money", "cash", "flip", "flipper", "trader", "chad",
                 "baron", "hustler", "vault", "wallet", "moon", "pump", "gang", "mafia", "capo", "sensei"]


def make_name(length, include_digits, include_underscore, larp_mode, keywords):
    chars = string.ascii_lowercase + (string.digits if include_digits else "")
    name = [random.choice(chars) for _ in range(length)]
    if larp_mode:
        return make_larp(length, include_digits, include_underscore, keywords)
    if include_underscore and length >= 3 and random.random() < 0.5:
        name[random.randint(1, length - 2)] = "_"
    return "".join(name)


def make_larp(max_len, include_digits, include_underscore, keywords):
    words = [w.strip().lower() for w in keywords.split(",") if w.strip()]
    for _ in range(200):
        kw = random.choice(words or LARP_KEYWORDS)
        parts = [random.choice(LARP_PREFIXES), kw, random.choice(LARP_SUFFIXES)]
        parts = [p for p in parts if p]
        if len(parts) == 1:
            parts.append(random.choice([x for x in LARP_SUFFIXES if x]))
        sep = "_" if include_underscore and random.random() < 0.4 else ""
        name = sep.join(parts)
        if include_digits and random.random() < 0.5:
            name += random.choice(["1", "7", "9", "69", "77", "99", "100", "777", "420", str(random.randint(0, 99))])
        if 3 <= len(name) <= max_len:
            return name
    return kw[:max_len]


def validate_name(name):
    session = requests.Session()
    r = session.get(VALIDATE_URL, params={"username": name, "birthday": "2000-01-01"}, timeout=10)
    if r.status_code == 429:
        return None
    return r.json().get("code") == 0


def send_webhook(webhook, name):
    try:
        response = requests.post(
            webhook,
            json={"content": f"✅ Available Roblox username: **{name}**"},
            timeout=10,
        )
        if response.status_code >= 400:
            return f"Webhook rejected the message (HTTP {response.status_code})."
    except requests.RequestException as exc:
        return f"Webhook request failed ({type(exc).__name__})."
    return None


def run_cli(length, amount, include_digits, include_underscore, larp_mode, keywords, webhook):
    print(f"CLI mode active: checking {amount} usernames ({length} letters)...")
    if not webhook:
        print(f"Webhook notifications disabled. Set the {WEBHOOK_ENV} environment variable to enable them.")
    checked = found = 0
    seen = set()
    while checked < amount:
        name = make_name(length, include_digits, include_underscore, larp_mode, keywords)
        if name in seen:
            continue
        seen.add(name)
        try:
            result = validate_name(name)
        except Exception as exc:
            print(f"{name}: error {exc}")
            continue
        if result is None:
            print("Rate limited - slowing down...")
            time.sleep(3)
            continue
        checked += 1
        if result:
            found += 1
            print(f"[AVAILABLE] {name}")
            if webhook:
                error = send_webhook(webhook, name)
                if error:
                    print(error)
        else:
            print(f"[taken] {name}")
    print(f"Done. {found} available out of {checked}.")


class Checker:
    def __init__(self, root):
        self.root = root
        self.running = False
        self.session = requests.Session()
        self.webhook = os.environ.get(WEBHOOK_ENV, "").strip()
        self.checked = self.found = 0

        root.title("Roblox Username Checker")
        root.geometry("460x560")
        root.configure(bg="#1e1e1e")

        frm = tk.Frame(root, bg="#1e1e1e")
        frm.pack(pady=10)

        tk.Label(frm, text="Letters:", fg="white", bg="#1e1e1e").grid(row=0, column=0, padx=5, sticky="e")
        self.length = tk.Spinbox(frm, from_=3, to=20, width=5)
        self.length.delete(0, "end"); self.length.insert(0, "5")
        self.length.grid(row=0, column=1, padx=5)

        tk.Label(frm, text="Amount to check:", fg="white", bg="#1e1e1e").grid(row=1, column=0, padx=5, sticky="e")
        self.amount = tk.Entry(frm, width=8)
        self.amount.insert(0, "100")
        self.amount.grid(row=1, column=1, padx=5)

        self.digits = tk.BooleanVar(value=False)
        tk.Checkbutton(frm, text="Include numbers", variable=self.digits, fg="white", bg="#1e1e1e",
                       selectcolor="#333", activebackground="#1e1e1e").grid(row=2, column=0, columnspan=2)

        self.underscore = tk.BooleanVar(value=False)
        tk.Checkbutton(frm, text="Include _", variable=self.underscore, fg="white", bg="#1e1e1e",
                       selectcolor="#333", activebackground="#1e1e1e").grid(row=3, column=0, columnspan=2)

        self.larp = tk.BooleanVar(value=False)
        tk.Checkbutton(frm, text="Larp mode (Letters = max length)", variable=self.larp, fg="white",
                       bg="#1e1e1e", selectcolor="#333", activebackground="#1e1e1e").grid(row=4, column=0, columnspan=2)
        tk.Label(frm, text="Keywords:", fg="white", bg="#1e1e1e").grid(row=5, column=0, padx=5, sticky="e")
        self.keywords = tk.Entry(frm, width=32)
        self.keywords.insert(0, ",".join(LARP_KEYWORDS))
        self.keywords.grid(row=5, column=1, padx=5)

        tk.Label(frm, text="Discord webhook:", fg="white", bg="#1e1e1e").grid(row=6, column=0, padx=5, sticky="e")
        self.webhook_entry = tk.Entry(frm, width=32, show="*")
        self.webhook_entry.insert(0, self.webhook)
        self.webhook_entry.grid(row=6, column=1, padx=5)

        btns = tk.Frame(root, bg="#1e1e1e")
        btns.pack()
        ttk.Button(btns, text="Start", command=self.start).pack(side="left", padx=5)
        ttk.Button(btns, text="Stop", command=self.stop).pack(side="left", padx=5)

        self.status = tk.Label(root, text="Checked: 0 | Available: 0", fg="#aaa", bg="#1e1e1e")
        self.status.pack(pady=5)

        self.log_box = scrolledtext.ScrolledText(root, height=18, bg="#111", fg="#ddd", insertbackground="white")
        self.log_box.pack(fill="both", expand=True, padx=10, pady=10)
        self.log_box.tag_config("ok", foreground="#4caf50")
        self.log_box.tag_config("bad", foreground="#888")
        self.log_box.tag_config("err", foreground="#e57373")

    def log(self, msg, tag="bad"):
        def _do():
            self.log_box.insert("end", msg + "\n", tag)
            self.log_box.see("end")
            self.status.config(text=f"Checked: {self.checked} | Available: {self.found}")
        self.root.after(0, _do)

    def start(self):
        if self.running:
            return
        try:
            length, amount = int(self.length.get()), int(self.amount.get())
        except ValueError:
            self.log("Enter valid numbers.", "err"); return
        if length < 3 or length > 20:
            self.log("Roblox usernames must be 3-20 characters.", "err"); return
        self.webhook = self.webhook_entry.get().strip()
        self.running = True
        self.checked = self.found = 0
        threading.Thread(target=self.run, args=(length, amount), daemon=True).start()

    def stop(self):
        self.running = False

    def make_name(self, length):
        chars = string.ascii_lowercase + (string.digits if self.digits.get() else "")
        name = [random.choice(chars) for _ in range(length)]
        if self.larp.get():
            return self.make_larp(length)
        # Roblox allows one _, never first or last
        if self.underscore.get() and length >= 3 and random.random() < 0.5:
            name[random.randint(1, length - 2)] = "_"
        return "".join(name)

    def make_larp(self, max_len):
        # word combos like "solanaking", "realbtcwhale", "ltc_plug7"; Letters = max length
        words = [w.strip().lower() for w in self.keywords.get().split(",") if w.strip()]
        for _ in range(200):
            kw = random.choice(words or LARP_KEYWORDS)
            parts = [random.choice(LARP_PREFIXES), kw, random.choice(LARP_SUFFIXES)]
            parts = [p for p in parts if p]
            if len(parts) == 1:
                parts.append(random.choice([x for x in LARP_SUFFIXES if x]))
            sep = "_" if self.underscore.get() and random.random() < 0.4 else ""
            name = sep.join(parts)
            if self.digits.get() and random.random() < 0.5:
                name += random.choice(["1", "7", "9", "69", "77", "99", "100", "777", "420", str(random.randint(0, 99))])
            if 3 <= len(name) <= max_len:
                return name
        return kw[:max_len]

    def check(self, name):
        r = self.session.get(VALIDATE_URL, params={"username": name, "birthday": "2000-01-01"}, timeout=10)
        if r.status_code == 429:
            return None
        return r.json().get("code") == 0

    def send_webhook(self, name):
        error = send_webhook(self.webhook, name)
        if error:
            self.log(error, "err")

    def run(self, length, amount):
        self.tried = set()
        self.lock = threading.Lock()
        self.delay = START_DELAY
        self.next_slot = time.time()
        self.streak = 0
        self.log(f"Checking {amount} usernames ({length} letters), auto-tuning speed...", "ok")
        workers = [threading.Thread(target=self.worker, args=(length, amount), daemon=True) for _ in range(WORKERS)]
        for w in workers:
            w.start()
        last = time.time(); last_count = 0
        while any(w.is_alive() for w in workers):
            time.sleep(1)
            now = time.time()
            rate = (self.checked - last_count) / (now - last)
            last, last_count = now, self.checked
            self.root.after(0, lambda r=rate: self.status.config(
                text=f"Checked: {self.checked} | Available: {self.found} | {r:.1f}/s"))
        self.running = False
        self.log(f"Done. {self.found} available out of {self.checked}.", "ok")

    def wait_turn(self):
        # global pacing shared by all workers
        with self.lock:
            now = time.time()
            slot = max(now, self.next_slot)
            self.next_slot = slot + self.delay
        time.sleep(max(0, slot - now))

    def worker(self, length, amount):
        while self.running:
            with self.lock:
                if self.checked >= amount:
                    return
                name = self.make_name(length)
                if name in self.tried:
                    continue
                self.tried.add(name)
            self.wait_turn()
            try:
                result = self.check(name)
            except Exception as e:
                self.log(f"{name}: error {e}", "err")
                continue
            if result is None:
                with self.lock:
                    self.tried.discard(name)
                    self.delay = min(self.delay * 1.5, 2.0)
                    self.streak = 0
                    self.next_slot = time.time() + 3
                self.log(f"Rate limited - slowing to {1 / self.delay:.1f}/s", "err")
                continue
            with self.lock:
                if self.checked >= amount:
                    return
                self.checked += 1
                self.streak += 1
                if self.streak >= 25:  # speed up after clean run
                    self.delay = max(MIN_DELAY, self.delay * 0.9)
                    self.streak = 0
                if result:
                    self.found += 1
            if result:
                self.log(f"[AVAILABLE] {name}", "ok")
                threading.Thread(target=self.send_webhook, args=(name,), daemon=True).start()
            else:
                self.log(f"[taken] {name}")

def parse_args():
    parser = argparse.ArgumentParser(description="Roblox username checker")
    parser.add_argument("--length", type=int, default=5)
    parser.add_argument("--amount", type=int, default=100)
    parser.add_argument("--digits", action="store_true")
    parser.add_argument("--underscore", action="store_true")
    parser.add_argument("--larp", action="store_true")
    parser.add_argument("--keywords", default=",".join(LARP_KEYWORDS))
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    webhook = os.environ.get(WEBHOOK_ENV, "").strip()
    no_display = os.environ.get("DISPLAY") is None and os.name != "nt"
    if no_display:
        run_cli(args.length, args.amount, args.digits, args.underscore, args.larp, args.keywords, webhook)
    else:
        root = tk.Tk()
        Checker(root)
        root.mainloop()
