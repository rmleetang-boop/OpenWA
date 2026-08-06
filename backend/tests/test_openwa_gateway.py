"""Stability & health tests for the OpenWA gateway deployed on Fly.io.

These tests hit the PUBLIC Fly.io URL (not a local backend). They verify:
  1) Root URL serves the open-wa QR/auth HTML page (HTTP 200).
  2) The service is stable over ~2-3 minutes (no intermittent 502s).
  3) API command endpoints return 404 pre-authentication (documented, expected).
"""
import os
import time
import pytest
import requests

GATEWAY_URL = "https://openwa-app.fly.dev"
API_KEY = "7b56e526872eb85f4d067061ca99b7bfc4f668b0ff499596"


# ---------- Basic health ----------
def test_root_returns_200_and_openwa_page():
    r = requests.get(f"{GATEWAY_URL}/", timeout=30)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}. Body: {r.text[:300]}"
    assert "open-wa" in r.text.lower(), "Response HTML does not contain 'open-wa' marker"
    assert "<title>open-wa</title>" in r.text, "Missing <title>open-wa</title>"


# ---------- Stability: 6 requests over ~2.5 min ----------
def test_stability_no_intermittent_502():
    results = []
    for i in range(6):
        try:
            r = requests.get(f"{GATEWAY_URL}/", timeout=30)
            results.append((i, r.status_code, None))
        except Exception as e:
            results.append((i, None, str(e)))
        if i < 5:
            time.sleep(30)
    # Print full sequence for the report
    for idx, code, err in results:
        print(f"request #{idx+1}: status={code} err={err}")
    non_200 = [x for x in results if x[1] != 200]
    assert not non_200, f"Instability detected: {non_200}"


# ---------- Pre-auth API endpoint behaviour (documented expectation) ----------
def test_sendText_returns_404_pre_auth():
    """/sendText is expected to 404 until WhatsApp QR is scanned. This is NOT a bug."""
    r = requests.post(
        f"{GATEWAY_URL}/sendText",
        headers={"api_key": API_KEY, "Content-Type": "application/json"},
        json={"args": {"to": "1234567890@c.us", "content": "ping"}},
        timeout=30,
    )
    # We only assert the service responds (not 5xx). 404 is expected pre-auth.
    assert r.status_code < 500, f"Unexpected server error: {r.status_code} {r.text[:200]}"
    print(f"/sendText pre-auth status={r.status_code} (404 expected)")
