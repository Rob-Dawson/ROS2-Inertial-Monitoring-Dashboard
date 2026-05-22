import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import plotly.express as px
import processing
import streamlit_antd_components as sac

# IMU_RAW_CSV = "./CSV_Experiment_Data/imu_raw.csv"
# IMU_DATA_MBF_CSV = "./CSV_Experiment_Data/imu_data_MBF.csv"
# IMU_DATA_CSV = "./CSV_Experiment_Data/imu_data_MBF_LPF_Madgwick.csv"
# JOINT_STATES_CSV = "./CSV_Experiment_Data/joint_states.csv"
# CMD_VEL_CSV = "./CSV_Experiment_Data/desired_velocity.csv"
# CRASH_STAMPS_CSV = "./CSV_Experiment_Data/crash_stamps.csv"
# ZUPT_CSV = "./CSV_Experiment_Data/zupt.csv"

IMU_RAW_CSV = "imu_raw.csv"
IMU_DATA_MBF_CSV = "imu_data_MBF.csv"
IMU_DATA_CSV = "imu_data_MBF_LPF_Madgwick.csv"
JOINT_STATES_CSV = "joint_states.csv"
CMD_VEL_CSV = "desired_velocity.csv"
CRASH_STAMPS_CSV = "crash_stamps.csv"
ZUPT_CSV = "zupt.csv"
ACCEL_WITHOUT_GRAVITY_BODY = "accel_gravity_removed_body.csv"
ACCEL_WITHOUT_GRAVITY_WORLD = "accel_gravity_removed_world.csv"

@st.cache_data
def load_csv(path):
    return pd.read_csv(path)

@st.cache_data
def load_and_process_data():

    df_imu_raw = load_csv(IMU_RAW_CSV)
    df_imu_mbf = load_csv(IMU_DATA_MBF_CSV)
    df_imu = load_csv(IMU_DATA_CSV)

    df_joint_states = load_csv(JOINT_STATES_CSV)
    df_cmd_vel = load_csv(CMD_VEL_CSV)
    df_crash = load_csv(CRASH_STAMPS_CSV)
    df_zupt = load_csv(ZUPT_CSV)
    df_accel_without_gravity_body = load_csv(ACCEL_WITHOUT_GRAVITY_BODY)
    df_accel_without_gravity_world = load_csv(ACCEL_WITHOUT_GRAVITY_WORLD)


    experiment_start = df_imu_raw["timestamp"].iloc[0]

    df_crash = processing.prepare_crash_events(df_crash, experiment_start)
    
    df_imu_raw = processing.add_relative_time(df_imu_raw, experiment_start)
    df_imu_mbf = processing.add_relative_time(df_imu_mbf, experiment_start)
    df_imu = processing.add_relative_time(df_imu, experiment_start)
    
    df_joint_states = processing.add_relative_time(df_joint_states, experiment_start)
    
    df_cmd_vel = processing.add_relative_time(df_cmd_vel, experiment_start)
    
    df_zupt = processing.add_relative_time(df_zupt, experiment_start)

    df_accel_without_gravity_body = processing.add_relative_time(df_accel_without_gravity_body, experiment_start)
    df_accel_without_gravity_world = processing.add_relative_time(df_accel_without_gravity_world, experiment_start)


    imu_raw_windows = processing.SlidingWindow(1.0, 0.5)
    df_raw_imu_features = imu_raw_windows.calculate(df_imu_raw)

    imu_raw_mbf_windows = processing.SlidingWindow(1.0, 0.5)
    df_raw_imu_mbf_features = imu_raw_mbf_windows.calculate(df_imu_mbf)

    imu_data_windows = processing.SlidingWindow(1.0, 0.5)
    df_imu_data_features = imu_data_windows.calculate(df_imu)

    accel_without_gravity_body_windows = processing.SlidingWindow(1.0, 0.5)
    df_accel_without_gravity_body_features = accel_without_gravity_body_windows.calculate(df_accel_without_gravity_body)

    accel_without_gravity_world_windows = processing.SlidingWindow(1.0, 0.5)
    df_accel_without_gravity_world_features = accel_without_gravity_world_windows.calculate(df_accel_without_gravity_world)


    return {
        "df_imu_raw": df_imu_raw,
        "df_imu_mbf": df_imu_mbf,
        "df_imu": df_imu,
        "df_accel_without_gravity_body": df_accel_without_gravity_body,
        "df_accel_without_gravity_world": df_accel_without_gravity_world,
        
        "df_joint_states": df_joint_states,
        "df_cmd_vel": df_cmd_vel,
        
        "df_crash": df_crash,
        "df_zupt": df_zupt,

        
        "df_raw_imu_features": df_raw_imu_features,
        "df_raw_imu_mbf_features": df_raw_imu_mbf_features,
        "df_imu_data_features": df_imu_data_features,
        "df_accel_without_gravity_world_features": df_accel_without_gravity_world_features,
        "df_accel_without_gravity_body_features": df_accel_without_gravity_body_features,
    }



data = load_and_process_data()


# df_imu = processing.add_relative_time(df_imu, experiment_start)

# df_imu_raw = processing.get_orientation(df_imu_raw, df_imu)

# gravity = processing.estimate_gravity(df_imu_raw, 0.0, 5.0)

# df_imu_raw = processing.remove_gravity(df_imu_raw, gravity)

# df_imu_raw = processing.add_magnitude(
#     df_imu_raw,
#     x_col="accel_dyn_x",
#     y_col="accel_dyn_y",
#     z_col="accel_dyn_z",
#     output_col="accel_dyn_mag",
# )

# st.title("Inertia Dashboard")
# st.write(df_imu_raw.columns)
# st.write(df_imu_raw["accel_dyn_x"])
# st.write(df_imu_raw[["t", "accel_dyn_x"]].head())
# st.write(df_imu_raw[["t", "accel_dyn_x"]].shape)
# st.write(df_imu_raw["accel_dyn_x"].isna().sum())
