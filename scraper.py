# Забирает данные с сайта, диагностирует трафик

#============================= СЕТЕВАЯ ДИАГНОСТИКА =============================
# Суммирование трафика (upload+download) по имени функции и общий итог.

from playwright.sync_api import Page

from config import (
    BROWSER_PAGE_LOAD_TIMEOUT_MS,
    WB_CARDS_DETAIL_BASE,
)
from net_usage import add_api_response




# По одному id запрашивает detail API и возвращает JSON-ответ
def wb_scrape_card_detail(page: Page, nm_id: int) -> dict:
    func = "wb_scrape_card_detail"
    resp = page.request.get(
        WB_CARDS_DETAIL_BASE + str(nm_id),
        timeout=BROWSER_PAGE_LOAD_TIMEOUT_MS,
    )
    if not resp.ok:
        raise RuntimeError(f"cards: http {resp.status} для id={nm_id}")

    add_api_response(resp, func)
    return resp.json()

