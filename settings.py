# Настройки поведения приложения.

from pathlib import Path

# =================================== RUNTIME ===================================
# Настройки поведения (во время работы программы).

LOG_MODE = 1  # 0 — выводить ошибки сразу (в терминале), 1 - выводить ошибку при завершении программы (в терминале).

# Параметры запуска браузера
BROWSER_START_URL = "https://www.wildberries.ru/"  # Стартовая страница при запуске браузера.
BROWSER_PROFILE_DIR = "wb_profile"  # Путь к браузерному профилю (cookies, storage).
BROWSER_HEADLESS = False  # Запуск браузера: False — с окном, True — без окна.
BROWSER_VIEWPORT = {"width": 1280, "height": 800}  # Размер viewport (размер сайта всегда такой, независимо от экрана и окна).
BROWSER_PAGE_LOAD_TIMEOUT_MS = 60000  # Таймаут одной операции прогрева (не всего прогрева)


# Параметры прогрева браузерного профиля перед началом работы.
WB_WARMUP_ENABLED = True # Выполнять прогрев профиля при запуске браузера.
WB_WARMUP_DELAY_MIN_MS = 1000  # Минимальная задержка ожидания на стартовой странице.
WB_WARMUP_DELAY_MAX_MS = 1200  # Максимальная задержка ожидания на стартовой странице.
WB_WARMUP_MAX_ATTEMPTS = 5  # Максимальное количество попыток прогрева.
WB_WARMUP_RETRY_DELAY_S = 2  # Пауза между повторами прогрева.


# Параметры поиска и извлечения списка товаров из выдачи.
WB_QUERY = "носки мужские"  # Поисковый запрос.
WB_SEARCH_API_URL_SUBSTRING = "/__internal/u-search/exactmatch/ru/common/v18/search"  # Прогрев считается успешным, если получен ответ search API WB со статусом 200
WB_SEARCH_ENTRYPOINT_BASE = "https://www.wildberries.ru/catalog/0/search.aspx?search="  # Страница поиска.
WB_CARDS_DETAIL_BASE = (  # Сюда подставляется id конкретной карточки товара
    "https://www.wildberries.ru/__internal/u-card/cards/v4/detail"
    "?appType=1&curr=rub&dest=-971647&spp=30"
    "&hide_vflags=4294967296&hide_dtype=9%3B11&ab_testing=false&lang=ru&nm="
)


# Правила выбора данных из полученных JSON.
WB_TOP_N = 10  # Количество собираемых карточек


# ==================================== OUTPUT ===================================
# Настройки вывода и завершения программы


# Параметры файлового вывода.
OUT_NAMES_PRICES_FILE = "wb_first_10_names_prices.txt"  # Файл с названиями и ценами.
REPORT_OUTPUT_DIR = Path(__file__).resolve().parent  # Каталог вывода результатов (рядом со скриптом)
CONTROLLER_WAIT_FOR_EXIT = True # Ожидать ввод перед завершением скрипта

