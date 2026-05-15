import streamlit as st
import plotly.express as px
import dashboard

st.set_page_config(layout="wide")
data = dashboard.load_and_process_data()

df = data["df_imu"]
df_crash = data["df_crash"]

AXIS_COLOURS = {
    "accel_x": "red",
    "accel_y": "green",
    "accel_z": "blue",
    "gyro_x": "orange",
    "gyro_y": "purple",
    "gyro_z": "yellow",
}

SIGNAL_GROUPS = {
    "Acceleration": ["accel_x", "accel_y", "accel_z"],
    "Gyroscope": ["gyro_x", "gyro_y", "gyro_z"],
    "Combined": [
        "accel_x", "accel_y", "accel_z",
        "gyro_x", "gyro_y", "gyro_z",
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
        return st.slider("Time window", 0.0, 450.0, (start_input, end_input), step=0.1)
    

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

def plot_signals(df, cols, title, plot_id, df_crash=None, start=None, end=None):
    
    available_cols = [col for col in cols if col in df.columns]
    fig = px.line(
        df,
        x="t",
        y=cols,
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
    )    
    
st.title("IMU + Mean Bias + Low Pass Filter Data")
max_time = float(df["t"].max())
start, end = time_window_controls(max_time)

window_df = df[(df["t"] >= start) & (df["t"] <= end)]

signal_group = st.selectbox(
    "Signal Group",
    list(SIGNAL_GROUPS.keys()),
)
cols = SIGNAL_GROUPS[signal_group]

plot_signals(
    window_df,
    cols,
    title=signal_group,
    plot_id="raw_imu",
    df_crash=df_crash,
    start=start,
    end=end,
)
