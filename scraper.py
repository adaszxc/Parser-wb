"""Модуль для получения сырых JSON-ответов Wildberries без обработки."""

from urllib.parse import quote

from playwright.sync_api import Page

from config import (
    BROWSER_PAGE_LOAD_TIMEOUT_MS,
    WB_CARDS_DETAIL_BASE,
    WB_QUERY,
    WB_SEARCH_API_PART,
    WB_SEARCH_ENTRYPOINT_BASE,
)
from parser import wb_parse_card_name_prices


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


# Для списка id получает карточки и возвращает строки с именем и ценами
def wb_scrape_cards_and_parse_names_prices(page: Page, ids: list[int]) -> list[dict]:
    rows: list[dict] = []
    for nm_id in ids:
        cards_json = wb_scrape_card_detail(page, nm_id)
        row = wb_parse_card_name_prices(cards_json, nm_id)
        rows.append(row)
    return rows
