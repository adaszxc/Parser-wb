# Взаимодейсвие модулей между собой.

from browser_emulator import close_browser, launch_browser_context
from config import MODE_OUTPUT_WITH_PRICES, OUT_NAMES_FILE, OUT_NAMES_PRICES_FILE, WB_TOP_N
from parser import wb_parse_card_name_prices, wb_parse_first_ids, wb_parse_first_names
from report import wb_save_names, wb_save_names_prices
from scraper import (
    wb_net_print_summary,
    wb_scrape_card_detail,
    wb_scrape_search_products,
)


def main() -> None:
    playwright = None
    context = None

    try:
        playwright, context, page = launch_browser_context()

        products = wb_scrape_search_products(page)

        if MODE_OUTPUT_WITH_PRICES:
            ids = wb_parse_first_ids(products, WB_TOP_N)

            rows: list[dict] = []
            for nm_id in ids:
                card_json = wb_scrape_card_detail(page, nm_id)
                rows.append(wb_parse_card_name_prices(card_json, nm_id))

            wb_save_names_prices(rows)
            print(f"Файл сохранён: {OUT_NAMES_PRICES_FILE}")
        else:
            names = wb_parse_first_names(products, WB_TOP_N)
            wb_save_names(names)
            print(f"Файл сохранён: {OUT_NAMES_FILE}")

        print()  # пустая строка перед NETWORK USAGE SUMMARY
        wb_net_print_summary()
        print()  # пустая строка после NETWORK USAGE SUMMARY

        print("Закрой браузер вручную, либо нажми Enter в терминале, чтобы завершить скрипт.")
        input()

    finally:
        close_browser(playwright, context)
