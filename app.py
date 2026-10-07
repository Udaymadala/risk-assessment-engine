import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(
    page_title="Enterprise Risk Assessment & Heatmap Engine",
    page_icon="🛡️",
    layout="wide"
)

# ---------------------------------------------------------
# Framework Data & Definitions (NIST SP 800-30 / 5x5 Matrix)
# ---------------------------------------------------------
LIKELIHOOD_LEVELS = {
    1: "1 - Rare (Highly improbable / non-routable)",
    2: "2 - Unlikely (Requires insider access or extreme conditions)",
    3: "3 - Moderate (Opportunistic attack / common exploit chain)",
    4: "4 - Likely (Public exploit exists / unpatched perimeter)",
    5: "5 - Almost Certain (Actively exploited in wild / zero controls)"
}

IMPACT_LEVELS = {
    1: "1 - Negligible (Local disruption / no data leakage)",
    2: "2 - Minor (Internal staff inconvenience / P2 data)",
    3: "3 - Moderate (FERPA or sensitive operational data exposure)",
    4: "4 - Major (Regulatory violation / HIPAA P4 data / research halt)",
    5: "5 - Catastrophic (System-wide outage / severe civil liability)"
}

CONTROL_CATALOG = {
    "Network Segmentation / Isolated VLAN": 0.25,
    "Strict Inbound/Outbound ACLs (Static IPs Only)": 0.20,
    "Multi-Factor Authentication (MFA) & Conditional Access": 0.30,
    "Endpoint Detection & Response (EDR) Active Blocking": 0.25,
    "Tokenization / De-identification Pipeline": 0.35,
    "At-Rest & In-Transit Cryptographic Controls": 0.20,
    "Role-Based Access Control (RBAC) & Least Privilege": 0.15,
    "Centralized Logging & SIEM Monitoring": 0.10,
    "Vendor BAA / Strict Data Protection Addendum Signed": 0.20
}

def get_severity(score: int) -> tuple[str, str]:
    if score >= 15:
        return "Critical", "#d9534f"
    elif score >= 10:
        return "High", "#f0ad4e"
    elif score >= 5:
        return "Medium", "#f7ecb5"
    return "Low", "#5cb85c"

# Initialize Session State for Risk Register
if "risk_register" not in st.session_state:
    st.session_state.risk_register = []

# ---------------------------------------------------------
# Sidebar: Risk Evaluation Input Form
# ---------------------------------------------------------
st.sidebar.header("Assess New Risk Scenario")

risk_title = st.sidebar.text_input(
    "Risk Title / Scenario",
    value="Legacy Workstation Running Unsupported OS"
)

asset_category = st.sidebar.selectbox(
    "Asset / System Classification",
    ["P4 - High / Restricted (PHI, SSN, PCI)", 
     "P3 - Moderate (FERPA, Research Data)", 
     "P2 - Internal Operations", 
     "P1 - Public Assets"]
)

inherent_l_val = st.sidebar.selectbox(
    "Inherent Likelihood (Before Controls)",
    options=list(LIKELIHOOD_LEVELS.keys()),
    format_func=lambda x: LIKELIHOOD_LEVELS[x],
    index=3  # Default: 4 - Likely
)

inherent_i_val = st.sidebar.selectbox(
    "Inherent Impact (Business / Compliance Consequence)",
    options=list(IMPACT_LEVELS.keys()),
    format_func=lambda x: IMPACT_LEVELS[x],
    index=3  # Default: 4 - Major
)

selected_controls = st.sidebar.multiselect(
    "Select Compensating Controls Implemented",
    options=list(CONTROL_CATALOG.keys()),
    default=[
        "Network Segmentation / Isolated VLAN",
        "Strict Inbound/Outbound ACLs (Static IPs Only)"
    ]
)

notes = st.sidebar.text_area(
    "Assessment Notes & Exceptions",
    value="Hardware cannot be upgraded without vendor replacement; network isolation verified."
)

# ---------------------------------------------------------
# Risk Calculations
# ---------------------------------------------------------
inherent_score = inherent_l_val * inherent_i_val
inherent_sev, inherent_color = get_severity(inherent_score)

# Calculate combined control effectiveness (capped at 80% to preserve residual risk reality)
total_effectiveness = min(0.80, sum(CONTROL_CATALOG[c] for c in selected_controls))
residual_score = max(1, round(inherent_score * (1.0 - total_effectiveness)))
residual_sev, residual_color = get_severity(residual_score)

# Estimate residual coordinates on 5x5 grid
residual_i = max(1, round(inherent_i_val * (1.0 - (total_effectiveness * 0.4))))
residual_l = max(1, round(residual_score / residual_i))
residual_l = min(5, max(1, residual_l))

if st.sidebar.button("Commit to Risk Register"):
    st.session_state.risk_register.append({
        "Title": risk_title,
        "Asset Tier": asset_category.split(" - ")[0],
        "Inherent Score": inherent_score,
        "Inherent Severity": inherent_sev,
        "Controls Applied": len(selected_controls),
        "Effectiveness": f"{int(total_effectiveness * 100)}%",
        "Residual Score": residual_score,
        "Residual Severity": residual_sev,
        "Notes": notes
    })
    st.sidebar.success("Added scenario to institutional register.")

# ---------------------------------------------------------
# Main Page Display
# ---------------------------------------------------------
st.title("🛡️ Institutional Risk Assessment Dashboard")
st.caption("Quantitative Likelihood × Impact Modeling aligned with NIST SP 800-30 and Institutional Data Tiers.")

# Top Metrics Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(
        label="Inherent Risk Score",
        value=f"{inherent_score} / 25",
        delta=inherent_sev,
        delta_color="inverse"
    )
with col2:
    st.metric(
        label="Total Control Mitigation",
        value=f"{int(total_effectiveness * 100)}%",
        delta=f"{len(selected_controls)} Active Controls"
    )
with col3:
    st.metric(
        label="Residual Risk Score",
        value=f"{residual_score} / 25",
        delta=f"-{inherent_score - residual_score} Points",
        delta_color="normal"
    )
with col4:
    st.metric(
        label="Residual Severity Status",
        value=residual_sev
    )

st.markdown("---")

# Visual Heatmap & Analysis
chart_col, detail_col = st.columns([3, 2])

with chart_col:
    st.subheader("Interactive 5×5 Risk Matrix")

    # Heatmap Grid Values (Likelihood x Impact)
    z_matrix = [
        [1,  2,  3,  4,  5],    # Impact 1
        [2,  4,  6,  8,  10],   # Impact 2
        [3,  6,  9,  12, 15],   # Impact 3
        [4,  8,  12, 16, 20],   # Impact 4
        [5,  10, 15, 20, 25]    # Impact 5
    ]

    custom_colorscale = [
        [0.0, "#2ecc71"],   # Low: Green
        [0.2, "#a3e048"],
        [0.36, "#f1c40f"],  # Medium: Yellow
        [0.56, "#e67e22"],  # High: Orange
        [1.0, "#e74c3c"]    # Critical: Red
    ]

    fig = go.Figure()

    # Background Risk Color Grid
    fig.add_trace(go.Heatmap(
        z=z_matrix,
        x=["1 - Rare", "2 - Unlikely", "3 - Moderate", "4 - Likely", "5 - Almost Certain"],
        y=["1 - Negligible", "2 - Minor", "3 - Moderate", "4 - Major", "5 - Catastrophic"],
        colorscale=custom_colorscale,
        showscale=False,
        hoverinfo="none",
        opacity=0.65
    ))

    # Inherent Risk Position Marker
    fig.add_trace(go.Scatter(
        x=[inherent_l_val - 1],
        y=[inherent_i_val - 1],
        mode="markers+text",
        name="Inherent Position",
        text=["Inherent Risk"],
        textposition="top center",
        marker=dict(color="#000000", size=18, symbol="diamond", line=dict(width=2, color="#ffffff"))
    ))

    # Residual Risk Position Marker
    fig.add_trace(go.Scatter(
        x=[residual_l - 1],
        y=[residual_i - 1],
        mode="markers+text",
        name="Residual Position",
        text=["Residual Risk"],
        textposition="bottom center",
        marker=dict(color="#004085", size=20, symbol="circle", line=dict(width=2, color="#ffffff"))
    ))

    # Connecting Vector Arrow (Trajectory of Control Effectiveness)
    fig.add_annotation(
        x=residual_l - 1,
        y=residual_i - 1,
        ax=inherent_l_val - 1,
        ay=inherent_i_val - 1,
        xref="x",
        yref="y",
        axref="x",
        ayref="y",
        text="",
        showarrow=True,
        arrowhead=3,
        arrowsize=1.5,
        arrowwidth=3,
        arrowcolor="#002b49"
    )

    fig.update_layout(
        xaxis_title="Likelihood (Frequency / Threat Feasibility)",
        yaxis_title="Impact (Business / Regulatory Severity)",
        margin=dict(l=40, r=40, t=30, b=40),
        height=450,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig, use_container_width=True)

with detail_col:
    st.subheader("Control Governance Breakdown")
    st.write(f"**Target Asset:** `{risk_title}`")
    st.write(f"**Data Classification Tier:** `{asset_category}`")

    if selected_controls:
        st.write("##### Enforced Safeguards:")
        for ctrl in selected_controls:
            reduction = int(CONTROL_CATALOG[ctrl] * 100)
            st.markdown(f"- **{ctrl}** (Mitigation Weight: `+{reduction}%`)")
    else:
        st.warning("No compensating controls selected. Inherent risk equals residual risk.")

    st.info(f"**Assessor Disposition:** {notes}")

st.markdown("---")

# ---------------------------------------------------------
# Enterprise Risk Register Table
# ---------------------------------------------------------
st.subheader("Institutional Risk Register")
if st.session_state.risk_register:
    df = pd.DataFrame(st.session_state.risk_register)
    st.dataframe(df, use_container_width=True)
    
    # CSV Export
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "Export Risk Register to CSV",
        data=csv,
        file_name="UCR_Risk_Register_Export.csv",
        mime="text/csv"
    )
else:
    st.caption("No risk assessments saved yet. Use the sidebar to configure and commit scenarios.")