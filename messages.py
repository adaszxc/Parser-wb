# Все текстовые шаблоны вывода программы

REPORT_LINE_TEMPLATE = '{name} | без скидок={basic} | со скидкой={wallet}'
NET_USAGE_HEADER = "Трафик что WB отдал:"
NET_USAGE_TOTAL_TEMPLATE = "Всего - {kb} КБ"
NET_USAGE_NON_SCRIPTED_TEMPLATE = "Не скриптовые - {kb} КБ"
NET_USAGE_SCRIPTED_HEADER = "Скриптовые запросы:"
NET_USAGE_SCRIPTED_ROW_TEMPLATE = "- {name} - {kb} КБ"
LOGGER_NO_ERRORS = "Ошибок нет"
LOGGER_NON_FATAL_HEADER = "Некритичные ошибки:"
LOGGER_IMMEDIATE_ERROR_TEMPLATE = "[{where}] {message}"
LOGGER_IMMEDIATE_ERROR_WITH_EXC_TEMPLATE = "[{where}] {message}: {exc_type}: {exc_text}"
LOGGER_SUMMARY_ROW_TEMPLATE = "{ts} {prefix} [{where}] {message}"
LOGGER_SUMMARY_ROW_WITH_EXC_TEMPLATE = "{ts} {prefix} [{where}] {message}: {exc_type}: {exc_text}"
LOGGER_FATAL_PREFIX = "FATAL"
LOGGER_ERROR_PREFIX = "ERROR"
CONTROLLER_FILE_SAVED_TEMPLATE = "Файл сохранён: {filename}"
CONTROLLER_EXIT_PROMPT = "Нажми Enter, чтобы завершить скрипт."
