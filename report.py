# Сохраняет данные в нужный формат

from config import OUT_NAMES_PRICES_FILE, REPORT_LINE_TEMPLATE, REPORT_OUTPUT_DIR


# Сохраняет имена и цены товаров в текстовый файл (в папке срипта)
def wb_save_names_prices(rows: list[dict]) -> None:
    out_path = REPORT_OUTPUT_DIR / OUT_NAMES_PRICES_FILE

    lines: list[str] = []
    for r in rows:
        lines.append(
            REPORT_LINE_TEMPLATE.format(name=r["name"], basic=r["basic"], wallet=r["wallet"])
        )

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
