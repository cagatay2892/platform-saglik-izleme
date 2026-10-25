from __future__ import annotations

import os

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

from telemetry import SCENARIOS, THRESHOLDS, generate_telemetry

API_URL = os.getenv("TELEMETRY_API_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="Platform Sağlık İzleme Simülatörü",
    page_icon="🛰️",
    layout="wide",
)

st.title("Platform Sağlık İzleme Simülatörü")
st.caption(
    "Sentetik ölçümler FastAPI üzerinden SQLite'a kaydedilir ve geçmişten görüntülenir."
)

with st.sidebar:
    st.header("Simülasyon ayarları")
    selected_label = st.selectbox("Arıza senaryosu", list(SCENARIOS.values()))
    scenario = next(key for key, label in SCENARIOS.items() if label == selected_label)
    sample_count = st.slider("Ölçüm sayısı", min_value=60, max_value=480, value=180, step=30)
    seed = st.number_input("Rastgelelik tohumu", min_value=0, max_value=999_999, value=42)
    create_run = st.button("Senaryoyu üret ve kaydet", type="primary")
    st.divider()
    st.caption("Eşikler: sıcaklık > 70 °C, titreşim > 1,2 g, gerilim < 21 V.")
    st.caption(f"API: {API_URL}")

try:
    health_response = requests.get(f"{API_URL}/health", timeout=3)
    health_response.raise_for_status()
except requests.RequestException:
    st.error(
        "API'ye bağlanılamadı. Önce ikinci terminalde API sunucusunu başlat: "
        "python -m uvicorn api:app --reload"
    )
    st.stop()

if create_run:
    generated = generate_telemetry(
        scenario=scenario,
        samples=sample_count,
        seed=int(seed),
    )
    payload = {
        "scenario": scenario,
        "readings": [
            {
                "timestamp": row["timestamp"].isoformat(),
                "temperature_c": row["temperature_c"],
                "vibration_g": row["vibration_g"],
                "voltage_v": row["voltage_v"],
            }
            for row in generated
        ],
    }
    try:
        response = requests.post(
            f"{API_URL}/simulations",
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        st.session_state["selected_run_id"] = response.json()["id"]
        st.success("Simülasyon kaydedildi.")
    except requests.RequestException as error:
        st.error(f"Simülasyon kaydedilemedi: {error}")

try:
    runs_response = requests.get(f"{API_URL}/simulations", timeout=5)
    runs_response.raise_for_status()
    runs = runs_response.json()
except requests.RequestException as error:
    st.error(f"Simülasyon geçmişi alınamadı: {error}")
    st.stop()

if not runs:
    st.info("Henüz kayıt yok. Sol menüden bir senaryo seçip simülasyonu başlat.")
    st.stop()

run_ids = [run["id"] for run in runs]
preferred_run = st.session_state.get("selected_run_id", run_ids[0])
selected_index = run_ids.index(preferred_run) if preferred_run in run_ids else 0
selected_run_id = st.selectbox(
    "Kayıtlı simülasyon",
    options=run_ids,
    index=selected_index,
    format_func=lambda run_id: next(
        (
            f"#{run_id} · {SCENARIOS.get(run['scenario'], run['scenario'])} · "
            f"{run['created_at'][:19].replace('T', ' ')}"
            for run in runs
            if run["id"] == run_id
        ),
        f"#{run_id}",
    ),
)

try:
    measurements_response = requests.get(
        f"{API_URL}/simulations/{selected_run_id}/measurements",
        timeout=5,
    )
    measurements_response.raise_for_status()
    measurements = measurements_response.json()
    alerts_response = requests.get(
        f"{API_URL}/simulations/{selected_run_id}/alerts",
        timeout=5,
    )
    alerts_response.raise_for_status()
    alert_events = alerts_response.json()
except requests.RequestException as error:
    st.error(f"Simülasyon verisi alınamadı: {error}")
    st.stop()

frame = pd.DataFrame(measurements)
frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
frame["alerts_text"] = frame["alerts"].apply(lambda items: " · ".join(items))
latest = frame.iloc[-1]
warning_rows = frame[frame["status"] == "UYARI"]

metric_columns = st.columns(4)
metric_columns[0].metric("Son sıcaklık", f"{latest['temperature_c']:.1f} °C")
metric_columns[1].metric("Son titreşim", f"{latest['vibration_g']:.2f} g")
metric_columns[2].metric("Son gerilim", f"{latest['voltage_v']:.1f} V")
metric_columns[3].metric("Uyarılı ölçüm", f"{len(warning_rows)} / {len(frame)}")

if latest["status"] == "UYARI":
    st.warning("Son ölçüm eşiklerden en az birini aşıyor. Olay kayıtlarını inceleyin.")
else:
    st.success("Son ölçüm tanımlı eşiklerin içinde.")

chart_columns = st.columns(3)
chart_specs = [
    ("temperature_c", "Sıcaklık (°C)", THRESHOLDS["temperature_c"], "red"),
    ("vibration_g", "Titreşim (g)", THRESHOLDS["vibration_g"], "orange"),
    ("voltage_v", "Gerilim (V)", THRESHOLDS["voltage_v"], "red"),
]

for column, (field, title, threshold, color) in zip(chart_columns, chart_specs):
    figure = px.line(frame, x="timestamp", y=field, title=title)
    figure.add_hline(
        y=threshold,
        line_dash="dash",
        line_color=color,
        annotation_text=f"Eşik: {threshold}",
        annotation_position="top left",
    )
    figure.update_layout(
        height=300,
        margin=dict(l=10, r=10, t=45, b=10),
        xaxis_title=None,
        yaxis_title=None,
        showlegend=False,
    )
    column.plotly_chart(figure, use_container_width=True)

st.subheader(f"Olay kayıtları ({len(alert_events)})")
if not alert_events:
    st.info("Bu simülasyonda eşik aşımı oluşmadı.")
else:
    alert_frame = pd.DataFrame(alert_events)
    alert_frame["alerts_text"] = alert_frame["alerts"].apply(lambda items: " · ".join(items))
    st.dataframe(
        alert_frame[
            ["timestamp", "temperature_c", "vibration_g", "voltage_v", "alerts_text"]
        ].rename(
            columns={
                "timestamp": "Zaman",
                "temperature_c": "Sıcaklık (°C)",
                "vibration_g": "Titreşim (g)",
                "voltage_v": "Gerilim (V)",
                "alerts_text": "Olay",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

csv_bytes = frame.drop(columns=["alerts"]).to_csv(index=False).encode("utf-8-sig")
st.download_button(
    "Seçili simülasyonu CSV indir",
    data=csv_bytes,
    file_name=f"simulasyon_{selected_run_id}.csv",
    mime="text/csv",
)

with st.expander("API ve proje sınırları"):
    st.write(
        "API belgeleri /docs adresinde bulunur. Ölçümler ve uyarılar yerel SQLite "
        "veritabanında kalıcı olarak saklanır. Bu portföy demosu sentetik veri kullanır; "
        "gerçek platforma bağlanmaz ve operasyonel kullanım için tasarlanmamıştır."
    )
