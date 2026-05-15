import pandas as pd
import numpy as np
from bisect import bisect_left
from mcap_ros2.reader import read_ros2_messages


MCAP_FILE = "Turtlebot Inertial Monitoring/Carpet/Flat/Crashes/rosbag2_2026_05_05-14_11_05/rosbag2_2026_05_05-14_11_05_0.mcap"
OUTPUT_FILE = "Inertial_monitoring_motion.csv"

def get_header_time(ros_msg):
    if hasattr(ros_msg, "header"):
        return ros_msg.header.stamp.sec + ros_msg.header.stamp.nanosec * 1e-9
    return None

def extract_topic_to_csv(mcap_file, topic, output_csv, row_fn):
    rows = []

    for msg in read_ros2_messages(mcap_file, topics=[topic]):
        ros_msg = msg.ros_msg

        row = row_fn(ros_msg)
        row["log_time"] = msg.log_time_ns / 1e9

        if "timestamp" not in row:
            header_time = get_header_time(ros_msg)
            row["timestamp"] = header_time if header_time is not None else row["log_time"]

        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv(output_csv, index=False)
    print(f"Saved {len(df)} rows to {output_csv}")


## IMU Mean Bias Filter + Low Pass Filter + Madgwick filter for orientation
def extract_imu(imu):

    return {
        "accel_x": imu.linear_acceleration.x,
        "accel_y": imu.linear_acceleration.y,
        "accel_z": imu.linear_acceleration.z,
        "gyro_x": imu.angular_velocity.x,
        "gyro_y": imu.angular_velocity.y,
        "gyro_z": imu.angular_velocity.z,
        "orientation_x": imu.orientation.x,
        "orientation_y": imu.orientation.y,
        "orientation_z": imu.orientation.z,
        "orientation_w": imu.orientation.w,
    }


##RAW IMU DATA from sensor no filtering
def extract_imu_raw(imu):
    return {
        "accel_x": imu.linear_acceleration.x,
        "accel_y": imu.linear_acceleration.y,
        "accel_z": imu.linear_acceleration.z,
        "gyro_x": imu.angular_velocity.x,
        "gyro_y": imu.angular_velocity.y,
        "gyro_z": imu.angular_velocity.z,
    }


## IMU Data mean bias filtered
def extract_imu_MBF(imu):
    return {
        "accel_x": imu.linear_acceleration.x,
        "accel_y": imu.linear_acceleration.y,
        "accel_z": imu.linear_acceleration.z,
        "gyro_x": imu.angular_velocity.x,
        "gyro_y": imu.angular_velocity.y,
        "gyro_z": imu.angular_velocity.z,
    }


def extract_joint_states(joint):
    row = {}
    for i, name in enumerate(joint.name):
        row[f"{name}_position"] = joint.position[i]
        if i < len(joint.velocity):
            row[f"{name}_velocity"] = joint.velocity[i]
        if i < len(joint.effort):
            row[f"{name}_effort"] = joint.effort[i]

    return row


def extract_zupt_message(zupt):
    return {
        "linear_x": zupt.twist.twist.linear.x,
        "linear_y": zupt.twist.twist.linear.y,
        "linear_z": zupt.twist.twist.linear.z,
        "angular_x": zupt.twist.twist.angular.x,
        "angular_y": zupt.twist.twist.angular.y,
        "angular_z": zupt.twist.twist.angular.z,
    }


def extract_crash_logs(crash):
    return {
        "crash_log": crash.data,
    }


def extract_cmd_vel(cmd):
    return {
        "desired_linear_vel_x": cmd.twist.linear.x,
        "desired_angular_vel_z": cmd.twist.angular.z,
    }


### IMU Extraction ###
# type: sensor_msgs/msg/Imu
extract_topic_to_csv(MCAP_FILE, "/imu_raw", "imu_raw.csv", extract_imu_raw)
extract_topic_to_csv(MCAP_FILE, "/imu/data_raw", "imu_data_MBF.csv", extract_imu_MBF)
extract_topic_to_csv(
    MCAP_FILE, "/imu/data", "imu_data_MBF_LPF_Madgwick.csv", extract_imu
)
### IMU Extraction ###

### Joint States ###
# type: sensor_msgs/msg/JointState
extract_topic_to_csv(
    MCAP_FILE, "/joint_states", "joint_states.csv", extract_joint_states
)
### Joint States ###

### ZUPT ###
# type: geometry_msgs/msg/TwistWithCovarianceStamped
extract_topic_to_csv(MCAP_FILE, "/zupt/twist", "zupt.csv", extract_zupt_message)
### ZUPT ###

### Manual Input Crashes ###
# type: std_msgs/msg/String
extract_topic_to_csv(
    MCAP_FILE, "/crash_stamped", "crash_stamps.csv", extract_crash_logs
)
### Manual Input Crashes ###

### Desired Velocity ###
# type: geometry_msgs/msg/TwistStamped
extract_topic_to_csv(MCAP_FILE, "/cmd_vel", "desired_velocity.csv", extract_cmd_vel)
### Desired Velocity ###
