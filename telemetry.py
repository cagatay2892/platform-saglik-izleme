from __future__ import annotations

from datetime import datetime, timedelta, timezone
import math
import random
from typing import Any

THRESHOLDS = {
    "temperature_c": 70.0,
    "vibration_g": 1.2,
    "voltage_v": 21.0,
}

SCENARIOS = {
    "normal": "Normal çalışma",
    "overheating": "Aşırı ısınma",
    "high_vibration": "Yüksek titreşim",
    "voltage_drop": "Güç düşümü",
}


def generate_telemetry(
    scenario: str = "normal",
    samples: int = 180,
    seed: int = 42,
) -> list[dict[str, Any]]:
    """Create reproducible, synthetic telemetry rows for a demo scenario."""
    if scenario not in SCENARIOS:
        raise ValueError(f"Unknown scenario: {scenario}")
    if samples < 1:
        raise ValueError("samples must be at least 1")

    rng = random.Random(seed)
    start = datetime.now(timezone.utc) - timedelta(minutes=samples - 1)
    fault_start = int(samples * 0.45)
    rows: list[dict[str, Any]] = []

    for index in range(samples):
        temperature = (
            38.0
            + 2.0 * math.sin(index / 13.0)
            + rng.gauss(0, 0.7)
        )
        vibration = 0.25 + 0.035 * math.sin(index / 8.0) + rng.gauss(0, 0.018)
        voltage = 24.4 - 0.35 * index / max(samples - 1, 1) + rng.gauss(0, 0.06)

        if scenario == "overheating" and index >= fault_start:
            temperature += min(38.0, (index - fault_start) * 0.55)
        elif scenario == "high_vibration" and index >= fault_start:
            vibration += min(1.8, (index - fault_start) * 0.04)
        elif scenario == "voltage_drop" and index >= fault_start:
            voltage -= min(6.0, (index - fault_start) * 0.14)

        alerts: list[str] = []
        if temperature > THRESHOLDS["temperature_c"]:
            alerts.append("Sıcaklık eşiği aşıldı")
        if vibration > THRESHOLDS["vibration_g"]:
            alerts.append("Titreşim eşiği aşıldı")
        if voltage < THRESHOLDS["voltage_v"]:
            alerts.append("Gerilim eşiğin altına düştü")

        rows.append(
            {
                "timestamp": start + timedelta(minutes=index),
                "temperature_c": round(temperature, 2),
                "vibration_g": round(vibration, 3),
                "voltage_v": round(voltage, 2),
                "status": "UYARI" if alerts else "NORMAL",
                "alerts": alerts,
            }
        )

    return rows
