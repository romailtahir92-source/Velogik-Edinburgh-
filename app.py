import streamlit as st
import math

# Mobile-friendly styling and wide layout
st.set_page_config(page_title="Voi Edinburgh Weekly Planner", layout="centered")

st.title("🚲 Voi Edinburgh Weekly Master Planner")
st.markdown("### Monday - Sunday Fleet Operations Optimizer")

# --- SIDEBAR: GLOBAL METRICS & PARAMETERS ---
st.sidebar.header("⚙️ Global Weekly Parameters")

current_dt = st.sidebar.slider("Current Downtime %", 5, 30, 20)
target_dt = st.sidebar.slider("Weekly Target Downtime %", 5, 25, 17)
open_tasks = st.sidebar.number_input("Outstanding Backlog Tasks (Start of Week)", value=150, step=10)
staff_cap = st.sidebar.slider("Individual Driver Capacity (Tasks/Shift)", 60, 140, 100)

# NEW: Dynamic Weekly Task Volume Increase Area
st.sidebar.markdown("---")
st.sidebar.subheader("📈 Dynamic Task Growth")
weekly_task_increase = st.sidebar.number_input(
    "Avg. Dynamic Task Increase (New Tasks/Week)", 
    value=140, 
    step=10,
    help="Account for natural business growth, summer peak spikes, or heavy weather churn over the week."
)

# --- LOGIC ENGINE (WEEKLY SCALE) ---
baseline_daily_tasks = 450  # Velogik standard baseline
daily_growth_fraction = weekly_task_increase / 7

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

# --- HOME PAGE SUMMARY ---
st.markdown("#### 📊 Weekly Workload Target Breakdown")
col_totals1, col_totals2, col_totals3 = st.columns(3)
with col_totals1:
    st.metric(label="Target Workload / Day", value=f"{total_daily_required_tasks} Tasks")
with col_totals2:
    st.metric(label="Weekly Dynamic Growth", value=f"+{round(daily_growth_fraction, 1)} tasks/day")
with col_totals3:
    st.metric(label="Hourly Fleet Velocity", value=f"{round(total_daily_required_tasks / 24, 1)} tasks/hr")

st.info(f"💡 **To hit your {target_dt}% downtime target this week:** Your team must clear a total of **{total_daily_required_tasks * 7} tasks** across the 7 days.")

st.write("---")
st.markdown("#### 📅 Monday - Sunday Shift Rosters")
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
