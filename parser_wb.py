from pathlib import Path
from urllib.parse import quote

from playwright.sync_api import Error, Page, sync_playwright


#===================================== CONFIG ===================================
# Редактируемые параметры.

# --------------------------- CONFIG: BROWSER EMULATOR --------------------------
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
BROWSER_PAGE_LOAD_TIMEOUT_MS = 60000  # Таймаут загрузки/запросов в миллисекундах.

# ----------------------------- CONFIG: WB SCRAPER ------------------------------
# Параметры поиска и извлечения списка товаров из выдачи.

WB_QUERY = "носки мужские"  # Поисковый запрос.
WB_SEARCH_API_PART = "/__internal/u-search/exactmatch/ru/common/v18/search"  # Маркер URL search API.
WB_SEARCH_ENTRYPOINT_BASE = "https://www.wildberries.ru/catalog/0/search.aspx?search="  # Страница поиска.

WB_CARDS_DETAIL_BASE = (  # Detail API карточки по одному nm.
    "https://www.wildberries.ru/__internal/u-card/cards/v4/detail"
    "?appType=1&curr=rub&dest=-971647&spp=30"
    "&hide_vflags=4294967296&hide_dtype=9%3B11&ab_testing=false&lang=ru&nm="
)

# ------------------------------ CONFIG: WB PARSER ------------------------------
# Правила выбора данных из полученных JSON.

WB_TOP_N = 10  # Берём products[0..N-1] без фильтрации.
WB_PRICE_SELECT_MODE = "min"  # "min" — минимальная цена по всем sizes[].

# ------------------------------ CONFIG: WB OUTPUT ------------------------------
# Параметры файлового вывода.

OUT_NAMES_FILE = "wb_first_10_names.txt"  # Файл только с названиями.
OUT_NAMES_PRICES_FILE = "wb_first_10_names_prices.txt"  # Файл с названиями и ценами.
MODE_OUTPUT_WITH_PRICES = 1  # 0 — сохранить только имена, 1 — сохранить имена + цены.


# ================================= BROWSER EMULATOR ============================
# Запуск headful Chromium с persistent-профилем и удержанием окна.


# Запускает браузер, открывает стартовую страницу, сохраняет результат и удерживает окно открытым.
def main() -> None:
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=BROWSER_PROFILE_DIR,
            headless=BROWSER_HEADLESS,
            args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
            user_agent=BROWSER_USER_AGENT,
            locale="ru-RU",
            viewport=BROWSER_VIEWPORT,
        )

        page = context.new_page()
        page.goto(
            BROWSER_START_URL,
            wait_until="domcontentloaded",
            timeout=BROWSER_PAGE_LOAD_TIMEOUT_MS,
        )

        products = wb_scrape_search_products(page)

        if MODE_OUTPUT_WITH_PRICES:
            ids = wb_parse_first_ids(products, WB_TOP_N)
            rows = wb_scrape_cards_and_parse_names_prices(page, ids)
            wb_save_names_prices(rows)
            print(f"Файл сохранён: {OUT_NAMES_PRICES_FILE}")
        else:
            names = wb_parse_first_names(products, WB_TOP_N)
            wb_save_names(names)
            print(f"Файл сохранён: {OUT_NAMES_FILE}")

        print("Закрой браузер вручную, либо нажми Enter в терминале, чтобы завершить скрипт.")

        try:
            input()
        finally:
            try:
                context.close()
            except Error:
                pass


# ================================= WB SCRAPER ==================================
# Получение сырых JSON-ответов Wildberries без обработки.


# Возвращает массив products из search API
def wb_scrape_search_products(page: Page) -> list[dict]:
    search_entrypoint = WB_SEARCH_ENTRYPOINT_BASE + quote(WB_QUERY)

    with page.expect_response(
        lambda r: (WB_SEARCH_API_PART in r.url) and (r.status == 200),
        timeout=BROWSER_PAGE_LOAD_TIMEOUT_MS,
    ) as resp_info:
        page.goto(search_entrypoint, wait_until="domcontentloaded", timeout=BROWSER_PAGE_LOAD_TIMEOUT_MS)

    search_json = resp_info.value.json()
    products = search_json.get("products")
    if not isinstance(products, list):
        raise RuntimeError("search: нет массива products[] в JSON")

    return products


# По одному id запрашивает detail API и возвращает JSON-ответ
def wb_scrape_card_detail(page: Page, nm_id: int) -> dict:
    resp = page.request.get(
        WB_CARDS_DETAIL_BASE + str(nm_id),
        timeout=BROWSER_PAGE_LOAD_TIMEOUT_MS,
    )
    if not resp.ok:
        raise RuntimeError(f"cards: http {resp.status} для id={nm_id}")
    return resp.json()


# ================================= WB PARSER ===================================
# Извлечение и нормализация данных из JSON по требованиям текущего шага.


# Извлекает имена товаров из products[0..top_n-1] без фильтрации
def wb_parse_first_names(products: list[dict], top_n: int) -> list[str]:
    if len(products) < top_n:
        raise RuntimeError(f"search: products меньше чем {top_n}: {len(products)}")

    names: list[str] = []
    for i in range(top_n):
        item = products[i]
        name = item.get("name") if isinstance(item, dict) else None
        if not isinstance(name, str):
            raise RuntimeError(f"search: products[{i}].name не строка: {name!r}")
        names.append(name)

    return names


# Извлекает id товаров из products[0..top_n-1] без фильтрации
def wb_parse_first_ids(products: list[dict], top_n: int) -> list[int]:
    if len(products) < top_n:
        raise RuntimeError(f"search: products меньше чем {top_n}: {len(products)}")

    ids: list[int] = []
    for i in range(top_n):
        item = products[i]
        nm_id = item.get("id") if isinstance(item, dict) else None
        if not isinstance(nm_id, int):
            raise RuntimeError(f"search: products[{i}].id не int: {nm_id!r}")
        ids.append(nm_id)

    return ids


# Возвращает (name, basic_u, wallet_u) из карточки, выбирая цены по правилам WB_PRICE_SELECT_MODE
def wb_parse_card_name_prices(cards_json: dict, nm_id: int) -> dict:
    data = cards_json.get("data")
    if isinstance(data, dict) and isinstance(data.get("products"), list):
        cards_products = data["products"]
    elif isinstance(cards_json.get("products"), list):
        cards_products = cards_json["products"]
    else:
        out_debug = Path(__file__).resolve().parent / "wb_cards_raw.json"
        out_debug.write_text(str(cards_json), encoding="utf-8")
        raise RuntimeError(f"cards: не найден products[] для id={nm_id}; сохранено wb_cards_raw.json")

    p_item = cards_products[0] if cards_products and isinstance(cards_products[0], dict) else None
    if not isinstance(p_item, dict):
        raise RuntimeError(f"cards: пустая карточка для id={nm_id}")

    name = p_item.get("name")
    if not isinstance(name, str):
        raise RuntimeError(f"cards: нет name для id={nm_id}")

    sizes = p_item.get("sizes")
    if not isinstance(sizes, list) or not sizes:
        raise RuntimeError(f"cards: нет sizes[] для id={nm_id}")

    basic_u: int | None = None
    wallet_u: int | None = None

    for s in sizes:
        if not isinstance(s, dict):
            continue
        price = s.get("price")
        if not isinstance(price, dict):
            continue

        b = price.get("basic")
        w = price.get("product")

        if isinstance(b, int):
            if WB_PRICE_SELECT_MODE == "min":
                basic_u = b if basic_u is None else min(basic_u, b)
            else:
                basic_u = b if basic_u is None else basic_u

        if isinstance(w, int):
            if WB_PRICE_SELECT_MODE == "min":
                wallet_u = w if wallet_u is None else min(wallet_u, w)
            else:
                wallet_u = w if wallet_u is None else wallet_u

    if basic_u is None or wallet_u is None:
        raise RuntimeError(f"cards: нет price.basic/product в sizes[] для id={nm_id}")

    return {
        "id": nm_id,
        "name": name,
        "basic": basic_u / 100,
        "wallet": wallet_u / 100,
    }


# Для списка id получает карточки и возвращает строки с именем и ценами
def wb_scrape_cards_and_parse_names_prices(page: Page, ids: list[int]) -> list[dict]:
    rows: list[dict] = []
    for nm_id in ids:
        cards_json = wb_scrape_card_detail(page, nm_id)
        row = wb_parse_card_name_prices(cards_json, nm_id)
        rows.append(row)
    return rows


# ================================= WB OUTPUT ===================================
# Сохранение результатов в файлы.


# Сохраняет имена товаров в текстовый файл рядом со скриптом
def wb_save_names(names: list[str]) -> None:
    out_path = Path(__file__).resolve().parent / OUT_NAMES_FILE
    out_path.write_text("\n".join(names) + "\n", encoding="utf-8")


# Сохраняет имена и цены товаров в текстовый файл рядом со скриптом
def wb_save_names_prices(rows: list[dict]) -> None:
    out_path = Path(__file__).resolve().parent / OUT_NAMES_PRICES_FILE

    lines: list[str] = []
    for r in rows:
        lines.append(f'{r["name"]} | basic={r["basic"]} | wallet={r["wallet"]}')

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
