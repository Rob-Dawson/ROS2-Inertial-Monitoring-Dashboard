import streamlit as st
import plotly.express as px
import dashboard
import plotly.graph_objects as go
import pandas as pd
st.set_page_config(layout="wide")
data = dashboard.load_and_process_data()

df = data["df_crash"]
AXIS_COLOURS = {
    "desired_linear_vel_x": "red",
    "desired_angular_vel_z": "yellow",
}


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
        return st.slider("Time window", 0.0, max_time, (start_input, end_input), step=0.1)

def plot_signals(df, title, start, end):
    fig = go.Figure()

    for _, row in df.iterrows():
        color = "red" if row["event"] == "crash_before" else "green"
        hover_text = (
            f"{row['event']}<br>"
            f"event t={row['t']:.6f}s<br>"
            )
        fig.add_trace(
            go.Scatter(
                x=[row["t"], row["t"]],
                y=[0, 1],
                mode="lines",
                line=dict(color=color, width=2),
                hovertemplate=hover_text + "<extra></extra>",
                showlegend=False,
            )
        )

    fig.update_xaxes(
        tickformat=".3f",
        range=[start, end]
        )

    fig.update_layout(
        title=title,
        xaxis_title="Time Since Start",
        yaxis=dict(visible=False),
        height=900,
        margin=dict(l=20, r=20, t=50, b=20),

    )

    st.plotly_chart(fig, use_container_width=True)

st.title("Crash Events")

experiment_start = df["timestamp"].iloc[0]
experiment_end = df["timestamp"].iloc[-1]
max_time = float(experiment_end - experiment_start)



start, end = time_window_controls(max_time)

window_df = df[(df["t"] >= start) & (df["t"] <= end)]
st.dataframe(df[["event","event_time", "t"]])
plot_signals(
    window_df,
    title="Crash Events",
    start=start,
    end=end,
)
