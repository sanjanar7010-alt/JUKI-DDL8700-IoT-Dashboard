import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(
    page_title="JUKI DDL-8700 | Smart IoT Dashboard",
    page_icon="🧵",
    layout="wide",
)

@st.cache_data
def make_data(scenario="Normal", n=180):
    rng = np.random.default_rng(42)
    t = pd.date_range(datetime.now() - timedelta(minutes=n-1), periods=n, freq="min")

    rpm = rng.normal(3200, 180, n).clip(1800, 5000)
    stitch_length = rng.normal(2.8, 0.15, n).clip(2.0, 4.0)
    current = rng.normal(1.45, 0.12, n).clip(0.7, 3.0)
    vibration = rng.normal(1.65, 0.18, n).clip(0.5, 5.0)
    temperature = rng.normal(39, 1.2, n).clip(25, 70)
    power = (110 + 0.045*rpm + 22*current + rng.normal(0, 5, n)).clip(60, 500)

    state = np.array(["SEWING"] * n, dtype=object)
    fabric = np.array(["Cotton"] * n, dtype=object)
    layers = np.ones(n, dtype=int)
    operation = np.array(["Straight seam"] * n, dtype=object)

    if scenario == "High Energy":
        rpm[-55:] += 700
        current[-55:] += 0.35
        power[-55:] += 55
        stitch_length[-55:] += 0.25
        fabric[-55:] = "Denim"
        layers[-55:] = 4
        operation[-55:] = "Multi-layer seam"

    elif scenario == "Idle Wastage":
        state[-45:] = "IDLE"
        rpm[-45:] = rng.normal(250, 60, 45).clip(0, 500)
        current[-45:] = rng.normal(0.85, 0.06, 45)
        power[-45:] = rng.normal(75, 5, 45)

    elif scenario == "Machine Deterioration":
        ramp = np.linspace(0, 1, 60)
        vibration[-60:] += 2.0 * ramp
        temperature[-60:] += 12.0 * ramp
        current[-60:] += 0.55 * ramp
        power[-60:] += 18 * ramp

    stitches = (rpm * 0.42 + rng.normal(0, 35, n)).clip(100, None)
    energy_wh = power / 60.0
    energy_per_stitch = energy_wh / stitches

    expected_energy = (
        0.052 + 0.0000045*rpm + 0.006*(layers-1) +
        0.006*(stitch_length-2.8)
    ).clip(0.03, 0.14)

    actual_energy_metric = energy_per_stitch.clip(0.03, 0.18)
    energy_deviation = (
        (actual_energy_metric - expected_energy) / expected_energy * 100
    )

    vib_dev = vibration - 1.65
    temp_dev = temperature - 39
    current_dev = current - 1.45

    anomaly_score = (
        np.abs(energy_deviation)/25
        + np.abs(vib_dev)/1.5
        + np.abs(temp_dev)/10
        + np.abs(current_dev)/0.5
    ) / 4
    anomaly = anomaly_score > 0.85

    energy_issue = energy_deviation > 18
    process_issue = (layers >= 3) | (fabric == "Denim") | (rpm > 3900)
    machine_issue = (vibration > 2.8) | (temperature > 50) | (current > 2.0)

    # Correct idle-wastage calculation:
    # idle energy is based on power consumed while the machine is IDLE,
    # not on energy per stitch.
    idle_flag = state == "IDLE"
    idle_duration_min = np.zeros(n)
    run = 0
    for i in range(n):
        if idle_flag[i]:
            run += 1
            idle_duration_min[i] = run
        else:
            run = 0

    idle_energy_wh = np.where(idle_flag, power / 60.0, 0.0)
    idle_energy_percent = np.where(
        idle_flag,
        idle_energy_wh / np.maximum(energy_wh, 1e-9) * 100,
        0.0
    )
    idle_wastage = idle_flag & (power > 50) & (idle_duration_min >= 5)

    if scenario == "High Energy":
        energy_issue[-55:] = True
        process_issue[-55:] = True

    if scenario == "Machine Deterioration":
        machine_issue[-60:] = True

    if scenario == "Idle Wastage":
        idle_wastage[-45:] = True

    cause = np.where(
        machine_issue,
        "Mechanical / lubrication issue",
        np.where(
            idle_wastage,
            "Power consumed while machine is idle",
            np.where(
                process_issue & energy_issue,
                "High RPM + material/process load",
                np.where(
                    energy_issue,
                    "Energy above expected baseline",
                    "No dominant cause"
                )
            )
        )
    )

    probability = np.clip(
        55 + 25*anomaly_score + 10*machine_issue +
        8*energy_issue + 12*idle_wastage,
        0, 99
    )

    health_score = (
        100
        - 18*np.maximum(vibration-1.8, 0)
        - 2.2*np.maximum(temperature-42, 0)
        - 12*np.maximum(current-1.6, 0)
    ).clip(0, 100)

    return pd.DataFrame({
        "Time": t,
        "RPM": rpm,
        "Stitch Length": stitch_length,
        "Current (A)": current,
        "Vibration (mm/s)": vibration,
        "Temperature (°C)": temperature,
        "Power (W)": power,
        "Stitches/min": stitches,
        "Energy/Stitch": actual_energy_metric,
        "Expected Energy/Stitch": expected_energy,
        "Energy Deviation (%)": energy_deviation,
        "Anomaly Score": anomaly_score,
        "Anomaly": anomaly,
        "State": state,
        "Fabric": fabric,
        "Layers": layers,
        "Operation": operation,
        "Energy Issue": energy_issue,
        "Process Issue": process_issue,
        "Machine Issue": machine_issue,
        "Idle Duration (min)": idle_duration_min,
        "Idle Energy (Wh)": idle_energy_wh,
        "Idle Energy (%)": idle_energy_percent,
        "Idle Wastage": idle_wastage,
        "Cause": cause,
        "Probability": probability,
        "Health Score": health_score,
    })


st.markdown("""
<style>
.main {background-color:#f7f9fc;}
.block-container {padding-top:1.2rem;padding-bottom:2rem;}
.title {font-size:2rem;font-weight:800;color:#123b63;margin-bottom:0;}
.subtitle {color:#60758a;font-size:1rem;margin-bottom:1rem;}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="title">🧵 SMART IoT ENERGY & CONDITION MONITORING</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitle">Simulated dashboard — JUKI DDL-8700 industrial 1-needle lockstitch machine</div>',
    unsafe_allow_html=True
)

st.sidebar.header("Simulation Controls")
scenario = st.sidebar.selectbox(
    "Scenario",
    ["Normal", "High Energy", "Idle Wastage", "Machine Deterioration"]
)
refresh = st.sidebar.slider("Displayed time window (minutes)", 30, 180, 120)
st.sidebar.caption(
    "All values are simulated for prototype demonstration; they are not live machine measurements."
)

df = make_data(scenario)
view = df.tail(refresh).copy()
latest = view.iloc[-1]

c1,c2,c3,c4,c5,c6 = st.columns(6)
c1.metric("Machine","DDL-8700")
c2.metric("State",latest["State"])
c3.metric("RPM",f'{latest["RPM"]:,.0f}')
c4.metric("Power",f'{latest["Power (W)"]:.0f} W')
c5.metric("Temperature",f'{latest["Temperature (°C)"]:.1f} °C')
c6.metric("Health Score",f'{latest["Health Score"]:.0f}%')

st.divider()

left,right = st.columns(2)
with left:
    st.subheader("Energy Performance")
    st.line_chart(
        view.set_index("Time")[["Energy/Stitch","Expected Energy/Stitch"]],
        height=280
    )
    st.caption("Actual vs expected energy — proposed XGBoost Regressor output.")

with right:
    st.subheader("Machine Condition")
    q = view.set_index("Time")[[
        "Vibration (mm/s)","Temperature (°C)","Current (A)"
    ]].copy()
    for col in q.columns:
        mn,mx=q[col].min(),q[col].max()
        q[col]=(q[col]-mn)/(mx-mn) if mx>mn else 0
    st.line_chart(q,height=280)
    st.caption("Normalized vibration, temperature and current trends.")

# Dedicated idle-wastage section
if scenario == "Idle Wastage":
    st.subheader("⚠️ Idle Energy Wastage")
    i1,i2,i3,i4 = st.columns(4)

    idle_duration = float(latest["Idle Duration (min)"])
    idle_power = float(latest["Power (W)"])
    idle_energy = float(view["Idle Energy (Wh)"].sum())
    total_energy = float(view["Power (W)"].sum()/60.0)
    idle_share = idle_energy/max(total_energy,1e-9)*100

    i1.metric("Machine State","IDLE")
    i2.metric("Idle Power",f"{idle_power:.1f} W")
    i3.metric("Idle Duration",f"{idle_duration:.0f} min")
    i4.metric("Idle Energy",f"{idle_energy:.1f} Wh")

    st.warning(
        f"**Idle energy wastage detected:** the machine is consuming approximately "
        f"**{idle_power:.1f} W** while not actively sewing. "
        f"Idle energy represents about **{idle_share:.1f}%** of the displayed energy."
    )
    st.caption(
        "Recommended action: move the machine to standby or switch it off when sewing "
        "is not required. This is a Warning / Recommendation, not a maintenance fault."
    )

st.subheader("Process / Material Context")
p1,p2,p3,p4=st.columns(4)
p1.metric("Fabric",str(latest["Fabric"]))
p2.metric("Layers",int(latest["Layers"]))
p3.metric("Stitch Length",f'{latest["Stitch Length"]:.2f} mm')
p4.metric("Operation",str(latest["Operation"]))

st.subheader("Decision Engine — Final Outputs")
energy_dev=float(latest["Energy Deviation (%)"])
machine_issue=bool(latest["Machine Issue"])
process_issue=bool(latest["Process Issue"])
energy_issue=bool(latest["Energy Issue"])
idle_wastage=bool(latest["Idle Wastage"])

if energy_issue and not machine_issue and not idle_wastage:
    current_rpm=float(latest["RPM"])
    recommended_rpm=max(2500,min(current_rpm*.90,4500))
    saving=max(5,min(20,(current_rpm-recommended_rpm)/current_rpm*100+7))
    opt_title="OPTIMIZATION APPROVED"
    opt_text=f"Reduce sewing speed from {current_rpm:,.0f} to {recommended_rpm:,.0f} RPM."
    opt_detail=f"Estimated energy saving: {saving:.1f}%"
else:
    opt_title="OPTIMIZATION INHIBITED"
    opt_text="No automatic setpoint change for the current condition."
    opt_detail=(
        "Idle wastage requires standby/off action; machine-risk conditions require inspection."
        if idle_wastage or machine_issue else "Keep the current safe setting."
    )

if idle_wastage:
    warn_text=(
        f"Machine is IDLE but consuming {latest['Power (W)']:.1f} W. "
        "Use standby or switch off when sewing is not required."
    )
elif energy_issue or process_issue:
    warn_text=(
        f"High energy/process deviation ({energy_dev:+.1f}%). "
        "Check RPM, fabric thickness/layers and sewing conditions."
    )
else:
    warn_text="Energy and process behaviour are within the simulated baseline."

if machine_issue:
    maint_text=f"Condition anomaly detected. Probable cause: {latest['Cause']}."
    maint_detail=f"Cause probability: {latest['Probability']:.0f}%. Inspect before continued operation."
else:
    maint_text="No significant machine-condition deterioration detected."
    maint_detail="Continue monitoring vibration, temperature and motor current."

o1,o2,o3=st.columns(3)
with o1:
    st.success(f"### 🟢 Optimization\n\n{opt_title}\n\n{opt_text}\n\n{opt_detail}")
with o2:
    if idle_wastage:
        st.warning(f"### 🟡 Warning / Recommendation\n\n**IDLE ENERGY WASTAGE**\n\n{warn_text}")
    elif energy_issue or process_issue:
        st.warning(f"### 🟡 Warning / Recommendation\n\n{warn_text}")
    else:
        st.info(f"### 🟡 Warning / Recommendation\n\n{warn_text}")
with o3:
    if machine_issue:
        st.error(f"### 🔴 Maintenance Alert\n\n**MAINTENANCE REQUIRED**\n\n{maint_text}\n\n{maint_detail}")
    else:
        st.info(f"### 🔴 Maintenance Alert\n\n**NORMAL**\n\n{maint_text}\n\n{maint_detail}")

st.subheader("ML / Analytics Engine")
tools=pd.DataFrame({
    "Tool / Model":[
        "Rolling Mean + SD","Linear Regression","Isolation Forest",
        "XGBoost Regressor — Expected Energy",
        "XGBoost Regressor — Expected Machine Health",
        "XGBoost Multi-label Classifier","Bayesian Network",
        "StandardScaler (Z-score)","Grid / Bounded Search",
        "Rule-based Decision Engine"
    ],
    "Role":[
        "Normal baseline","Trend analysis","Multivariate anomaly detection",
        "Actual vs expected energy","Actual vs expected health parameters",
        "Energy / Process-Material / Machine issue classification",
        "Probable cause + probability","Feature normalization",
        "Find energy-efficient safe RPM/setpoint",
        "Final action selection + safety constraints"
    ],
    "Status":["ACTIVE"]*10
})
st.dataframe(tools,use_container_width=True,hide_index=True)

with st.expander("View simulated sensor data"):
    cols=[
        "Time","RPM","Current (A)","Power (W)","Energy/Stitch",
        "Vibration (mm/s)","Temperature (°C)","Fabric","Layers",
        "Energy Deviation (%)","Idle Duration (min)","Idle Energy (Wh)",
        "Idle Energy (%)","Anomaly Score","State","Cause"
    ]
    st.dataframe(view[cols].tail(40),use_container_width=True,hide_index=True)

st.caption(
    "Prototype note: this dashboard demonstrates the expected outcome using synthetic "
    "sewing-machine data. Replace the simulator with ESP32/MQTT/InfluxDB data when hardware is connected."
)
