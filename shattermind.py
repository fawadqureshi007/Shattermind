#!/usr/bin/env python3
# SHATTERMIND - Next Generation Recon & Vulnerability Intelligence Framework

import requests
import socket
import dns.resolver
import whois
import re
import subprocess
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# =========================
# 🎨 Banner
# =========================
def banner():
    print("""
╔══════════════════════════════════════════════╗
║            SHATTERMIND Framework             ║
║   Recon | OSINT | Vulnerability Intelligence ║
╚══════════════════════════════════════════════╝
    """)

# =========================
# 🌐 Recon Engine
# =========================
def website_info(target):
    try:
        r = requests.get(target, timeout=5)
        print(f"[+] Title: {re.findall('<title>(.*?)</title>', r.text)[0]}")
        print(f"[+] Server: {r.headers.get('Server')}")
    except:
        print("[-] Error fetching website")

    try:
        ip = socket.gethostbyname(target.replace("http://","").replace("https://",""))
        print(f"[+] IP Address: {ip}")
    except:
        pass

def cloudflare_detect(target):
    try:
        r = requests.get(target)
        if "cloudflare" in str(r.headers).lower():
            print("[+] Cloudflare Detected")
        else:
            print("[-] No Cloudflare")
    except:
        pass

def robots_enum(target):
    try:
        r = requests.get(urljoin(target, "/robots.txt"))
        print("[+] robots.txt:\n", r.text)
    except:
        pass

def dns_info(domain):
    try:
        result = dns.resolver.resolve(domain, 'A')
        for ip in result:
            print(f"[+] DNS A Record: {ip}")
    except:
        pass

def whois_lookup(domain):
    try:
        info = whois.whois(domain)
        print(f"[+] WHOIS Org: {info.org}")
    except:
        pass

# =========================
# 🧬 Enumeration Module
# =========================
def subdomain_enum(domain):
    subs = ["www", "mail", "ftp", "dev", "test"]
    for sub in subs:
        try:
            full = f"{sub}.{domain}"
            socket.gethostbyname(full)
            print(f"[+] Found: {full}")
        except:
            pass

def reverse_ip(ip):
    print("[!] Reverse IP lookup requires API (hackertarget etc.)")

def banner_grab(domain):
    try:
        s = socket.socket()
        s.connect((domain, 80))
        s.send(b"HEAD / HTTP/1.1\r\nHost: "+domain.encode()+b"\r\n\r\n")
        print(s.recv(1024).decode())
        s.close()
    except:
        pass

# =========================
# 🛡 Security Scanner
# =========================
def nmap_scan(target):
    print("[*] Running Nmap Scan...")
    subprocess.call(["nmap", "-F", target])

def sensitive_files(target):
    paths = ["/.env", "/config.php", "/backup.zip"]
    for p in paths:
        url = target + p
        try:
            r = requests.get(url)
            if r.status_code == 200:
                print(f"[+] Found Sensitive File: {url}")
        except:
            pass

def sql_test(target):
    payload = "'"
    try:
        r = requests.get(target + payload)
        if "sql" in r.text.lower():
            print("[+] Possible SQL Injection")
    except:
        pass

# =========================
# 📡 Intelligence Layer
# =========================
def crawler(target):
    try:
        r = requests.get(target)
        soup = BeautifulSoup(r.text, "html.parser")
        for link in soup.find_all("a"):
            print("[+] Link:", link.get("href"))
    except:
        pass

def social_links(target):
    try:
        r = requests.get(target)
        socials = re.findall(r"(facebook|twitter|linkedin)\.com/[^\"]+", r.text)
        for s in socials:
            print("[+] Social:", s)
    except:
        pass

# =========================
# 🧩 CMS Detection
# =========================
def cms_detect(target):
    try:
        r = requests.get(target).text.lower()

        if "wp-content" in r:
            print("[+] WordPress Detected")
        elif "joomla" in r:
            print("[+] Joomla Detected")
        elif "drupal" in r:
            print("[+] Drupal Detected")
        elif "magento" in r:
            print("[+] Magento Detected")
        else:
            print("[-] Unknown CMS")

    except:
        pass

# =========================
# 🚀 Main Controller
# =========================
def run(target):
    print("\n[ RECON ENGINE ]")
    website_info(target)
    cloudflare_detect(target)
    robots_enum(target)
    dns_info(target.replace("http://","").replace("https://",""))
    whois_lookup(target.replace("http://","").replace("https://",""))

    print("\n[ ENUMERATION ]")
    subdomain_enum(target.replace("http://","").replace("https://",""))
    banner_grab(target.replace("http://","").replace("https://",""))

    print("\n[ SECURITY SCAN ]")
    nmap_scan(target)
    sensitive_files(target)
    sql_test(target)

    print("\n[ INTELLIGENCE ]")
    crawler(target)
    social_links(target)

    print("\n[ CMS DETECTION ]")
    cms_detect(target)


# =========================
# ▶ Entry
# =========================
if __name__ == "__main__":
    banner()
    target = input("Enter Target (https://example.com): ")
    run(target)
