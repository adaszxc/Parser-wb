# Запуск Chromium с persistent-профилем, прогрев профиля и управление жизненным циклом браузера.

import os
import time
import random
from urllib.parse import quote

from playwright.sync_api import BrowserContext, Error, Page, Playwright, sync_playwright

from config import (
    BROWSER_HEADLESS,
    BROWSER_PAGE_LOAD_TIMEOUT_MS,
    BROWSER_PROFILE_DIR,
    BROWSER_START_URL,
    BROWSER_USER_AGENT,
    BROWSER_VIEWPORT,
    WB_QUERY,
    WB_SEARCH_API_PART,
    WB_SEARCH_ENTRYPOINT_BASE,
    WB_WARMUP_DELAY_MAX_MS,
    WB_WARMUP_DELAY_MIN_MS,
    WB_WARMUP_ENABLED,
    WB_WARMUP_MAX_ATTEMPTS,
)





#================================ PROFILE DIRECTORY ==============================
# Проверка и подготовка директории persistent-профиля браузера.

def _ensure_profile_dir(path: str) -> None:
    if os.path.exists(path):
        if not os.path.isdir(path):
            raise RuntimeError(f"Путь '{path}' существует, но это не директория")
        return

    os.makedirs(path, exist_ok=True)


#===================================== WARMUP ===================================
# Прогрев профиля WB для установки cookies и начального состояния.

def _warmup_wb(page: Page) -> list[dict]:
    if not WB_WARMUP_ENABLED:
        return []

    last_err: Exception | None = None

    for attempt in range(1, WB_WARMUP_MAX_ATTEMPTS + 1):
        try:
            page.goto(
                BROWSER_START_URL,
                wait_until="domcontentloaded",
                timeout=BROWSER_PAGE_LOAD_TIMEOUT_MS,
            )

            delay_ms = random.randint(WB_WARMUP_DELAY_MIN_MS, WB_WARMUP_DELAY_MAX_MS)
            page.wait_for_timeout(delay_ms)

            search_entrypoint = WB_SEARCH_ENTRYPOINT_BASE + quote(WB_QUERY)
            with page.expect_response(
                lambda r: (WB_SEARCH_API_PART in r.url) and (r.status == 200),
                timeout=BROWSER_PAGE_LOAD_TIMEOUT_MS,
            ) as resp_info:
                page.goto(
                    search_entrypoint,
                    wait_until="domcontentloaded",
                    timeout=BROWSER_PAGE_LOAD_TIMEOUT_MS,
                )

            resp = resp_info.value
            search_json = resp.json()
            products = search_json.get("products")
            if not isinstance(products, list):
                raise RuntimeError("warmup: search без products[]")

            return products

        except Exception as e:
            last_err = e
            print(f"[warmup] failed, retry {attempt}/{WB_WARMUP_MAX_ATTEMPTS}")
            time.sleep(1.2)

    raise RuntimeError(
        f"warmup: не удалось прогреть профиль за {WB_WARMUP_MAX_ATTEMPTS} попыток: {last_err}"
    ) from last_err




#=============================== BROWSER LIFECYCLE ===============================
# Запуск и корректное завершение persistent-контекста Chromium.

def launch_browser_context() -> tuple[Playwright, BrowserContext, Page, list[dict]]:
    _ensure_profile_dir(BROWSER_PROFILE_DIR)

    playwright = sync_playwright().start()
    context = playwright.chromium.launch_persistent_context(
        user_data_dir=BROWSER_PROFILE_DIR,
        headless=BROWSER_HEADLESS,
        args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
        user_agent=BROWSER_USER_AGENT,
        locale="ru-RU",
        viewport=BROWSER_VIEWPORT,
    )

    page = context.new_page()
    products = _warmup_wb(page)

    return playwright, context, page, products




def close_browser(playwright: Playwright | None, context: BrowserContext | None) -> None:
    if context is not None:
        try:
            context.close()
        except Error:
            pass

    if playwright is not None:
        try:
            playwright.stop()
        except Error:
            pass
