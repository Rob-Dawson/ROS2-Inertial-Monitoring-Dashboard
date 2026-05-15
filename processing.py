#!/usr/bin/env python3
import pandas as pd
import numpy as np
from scipy.spatial.transform import Rotation as R


def calcRMS(window):
    if len(window) == 0:
        return "rms", np.nan
    window_np = np.array(window)
    rms = np.sqrt(np.mean(window_np * window_np))
    return "rms", rms


def calcSTD(window):
    if len(window) == 0:
        return "STD", np.nan

    window_np = np.array(window)
    std_dev = np.std(window_np)
    return "STD", std_dev


def calcMean(window):
    if len(window) == 0:
        return "mean", np.nan
    window_np = np.array(window)
    mean = np.mean(window)
    return "mean", mean


feature_map = {
    "accel_x": [calcRMS, calcSTD, calcMean],
    "accel_y": [calcRMS, calcSTD, calcMean],
    "accel_z": [calcRMS, calcSTD, calcMean],
    "gyro_x": [calcRMS, calcSTD, calcMean],
    "gyro_y": [calcRMS, calcSTD, calcMean],
    "gyro_z": [calcRMS, calcSTD, calcMean],
    "orientation_x": [calcRMS, calcSTD, calcMean],
    "orientation_y": [calcRMS, calcSTD, calcMean],
    "orientation_z": [calcRMS, calcSTD, calcMean],
    "orientation_w": [calcRMS, calcSTD, calcMean],
    # "cmd_vel"
    # "wheel_left_joint_velocity"
    # "wheel_right_joint_velocity"
    # "desired_linear_vel_x"
    # "desired_angular_vel_z"
}
signals = [
    "accel_x",
    "accel_y",
    "accel_z",
    "gyro_x",
    "gyro_y",
    "gyro_z",
    "orientation_x",
    "orientation_y",
    "orientation_z",
    "orientation_w",
    # "cmd_vel",
    # "wheel_left_joint_velocity",
    # "wheel_right_joint_velocity",
    # "desired_linear_vel_x",
    # "desired_angular_vel_z"
]


class SlidingWindow:
    def __init__(self, window_seconds, overlap=0.5):
        self.window_seconds = window_seconds
        self.overlap = overlap
        self.stride = window_seconds * (1 - overlap)
        self.features_df = pd.DataFrame()

    def calculate(self, df):
        return self.rolling(df)

    def rolling(self, df: pd.DataFrame):
        df = df.sort_values(by="t")
        window_start = df["t"].min()
        window_end = window_start + self.window_seconds
        dataset_end = df["t"].max()
        feature_rows = []

        while window_end <= dataset_end:

            window_df = df[(df["t"] >= window_start) & (df["t"] < window_end)]
            feature_row = {
                "t": window_start + self.window_seconds / 2,
                "start_time": window_start,
                "end_time": window_end,
                "sample_count": len(window_df),
            }

            for signal in signals:
                if signal not in window_df.columns:
                    for feature_name in feature_map[signal]:
                        name, feature = feature_name(signal_window)

                        feature_row[f"{signal}_{name}"] = np.nan
                    continue

                signal_window = window_df[signal].dropna().to_numpy()
                if signal_window.size == 0:
                    for feature_name in feature_map[signal]:
                        name, feature = feature_name(signal_window)

                        feature_row[f"{signal}_{name}"] = np.nan
                    continue

                for feature_name in feature_map[signal]:
                    name, feature = feature_name(signal_window)
                    feature_row[f"{signal}_{name}"] = feature
            feature_rows.append(feature_row)
            window_start += self.stride
            window_end = window_start + self.window_seconds

        return pd.DataFrame(feature_rows)

def prepare_crash_events(df_source, experiment_start):
    df = df_source.copy()
    df[["event", "event_time"]] = df["crash_log"].str.split(",", n=1, expand=True)
    df["event_time"] = pd.to_numeric(df["event_time"], errors="coerce")
    df = df.dropna(subset=["event_time"])
    df["t"] = df["event_time"] - experiment_start
    return df

def add_relative_time(df, start_time):
    df = df.copy()
    df["t"] = df["timestamp"] - start_time
    return df


def get_orientation(df_source, df_orientation):
    orientation_cols = [
        "timestamp",
        "orientation_x",
        "orientation_y",
        "orientation_z",
        "orientation_w",
    ]
    return pd.merge_asof(
        df_source.sort_values("timestamp"),
        df_orientation[orientation_cols].sort_values("timestamp"),
        on="timestamp",
        direction="nearest",
        tolerance=0.1,
    )


def estimate_gravity(df, start, end):

    window_df = df[(df["t"] >= start) & (df["t"] <= end)]
    accel = window_df[["accel_x", "accel_y", "accel_z"]].to_numpy()

    accel_mag = np.linalg.norm(accel, axis=1)

    return accel_mag.mean()


def remove_gravity(df, gravity):
    data = df.copy()
    gravity_world = np.array([0.0, 0.0, gravity])

    orientation_cols = [
        "orientation_x",
        "orientation_y",
        "orientation_z",
        "orientation_w",
    ]

    print(df[orientation_cols].head())
    print(df[orientation_cols].isna().sum())
    print(df[orientation_cols].shape)

    orientation = df[
        [
            "orientation_x",
            "orientation_y",
            "orientation_z",
            "orientation_w",
        ]
    ].to_numpy()

    accel = df[
        [
            "accel_x",
            "accel_y",
            "accel_z",
        ]
    ].to_numpy()

    rot = R.from_quat(orientation)
    gravity_body = rot.apply([0, 0, gravity])
    dynamic_accel = accel - gravity_body
    df["accel_dyn_x"] = dynamic_accel[:, 0]
    df["accel_dyn_y"] = dynamic_accel[:, 1]
    df["accel_dyn_z"] = dynamic_accel[:, 2]
    return df


def add_magnitude(df, x_col, y_col, z_col, output_col):
    df = df.copy()
    df[output_col] = np.sqrt(df[x_col] ** 2 + df[y_col] ** 2 + df[z_col] ** 2)
    return df
