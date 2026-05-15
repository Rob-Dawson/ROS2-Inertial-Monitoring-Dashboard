import streamlit as st
import plotly.express as px
import dashboard
import plotly.graph_objects as go
st.set_page_config(layout="wide")
data = dashboard.load_and_process_data()

df = data["df_zupt"]
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
        return st.slider("Time window", 0.0, 450.0, (start_input, end_input), step=0.1)

def plot_signals(df, cols, title):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["t"],
            y=[1] * len(df),
            mode="markers",
            marker=dict(size=10),
            name="Zupt Event",
    ))


    fig.update_layout(
        title="Zupt Timeline",
        xaxis_title = "Time Since Start",
        yaxis=dict(
            showticklabels=False,
            range=[0, 2],
        ),
        height=900,
        margin=dict(l=20, r=20, t=50, b=20),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"scrollZoom": True},
    )    

st.title("ZUPT")
max_time = float(df["t"].max())
start, end = time_window_controls(max_time)

window_df = df[(df["t"] >= start) & (df["t"] <= end)]

plot_signals(
    window_df,
    cols=["desired_linear_vel_x","desired_angular_vel_z"],
    title="Desired Velocity",
)
