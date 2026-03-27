#!/usr/bin/env python3

import os
import sys
import argparse
import threading
from datetime import datetime

# ---------------- CONFIG ----------------
TELEGRAM_TOKEN = ""   # add if needed
CHAT_ID = ""          # add if needed

# ---------------- Banner ----------------
def banner():
    print("""
   ███████╗██╗  ██╗ █████╗ ████████╗████████╗███████╗██████╗ ███╗   ███╗
   ██╔════╝██║  ██║██╔══██╗╚══██╔══╝╚══██╔══╝██╔════╝██╔══██╗████╗ ████║
   ███████╗███████║███████║   ██║      ██║   █████╗  ██████╔╝██╔████╔██║
   ╚════██║██╔══██║██╔══██║   ██║      ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║
   ███████║██║  ██║██║  ██║   ██║      ██║   ███████╗██║  ██║██║ ╚═╝ ██║
   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝      ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝
        ShatterMind v2 🔥
    """)

# ---------------- Utils ----------------
def run(cmd):
    print(f"[+] {cmd}")
    os.system(cmd)

def workspace(domain):
    path = f"output/{domain}_{datetime.now().strftime('%H%M%S')}"
    os.makedirs(path, exist_ok=True)
    return path

def dedup(file):
    if os.path.exists(file):
        with open(file) as f:
            data = list(set(f.readlines()))
        with open(file, "w") as f:
            f.writelines(data)

# ---------------- Telegram ----------------
def send_telegram(msg):
    if TELEGRAM_TOKEN and CHAT_ID:
        os.system(f"curl -s -X POST https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage -d chat_id={CHAT_ID} -d text='{msg}'")

# ---------------- Modules ----------------
def subdomain(domain, out, mode):
    run(f"subfinder -d {domain} -silent > {out}/subs.txt")
    if mode == "deep":
        run(f"amass enum -d {domain} >> {out}/subs.txt")
    dedup(f"{out}/subs.txt")

def live(out):
    run(f"httpx -l {out}/subs.txt -silent > {out}/live.txt")

def urls(domain, out):
    run(f"gau {domain} >> {out}/urls.txt")
    run(f"waybackurls {domain} >> {out}/urls.txt")
    dedup(f"{out}/urls.txt")

def param_discovery(out):
    print("[+] Extracting parameters...")
    run(f"grep '=' {out}/urls.txt | sort -u > {out}/params.txt")

def js_scan(out):
    print("[+] JS Analysis...")
    run(f"grep '.js' {out}/urls.txt > {out}/js.txt")

def ports(out):
    run(f"nmap -iL {out}/live.txt -T4 -oN {out}/ports.txt")

def vuln(out):
    run(f"nuclei -l {out}/live.txt -severity medium,high,critical -o {out}/vulns.txt")

# ---------------- Multithreading ----------------
def threaded(tasks):
    threads = []
    for t in tasks:
        th = threading.Thread(target=t)
        th.start()
        threads.append(th)
    for th in threads:
        th.join()

# ---------------- Main ----------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--domain", required=True)
    parser.add_argument("-m", "--mode", choices=["fast","deep"], default="fast")
    args = parser.parse_args()

    banner()

    out = workspace(args.domain)
    print(f"[+] Output: {out}")

    # Phase 1
    subdomain(args.domain, out, args.mode)
    live(out)

    # Phase 2 (parallel)
    threaded([
        lambda: urls(args.domain, out),
    ])

    # Phase 3
    param_discovery(out)
    js_scan(out)

    if args.mode == "deep":
        ports(out)

    vuln(out)

    # Alerts
    if os.path.exists(f"{out}/vulns.txt"):
        send_telegram(f"ShatterMind Found Vulnerabilities on {args.domain}")

    print("\n✅ Completed. Check:", out)

if __name__ == "__main__":
    main()
