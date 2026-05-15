import streamlit as st
import plotly.express as px
import dashboard

st.set_page_config(layout="wide")
data = dashboard.load_and_process_data()

df = data["df_joint_states"]
AXIS_COLOURS = {
    "wheel_left_joint_velocity": "red",
    "wheel_right_joint_velocity": "green",

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
    fig = px.line(
        df,
        x="t",
        y=cols,
        title=title,
        color_discrete_map=AXIS_COLOURS,
    )

    fig.update_layout(
        height=900,
        margin=dict(l=20, r=20, t=50, b=20),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"scrollZoom": True},
    )    
    
st.title("Actual Velocity")
max_time = float(df["t"].max())
start, end = time_window_controls(max_time)

window_df = df[(df["t"] >= start) & (df["t"] <= end)]



st.dataframe(df[["wheel_left_joint_velocity",
                 "wheel_right_joint_velocity", 
                 "timestamp",
                 "t"]])
plot_signals(
    window_df,
    cols=["wheel_left_joint_velocity", "wheel_right_joint_velocity"],
    title="Velocity",
)
