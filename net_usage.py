# =============================== WB TRAFFIC COUNTER ===============================
# Считает объём данных, которые инфраструктура WB отдала клиенту.
# Разделяет трафик на скриптовый (явные API-вызовы) и не скриптовый (браузерные).

from __future__ import annotations
from dataclasses import dataclass, field
from urllib.parse import urlparse
from playwright.sync_api import Page, Response


# =============================== DATA MODELS ======================================

@dataclass
class _Bucket:
    bytes: int = 0


@dataclass
class WBTraffic:
    scripted: dict[str, _Bucket] = field(default_factory=dict)
    non_scripted_bytes: int = 0

    def add_scripted(self, name: str, n: int) -> None:
        if n <= 0:
            return
        b = self.scripted.setdefault(name, _Bucket())
        b.bytes += n

    def add_non_scripted(self, n: int) -> None:
        if n <= 0:
            return
        self.non_scripted_bytes += n

    def scripted_total(self) -> int:
        return sum(b.bytes for b in self.scripted.values())

    def total(self) -> int:
        return self.non_scripted_bytes + self.scripted_total()


WB_TRAFFIC = WBTraffic()
_SCRIPTED_URLS: set[str] = set()


# =============================== SIZE HELPERS =====================================

# Размер ответа в байтах, как он был передан по сети (сжатое тело).
def _encoded_response_size(resp: Response) -> int:
    try:
        h = resp.headers.get("content-length")
        if isinstance(h, str):
            return max(0, int(h))
    except Exception:
        pass
    return 0


# =============================== BROWSER HOOK =====================================

# Учитывает все браузерные ответы WB как не скриптовые.
def attach_wb_browser_counter(page: Page) -> None:
    def on_response(resp: Response) -> None:
        try:
            u = urlparse(resp.url)
            host = (u.hostname or "").lower()
            if "wildberries" not in host and "wbstatic" not in host:
                return

            # Если вдруг скриптовый ответ попал в page.on("response"), не считаем его как не скриптовый.
            if resp.url in _SCRIPTED_URLS:
                return

            n = _encoded_response_size(resp)
            WB_TRAFFIC.add_non_scripted(n)
        except Exception:
            return

    page.on("response", on_response)


# =============================== SCRIPTED API =====================================

# Учитывает ответ явного API-вызова как скриптовый.
def add_scripted_response(resp: Response, name: str) -> None:
    # Помечаем URL как скриптовый, чтобы не попал в не скриптовые при браузерном хуке.
    try:
        _SCRIPTED_URLS.add(resp.url)
    except Exception:
        pass

    n = _encoded_response_size(resp)
    if n == 0:
        try:
            n = len(resp.body())
        except Exception:
            n = 0

    WB_TRAFFIC.add_scripted(name, n)



# =============================== REPORT ===========================================

# Печатает итоговый отчёт по трафику WB.
def print_wb_traffic() -> None:
    print("Трафик что WB отдал:")
    print(f"Всего - {WB_TRAFFIC.total() // 1024} КБ")
    print(f"Не скриптовые - {WB_TRAFFIC.non_scripted_bytes // 1024} КБ")
    print("Скриптовые запросы:")
    for name, b in WB_TRAFFIC.scripted.items():
        print(f"- {name} - {b.bytes // 1024} КБ")
