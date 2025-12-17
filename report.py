# Сохраняет данные в нужный формат

from pathlib import Path
from config import OUT_NAMES_PRICES_FILE


# Сохраняет имена и цены товаров в текстовый файл (в папке срипта)
def wb_save_names_prices(rows: list[dict]) -> None:
    out_path = Path(__file__).resolve().parent / OUT_NAMES_PRICES_FILE

    lines: list[str] = []
    for r in rows:
        lines.append(
            f'{r["name"]} | без скидок={r["basic"]} | со скидкой={r["wallet"]}'
        )

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
