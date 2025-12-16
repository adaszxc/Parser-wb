"""Модуль для сохранения результатов парсинга в файлы."""

from pathlib import Path

from config import OUT_NAMES_FILE, OUT_NAMES_PRICES_FILE


# Сохраняет имена товаров в текстовый файл рядом со скриптом
def wb_save_names(names: list[str]) -> None:
    out_path = Path(__file__).resolve().parent / OUT_NAMES_FILE
    out_path.write_text("\n".join(names) + "\n", encoding="utf-8")


# Сохраняет имена и цены товаров в текстовый файл рядом со скриптом
def wb_save_names_prices(rows: list[dict]) -> None:
    out_path = Path(__file__).resolve().parent / OUT_NAMES_PRICES_FILE

    lines: list[str] = []
    for r in rows:
        lines.append(
            f'{r["name"]} | без скидок={r["basic"]} | со скидкой={r["wallet"]}'
        )

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
