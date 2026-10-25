from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_DATABASE_PATH = Path(__file__).resolve().parent / "telemetry.db"
DATABASE_PATH = Path(os.getenv("TELEMETRY_DB_PATH", str(DEFAULT_DATABASE_PATH)))


def _connect() -> sqlite3.Connection:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH, timeout=15)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database() -> None:
    connection = _connect()
    try:
        with connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS simulation_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scenario TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS measurements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    temperature_c REAL NOT NULL,
                    vibration_g REAL NOT NULL,
                    voltage_v REAL NOT NULL,
                    status TEXT NOT NULL,
                    alerts_json TEXT NOT NULL,
                    FOREIGN KEY (run_id) REFERENCES simulation_runs(id)
                        ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_measurements_run_timestamp
                    ON measurements(run_id, timestamp);
                """
            )
    finally:
        connection.close()


def create_simulation(
    scenario: str,
    readings: list[dict[str, Any]],
) -> dict[str, Any]:
    created_at = datetime.now(timezone.utc).isoformat()
    connection = _connect()
    try:
        with connection:
            cursor = connection.execute(
                "INSERT INTO simulation_runs (scenario, created_at) VALUES (?, ?)",
                (scenario, created_at),
            )
            run_id = int(cursor.lastrowid)
            connection.executemany(
                """
                INSERT INTO measurements (
                    run_id, timestamp, temperature_c, vibration_g,
                    voltage_v, status, alerts_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        run_id,
                        reading["timestamp"].isoformat(),
                        reading["temperature_c"],
                        reading["vibration_g"],
                        reading["voltage_v"],
                        reading["status"],
                        json.dumps(reading["alerts"], ensure_ascii=False),
                    )
                    for reading in readings
                ],
            )
    finally:
        connection.close()

    result = get_simulation(run_id)
    if result is None:
        raise RuntimeError("Saved simulation could not be read back")
    return result


def get_simulation(run_id: int) -> dict[str, Any] | None:
    connection = _connect()
    try:
        row = connection.execute(
            """
            SELECT
                r.id,
                r.scenario,
                r.created_at,
                COUNT(m.id) AS measurement_count,
                SUM(CASE WHEN m.status = 'UYARI' THEN 1 ELSE 0 END) AS alert_count
            FROM simulation_runs AS r
            LEFT JOIN measurements AS m ON m.run_id = r.id
            WHERE r.id = ?
            GROUP BY r.id
            """,
            (run_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        connection.close()


def list_simulations(limit: int = 20) -> list[dict[str, Any]]:
    connection = _connect()
    try:
        rows = connection.execute(
            """
            SELECT
                r.id,
                r.scenario,
                r.created_at,
                COUNT(m.id) AS measurement_count,
                SUM(CASE WHEN m.status = 'UYARI' THEN 1 ELSE 0 END) AS alert_count
            FROM simulation_runs AS r
            LEFT JOIN measurements AS m ON m.run_id = r.id
            GROUP BY r.id
            ORDER BY r.id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


def list_measurements(run_id: int) -> list[dict[str, Any]]:
    connection = _connect()
    try:
        rows = connection.execute(
            """
            SELECT
                id, run_id, timestamp, temperature_c, vibration_g,
                voltage_v, status, alerts_json
            FROM measurements
            WHERE run_id = ?
            ORDER BY timestamp ASC, id ASC
            """,
            (run_id,),
        ).fetchall()
        return [
            {
                **{key: row[key] for key in row.keys() if key != "alerts_json"},
                "alerts": json.loads(row["alerts_json"]),
            }
            for row in rows
        ]
    finally:
        connection.close()


def list_alerts(run_id: int) -> list[dict[str, Any]]:
    connection = _connect()
    try:
        rows = connection.execute(
            """
            SELECT
                id, timestamp, temperature_c, vibration_g, voltage_v, alerts_json
            FROM measurements
            WHERE run_id = ? AND status = 'UYARI'
            ORDER BY timestamp DESC, id DESC
            """,
            (run_id,),
        ).fetchall()
        return [
            {
                "measurement_id": row["id"],
                "timestamp": row["timestamp"],
                "temperature_c": row["temperature_c"],
                "vibration_g": row["vibration_g"],
                "voltage_v": row["voltage_v"],
                "alerts": json.loads(row["alerts_json"]),
            }
            for row in rows
        ]
    finally:
        connection.close()
