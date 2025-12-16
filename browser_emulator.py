"""Запуск headful Chromium с persistent-профилем и удержанием окна."""

from playwright.sync_api import BrowserContext, Error, Page, Playwright, sync_playwright

from config import (
    BROWSER_HEADLESS,
    BROWSER_PAGE_LOAD_TIMEOUT_MS,
    BROWSER_PROFILE_DIR,
    BROWSER_START_URL,
    BROWSER_USER_AGENT,
    BROWSER_VIEWPORT,
)


def launch_browser_context() -> tuple[Playwright, BrowserContext, Page]:
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
    page.goto(
        BROWSER_START_URL,
        wait_until="domcontentloaded",
        timeout=BROWSER_PAGE_LOAD_TIMEOUT_MS,
    )

    return playwright, context, page


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
