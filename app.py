import streamlit as st
import pandas as pd
import numpy as np

# =========================================================
# PAGE SETUP
# =========================================================

st.set_page_config(
    page_title="JUKI DDL-8700 | Smart IoT",
    page_icon="🧵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CUSTOM DESIGN
# =========================================================

st.markdown("""
<style>

.block-container {
    padding-top: 1rem;
    max-width: 1500px;
}

.hero {
    padding: 25px 30px;
    border-radius: 18px;
    background: linear-gradient(135deg, #111a33, #1c2b52);
    border: 1px solid #30446f;
    margin-bottom: 20px;
}

.hero h1 {
    margin: 0;
    font-size: 2.2rem;
}

.hero p {
    color: #aebbd8;
    margin-top: 8px;
}

.section-title {
    font-size: 1.4rem;
    font-weight: 700;
    margin-top: 22px;
    margin-bottom: 12px;
}

.card {
    background: #111a30;
    border: 1px solid #2b3b68;
    border-radius: 14px;
    padding: 15px;
    min-height: 105px;
}

.small {
    color: #9eacc9;
    font-size: 0.82rem;
}

.value {
    font-size: 1.55rem;
    font-weight: 750;
    margin-top: 6px;
}

.pipeline {
    display: flex;
    gap: 7px;
    flex-wrap: wrap;
    align-items: center;
    margin-bottom: 20px;
}

.step {
    padding: 9px 12px;
    border-radius: 9px;
    background: #121b34;
    border: 1px solid #30446f;
    font-size: 0.82rem;
}

.arrow {
    color: #7893c5;
    font-weight: bold;
}

.decision {
    padding: 18px;
    border-radius: 14px;
    background: #111a30;
    min-height: 175px;
    border: 1px solid #30446f;
}

.green {
    border-left: 5px solid #39d98a;
}

.yellow {
    border-left: 5px solid #f2c94c;
}

.red {
    border-left: 5px solid #ff647c;
}

.blue {
    border-left: 5px solid #62a8ff;
}

.analysis-box {
    background: #111a30;
    border: 1px solid #2b3b68;
    border-radius: 14px;
    padding: 18px;
    min-height: 230px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# HELPER FUNCTION
# =========================================================

def metric_card(label, value, sub=""):
    st.markdown(
        f"""
        <div class="card">
            <div class="small">{label}</div>
            <div class="value">{value}</div>
            <div class="small">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# HEADER
# =========================================================

st.markdown("""
<div class="hero">

<h1>🧵 JUKI DDL-8700 — Smart IoT Energy & Condition Monitoring</h1>

<p>
Low-cost IoT retrofit simulation:
Sensor Data → Analysis → Cause Identification → Decision Engine
→ Optimization / Recommendation / Maintenance
</p>

</div>
""", unsafe_allow_html=True)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("⚙️ Simulation Controls")

scenario = st.sidebar.selectbox(
    "Machine Scenario",
    [
        "Normal Sewing",
        "Controllable Energy — High RPM",
        "Controllable Energy — Idle Wastage",
        "Process / Operator / Material Issue",
        "Machine Condition Deterioration"
    ]
)

fabric = st.sidebar.selectbox(
    "Fabric Type",
    [
        "Cotton",
        "Denim",
        "Polyester",
        "Knit"
    ]
)

layers = st.sidebar.slider(
    "Fabric Layers",
    1,
    8,
    2
)

rpm = st.sidebar.slider(
    "Sewing Speed (RPM)",
    500,
    5000,
    3000,
    100
)

stitch_length = st.sidebar.slider(
    "Stitch Length (mm)",
    1.0,
    5.0,
    2.5,
    0.1
)

acceleration = st.sidebar.slider(
    "Acceleration Setting",
    1,
    10,
    5
)

st.sidebar.divider()

st.sidebar.caption(
    "Simulation values represent the expected behaviour "
    "of the proposed JUKI DDL-8700 IoT retrofit system."
)


# =========================================================
# SIMULATED SENSOR DATA
# =========================================================

if scenario == "Normal Sewing":

    machine_state = "SEWING"

    power = 185
    current = 1.25
    vibration = 1.7
    temperature = 42

    idle_duration = 0

    process_issue = False
    machine_issue = False


elif scenario == "Controllable Energy — High RPM":

    machine_state = "SEWING"

    power = 255
    current = 1.65
    vibration = 1.9
    temperature = 45

    idle_duration = 0

    process_issue = False
    machine_issue = False


elif scenario == "Controllable Energy — Idle Wastage":

    machine_state = "IDLE"

    power = 75
    current = 0.85
    vibration = 1.1
    temperature = 38

    idle_duration = 45

    process_issue = False
    machine_issue = False


elif scenario == "Process / Operator / Material Issue":

    machine_state = "SEWING"

    power = 245
    current = 1.55
    vibration = 1.9
    temperature = 44

    idle_duration = 0

    process_issue = True
    machine_issue = False


else:

    machine_state = "SEWING"

    power = 238
    current = 1.58
    vibration = 4.8
    temperature = 61

    idle_duration = 0

    process_issue = False
    machine_issue = True


# =========================================================
# MATERIAL / PROCESS EFFECT
# =========================================================

material_factor = {

    "Cotton": 1.00,
    "Denim": 1.15,
    "Polyester": 0.98,
    "Knit": 1.05

}[fabric]

layer_factor = 1 + (layers - 1) * 0.055

stitch_factor = 1 + (stitch_length - 2.5) * 0.025


# =========================================================
# EXPECTED ENERGY MODEL
# =========================================================

if machine_state == "IDLE":

    expected_power = 8

else:

    expected_power = (
        190
        + (rpm - 3000) * 0.025
    )

    expected_power *= material_factor
    expected_power *= layer_factor
    expected_power *= stitch_factor


# =========================================================
# ENERGY CALCULATIONS
# =========================================================

energy_deviation = power - expected_power

energy_deviation_percent = (
    energy_deviation / expected_power
) * 100


# =========================================================
# PRODUCTION CALCULATIONS
# =========================================================

simulation_minutes = 60

if machine_state == "SEWING":

    stitch_count = int(
        rpm * simulation_minutes * 0.72
    )

else:

    stitch_count = 0


energy_wh = power * simulation_minutes / 60

idle_energy_wh = (
    power * idle_duration / 60
)

if energy_wh > 0:

    idle_energy_percent = (
        idle_energy_wh / energy_wh
    ) * 100

else:

    idle_energy_percent = 0


if stitch_count > 0:

    energy_per_stitch = (
        energy_wh / stitch_count
    )

else:

    energy_per_stitch = 0


# =========================================================
# COMMON ANALYSIS
# =========================================================

energy_anomaly = False

if machine_state == "IDLE":

    if idle_energy_wh > 5:

        energy_anomaly = True

else:

    if power > expected_power * 1.10:

        energy_anomaly = True


# Vibration anomaly
vibration_anomaly = vibration > 3.5

# Temperature anomaly
temperature_anomaly = temperature > 55

# Current anomaly
current_anomaly = current > 2.0


# =========================================================
# MACHINE CONDITION ANALYSIS
# =========================================================

machine_condition_anomaly = (

    vibration_anomaly
    or
    temperature_anomaly
    or
    current_anomaly
)


# =========================================================
# PROCESS / MATERIAL ANALYSIS
# =========================================================

process_material_anomaly = process_issue


# =========================================================
# FINAL CAUSE DECISION
# =========================================================

if machine_condition_anomaly:

    final_output = "MAINTENANCE ALERT"

    probable_cause = "Machine-condition deterioration"

    probability = 0.91

    automatic_optimization_allowed = False


elif process_material_anomaly:

    final_output = "WARNING / RECOMMENDATION"

    probable_cause = "Process / Operator / Material"

    probability = 0.88

    automatic_optimization_allowed = False


elif energy_anomaly:

    final_output = "AUTO OPTIMIZATION"

    probable_cause = "Controllable energy parameter"

    probability = 0.94

    automatic_optimization_allowed = True


else:

    final_output = "NORMAL"

    probable_cause = "No significant abnormality"

    probability = 0.96

    automatic_optimization_allowed = False


# =========================================================
# OPTIMIZATION
# =========================================================

if scenario == "Controllable Energy — Idle Wastage":

    optimization_action = "AUTO STANDBY"

    optimized_setting = "STANDBY / POWER-SAVING"

    optimized_power = 8

    power_saving = power - optimized_power

    saving_percent = (
        power_saving / power
    ) * 100

    optimization_message = (
        "Idle energy is caused by a controllable machine state. "
        "The system automatically requests standby / power-saving mode."
    )


elif scenario == "Controllable Energy — High RPM":

    optimized_rpm = max(
        1200,
        rpm - 500
    )

    optimization_action = "RPM OPTIMIZATION"

    optimized_setting = (
        f"{optimized_rpm:,} RPM"
    )

    optimized_power = max(
        150,
        power - 38
    )

    power_saving = power - optimized_power

    saving_percent = (
        power_saving / power
    ) * 100

    optimization_message = (
        "Energy consumption is high, but no process/material "
        "or machine-condition cause was detected. "
        "A safe RPM reduction is therefore eligible."
    )


else:

    optimization_action = "NO AUTOMATIC CHANGE"

    optimized_setting = "No automatic change"

    optimized_power = power

    power_saving = 0

    saving_percent = 0

    optimization_message = (
        "Automatic optimization is inhibited."
    )


# =========================================================
# MACHINE HEALTH SCORE
# =========================================================

health_score = (
    100
    - vibration * 7
    - max(0, temperature - 40) * 0.8
)

health_score = max(
    0,
    min(100, health_score)
)

if machine_issue:

    health_score = 58


# =========================================================
# SYSTEM DATA FLOW
# =========================================================

st.markdown(
    '<div class="section-title">🔄 System Data & Analysis Flow</div>',
    unsafe_allow_html=True
)

st.markdown("""
<div class="pipeline">

<div class="step">Sensors</div>
<div class="arrow">→</div>

<div class="step">ESP32</div>
<div class="arrow">→</div>

<div class="step">Wi-Fi / MQTT</div>
<div class="arrow">→</div>

<div class="step">InfluxDB + SQL</div>
<div class="arrow">→</div>

<div class="step">Preprocessing</div>
<div class="arrow">→</div>

<div class="step">Feature Extraction</div>
<div class="arrow">→</div>

<div class="step">Common Analysis</div>
<div class="arrow">→</div>

<div class="step">Integrated Analysis</div>
<div class="arrow">→</div>

<div class="step">XGBoost</div>
<div class="arrow">→</div>

<div class="step">Bayesian Network</div>
<div class="arrow">→</div>

<div class="step">Decision Engine</div>

</div>
""", unsafe_allow_html=True)


# =========================================================
# MACHINE OVERVIEW
# =========================================================

st.markdown(
    '<div class="section-title">1. 🧵 Live Machine Overview</div>',
    unsafe_allow_html=True
)

cols = st.columns(6)

with cols[0]:
    metric_card(
        "Machine",
        "JUKI DDL-8700",
        "IoT retrofit"
    )

with cols[1]:
    metric_card(
        "Machine State",
        machine_state,
        "State classification"
    )

with cols[2]:
    metric_card(
        "RPM",
        f"{rpm:,}",
        "Sewing speed"
    )

with cols[3]:
    metric_card(
        "Power",
        f"{power:.0f} W",
        "Active power"
    )

with cols[4]:
    metric_card(
        "Energy",
        f"{energy_wh:.1f} Wh",
        "1-hour simulation"
    )

with cols[5]:
    metric_card(
        "Health",
        f"{health_score:.0f}%",
        "Machine condition"
    )


# =========================================================
# SENSOR DATA
# =========================================================

st.markdown(
    '<div class="section-title">2. 📡 Sensor Data Received</div>',
    unsafe_allow_html=True
)

cols = st.columns(6)

with cols[0]:
    metric_card(
        "Voltage",
        "230 V",
        "PZEM-004T"
    )

with cols[1]:
    metric_card(
        "Current",
        f"{current:.2f} A",
        "Energy / motor current"
    )

with cols[2]:
    metric_card(
        "Vibration",
        f"{vibration:.1f}",
        "MPU6050 RMS"
    )

with cols[3]:
    metric_card(
        "Temperature",
        f"{temperature:.0f} °C",
        "DS18B20"
    )

with cols[4]:
    metric_card(
        "RPM",
        f"{rpm:,}",
        "Pulse sensor"
    )

with cols[5]:
    metric_card(
        "Stitch Count",
        f"{stitch_count:,}",
        "Output detection"
    )


# =========================================================
# ANALYSIS ENGINE
# =========================================================

st.markdown(
    '<div class="section-title">3. 🧠 Analysis Engine</div>',
    unsafe_allow_html=True
)

a, b, c = st.columns(3)

with a:

    st.markdown(
        '<div class="analysis-box">',
        unsafe_allow_html=True
    )

    st.markdown("### Common Analysis")

    st.write("✓ Rolling Mean + SD → normal baseline")

    st.write("✓ Linear Regression → trends")

    st.write("✓ Isolation Forest → multivariate anomaly")

    st.write(
        f"✓ Machine State → **{machine_state}**"
    )

    st.markdown("</div>", unsafe_allow_html=True)


with b:

    st.markdown(
        '<div class="analysis-box">',
        unsafe_allow_html=True
    )

    st.markdown("### Integrated Analysis")

    st.write(
        f"Energy model → expected **{expected_power:.1f} W**"
    )

    st.write(
        f"Actual − expected → **{energy_deviation:+.1f} W**"
    )

    st.write(
        f"Process / Material → "
        f"**{'ABNORMAL' if process_material_anomaly else 'NORMAL'}**"
    )

    st.write(
        f"Machine Condition → "
        f"**{'ABNORMAL' if machine_condition_anomaly else 'NORMAL'}**"
    )

    st.markdown("</div>", unsafe_allow_html=True)


with c:

    st.markdown(
        '<div class="analysis-box">',
        unsafe_allow_html=True
    )

    st.markdown("### Cause Identification")

    st.write(
        f"XGBoost Multi-Label → **{final_output}**"
    )

    st.write(
        f"Bayesian Network → **{probable_cause}**"
    )

    st.write(
        f"Probability → **{probability:.0%}**"
    )

    st.write(
        "Decision Engine → final action"
    )

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# ENERGY PERFORMANCE
# =========================================================

st.markdown(
    '<div class="section-title">4. ⚡ Energy Performance</div>',
    unsafe_allow_html=True
)

cols = st.columns(4)

with cols[0]:
    metric_card(
        "Expected Power",
        f"{expected_power:.1f} W",
        "XGBoost energy model"
    )

with cols[1]:
    metric_card(
        "Energy Deviation",
        f"{energy_deviation:+.1f} W",
        f"{energy_deviation_percent:+.1f}%"
    )

with cols[2]:
    metric_card(
        "Energy / Stitch",
        (
            f"{energy_per_stitch:.4f} Wh"
            if stitch_count > 0
            else "N/A"
        ),
        "Productivity measure"
    )

with cols[3]:
    metric_card(
        "Idle Energy",
        f"{idle_energy_wh:.1f} Wh",
        f"{idle_energy_percent:.1f}% of energy"
    )


# =========================================================
# PROCESS / MATERIAL
# =========================================================

st.markdown(
    '<div class="section-title">5. 🧵 Process & Material Context</div>',
    unsafe_allow_html=True
)

cols = st.columns(4)

with cols[0]:
    metric_card(
        "Fabric",
        fabric,
        "Material type"
    )

with cols[1]:
    metric_card(
        "Layers",
        layers,
        "Fabric plies"
    )

with cols[2]:
    metric_card(
        "Stitch Length",
        f"{stitch_length:.1f} mm",
        "Machine setting"
    )

with cols[3]:
    metric_card(
        "Acceleration",
        acceleration,
        "Control setting"
    )


# =========================================================
# MACHINE CONDITION
# =========================================================

st.markdown(
    '<div class="section-title">6. 🔧 Machine Condition</div>',
    unsafe_allow_html=True
)

cols = st.columns(4)

with cols[0]:
    metric_card(
        "Vibration",
        f"{vibration:.1f}",
        "MPU6050"
    )

with cols[1]:
    metric_card(
        "Temperature",
        f"{temperature:.0f} °C",
        "DS18B20"
    )

with cols[2]:
    metric_card(
        "Motor Current",
        f"{current:.2f} A",
        "Current signature"
    )

with cols[3]:
    metric_card(
        "Health Score",
        f"{health_score:.0f}%",
        "Condition estimate"
    )


# =========================================================
# SENSOR TRENDS
# =========================================================

st.markdown(
    '<div class="section-title">7. 📈 Sensor Trends</div>',
    unsafe_allow_html=True
)

rng = np.random.default_rng(42)

time = pd.date_range(
    "2026-09-14 09:00",
    periods=60,
    freq="min"
)

power_trend = rng.normal(
    power,
    max(2, power * 0.035),
    60
)

vibration_trend = rng.normal(
    vibration,
    0.10,
    60
)

temperature_trend = np.linspace(
    max(30, temperature - 4),
    temperature,
    60
)

trend = pd.DataFrame(
    {
        "Power (W)": power_trend,
        "Vibration": vibration_trend,
        "Temperature (°C)": temperature_trend
    },
    index=time
)

if machine_state == "IDLE":

    trend.iloc[:45, 0] = rng.normal(
        185,
        5,
        45
    )

    trend.iloc[45:, 0] = rng.normal(
        75,
        2,
        15
    )


c1, c2 = st.columns(2)

with c1:

    st.markdown("**Power Consumption**")

    st.line_chart(
        trend[["Power (W)"]],
        height=280
    )

with c2:

    st.markdown("**Machine Condition**")

    st.line_chart(
        trend[
            [
                "Vibration",
                "Temperature (°C)"
            ]
        ],
        height=280
    )


# =========================================================
# IDLE AUTO OPTIMIZATION
# =========================================================

if scenario == "Controllable Energy — Idle Wastage":

    st.markdown(
        '<div class="section-title">8. ⚡ Idle Wastage → Automatic Optimization</div>',
        unsafe_allow_html=True
    )

    st.success(
        f"""
        **Idle energy wastage confirmed.**

        Machine is idle for **{idle_duration} minutes**
        while consuming **{idle_energy_wh:.1f} Wh**.

        No process/material or machine-condition abnormality was detected.

        Therefore, the energy wastage is classified as a
        **controllable parameter** and automatic standby is permitted.
        """
    )

    cols = st.columns(4)

    with cols[0]:
        metric_card(
            "Idle Duration",
            f"{idle_duration} min",
            "No sewing output"
        )

    with cols[1]:
        metric_card(
            "Before",
            f"{power:.0f} W",
            "Idle consumption"
        )

    with cols[2]:
        metric_card(
            "Automatic Action",
            "STANDBY",
            "Power-saving mode"
        )

    with cols[3]:
        metric_card(
            "After",
            f"{optimized_power:.0f} W",
            f"Saving ≈ {power_saving:.0f} W"
        )


# =========================================================
# FINAL THREE OUTPUTS
# =========================================================

st.markdown(
    '<div class="section-title">9. 🎯 Decision Engine — Final Outputs</div>',
    unsafe_allow_html=True
)

o1, o2, o3 = st.columns(3)


# ---------------------------------------------------------
# OPTIMIZATION
# ---------------------------------------------------------

with o1:

    st.markdown(
        f"""
        <div class="decision green">

        <h3>🟢 Optimization</h3>

        <p>
        <b>Status:</b>
        {"AUTO-OPTIMIZATION ELIGIBLE"
        if automatic_optimization_allowed
        else "INHIBITED"}
        </p>

        <p>
        <b>Action:</b>
        {optimized_setting}
        </p>

        <p>
        {optimization_message}
        </p>

        <p>
        <b>Expected Saving:</b>
        {power_saving:.0f} W
        ({saving_percent:.1f}%)
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )


# ---------------------------------------------------------
# WARNING / RECOMMENDATION
# ---------------------------------------------------------

with o2:

    if process_material_anomaly:

        warning_status = "ACTION REQUIRED"

        warning_text = (
            "Energy consumption is associated with "
            "process/operator/material conditions."
        )

        recommendation = (
            f"Check {fabric} fabric, {layers} layers, "
            f"stitch length, handling and operator practice."
        )

    else:

        warning_status = "NO WARNING"

        warning_text = (
            "No process/operator/material abnormality detected."
        )

        recommendation = (
            "Continue monitoring process and material context."
        )

    st.markdown(
        f"""
        <div class="decision yellow">

        <h3>🟡 Warning / Recommendation</h3>

        <p>
        <b>Status:</b>
        {warning_status}
        </p>

        <p>
        {warning_text}
        </p>

        <p>
        {recommendation}
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )


# ---------------------------------------------------------
# MAINTENANCE ALERT
# ---------------------------------------------------------

with o3:

    if machine_condition_anomaly:

        maintenance_status = "MAINTENANCE REQUIRED"

        maintenance_text = (
            f"Abnormal machine-condition evidence detected. "
            f"Vibration = {vibration:.1f}, "
            f"Temperature = {temperature:.0f} °C, "
            f"Current = {current:.2f} A."
        )

        maintenance_action = (
            "Inspect lubrication, bearings, alignment and motor condition."
        )

    else:

        maintenance_status = "NO ALERT"

        maintenance_text = (
            "Machine-condition parameters are within "
            "the simulated healthy range."
        )

        maintenance_action = (
            "Continue condition monitoring."
        )

    st.markdown(
        f"""
        <div class="decision red">

        <h3>🔴 Maintenance Alert</h3>

        <p>
        <b>Status:</b>
        {maintenance_status}
        </p>

        <p>
        {maintenance_text}
        </p>

        <p>
        {maintenance_action}
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# OPTIMIZATION SAFETY GATE
# =========================================================

st.markdown(
    '<div class="section-title">10. 🛡️ Optimization Supervisor / Safety Gate</div>',
    unsafe_allow_html=True
)

checks = pd.DataFrame(
    {
        "Safety / Control Check": [
            "Data Quality",
            "Machine Condition Inhibit",
            "RPM / Setpoint Limits",
            "Process Constraints",
            "Operator Override",
            "Command Acknowledgement"
        ],

        "Result": [

            "PASS",

            (
                "BLOCKED"
                if machine_condition_anomaly
                else "PASS"
            ),

            "PASS",

            (
                "BLOCKED"
                if process_material_anomaly
                else "PASS"
            ),

            "NO OVERRIDE",

            "SIMULATED ACK"
        ]
    }
)

st.dataframe(
    checks,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# CLOSED LOOP
# =========================================================

if automatic_optimization_allowed:

    st.info(
        """
        **Closed-loop optimization active:**

        Approved setting → JUKI control system → sewing motor
        → sensor feedback → energy measurement
        → compare with target → maintain / adjust setting.
        """
    )


# =========================================================
# ML / ANALYTICS
# =========================================================

st.markdown(
    '<div class="section-title">11. 🤖 ML & Analytics Used</div>',
    unsafe_allow_html=True
)

tools = pd.DataFrame(
    {
        "Method": [

            "Rolling Mean + SD",

            "Linear Regression",

            "Isolation Forest",

            "StandardScaler",

            "XGBoost Regressor — Energy",

            "XGBoost Regressor — Machine Health",

            "XGBoost Multi-Label Classifier",

            "Bayesian Network",

            "Grid / Bounded Search",

            "Closed-Loop Control"
        ],

        "Role in Project": [

            "Establish healthy operating baseline",

            "Detect trends in energy and machine variables",

            "Detect multivariate abnormal behaviour",

            "Normalize continuous features",

            "Predict expected energy from RPM, process and material context",

            "Predict expected vibration/current/temperature behaviour",

            "Classify abnormality as Energy, Process/Material or Machine",

            "Infer probable cause and probability",

            "Search safe RPM values for efficient operation",

            "Measure → Compare → Correct controllable setting"
        ]
    }
)

st.dataframe(
    tools,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "Simulation dashboard — sensor values and model outputs are synthetic. "
    "The dashboard demonstrates the expected architecture and decision logic "
    "of the proposed low-cost IoT retrofit system for the JUKI DDL-8700."
)
