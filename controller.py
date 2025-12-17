# Взаимодейсвие модулей между собой.

from browser_emulator import close_browser, launch_browser_context
from config import OUT_NAMES_PRICES_FILE, WB_TOP_N
from parser import wb_parse_card_name_prices, wb_parse_first_ids
from report import wb_save_names_prices
from net_usage import wb_net_print_summary
from scraper import wb_scrape_card_detail
import logger


def main() -> None:
    playwright = None
    context = None

    try:
        playwright, context, page, products = launch_browser_context()


        ids = wb_parse_first_ids(products, WB_TOP_N)

        rows: list[dict] = []
        for nm_id in ids:
            card_json = wb_scrape_card_detail(page, nm_id)
            try:
                rows.append(wb_parse_card_name_prices(card_json, nm_id))
            except RuntimeError as e:
                logger.record_error("controller:main", f"card parse failed id={nm_id}", e, fatal=True)
                raise



        wb_save_names_prices(rows)
        print(f"Файл сохранён: {OUT_NAMES_PRICES_FILE}")

        print()  # пустая строка перед NETWORK USAGE SUMMARY
        wb_net_print_summary()
        print()  # пустая строка после NETWORK USAGE SUMMARY

        print("Нажми Enter, чтобы завершить скрипт.")
        try:
            input()
        except KeyboardInterrupt:
            pass

    finally:
        close_browser(playwright, context)
        logger.print_end_summary()
