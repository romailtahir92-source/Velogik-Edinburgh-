import streamlit as st
import math

# Mobile-friendly styling and wide layout
st.set_page_config(page_title="Voi Edinburgh Weekly Planner", layout="centered")

st.title("🚲 Voi Edinburgh Weekly Master Planner")
st.markdown("### Monday - Sunday Fleet Operations Optimizer")
st.write("---")

# --- SECTION 1: TOP GLOBAL PARAMETERS (FULLY ADJUSTABLE) ---
st.markdown("#### ⚙️ Top Core Metrics & Target Controls")
col_top1, col_top2 = st.columns(2)

with col_top1:
    current_dt = st.slider("Current Downtime %", 5, 30, 20)
    target_dt = st.slider("Weekly Target Downtime %", 5, 25, 17)
    weekly_task_increase = st.number_input(
        "Average Task Increase Per Week (Dynamic Churn)", 
        value=140, 
        step=10,
        help="Adjust this to account for seasonal growth or high-demand festival spikes over the week."
    )

with col_top2:
    open_tasks = st.number_input("Outstanding Backlog Tasks (Start of Week)", value=150, step=10)
    staff_cap = st.slider("Individual Driver Capacity (Tasks/Shift)", 60, 140, 100)

# --- LOGIC ENGINE ---
baseline_daily_tasks = 450  # Velogik standard baseline
daily_growth_fraction = weekly_task_increase / 7
hourly_growth_fraction = weekly_task_increase / (7 * 24)

dt_gap = max(0, current_dt - target_dt)
daily_backlog_clear_demand = (dt_gap * 0.2 * open_tasks)

# True Daily Workload required to hit the weekly downtime target
total_daily_required_tasks = math.ceil(baseline_daily_tasks + daily_growth_fraction + daily_backlog_clear_demand)

# Split required daily tasks between shifts (45% Day / 55% Night due to the 4.5h evening black hole)
day_required_tasks = math.ceil(total_daily_required_tasks * 0.45)
night_required_tasks = math.ceil(total_daily_required_tasks * 0.55)

# Calculate IDEAL staff counts needed per day (Forced to whole numbers via ceiling)
ideal_total_headcount = math.ceil(total_daily_required_tasks / staff_cap)
ideal_night_staff = math.ceil(ideal_total_headcount * 0.55)
ideal_day_staff = max(1, ideal_total_headcount - ideal_night_staff)

# --- MAIN WORKLOAD SUMMARY ---
st.write("---")
st.markdown("#### 📊 Target Workload Breakdown")
col_totals1, col_totals2 = st.columns(2)
with col_totals1:
    st.metric(label="Target Workload Required / Day", value=f"{total_daily_required_tasks} Tasks")
with col_totals2:
    st.metric(label="Total Required Targets / Week", value=f"{total_daily_required_tasks * 7} Tasks")

st.info(f"💡 **Target Strategy:** To drop downtime from {current_dt}% down to {target_dt}%, your team must systematically clear at least **{total_daily_required_tasks} total tasks every 24 hours**.")

# --- SECTION 2: MONDAY - SUNDAY ROSTERS ---
st.write("---")
st.markdown("#### 📅 Monday - Sunday Shift Schedules")
st.write("Tap on each day to adjust your live schedule and view the shift impact summaries.")

# Pre-programmed defaults matching your actual team constraints
default_schedule = {
    "Monday": {"day": 2, "night": 1},
    "Tuesday": {"day": 2, "night": 1},
    "Wednesday": {"day": 2, "night": 1},
    "Thursday": {"day": 2, "night": 2},
    "Friday": {"day": 2, "night": 3},
    "Saturday": {"day": 2, "night": 3},
    "Sunday": {"day": 2, "night": 2}
}

# Create clean interactive tabs for each day
tabs = st.tabs(list(default_schedule.keys()))

for idx, (day, staff) in enumerate(default_schedule.items()):
    with tabs[idx]:
        st.markdown(f"### {day} Operational Status")
        
        # Staff Adjustment Inputs for this specific day
        col_input_day, col_input_night = st.columns(2)
        with col_input_day:
            actual_day = st.number_input(
                f"Actual Day Staff ({day})", 
                value=staff["day"], min_value=0, step=1, key=f"day_{day}"
            )
        with col_input_night:
            actual_night = st.number_input(
                f"Actual Night Staff ({day})", 
                value=staff["night"], min_value=0, step=1, key=f"night_{day}"
            )
            
        st.write(" ")
        
        # Display Results Dashboard for this specific day
        col_res_day, col_res_night = st.columns(2)
        
        # Day Shift Box Evaluation
        with col_res_day:
            st.info("☀️ **Day Shift** (07:00 - 17:30)")
            st.write(f"🎯 **Ideal Staff Target:** **{ideal_day_staff}**")
            st.write(f"🏃‍♂️ **Actual Staff On-Street:** **{actual_day}**")
            
            if actual_day > 0:
                day_capacity = actual_day * staff_cap
                deficit = day_required_tasks - day_capacity
                if deficit > 0:
                    st.warning(f"⚠️ **Understaffed shortfall:**\n\nDrivers must pull **{staff_cap} tasks** each. **{deficit} tasks** will overflow into the evening gap.")
                else:
                    st.success(f"✅ **Adequate Coverage.**\n\nTarget allocation: **{math.ceil(day_required_tasks / actual_day)} tasks/person**.")
            else:
                st.error(f"🚨 **Critical Alert:** 0 staff. All {day_required_tasks} tasks fall behind.")
                
        # Night Shift Box Evaluation
        with col_res_night:
            st.error("🌙 **Night Shift** (22:00 - 07:00)")
            st.write(f"🎯 **Ideal Staff Target:** **{ideal_night_staff}**")
            st.write(f"🏃‍♂️ **Actual Staff On-Street:** **{actual_night}**")
            
            if actual_night > 0:
                night_capacity = actual_night * staff_cap
                deficit = night_required_tasks - night_capacity
                if deficit > 0:
                    st.warning(f"⚠️ **Understaffed shortfall:**\n\nDrivers must pull **{staff_cap} tasks** each. **{deficit} tasks** leak to downtime clock.")
                else:
                    st.success(f"✅ **Adequate Coverage.**\n\nTarget allocation: **{math.ceil(night_required_tasks / actual_night)} tasks/person**.")
            else:
                st.error(f"🚨 **Critical Alert:** 0 staff. All {night_required_tasks} tasks leak to downtime.")

# --- SECTION 3: BOTTOM OPERATIONAL GUIDANCE EXPLANATION ---
st.write("---")
st.markdown("### 📋 Dynamic Velocity Guidance")
st.markdown(
    f"Based on your adjustable configuration of an average **{weekly_task_increase} dynamic task increase per week**, "
    f"here is how the fleet's natural churn scale impacts your daily scheduling decisions:"
)

col_guide1, col_guide2, col_guide3 = st.columns(3)
with col_guide1:
    st.metric(label="Weekly Target Influx", value=f"+{weekly_task_increase} Tasks")
with col_guide2:
    st.metric(label="Daily Churn Rate", value=f"+{round(daily_growth_fraction, 1)} Tasks")
with col_guide3:
    st.metric(label="Hourly Task Velocity", value=f"+{round(hourly_growth_fraction, 1)} Tasks")

st.markdown(
    f"> **Supervisor Advisory Note:** The fleet naturally accumulates approximately **{round(daily_growth_fraction, 1)} new tasks every single day**, "
    f"which breaks down to an incoming velocity of **{round(hourly_growth_fraction, 1)} new tasks every single hour** across Edinburgh.\n"
    f">\n"
    f"> Because these parameters are fully adjustable, raising the weekly task increase will automatically scale up the **Ideal Staff Target** "
    f"shown in the schedule tabs above. Use higher values during summer peaks (like the Fringe Festival) or severe weather events "
    f"to ensure your rosters scale up before downtime accumulates."
)
