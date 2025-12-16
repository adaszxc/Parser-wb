# Забирает данные с сайта, диагностирует трафик

#============================= СЕТЕВАЯ ДИАГНОСТИКА =============================
# Суммирование трафика (upload+download) по имени функции и общий итог.

from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import quote

from playwright.sync_api import Page, Response

from config import (
    BROWSER_PAGE_LOAD_TIMEOUT_MS,
    WB_CARDS_DETAIL_BASE,
    WB_QUERY,
    WB_SEARCH_API_BASE,
)



@dataclass
class _NetBucket:
    uploaded: int = 0
    downloaded: int = 0

    @property
    def total(self) -> int:
        return self.uploaded + self.downloaded


@dataclass
class _NetUsage:
    buckets: dict[str, _NetBucket] = field(default_factory=dict)

    def add(self, func_name: str, *, uploaded: int = 0, downloaded: int = 0) -> None:
        if uploaded <= 0 and downloaded <= 0:
            return
        b = self.buckets.setdefault(func_name, _NetBucket())
        if uploaded > 0:
            b.uploaded += uploaded
        if downloaded > 0:
            b.downloaded += downloaded

    def total(self) -> int:
        return sum(b.total for b in self.buckets.values())

    def _fmt(self, n_bytes: int) -> str:
        kb = 1024
        mb = 1024 * 1024
        if n_bytes >= mb:
            return f"{n_bytes / mb:.1f} mb"
        return f"{int(round(n_bytes / kb))} kb"

    def print_summary(self) -> None:
        print("NETWORK USAGE SUMMARY")
        print(f"Total - {self._fmt(self.total())}")

        items = sorted(self.buckets.items(), key=lambda kv: kv[1].total, reverse=True)
        for func_name, b in items:
            if b.total <= 0:
                continue
            print(f"{func_name} - {self._fmt(b.total)}")


_WB_NET = _NetUsage()


def wb_net_print_summary() -> None:
    _WB_NET.print_summary()


def _wb_resp_size_bytes(resp: Response) -> int:
    h = resp.headers.get("content-length")
    if isinstance(h, str):
        try:
            return max(0, int(h))
        except ValueError:
            pass
    try:
        return len(resp.body())
    except Exception:
        return 0


#=============================== WB RAW API ===================================
# Получение сырых JSON-ответов Wildberries без обработки.


# Возвращает массив products из search API
def wb_scrape_search_products(page: Page) -> list[dict]:
    func = "wb_scrape_search_products"

    resp = page.request.get(
        WB_SEARCH_API_BASE + quote(WB_QUERY),
        timeout=BROWSER_PAGE_LOAD_TIMEOUT_MS,
    )
    if not resp.ok:
        raise RuntimeError(f"search: http {resp.status}")

    _WB_NET.add(func, downloaded=_wb_resp_size_bytes(resp))

    search_json = resp.json()
    products = search_json.get("products")
    if not isinstance(products, list):
        raise RuntimeError("search: нет массива products[] в JSON")

    return products



# По одному id запрашивает detail API и возвращает JSON-ответ
def wb_scrape_card_detail(page: Page, nm_id: int) -> dict:
    func = "wb_scrape_card_detail"
    resp = page.request.get(
        WB_CARDS_DETAIL_BASE + str(nm_id),
        timeout=BROWSER_PAGE_LOAD_TIMEOUT_MS,
    )
    if not resp.ok:
        raise RuntimeError(f"cards: http {resp.status} для id={nm_id}")

    _WB_NET.add(func, downloaded=_wb_resp_size_bytes(resp))
    return resp.json()
