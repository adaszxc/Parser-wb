"""Конфигурация параметров запуска и обработки Wildberries.

Все редактируемые настройки собраны здесь для дальнейшего использования модулями
приложения."""

from pathlib import Path

# ============================== CONFIG: DIAGNOSTICS =============================
# Режим вывода ошибок.

LOG_MODE = 1  # 0 — печатать ошибки сразу, 1 - печатать ошибки в конце.

# ================================ CONFIG: RANDOM ===============================
# Управление генератором случайных чисел.

RANDOM_SEED = None  # Значение для random.seed.

# =========================== CONFIG: BROWSER EMULATOR ==========================
# Параметры запуска Playwright и окружения браузера.

BROWSER_START_URL = "https://www.wildberries.ru/"  # Стартовая страница при запуске браузера.
BROWSER_PROFILE_DIR = "wb_profile"  # Каталог persistent-профиля Chromium (cookies, localStorage, сессия).
BROWSER_USER_AGENT = (  # User-Agent, с которым браузер представляется сайту.
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)
BROWSER_HEADLESS = False  # False — с окном, True — без окна.
BROWSER_VIEWPORT = {"width": 1280, "height": 800}  # Размер viewport браузера.
BROWSER_LOCALE = "ru-RU"  # Локаль браузера.
BROWSER_LAUNCH_ARGS = [  # Доп. параметры запуска Chromium.
    "--disable-blink-features=AutomationControlled",
    "--start-maximized",
]
BROWSER_PAGE_LOAD_TIMEOUT_MS = 60000  # Таймаут загрузки/запросов в миллисекундах.

# --------------------------- CONFIG: WB PROFILE WARMUP --------------------------
# Параметры прогрева браузерного профиля перед началом работы.

WB_WARMUP_ENABLED = True  # Выполнять прогрев профиля при запуске браузера.
WB_WARMUP_DELAY_MIN_MS = 1000 # Минимальная задержка ожидания на стартовой странице.
WB_WARMUP_DELAY_MAX_MS = 1200 # Максимальная задержка ожидания на стартовой странице.
WB_WARMUP_MAX_ATTEMPTS = 5  # Максимальное количество попыток прогрева.
WB_WARMUP_RETRY_DELAY_S = 1.2  # Пауза между повторами прогрева.


# ============================= CONFIG: WB SCRAPER ==============================
# Параметры поиска и извлечения списка товаров из выдачи.

WB_QUERY = "носки мужские"  # Поисковый запрос.
WB_SEARCH_API_URL_SUBSTRING = "/__internal/u-search/exactmatch/ru/common/v18/search"  # Маркер URL search API.
WB_SEARCH_ENTRYPOINT_BASE = "https://www.wildberries.ru/catalog/0/search.aspx?search="  # Страница поиска.
WB_CARDS_DETAIL_BASE = (  # Detail API карточки по одному nm.
    "https://www.wildberries.ru/__internal/u-card/cards/v4/detail"
    "?appType=1&curr=rub&dest=-971647&spp=30"
    "&hide_vflags=4294967296&hide_dtype=9%3B11&ab_testing=false&lang=ru&nm="
)


# =============================== CONFIG: PARSER ================================
# Правила выбора данных из полученных JSON.

WB_TOP_N = 10  # Берём products[0..N-1] без фильтрации.
WB_PRICE_SELECT_MODE = "min"  # "min" — минимальная цена по всем sizes[].


# ================================ CONFIG: REPORT ===============================
# Параметры файлового вывода.

OUT_NAMES_PRICES_FILE = "wb_first_10_names_prices.txt"  # Файл с названиями и ценами.
REPORT_OUTPUT_DIR = Path(__file__).resolve().parent  # Каталог вывода результатов.
REPORT_LINE_TEMPLATE = '{name} | без скидок={basic} | со скидкой={wallet}'
NET_USAGE_HEADER = "Трафик что WB отдал:"
NET_USAGE_TOTAL_TEMPLATE = "Всего - {kb} КБ"
NET_USAGE_NON_SCRIPTED_TEMPLATE = "Не скриптовые - {kb} КБ"
NET_USAGE_SCRIPTED_HEADER = "Скриптовые запросы:"
NET_USAGE_SCRIPTED_ROW_TEMPLATE = "- {name} - {kb} КБ"
LOGGER_NO_ERRORS = "Ошибок нет"
LOGGER_NON_FATAL_HEADER = "Некритичные ошибки:"
LOGGER_IMMEDIATE_ERROR_TEMPLATE = "[{where}] {message}"
LOGGER_IMMEDIATE_ERROR_WITH_EXC_TEMPLATE = "[{where}] {message}: {exc_type}: {exc_text}"
LOGGER_SUMMARY_ROW_TEMPLATE = "{ts} {prefix} [{where}] {message}"
LOGGER_SUMMARY_ROW_WITH_EXC_TEMPLATE = "{ts} {prefix} [{where}] {message}: {exc_type}: {exc_text}"
LOGGER_FATAL_PREFIX = "FATAL"
LOGGER_ERROR_PREFIX = "ERROR"
CONTROLLER_FILE_SAVED_TEMPLATE = "Файл сохранён: {filename}"
CONTROLLER_EXIT_PROMPT = "Нажми Enter, чтобы завершить скрипт."
CONTROLLER_WAIT_FOR_EXIT = True
