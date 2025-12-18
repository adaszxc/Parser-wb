# Запуск и управление Chromium через Playwright, прогрев сессии и сохранение профиля (cookies/storage).

import os
import time
import random
from urllib.parse import quote
from playwright.sync_api import BrowserContext, Page, Playwright, sync_playwright
from net_usage import attach_wb_browser_counter
import logger
from config import (
    BROWSER_HEADLESS,
    BROWSER_PAGE_LOAD_TIMEOUT_MS,
    BROWSER_PROFILE_DIR,
    BROWSER_START_URL,
    BROWSER_USER_AGENT,
    BROWSER_VIEWPORT,
    BROWSER_LAUNCH_ARGS,
    BROWSER_LOCALE,
    WB_QUERY,
    WB_SEARCH_API_URL_SUBSTRING,
    WB_SEARCH_ENTRYPOINT_BASE,
    WB_WARMUP_DELAY_MAX_MS,
    WB_WARMUP_DELAY_MIN_MS,
    WB_WARMUP_ENABLED,
    WB_WARMUP_MAX_ATTEMPTS,
    WB_WARMUP_RETRY_DELAY_S,
)


# Проверка и создание каталога браузерного профиля (папки с cookies/storage).
def _ensure_profile_dir(path: str) -> None:
    if os.path.exists(path):
        if not os.path.isdir(path):
            raise RuntimeError(f"Путь '{path}' существует, но это не директория")
        return

    os.makedirs(path, exist_ok=True)


# Прогревает браузерную сессию.
def _warmup_wb(page: Page) -> list[dict]:
    def _fetch_products(with_delay: bool) -> list[dict]:
        page.goto(
            BROWSER_START_URL,
            wait_until="domcontentloaded",
            timeout=BROWSER_PAGE_LOAD_TIMEOUT_MS,
        )

        if with_delay:
            delay_ms = random.randint(WB_WARMUP_DELAY_MIN_MS, WB_WARMUP_DELAY_MAX_MS)
            page.wait_for_timeout(delay_ms)

        search_entrypoint = WB_SEARCH_ENTRYPOINT_BASE + quote(WB_QUERY)
        with page.expect_response(
            lambda r: (WB_SEARCH_API_URL_SUBSTRING in r.url) and (r.status == 200),
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

    if not WB_WARMUP_ENABLED:
        try:
            return _fetch_products(with_delay=False)
        except Exception as e:
            raise RuntimeError(
                "warmup отключен: первичный search не выполнен"
            ) from e

    last_err: Exception | None = None

    for attempt in range(1, WB_WARMUP_MAX_ATTEMPTS + 1):
        try:
            return _fetch_products(with_delay=True)

        except Exception as e:
            last_err = e
            logger.record_error(
                "browser_emulator:_warmup_wb",
                f"warmup failed, retry {attempt}/{WB_WARMUP_MAX_ATTEMPTS}",
                e,
            )
            time.sleep(WB_WARMUP_RETRY_DELAY_S)

    logger.record_error(
        "browser_emulator:_warmup_wb",
        f"warmup failed after {WB_WARMUP_MAX_ATTEMPTS} attempts",
        last_err,
        fatal=True,
    )
    raise RuntimeError(
        f"warmup: не удалось прогреть профиль за {WB_WARMUP_MAX_ATTEMPTS} попыток: {last_err}"
    ) from last_err


# Запускает Chromium и вызывает прогрев.
def launch_browser_context() -> tuple[Playwright, BrowserContext, Page, list[dict]]:
    _ensure_profile_dir(BROWSER_PROFILE_DIR)

    playwright = sync_playwright().start()
    context = playwright.chromium.launch_persistent_context(
        user_data_dir=BROWSER_PROFILE_DIR,
        headless=BROWSER_HEADLESS,
        args=BROWSER_LAUNCH_ARGS,
        user_agent=BROWSER_USER_AGENT,
        locale=BROWSER_LOCALE,
        viewport=BROWSER_VIEWPORT,
    )

    page = context.new_page()
    attach_wb_browser_counter(page)
    products = _warmup_wb(page)


    return playwright, context, page, products


# Закрывает Chromium.
def close_browser(playwright: Playwright | None, context: BrowserContext | None) -> None:
    if context is not None:
        try:
            context.close()
        except Exception as e:
            logger.record_error("browser_emulator:close_browser", "failed to close context", e)

    if playwright is not None:
        try:
            playwright.stop()
        except Exception as e:
            logger.record_error("browser_emulator:close_browser", "failed to stop playwright", e)
