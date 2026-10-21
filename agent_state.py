"""Агент умного дома: пороги реакции, события датчиков и решения.

Итерация 1. Модуль читает список событий датчиков (словари), применяет
пороги реакции по климату, свету и безопасности и формирует по каждой
комнате пару решений: ``climate_action`` и ``security_action``.

Запуск::

    python agent_state.py
"""

from __future__ import annotations

from typing import Any

# --- 1. Пороги реакции агента ------------------------------------------------
# Климат: комфортный диапазон температур воздуха в помещении, °C.
# Свет: освещённость ниже порога считается «темно», лк.
# Безопасность: режимы контроллера, в которых движение требует проверки,
# и максимальная освещённость, при которой движение считается подозрительным.
THRESHOLDS: dict[str, dict[str, Any]] = {
    "climate": {
        "comfort_min": 18.0,
        "comfort_max": 26.0,
    },
    "light": {
        "dim_below": 100.0,
    },
    "security": {
        "watched_modes": ("away", "night"),
        "dark_light_max": 100.0,
    },
}

# --- 2. События датчиков -----------------------------------------------------
# Каждое событие — словарь с показаниями датчиков одной комнаты в момент time.
EVENTS: list[dict[str, Any]] = [
    {
        "time": "2026-10-21T18:40:00",
        "room": "kitchen",
        "temperature": 22.4,
        "light": 320.0,
        "motion": True,
        "door": "closed",
        "controller_mode": "home",
    },
    {
        "time": "2026-10-21T18:41:00",
        "room": "hall",
        "temperature": 21.1,
        "light": 140.0,
        "motion": False,
        "door": "open",
        "controller_mode": "home",
    },
    {
        "time": "2026-10-21T18:42:00",
        "room": "bedroom",
        "temperature": 27.8,
        "light": 45.0,
        "motion": False,
        "door": "closed",
        "controller_mode": "home",
    },
]


def decide_climate(
    event: dict[str, Any],
    thresholds: dict[str, dict[str, Any]] = THRESHOLDS,
) -> str:
    """Вернуть решение по климату для одного события датчиков."""
    temperature = float(event["temperature"])
    comfort_min = float(thresholds["climate"]["comfort_min"])
    comfort_max = float(thresholds["climate"]["comfort_max"])

    if temperature < comfort_min:
        return "turn_on_heating"
    if temperature > comfort_max:
        return "turn_on_cooling"
    return "keep_climate"


def decide_security(
    event: dict[str, Any],
    thresholds: dict[str, dict[str, Any]] = THRESHOLDS,
) -> str:
    """Вернуть решение по безопасности для одного события датчиков.

    Приоритет проверок: открытая дверь важнее движения. Движение в тёмном
    помещении в «наблюдаемом» режиме контроллера трактуется как вторжение,
    движение при свете — как повод для дополнительной проверки.
    """
    security = thresholds["security"]
    light = float(event["light"])
    motion = bool(event["motion"])
    mode = str(event["controller_mode"])
    door = str(event["door"])

    if door == "open":
        return "send_door_warning"

    if motion and mode in security["watched_modes"]:
        if light < float(security["dark_light_max"]):
            return "send_intrusion_warning"
        return "check_motion"

    return "security_ok"


def is_dim(
    event: dict[str, Any],
    thresholds: dict[str, dict[str, Any]] = THRESHOLDS,
) -> bool:
    """Вернуть True, если в комнате темнее порога ``light.dim_below``."""
    return float(event["light"]) < float(thresholds["light"]["dim_below"])


def build_decisions(
    events: list[dict[str, Any]],
    thresholds: dict[str, dict[str, Any]] = THRESHOLDS,
) -> list[dict[str, str]]:
    """Обработать события циклом и собрать решения в список."""
    decisions: list[dict[str, str]] = []

    for event in events:
        decision = {
            "room": str(event["room"]),
            "climate_action": decide_climate(event, thresholds),
            "security_action": decide_security(event, thresholds),
        }
        decisions.append(decision)

    return decisions


def main() -> None:
    """Точка входа: обработать события и вывести решения на экран."""
    for decision in build_decisions(EVENTS):
        print(decision)


if __name__ == "__main__":
    main()
