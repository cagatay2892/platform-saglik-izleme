from __future__ import annotations

from datetime import datetime
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from database import (
    create_simulation,
    get_simulation,
    initialize_database,
    list_alerts,
    list_measurements,
    list_simulations,
)
from telemetry import SCENARIOS, evaluate_alerts

ScenarioName = Literal["normal", "overheating", "high_vibration", "voltage_drop"]

app = FastAPI(
    title="Platform Sağlık İzleme API",
    description="Sentetik telemetri simülasyonlarını kaydeden yerel API.",
    version="2.0.0",
)
initialize_database()


class TelemetryInput(BaseModel):
    timestamp: datetime
    temperature_c: float = Field(ge=-50, le=150)
    vibration_g: float = Field(ge=0, le=20)
    voltage_v: float = Field(ge=0, le=60)


class SimulationInput(BaseModel):
    scenario: ScenarioName
    readings: list[TelemetryInput]


class SimulationSummary(BaseModel):
    id: int
    scenario: str
    created_at: datetime
    measurement_count: int
    alert_count: int


class MeasurementOutput(BaseModel):
    id: int
    run_id: int
    timestamp: datetime
    temperature_c: float
    vibration_g: float
    voltage_v: float
    status: str
    alerts: list[str]


class AlertOutput(BaseModel):
    measurement_id: int
    timestamp: datetime
    temperature_c: float
    vibration_g: float
    voltage_v: float
    alerts: list[str]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "database": "connected"}


@app.post("/simulations", response_model=SimulationSummary, status_code=201)
def save_simulation(payload: SimulationInput) -> dict:
    if len(payload.readings) < 1 or len(payload.readings) > 480:
        raise HTTPException(
            status_code=422,
            detail="A simulation must contain between 1 and 480 readings.",
        )

    readings = []
    for item in payload.readings:
        values = item.model_dump()
        alerts = evaluate_alerts(
            values["temperature_c"],
            values["vibration_g"],
            values["voltage_v"],
        )
        readings.append(
            {
                **values,
                "status": "UYARI" if alerts else "NORMAL",
                "alerts": alerts,
            }
        )

    return create_simulation(payload.scenario, readings)


@app.get("/simulations", response_model=list[SimulationSummary])
def simulations(
    limit: int = Query(default=20, ge=1, le=100),
) -> list[dict]:
    return list_simulations(limit)


@app.get(
    "/simulations/{run_id}/measurements",
    response_model=list[MeasurementOutput],
)
def simulation_measurements(run_id: int) -> list[dict]:
    if get_simulation(run_id) is None:
        raise HTTPException(status_code=404, detail="Simulation not found.")
    return list_measurements(run_id)


@app.get("/simulations/{run_id}/alerts", response_model=list[AlertOutput])
def simulation_alerts(run_id: int) -> list[dict]:
    if get_simulation(run_id) is None:
        raise HTTPException(status_code=404, detail="Simulation not found.")
    return list_alerts(run_id)


@app.get("/scenarios")
def scenarios() -> dict[str, str]:
    return SCENARIOS
