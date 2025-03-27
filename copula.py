from __future__ import annotations

from aiogram import Dispatcher

from service.service_core import Service

dp = Dispatcher()
service: Service | None = None  # Keep None as the initial value


def get_service() -> Service:
    if service is None:
        raise RuntimeError("Service has not been initialized yet")
    return service
