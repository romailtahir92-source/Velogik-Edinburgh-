import streamlit as st
import math

# Mobile-friendly styling and wide layout
st.set_page_config(page_title="Voi Edinburgh Ops Optimizer", layout="centered")

st.title("🚲 Voi Edinburgh Ops Dashboard")
st.markdown("### Whole-Number Staffing & Task Allocator")
st.write("Compare ideal staffing targets against your actual team available today.")

st.write("---")

# Section 1: Inputs for Targets & Capacity
st.markdown("#### 📊 Step 1: Input Live Fleet Metrics")
col_left, col_right = st.columns(2)

with col_left:
    current_dt = st.slider("Current Downtime %", 5, 30, 20)
    target_dt = st.slider("Target Downtime %", 5, 25, 17)

with col_right:
    open_tasks = st.number_input("Total Current Open Tasks", value=150, step=10)
    staff_cap = st.slider("Individual Driver Capacity (Tasks/Shift)", 60, 140, 100)

# Section 2: Inputs for Actual Live Staffing
st.write("---")
st.markdown("#### 👥 Step 2: Input Actual Available Staff For Today")
col_actual_day, col_actual_night = st.columns(2)

with col_actual_day:
    actual_day_staff = st.number_input("Actual Day Staff Checked In", value=2, min_value=0, step=1)

with col_actual_night:
    actual_night_staff = st.number_input("Actual Night Staff Checked In", value=1, min_value=0, step=1)

# --- LOGIC ENGINE ---
baseline_tasks = 450  # Based on Velogik data trends
dt_gap = max(0, current_dt - target_dt)
backlog_clear_demand = dt_gap * 0.2 * open_tasks
total_required_tasks = math.ceil(baseline_tasks + backlog_clear_demand)

# Split required tasks between shifts (45% Day / 55% Night due to 4.5h gap)
day_required_tasks = math.ceil(total_required_tasks * 0.45)
night_required_tasks = math.ceil(total_required_tasks * 0.55)

# Calculate IDEAL staff counts (Forced to whole numbers via ceiling)
ideal_total_headcount = math.ceil(total_required_tasks / staff_cap)
ideal_night_staff = math.ceil(ideal_total_headcount * 0.55)
ideal_day_staff = max(1, ideal_total_headcount - ideal_night_staff)

st.write("---")
st.markdown("### 📋 Shift Deployment Manifest")

# Display Columns
col1, col2 = st.columns(2)

# --- DAY SHIFT COLUMN ---
with col1:
    st.info("☀️ **Day Shift** (07:00 - 17:30)")
    st.markdown(f"🌟 **IDEAL Staff Needed:** **{ideal_day_staff}**")
    st.markdown(f"🏃‍♂️ **ACTUAL Staff Available:** **{actual_day_staff}**")
    
    if actual_day_staff > 0:
        actual_day_max_cap = actual_day_staff * staff_cap
        day_deficit = day_required_tasks - actual_day_max_cap
        
        if day_deficit > 0:
            st.warning(f"⚠️ **Understaffed by {ideal_day_staff - actual_day_staff} driver(s).**\n\nYour active day drivers must work at max capacity (**{staff_cap} tasks each**).\n\n*Shortfall: {day_deficit} tasks will roll over into the evening.*")
        else:
            per_person_day_target = math.ceil(day_required_tasks / actual_day_staff)
            st.success(f"✅ **Staffing Adequate.**\n\nTarget quota per active driver: **{per_person_day_target} tasks**.")
    else:
        st.error(f"🚨 **0 Day Staff Active!**\n\nAll {day_required_tasks} daytime tasks will drop into the backlog.")

# --- NIGHT SHIFT COLUMN ---
with col2:
    st.error("🌙 **Night Shift** (22:00 - 07:00)")
    st.markdown(f"🌟 **IDEAL Staff Needed:** **{ideal_night_staff}**")
    st.markdown(f"🏃‍♂️ **ACTUAL Staff Available:** **{actual_night_staff}**")
    
    if actual_night_staff > 0:
        actual_night_max_cap = actual_night_staff * staff_cap
        night_deficit = night_required_tasks - actual_night_max_cap
        
        if night_deficit > 0:
            st.warning(f"⚠️ **Understaffed by {ideal_night_staff - actual_night_staff} driver(s).**\n\nYour active night drivers must work at max capacity (**{staff_cap} tasks each**).\n\n*Shortfall: {night_deficit} tasks will bleed directly into tomorrow's downtime.*")
        else:
            per_person_night_target = math.ceil(night_required_tasks / actual_night_staff)
            st.success(f"✅ **Staffing Adequate.**\n\nTarget quota per active driver: **{per_person_night_target} tasks**.")
    else:
        st.error(f"🚨 **0 Night Staff Active!**\n\nAll {night_required_tasks} overnight tasks will bleed heavily into downtime.")

st.write("---")
st.caption("Target calculations dynamically weight the Night Shift heavier to actively protect your 5% downtime metric from the 4.5-hour evening gap.")
