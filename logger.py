# Выводит зарегистрированные ошибки в терминал

from __future__ import annotations
import sys
from dataclasses import dataclass
from datetime import datetime
from config import LOG_MODE


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


# Выводит строку в stderr (сейчас в терминал)
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
            _emit(f"[{where}] {message}")
        else:
            _emit(f"[{where}] {message}: {exc_type}: {exc_text}")


# Печатает итоговый отчёт по завершении программы.
def print_end_summary() -> None:
    if not _errors:
        _emit("Ошибок нет")
        return

    if LOG_MODE == 1:
        _emit("Некритичные ошибки:")
        for err in _errors:
            prefix = "FATAL" if err.fatal else "ERROR"
            if err.exc_type is None:
                _emit(f"{err.ts} {prefix} [{err.where}] {err.message}")
            else:
                _emit(f"{err.ts} {prefix} [{err.where}] {err.message}: {err.exc_type}: {err.exc_text}")
