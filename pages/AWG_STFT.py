import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from scipy.signal import stft
import dashboard

st.set_page_config(layout="wide")

data = dashboard.load_and_process_data()
df = data["df_accel_without_gravity_body"]
df_crash = data["df_crash"]

st.title("IMU STFT Viewer")

def add_crash_regions(fig, df_crash):
    crash_before = df_crash[df_crash["event"] == "crash_before"]["t"].to_list()
    crash_after = df_crash[df_crash["event"] == "crash_after"]["t"].to_list()

    for start, end in zip(crash_before, crash_after):
        fig.add_vrect(
            x0=start,
            x1=end,
            fillcolor="red",
            opacity=0.2,
            line_width=0,
            annotation_text="crash",
            annotation_position="top left",
        )
    return fig


def time_window_controls(max_time):
    col1, col2 = st.columns(2)

    with col1:
        start_input = st.number_input(
            "Start Time",
            min_value=0.0,
            max_value=max_time,
            value=0.0,
            step=0.1,
        )

    with col2:
        end_input = st.number_input(
            "End Time",
            min_value=0.0,
            max_value=max_time,
            value=min(max_time, start_input + 10.0),
            step=0.1,
        )

    return st.slider(
        "Time window",
        0.0,
        max_time,
        (start_input, end_input),
        step=0.1,
    )


def resample_signal(window_df, signal, target_fs):
    window_df = window_df.sort_values("t")

    t_old = window_df["t"].to_numpy()
    y_old = window_df[signal].to_numpy()

    valid = np.isfinite(t_old) & np.isfinite(y_old)

    if valid.sum() < 2:
        return None, None

    t_old = t_old[valid]
    y_old = y_old[valid]

    t_start = t_old[0]
    t_end = t_old[-1]

    t_new = np.arange(t_start, t_end, 1.0 / target_fs)

    if len(t_new) < 4:
        return None, None

    y_new = np.interp(t_new, t_old, y_old)

    return t_new, y_new


def compute_stft(t, y, target_fs, nperseg, noverlap):
    y = y - np.mean(y)

    f, tt, Zxx = stft(
        y,
        fs=target_fs,
        window="hann",
        nperseg=nperseg,
        noverlap=noverlap,
        boundary=None,
    )

    power_db = 10 * np.log10(np.abs(Zxx) ** 2 + 1e-12)

    # Convert STFT relative time back to real dataset time
    stft_time = t[0] + tt

    return f, stft_time, power_db


max_time = float(df["t"].max())
start, end = time_window_controls(max_time)

window_df = df[(df["t"] >= start) & (df["t"] <= end)]

numeric_cols = [
    c for c in df.columns
    if c != "t" and pd.api.types.is_numeric_dtype(df[c])
]

signal = st.selectbox("Signal", numeric_cols)

col1, col2, col3 = st.columns(3)

with col1:
    target_fs = st.number_input(
        "Target sample rate Hz",
        min_value=10,
        max_value=1000,
        step=10,
    )

with col2:
    nperseg = st.number_input(
        "STFT nperseg",
        min_value=16,
        max_value=1024,
        step=16,
    )

with col3:
    noverlap = st.number_input(
        "STFT noverlap",
        min_value=0,
        max_value=int(nperseg) - 1,
        step=8,
    )

t_resampled, y_resampled = resample_signal(
    window_df,
    signal=signal,
    target_fs=int(target_fs),
)

if t_resampled is None:
    st.error("Not enough samples in this selected time window.")
    st.stop()

f, stft_time, power_db = compute_stft(
    t=t_resampled,
    y=y_resampled,
    target_fs=int(target_fs),
    nperseg=int(nperseg),
    noverlap=int(noverlap),
)

st.subheader("Time-domain signal")

fig_signal = go.Figure()
fig_signal.add_trace(
    go.Scatter(
        x=t_resampled,
        y=y_resampled,
        mode="lines",
        name=signal,
    )
)

fig_signal.update_layout(
    height=350,
    margin=dict(l=20, r=20, t=40, b=20),
    xaxis_title="Time (s)",
    yaxis_title=signal,
)

fig_signal = add_crash_regions(fig_signal, df_crash)

st.plotly_chart(
    fig_signal,
    use_container_width=True,
    config={"scrollZoom": True},
)

st.subheader("STFT Spectrogram")

fig_stft = go.Figure(
    data=go.Heatmap(
        x=stft_time,
        y=f,
        z=power_db,
        colorscale="Viridis",
        colorbar=dict(title="Power dB"),
    )
)

fig_stft.update_layout(
    height=700,
    margin=dict(l=20, r=20, t=40, b=20),
    xaxis_title="Time (s)",
    yaxis_title="Frequency (Hz)",
)

fig_stft.update_yaxes(range=[0, int(target_fs) / 2])

# fig_stft = add_crash_regions(fig_stft, df_crash)

st.plotly_chart(
    fig_stft,
    use_container_width=True,
    config={"scrollZoom": True},
)