import json
from urllib.parse import quote

from playwright.sync_api import sync_playwright


#================================== НАСТРОЙКИ ==================================
# Базовые параметры запроса и файлового вывода.
URL_HOME = "https://www.wildberries.ru/"
QUERY = "носки мужские"
PROFILE_DIR = "wb_profile"
from pathlib import Path

OUT_FILE = str(Path(__file__).resolve().parent / "products.txt")


SEARCH_ENTRYPOINT = "https://www.wildberries.ru/catalog/0/search.aspx?search=" + quote(QUERY)
SEARCH_API_PART = "/__internal/u-search/exactmatch/ru/common/v18/search"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


#================================= PLAYWRIGHT ==================================
# Запуск headful Chromium с постоянным профилем, чтобы не терять куки/состояние.
def main() -> None:
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
            user_agent=USER_AGENT,
            locale="ru-RU",
            viewport={"width": 1280, "height": 800},
        )
        page = context.new_page()


#================================ СБОР PRODUCTS ================================
# Открытие поиска и перехват JSON-ответа, который делает сам сайт.
        page.goto(URL_HOME, wait_until="domcontentloaded", timeout=60000)

        try:
            with page.expect_response(
                lambda r: (SEARCH_API_PART in r.url) and (r.status == 200),
                timeout=60000,
            ) as resp_info:
                page.goto(SEARCH_ENTRYPOINT, wait_until="domcontentloaded", timeout=60000)

            resp = resp_info.value
            data = resp.json()
            products = data.get("products")

            if not isinstance(products, list):
                raise RuntimeError("No products[] in response JSON")

            with open(OUT_FILE, "w", encoding="utf-8") as f:
                for product in products:
                    f.write(json.dumps(product, ensure_ascii=False) + "\n")

            print(f"OK: сохранено {len(products)} товаров в {OUT_FILE}")
            print(f"CWD: {Path.cwd()}")


            print(f"OK: сохранено {len(products)} товаров в {OUT_FILE}")

        except Exception as e:
            print(f"ERR: products не получены: {e}")


#=============================== УДЕРЖАНИЕ ОКНА ================================
# Держим окно открытым, пока пользователь не закроет браузер вручную.
        print("Окно удерживается. Закрой браузер вручную, либо нажми Enter в терминале, чтобы завершить скрипт.")
        from playwright.sync_api import Error

        try:
            input()
        finally:
            try:
                context.close()
            except Error:
                pass

if __name__ == "__main__":
    main()
