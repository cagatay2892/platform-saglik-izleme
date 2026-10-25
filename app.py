from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from telemetry import SCENARIOS, THRESHOLDS, generate_telemetry

st.set_page_config(
    page_title="Platform Sağlık İzleme Simülatörü",
    page_icon="🛰️",
    layout="wide",
)

st.title("Platform Sağlık İzleme Simülatörü")
st.caption(
    "Sentetik sensör verileriyle çalışan, eşik tabanlı bir durum izleme demosu."
)

with st.sidebar:
    st.header("Simülasyon ayarları")
    selected_label = st.selectbox("Arıza senaryosu", list(SCENARIOS.values()))
    scenario = next(key for key, label in SCENARIOS.items() if label == selected_label)
    sample_count = st.slider("Ölçüm sayısı", min_value=60, max_value=480, value=180, step=30)
    seed = st.number_input("Rastgelelik tohumu", min_value=0, max_value=999_999, value=42)
    st.divider()
    st.caption(
        "Eşikler: sıcaklık > 70 °C, titreşim > 1,2 g, gerilim < 21 V."
    )

frame = pd.DataFrame(
    generate_telemetry(scenario=scenario, samples=sample_count, seed=int(seed))
)
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

st.subheader("Olay kayıtları")
if warning_rows.empty:
    st.info("Seçili senaryoda eşik aşımı oluşmadı.")
else:
    visible_columns = ["timestamp", "temperature_c", "vibration_g", "voltage_v", "alerts_text"]
    st.dataframe(
        warning_rows[visible_columns].rename(
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
    "Ölçüm verisini CSV indir",
    data=csv_bytes,
    file_name="sentetik_telemetri.csv",
    mime="text/csv",
)

with st.expander("Proje kapsamı ve sınırlar"):
    st.write(
        "Bu çalışma, portföy gösterimi için hazırlanmış sentetik bir simülasyondur. "
        "Kurallar yalnızca tanımlı eşikleri uygular; gerçek platforma bağlanmaz, "
        "arıza tahmini yaptığını iddia etmez ve operasyonel kullanım için tasarlanmamıştır."
    )
