import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

import dashboard

st.set_page_config(layout="wide")
data = dashboard.load_and_process_data()

df_imu_raw = data["df_imu_raw"]
df_cmd = data["df_cmd_vel"]
df_imu = data["df_imu"]
df_joint = data["df_joint_states"]
df_zupt =  data["df_zupt"]
df_crash =  data["df_crash"]
df_accel_without_gravity_body =  data["df_accel_without_gravity_body"]
df_accel_without_gravity_world =  data["df_accel_without_gravity_world"]


def add_imu_features(df):
    df = df.copy()

    df["accel_mag"] = np.sqrt(df.accel_x**2 + df.accel_y**2 + df.accel_z**2)
    df["gyro_mag"] = np.sqrt(df.gyro_x**2 + df.gyro_y**2 + df.gyro_z**2)

    return df


def prepare_crash_events(df_crash, experiment_start):
    df = df_crash.copy()

    df[["event", "event_time"]] = df["crash_log"].str.split(",", n=1, expand=True)
    df["event_time"] = pd.to_numeric(df["event_time"], errors="coerce")
    df = df.dropna(subset=["event_time"])

    df["t"] = df["event_time"] - experiment_start

    return df


def window(df, start, end):
    return df[(df["t"] >= start) & (df["t"] <= end)]


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
            value=max_time,
            step=0.1,
        )

    return st.slider(
        "Time window",
        min_value=0.0,
        max_value=max_time,
        value=(start_input, end_input),
        step=0.1,
    )


st.title("Experiment Overview")

experiment_start = df_imu_raw["timestamp"].iloc[0]
experiment_end = df_imu_raw["timestamp"].iloc[-1]
max_time = float(experiment_end - experiment_start)

# df_cmd = add_relative_time(dashboard.df_cmd_vel, experiment_start)
# df_joint = add_relative_time(dashboard.df_joint_states, experiment_start)
# df_imu_raw = add_imu_features(add_relative_time(dashboard.df_imu_raw, experiment_start))
# df_imu = add_imu_features(add_relative_time(dashboard.df_imu, experiment_start))
# df_zupt = add_relative_time(dashboard.df_zupt, experiment_start)
# df_crash = prepare_crash_events(dashboard.df_crash, experiment_start)




start, end = time_window_controls(max_time)



signals = {
    "Desired linear velocity": (df_cmd, "desired_linear_vel_x"),
    "Desired angular velocity": (df_cmd, "desired_angular_vel_z"),

    "Raw accel X": (df_imu_raw, "accel_x"),
    "Raw accel Y": (df_imu_raw, "accel_y"),
    "Raw accel Z": (df_imu_raw, "accel_z"),

    "Raw gyro X": (df_imu_raw, "gyro_x"),
    "Raw gyro Y": (df_imu_raw, "gyro_y"),
    "Raw gyro Z": (df_imu_raw, "gyro_z"),

    "Filtered accel X": (df_imu, "accel_x"),
    "Filtered accel Y": (df_imu, "accel_y"),
    "Filtered accel Z": (df_imu, "accel_z"),

    "Filtered gyro X": (df_imu, "gyro_x"),
    "Filtered gyro Y": (df_imu, "gyro_y"),
    "Filtered gyro Z": (df_imu, "gyro_z"),

    "Desired Linear Velocity": (df_cmd, "desired_linear_vel_x"),
    "Desired Angular Velocity": (df_cmd, "desired_angular_vel_z"),

    "Actual Linear Velocity": (df_joint, "wheel_left_joint_velocity"),
    "Actual Angular Velocity": (df_joint, "wheel_right_joint_velocity"),

    "Acceleration Without Gravity Body X": (df_accel_without_gravity_body, "accel_x"),
    "Acceleration Without Gravity Body Y": (df_accel_without_gravity_body, "accel_y"),
    "Acceleration Without Gravity Body Z": (df_accel_without_gravity_body, "accel_z"),
    
    
    
    "Acceleration Without Gravity World X": (df_accel_without_gravity_world, "accel_x"),
    "Acceleration Without Gravity World Y": (df_accel_without_gravity_world, "accel_y"),
    "Acceleration Without Gravity World Z": (df_accel_without_gravity_world, "accel_z"),


}

# Add all joint velocity columns automatically
for col in df_joint.columns:
    if col.endswith("_velocity"):
        signals[f"Joint {col}"] = (df_joint, col)

selected = st.multiselect(
    "Measurements to show",
    list(signals.keys()),
    default=[
        "Desired linear velocity",
        # "Raw accel magnitude",
    ],
)

fig = go.Figure()

for label in selected:
    source_df, col = signals[label]
    wdf = window(source_df, start, end)

    fig.add_trace(
        go.Scatter(
            x=wdf["t"],
            y=wdf[col],
            mode="lines",
            name=label,
        )
    )

show_zupt = st.checkbox("Show ZUPT events", value=True)
show_crashes = st.checkbox("Show crash events", value=True)

if show_zupt:
    zdf = window(df_zupt, start, end)

    fig.add_trace(
        go.Scatter(
            x=zdf["t"],
            y=[0] * len(zdf),
            mode="markers",
            marker=dict(size=8),
            name="ZUPT",
        )
    )

if show_crashes:
    cdf = window(df_crash, start, end)

    for _, row in cdf.iterrows():
        fig.add_vline(
            x=row["t"],
            line_width=2,
            line_color="red" if row["event"] == "crash_before" else "green",
            annotation_text=row["event"],
            annotation_position="top",
        )

fig.update_xaxes(range=[start, end])

fig.update_layout(
    title="Selected Measurements",
    xaxis_title="Time Since Start (s)",
    height=900,
    margin=dict(l=20, r=20, t=60, b=20),
    legend=dict(orientation="h"),
)

st.plotly_chart(
    fig,
    use_container_width=True,
    config={"scrollZoom": True},
)