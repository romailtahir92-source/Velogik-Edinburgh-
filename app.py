import streamlit as st
import math

# Mobile-friendly styling and layout
st.set_page_config(page_title="Voi Edinburgh Ops Optimizer", layout="centered")

st.title("🚲 Voi Edinburgh Ops Dashboard")
st.markdown("### Whole-Number Staffing & Task Allocator")
st.write("Adjust the live metrics below to instantly calculate shift quotas.")

st.write("---")

# Layout columns for inputs
col_left, col_right = st.columns(2)

with col_left:
    current_dt = st.slider("Current Downtime %", 5, 30, 20)
    target_dt = st.slider("Target Downtime %", 5, 25, 17)

with col_right:
    open_tasks = st.number_input("Total Current Open Tasks", value=150, step=10)
    staff_cap = st.slider("Driver Task Capacity (Per Shift)", 60, 140, 100)

# Logic Engine
baseline_tasks = 450  # Based on Velogik data trends
dt_gap = max(0, current_dt - target_dt)
backlog_clear_demand = dt_gap * 0.2 * open_tasks
total_required_tasks = math.ceil(baseline_tasks + backlog_clear_demand)

# Headcount Calculation (Forced to Whole Numbers via Ceiling)
total_headcount = math.ceil(total_required_tasks / staff_cap)

# Roster Allocation (Weighting Night Shift to account for the 4.5h evening gap)
night_staff = math.ceil(total_headcount * 0.55)
day_staff = max(1, total_headcount - night_staff)

st.write("---")

# Total overview
st.success(f"**Total Headcount Required:** {day_staff + night_staff} Staff Members")

# Display shift assignments
col1, col2 = st.columns(2)

with col1:
    st.info("☀️ **Day Shift**\n\n(07:00 - 17:30)")
    st.metric(label="Staff Needed", value=f"{day_staff}")
    st.write(f"**Team Task Quota:** {math.ceil(total_required_tasks * 0.45)} tasks")

with col2:
    st.error("🌙 **Night Shift**\n\n(22:00 - 07:00)")
    st.metric(label="Staff Needed", value=f"{night_staff}")
    st.write(f"**Team Task Quota:** {math.ceil(total_required_tasks * 0.55)} tasks")

st.warning("⚠️ *Note: Night Shift quotas are intentionally weighted heavier to liquidate the task backlog built up during the 4.5-hour evening operational gap.*")
