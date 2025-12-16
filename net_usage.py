from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import urlparse

from playwright.sync_api import Page, Response

def _req_upload_size_bytes(resp: Response) -> int:
    try:
        req = resp.request
        h = req.headers.get("content-length")
        if isinstance(h, str):
            try:
                return max(0, int(h))
            except ValueError:
                return 0
    except Exception:
        return 0
    return 0



@dataclass
class _NetBucket:
    uploaded: int = 0
    downloaded: int = 0

    @property
    def total(self) -> int:
        return self.uploaded + self.downloaded


@dataclass
class NetUsage:
    buckets: dict[str, _NetBucket] = field(default_factory=dict)

    def add(self, bucket: str, *, uploaded: int = 0, downloaded: int = 0) -> None:
        if uploaded <= 0 and downloaded <= 0:
            return
        b = self.buckets.setdefault(bucket, _NetBucket())
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
        for name, b in items:
            if b.total <= 0:
                continue
            print(f"{name} - {self._fmt(b.total)}")


WB_NET = NetUsage()


def wb_net_print_summary() -> None:
    WB_NET.print_summary()


def _resp_download_size_bytes(resp: Response, *, allow_body_fallback: bool) -> int:
    h = resp.headers.get("content-length")
    if isinstance(h, str):
        try:
            return max(0, int(h))
        except ValueError:
            return 0

    if not allow_body_fallback:
        return 0

    try:
        return len(resp.body())
    except Exception:
        return 0


def attach_wb_traffic_counter(page: Page) -> None:
    try:
        cdp = page.context.new_cdp_session(page)
        cdp.send("Network.enable")

        req_meta: dict[str, tuple[str, int]] = {}

        def on_request_will_be_sent(params: dict) -> None:
            request_id = params.get("requestId")
            req = params.get("request") or {}
            url = req.get("url")
            if not isinstance(request_id, str) or not isinstance(url, str):
                return

            try:
                u = urlparse(url)
                host = (u.hostname or "").lower()
                if not host.endswith("wildberries.ru"):
                    return
            except Exception:
                return

            headers = req.get("headers") or {}
            up = 0
            if isinstance(headers, dict):
                h = headers.get("content-length")
                if isinstance(h, str):
                    try:
                        up = max(0, int(h))
                    except ValueError:
                        up = 0

            req_meta[request_id] = (url, up)

        def on_loading_finished(params: dict) -> None:
            request_id = params.get("requestId")
            if not isinstance(request_id, str):
                return

            meta = req_meta.pop(request_id, None)
            if meta is None:
                return

            _, uploaded = meta

            downloaded = params.get("encodedDataLength")
            if not isinstance(downloaded, int):
                return

            WB_NET.add("wb_browser", uploaded=uploaded, downloaded=max(0, downloaded))

        def on_loading_failed(params: dict) -> None:
            request_id = params.get("requestId")
            if isinstance(request_id, str):
                req_meta.pop(request_id, None)

        cdp.on("Network.requestWillBeSent", on_request_will_be_sent)
        cdp.on("Network.loadingFinished", on_loading_finished)
        cdp.on("Network.loadingFailed", on_loading_failed)

        return

    except Exception:
        pass

    def on_response(resp: Response) -> None:
        try:
            u = urlparse(resp.url)
            host = (u.hostname or "").lower()
            if not host.endswith("wildberries.ru"):
                return

            downloaded = _resp_download_size_bytes(resp, allow_body_fallback=False)
            uploaded = _req_upload_size_bytes(resp)
            WB_NET.add("wb_browser", uploaded=uploaded, downloaded=downloaded)
        except Exception:
            return

    page.on("response", on_response)




def add_api_response(resp: Response, bucket: str) -> None:
    downloaded = _resp_download_size_bytes(resp, allow_body_fallback=True)
    uploaded = _req_upload_size_bytes(resp)
    WB_NET.add(bucket, uploaded=uploaded, downloaded=downloaded)
