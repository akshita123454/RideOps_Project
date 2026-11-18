"""
ui_layout.py — Institutional / Banking Design System & Top Navigation.

Features:
  - Clean white background, slate borders, black and corporate blue typography
  - Complete suppression of default sidebar
  - Top navigation bar with page routing
  - 3-dot options menu popover (right-aligned) with system controls and module links
"""

import streamlit as st


ENTERPRISE_CSS = """
<style>
/* ── Institutional Enterprise / Banking Styling ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    color: #0F172A;
}

/* Hide default Streamlit sidebar completely */
[data-testid="stSidebar"], section[data-testid="stSidebar"], [data-testid="collapsedControl"] {
    display: none !important;
}

/* Adjust main container spacing */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
    padding-left: 2.5rem !important;
    padding-right: 2.5rem !important;
    max-width: 1350px !important;
}

/* Top App Header / Navigation container */
.top-nav-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 0 1.25rem 0;
    border-bottom: 1px solid #E2E8F0;
    margin-bottom: 1.5rem;
}

.brand-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #0F172A;
    letter-spacing: -0.02em;
    display: inline-flex;
    align-items: center;
    gap: 8px;
}

.brand-badge {
    background-color: #EFF6FF;
    color: #1D4ED8;
    border: 1px solid #BFDBFE;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

.brand-sub {
    font-size: 0.85rem;
    color: #64748B;
    margin-left: 12px;
    border-left: 1px solid #CBD5E1;
    padding-left: 12px;
}

/* Metric card styling */
div[data-testid="stMetric"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 4px !important;
    padding: 12px 16px !important;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03) !important;
}

div[data-testid="stMetricLabel"] p {
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    color: #475569 !important;
}

div[data-testid="stMetricValue"] div {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    color: #0F172A !important;
}

/* Institutional Status Badges */
.badge-normal {
    display: inline-block;
    padding: 4px 10px;
    font-size: 0.75rem;
    font-weight: 700;
    color: #047857;
    background-color: #ECFDF5;
    border: 1px solid #A7F3D0;
    border-radius: 4px;
    letter-spacing: 0.04em;
}

.badge-elevated {
    display: inline-block;
    padding: 4px 10px;
    font-size: 0.75rem;
    font-weight: 700;
    color: #B45309;
    background-color: #FFFBEB;
    border: 1px solid #FDE68A;
    border-radius: 4px;
    letter-spacing: 0.04em;
}

.badge-critical {
    display: inline-block;
    padding: 4px 10px;
    font-size: 0.75rem;
    font-weight: 700;
    color: #B91C1C;
    background-color: #FEF2F2;
    border: 1px solid #FECACA;
    border-radius: 4px;
    letter-spacing: 0.04em;
}

/* Institutional Card Box */
.institutional-card {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 4px;
    padding: 16px 20px;
    margin-bottom: 1rem;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.02);
}

.institutional-card-header {
    font-size: 0.85rem;
    font-weight: 600;
    color: #1E40AF;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 6px;
}

/* Headings */
h1 {
    color: #0F172A !important;
    font-size: 1.65rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
}

h2, h3 {
    color: #1E3A8A !important;
    font-weight: 600 !important;
    letter-spacing: -0.01em !important;
}

/* Cleaner Tables */
div[data-testid="stDataFrame"] {
    border: 1px solid #E2E8F0 !important;
    border-radius: 4px !important;
}

/* Buttons */
button[kind="primary"] {
    background-color: #1D4ED8 !important;
    border-color: #1D4ED8 !important;
    color: #FFFFFF !important;
    border-radius: 4px !important;
    font-weight: 500 !important;
}

button[kind="secondary"] {
    background-color: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    color: #1E293B !important;
    border-radius: 4px !important;
    font-weight: 500 !important;
}
</style>
"""


def render_enterprise_navbar(active_page="overview"):
    """
    Renders top corporate navigation bar and a 3-dot options menu.
    Suppresses the sidebar and sets the banking/enterprise UI theme.
    """
    st.markdown(ENTERPRISE_CSS, unsafe_allow_html=True)

    # Top Bar Header Layout
    nav_col1, nav_col2, nav_col3 = st.columns([4, 6, 1])

    with nav_col1:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 8px; padding-top: 4px;">
                <span style="font-weight: 800; font-size: 1.15rem; color: #0F172A; letter-spacing: -0.02em;">RideOps</span>
                <span style="font-weight: 500; font-size: 0.85rem; color: #64748B;">Operations Intelligence System</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with nav_col2:
        # Navigation page links in horizontal top bar
        c_p1, c_p2, c_p3, c_p4 = st.columns(4)
        with c_p1:
            st.page_link(
                "app.py",
                label="System Overview",
                use_container_width=True,
                disabled=(active_page == "overview"),
            )
        with c_p2:
            st.page_link(
                "pages/1_Agent_Cockpit.py",
                label="Agent Console",
                use_container_width=True,
                disabled=(active_page == "cockpit"),
            )
        with c_p3:
            st.page_link(
                "pages/2_Ops_Command.py",
                label="Operations Command",
                use_container_width=True,
                disabled=(active_page == "command"),
            )
        with c_p4:
            st.page_link(
                "pages/3_Bug_Radar.py",
                label="Defect Radar",
                use_container_width=True,
                disabled=(active_page == "radar"),
            )

    with nav_col3:
        # Three-dot options menu (Institutional style)
        with st.popover("⋮ Options", help="System Options & Navigation"):
            st.markdown(
                """
                <div style="font-weight: 700; font-size: 0.85rem; color: #0F172A; margin-bottom: 8px;">
                    MODULE DIRECTORY
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.page_link("app.py", label="Overview · Backlog Pressure Index")
            st.page_link("pages/1_Agent_Cockpit.py", label="Frontline Triage & Checklists")
            st.page_link("pages/2_Ops_Command.py", label="Throughput Flow & Simulator")
            st.page_link("pages/3_Bug_Radar.py", label="Systemic Defect Clustering")

            st.divider()
            st.markdown(
                """
                <div style="font-size: 0.72rem; color: #64748B; line-height: 1.4;">
                    <strong>Environment:</strong> Production (v2.4)<br>
                    <strong>Data Scope:</strong> 1,444 Corporate Records<br>
                    <strong>Timeframe:</strong> Jul 02 – Sep 30, 2026<br>
                    <strong>Clients:</strong> 200 Corporate Accounts
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Purge Cache & Reload", use_container_width=True):
                st.cache_data.clear()
                st.rerun()

    st.markdown("<div style='border-bottom: 1px solid #E2E8F0; margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)
