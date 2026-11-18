"""
data_loader.py — Load, parse, and enrich the RideOps ticket dataset.

Adds derived columns that every other module depends on:
  resolution_hrs, frt_minutes, is_escalated, is_reopened,
  is_open, is_wasteful_esc, created_week, created_month
"""

import pandas as pd
import streamlit as st
from pathlib import Path

WASTEFUL_OUTCOMES = [
    "Config issue - returned to L1",
    "Not a bug - how-to",
    "Insufficient info - returned to L1",
    "Duplicate of known issue",
    "Not reproducible",
]

# Category-specific checklists an agent should complete BEFORE escalating
ESCALATION_CHECKLISTS = {
    "Roster / booking not syncing": [
        "Confirm the booking cutoff time configured in admin panel",
        "Check if this is a known sync propagation delay (allow up to 15 min)",
        "Verify the employee's app version is current",
        "Compare the roster screen vs the booking screen — attach screenshot",
        "Search open tickets for the same client + roster issue in the last 7 days",
    ],
    "Live tracking / GPS incorrect": [
        "Ask the driver to toggle GPS off and on in device settings",
        "Confirm the driver app version and phone model",
        "Check if the tracking link uses HTTPS (older links break on some browsers)",
        "Verify that the trip is in 'active' status (not pre-assigned or completed)",
        "Look for a network / GPS config flag in the client's admin panel",
    ],
    "Report export failing": [
        "Try the export again in an incognito/private browser tab",
        "Check if the date range is within the allowed limit (90 days)",
        "Verify the user has the 'Reports' permission in their role",
        "Confirm whether this is a known issue in the current release notes",
        "If Excel export, try CSV format as a workaround and note it in the ticket",
    ],
    "OTP / boarding issue": [
        "Confirm the employee's phone number on file matches what they're using",
        "Check if the OTP was sent (verify SMS delivery log if accessible)",
        "Ask if the employee boarded a different vehicle than assigned",
        "Verify the trip assignment hasn't been changed in the last 30 min",
        "Check if the OTP timer expired (default window is 10 min)",
    ],
    "Billing / invoice discrepancy": [
        "Compare the trip count in the invoice vs the roster for that period",
        "Check for cancelled trips that may still appear in billing",
        "Verify the billing cycle dates match the client's contract",
        "Look at the client's rate card configuration in admin",
        "Check if there's a known billing batch delay for this month",
    ],
    "Login / access issue": [
        "Confirm the user's email domain matches the SSO/client configuration",
        "Check if the account is active or was deactivated",
        "For 'access to module' requests — verify role permissions in admin panel",
        "Try resetting the user's password from the admin side",
        "Check if multi-factor authentication is blocking the login",
    ],
    "Cab delay / no-show complaint": [
        "Pull the trip timeline — was the cab assigned? Did the driver accept?",
        "Check the driver's last GPS ping time to verify arrival",
        "Confirm the pickup location coordinates match the employee's address",
        "Check if there was a driver reassignment that wasn't communicated",
        "Note whether this is a repeat complaint for this route/driver",
    ],
    "Employee address / geocode change": [
        "Verify the new address was saved successfully in the employee profile",
        "Check if the geocode (lat/long) was recomputed after the address update",
        "Confirm the routing engine has picked up the new geocode",
        "Check if there's a cache refresh delay (can take up to 24 hrs for some clients)",
        "Verify this doesn't require a zone reassignment",
    ],
    "How-to / feature request": [
        "Search the knowledge base / help docs for a matching article",
        "If it's a feature request, log it and tag it — do NOT escalate to engineering",
        "If it's a how-to question, walk the client through the steps live",
        "Check if a similar request was already answered for another client",
        "Confirm whether this feature exists but is hidden behind a config toggle",
    ],
    "Driver / vehicle compliance docs": [
        "Check if the document upload portal is working (try a test upload)",
        "Verify the document type required matches what the driver submitted",
        "Confirm the expiry date logic — some documents auto-expire",
        "Check if there's a manual verification queue with a backlog",
        "Look for a known issue with the OCR/document parsing service",
    ],
}


@st.cache_data
def load_tickets():
    """Load the support tickets CSV and add derived columns."""

    base = Path(__file__).resolve().parent.parent
    candidates = [
        base / "data" / "rideops_support_tickets.csv",
        base.parent / "rideops_support_tickets.csv",
    ]

    df = None
    for p in candidates:
        if p.exists():
            df = pd.read_csv(p)
            break

    if df is None:
        st.error("Cannot find rideops_support_tickets.csv — place it in nerve_center/data/")
        st.stop()

    # --- datetime parsing ---
    for col in ["created_at", "first_response_at", "first_closed_at", "final_closed_at"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    # --- derived time metrics ---
    mask_closed = df["final_closed_at"].notna()
    df["resolution_hrs"] = None
    df.loc[mask_closed, "resolution_hrs"] = (
        (df.loc[mask_closed, "final_closed_at"] - df.loc[mask_closed, "created_at"])
        .dt.total_seconds() / 3600
    )
    df["resolution_hrs"] = pd.to_numeric(df["resolution_hrs"], errors="coerce")

    mask_resp = df["first_response_at"].notna()
    df["frt_minutes"] = None
    df.loc[mask_resp, "frt_minutes"] = (
        (df.loc[mask_resp, "first_response_at"] - df.loc[mask_resp, "created_at"])
        .dt.total_seconds() / 60
    )
    df["frt_minutes"] = pd.to_numeric(df["frt_minutes"], errors="coerce")

    # --- boolean flags ---
    df["is_escalated"] = df["escalated_to_eng"] == "Yes"
    df["is_reopened"] = df["reopen_count"] > 0
    df["is_open"] = df["status"] != "Closed"
    df["is_wasteful_esc"] = df["is_escalated"] & df["eng_outcome"].isin(WASTEFUL_OUTCOMES)

    # --- period columns ---
    df["created_week"] = df["created_at"].dt.to_period("W").apply(lambda r: r.start_time)
    df["created_month"] = df["created_at"].dt.to_period("M").astype(str)

    return df
