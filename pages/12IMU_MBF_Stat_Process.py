import streamlit as st
import plotly.express as px
import dashboard

st.set_page_config(layout="wide")
data = dashboard.load_and_process_data()

df_features = data["df_raw_imu_features"]
df_crash = data["df_crash"]

AXIS_COLOURS = {
    "accel_x_STD": "red",
    "accel_y_STD": "green",
    "accel_z_STD": "blue",
    "accel_x_rms": "orange",
    "accel_y_rms": "purple",
    "accel_z_rms": "yellow",
}

SIGNAL_GROUPS = {
    "Acceleration Features": [
        "accel_x_STD", "accel_y_STD", "accel_z_STD",
        "accel_x_rms", "accel_y_rms", "accel_z_rms",
    ],
    "Gyro Features": [
        "gyro_x_STD", "gyro_y_STD", "gyro_z_STD",
        "gyro_x_rms", "gyro_y_rms", "gyro_z_rms",
    ],
}


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
        0.0,
        max_time,
        (start_input, end_input),
        step=0.1,
    )

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

# def add_crash_overlays(fig, df_crash, start, end):

#     for _, row in df_crash.iterrows():
#         fig.add_vrect(
#             x=row["t"],
#             line_width=2,
#             line_color="red" if row["event"] == "crash_before" else "green",
#             annotation_text=row["event"],
#             annotation_position="top",
#         )

#     return fig


def plot_signals(df, cols, title, plot_id, df_crash=None, start=None, end=None):
    available_cols = [col for col in cols if col in df.columns]

    fig = px.line(
        df,
        x="t",
        y=available_cols,
        title=title,
        color_discrete_map=AXIS_COLOURS,
    )

    if df_crash is not None and start is not None and end is not None:
        fig = add_crash_regions(fig, df_crash)

    fig.update_layout(
        height=900,
        margin=dict(l=20, r=20, t=50, b=20),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"scrollZoom": True},
        key=plot_id,
    )

    return fig


st.title("IMU Feature Data")
st.caption("Windowed features calculated from raw IMU data")
st.caption("Features include RMS, STD, and mean")



max_time = float(df_features["t"].max())
start, end = time_window_controls(max_time)

features_window = window(df_features, start, end)
signal_group = st.selectbox(
    "Signal Group",
    list(SIGNAL_GROUPS.keys()),
)

cols = SIGNAL_GROUPS[signal_group]

plot_signals(
    features_window,
    cols,
    title=signal_group,
    plot_id="raw_imu_mbf_stat_processed",
    df_crash=df_crash,
    start=start,
    end=end,
)

st.subheader("Crash Events in Selected Window")
st.dataframe(df_crash[["event","event_time", "t"]])
