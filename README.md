# ⚡ KOCMOC1337 Network Testing Toolkit

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/AsyncIO-Powered-green?style=for-the-badge">
  <img src="https://img.shields.io/badge/Terminal-UI-purple?style=for-the-badge">
</p>

<p align="center">
  <b>Advanced asynchronous network testing framework with a custom terminal interface.</b>
</p>

---

## 🚀 About Project

**KOCMOC1337 Network Testing Toolkit** — Python-проект с красивым терминальным интерфейсом, асинхронной архитектурой и системой статистики.

Проект разработан для изучения сетевых технологий, работы с асинхронными запросами и тестирования собственных сервисов в контролируемой среде.

Главные особенности:

- ⚡ Асинхронная архитектура
- 🎨 Кастомный Terminal UI
- 📊 Система статистики
- 🗂 История операций
- 🔌 Управление прокси
- ⚙️ Гибкая конфигурация

---

# ✨ Features

## 🎨 Custom Terminal Interface

Уникальный интерфейс:

- ASCII Banner **KOCMOC1337**
- Анимация появления логотипа
- Цветной вывод
- Информационные панели
- Статус выполнения процессов

Пример:

```
╔══════════════════════════════════════╗
║             KOCMOC1337              ║
╠══════════════════════════════════════╣
║       Network Testing Toolkit        ║
╚══════════════════════════════════════╝
```

---

# ⚡ Async Engine

Используемые технологии:

- `asyncio`
- `aiohttp`
- `socket`
- Асинхронные задачи
- Управление потоками

Высокая производительность достигается благодаря неблокирующей архитектуре Python.

---

# 📊 Statistics System

Проект автоматически сохраняет:

- Количество запусков
- Количество операций
- Успешные результаты
- Ошибки
- Историю работы


Файлы:

```
total_stats.json
history.json
```

---

# 🔌 Proxy Manager

Система управления прокси:

Поддерживается файл:

```
proxies.txt
```

Функции:

```
[1] Add proxy manually
[2] Load proxies
[3] Show list
[4] Clear list
[5] Check proxies
```

---

# ⚙️ Configuration

Основные настройки:

```python
CONFIG = {
    "max_threads": 1000,
    "timeout": 3,
    "max_duration": 0,
    "save_results": True,
    "proxy_rotation_interval": 10
}
```

Изменение параметров доступно через встроенное меню.

---

# 📂 Project Structure

```
KOCMOC1337/
│
├── main.py
├── proxies.txt
├── history.json
├── total_stats.json
│
└── README.md
```

---

# 📦 Installation

## Requirements

- Python 3.10+
- pip


Установка зависимостей:

```bash
pip install aiohttp colorama
```


Запуск:

```bash
python main.py
```

---

# 🖥 Menu

Главное меню:

```
1. DDos Ip Address
2. View Url Ip Address
3. DDos Site Logs
4. Proxy Management
5. Total Statistics
6. History
7. Settings
99. Exit
```

---

# 🛠 Technologies

| Technology | Usage |
|-|-|
| Python | Core language |
| asyncio | Async operations |
| aiohttp | HTTP networking |
| socket | Network communication |
| JSON | Data storage |
| ANSI Colors | Terminal graphics |

---

# 📈 Future Updates

Планы развития:

- [ ] Улучшенный GUI
- [ ] Больше статистики
- [ ] Экспорт отчётов
- [ ] Расширенный логгер
- [ ] Новые модули анализа
- [ ] Улучшение интерфейса

---

# ⚠️ Disclaimer

Этот проект создан исключительно для:

✅ обучения Python  
✅ исследования сетевых технологий  
✅ тестирования собственных систем  
✅ разработки навыков программирования  


Используйте программное обеспечение только на ресурсах, где у вас есть разрешение.

Автор не несёт ответственности за неправильное использование проекта.

---

# 👤 Author

**verifactor**

Project:

```
KOCMOC1337
```

---

<p align="center">
⭐ Star the repository if you like this project ⭐
</p>
