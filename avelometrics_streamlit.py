import streamlit as st
import json
import pandas as pd
import matplotlib.pyplot as plt

def load_json(file):
    data = json.load(file)
    return data

def extract_shoe_data(data, shoe_key):
    if shoe_key not in data:
        return None
    shoe_data = data[shoe_key]
    total_steps = shoe_data.get("total_steps", 0)
    distance_cm = shoe_data.get("distance_in_cm", 0)
    duration_ms = shoe_data.get("duration_in_milliseconds", 0)
    
    strides = []
    for segment in shoe_data.get("segments", []):
        for stride in segment.get("strides", []):
            strides.append({
                "shoe": shoe_key,
                "mid_step_time": stride.get("mid_step_in_milliseconds", 0),
                "stride_velocity": stride.get("stride_velocity_in_cmps", 0),
                "stride_length": stride.get("stride_length_in_cm", 0)
            })
    
    return total_steps, distance_cm, pd.DataFrame(strides)

st.title("Running Data Parser")

uploaded_file = st.file_uploader("Upload your JSON file", type=["json"])

if uploaded_file is not None:
    data = load_json(uploaded_file)
    
    shoe_one_data = extract_shoe_data(data, "shoe_one")
    shoe_two_data = extract_shoe_data(data, "shoe_two")
    
    # Display total steps and distance for each shoe
    if shoe_one_data:
        st.subheader("Shoe One Summary")
        st.write(f"Total Steps: {shoe_one_data[0]}")
        st.write(f"Total Distance: {shoe_one_data[1] / 100} meters")
    
    if shoe_two_data:
        st.subheader("Shoe Two Summary")
        st.write(f"Total Steps: {shoe_two_data[0]}")
        st.write(f"Total Distance: {shoe_two_data[1] / 100} meters")
    
    # Combine data for both shoes
    df = pd.concat([shoe_one_data[2], shoe_two_data[2]], ignore_index=True) if shoe_one_data and shoe_two_data else shoe_one_data[2] if shoe_one_data else shoe_two_data[2]
    
    # Plot Stride Velocity over Time
    if not df.empty:
        st.subheader("Stride Velocity Over Time")
        fig, ax = plt.subplots()
        for key, group in df.groupby("shoe"):
            ax.plot(group["mid_step_time"], group["stride_velocity"], label=key)
        ax.set_xlabel("Time (ms)")
        ax.set_ylabel("Stride Velocity (cm/s)")
        ax.legend()
        st.pyplot(fig)
    
    # Plot Stride Length over Time
    if not df.empty:
        st.subheader("Stride Length Over Time")
        fig, ax = plt.subplots()
        for key, group in df.groupby("shoe"):
            ax.plot(group["mid_step_time"], group["stride_length"], label=key)
        ax.set_xlabel("Time (ms)")
        ax.set_ylabel("Stride Length (cm)")
        ax.legend()
        st.pyplot(fig)
