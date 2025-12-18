# Сохраняет данные в нужный формат

from messages import REPORT_LINE_TEMPLATE
from settings import OUT_NAMES_PRICES_FILE, REPORT_OUTPUT_DIR


# Сохраняет имена и цены товаров в текстовый файл (в папке срипта)
def wb_save_names_prices(rows: list[dict]) -> None:
    out_path = REPORT_OUTPUT_DIR / OUT_NAMES_PRICES_FILE

    lines: list[str] = []
    for i, r in enumerate(rows, start=1):
        lines.append(
            f"{i}. " + REPORT_LINE_TEMPLATE.format(
                name=r["name"],
                basic=r["basic"],
                wallet=r["wallet"],
            )
        )

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
