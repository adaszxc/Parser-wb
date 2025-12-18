# Выводит зарегистрированные ошибки в терминал.

from __future__ import annotations
import sys
from dataclasses import dataclass
from datetime import datetime
from messages import (
    LOGGER_IMMEDIATE_ERROR_TEMPLATE,
    LOGGER_IMMEDIATE_ERROR_WITH_EXC_TEMPLATE,
    LOGGER_NO_ERRORS,
    LOGGER_NON_FATAL_HEADER,
    LOGGER_SUMMARY_ROW_TEMPLATE,
    LOGGER_SUMMARY_ROW_WITH_EXC_TEMPLATE,
    LOGGER_FATAL_PREFIX,
    LOGGER_ERROR_PREFIX,
)
from settings import LOG_MODE


@dataclass(frozen=True)
class LoggedError:
    ts: str
    where: str
    message: str
    exc_type: str | None
    exc_text: str | None
    fatal: bool


_errors: list[LoggedError] = []


# Возвращает текущее время для метки лога.
def _now_ts() -> str:
    return datetime.now().strftime("%H:%M:%S")


# Преобразует исключение в тип и текст для хранения.
def _format_exc(exc: BaseException | None) -> tuple[str | None, str | None]:
    if exc is None:
        return None, None
    return type(exc).__name__, str(exc)


# Выводит строку в stderr (сейчас в терминал).
def _emit(line: str) -> None:
    print(line, file=sys.stderr)


# Фиксирует ошибку и при необходимости выводит её сразу.
def record_error(where: str, message: str, exc: BaseException | None = None, fatal: bool = False) -> None:
    exc_type, exc_text = _format_exc(exc)
    _errors.append(
        LoggedError(
            ts=_now_ts(),
            where=where,
            message=message,
            exc_type=exc_type,
            exc_text=exc_text,
            fatal=fatal,
        )
    )

    if LOG_MODE == 0:
        if exc_type is None:
            _emit(
                LOGGER_IMMEDIATE_ERROR_TEMPLATE.format(
                    where=where,
                    message=message,
                )
            )
        else:
            _emit(
                LOGGER_IMMEDIATE_ERROR_WITH_EXC_TEMPLATE.format(
                    where=where,
                    message=message,
                    exc_type=exc_type,
                    exc_text=exc_text,
                )
            )


# Печатает итоговый отчёт по завершении программы.
def print_end_summary() -> None:
    if not _errors:
        _emit(LOGGER_NO_ERRORS)
        return

    if LOG_MODE == 1:
        _emit(LOGGER_NON_FATAL_HEADER)
        for err in _errors:
            prefix = LOGGER_FATAL_PREFIX if err.fatal else LOGGER_ERROR_PREFIX
            if err.exc_type is None:
                _emit(
                    LOGGER_SUMMARY_ROW_TEMPLATE.format(
                        ts=err.ts,
                        prefix=prefix,
                        where=err.where,
                        message=err.message,
                    )
                )
            else:
                _emit(
                    LOGGER_SUMMARY_ROW_WITH_EXC_TEMPLATE.format(
                        ts=err.ts,
                        prefix=prefix,
                        where=err.where,
                        message=err.message,
                        exc_type=err.exc_type,
                        exc_text=err.exc_text,
                    )
                )
