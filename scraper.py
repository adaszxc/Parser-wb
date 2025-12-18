# Достает данные карточек с WB через API

from playwright.sync_api import Page
from settings import (
    BROWSER_PAGE_LOAD_TIMEOUT_MS,
    WB_CARDS_DETAIL_BASE,
)
from net_usage import add_scripted_response, register_scripted_prefix

# Регистрация скриптового запроса для исключения из браузерного трафика
register_scripted_prefix("wb_scrape_card_detail", WB_CARDS_DETAIL_BASE)


# Возвращает JSON карточки по nm_id (идентификатор конкретной карточки).
def wb_scrape_card_detail(page: Page, nm_id: int) -> dict:
    func = "wb_scrape_card_detail"
    resp = page.request.get(
        WB_CARDS_DETAIL_BASE + str(nm_id),
        timeout=BROWSER_PAGE_LOAD_TIMEOUT_MS,
    )
    if not resp.ok:
        raise RuntimeError(f"cards: http {resp.status} для id={nm_id}")

    add_scripted_response(resp, func)
    return resp.json()
