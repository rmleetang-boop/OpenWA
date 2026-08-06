# PRD — OpenWA Gateway Deployment on Fly.io

## Problem Statement
Deploy the official OpenWA Gateway (Docker method) to the user's Fly.io app, with persistent storage for /app/data and port 2785 exposed. Do not modify OpenWA core.

## User Choices
- Image: official `openwa/wa-automate:latest`
- Region: jnb (Johannesburg)
- API key: generated and stored as Fly secret `WA_KEY`
- Volume: 1 GB

## What Was Done (Jun 2026)
- Actual Fly app name is `openwa-app` (user wrote "opnwa-app"; token org only contains `openwa-app`)
- Created `/app/openwa-deploy/fly.toml` (image deploy, mounts `openwa_data` -> /app/data, internal_port 2785, 1GB RAM shared-cpu-1x, min 1 machine running)
- Created 1GB volume `openwa_data` in jnb (vol_vz8d9p03x98xe99v)
- Set secret WA_KEY (API key, also saved in /app/openwa-deploy/.apikey)
- Env: WA_PORT=2785, WA_HOST=0.0.0.0 (required for fly-proxy), WA_IN_DOCKER=true, WA_SESSION_DATA_PATH=/app/data, WA_POPUP=false
- Deployed machine 8576e6da1e4018; verified https://openwa-app.fly.dev/ returns the open-wa QR auth page (200)

## Notes
- WhatsApp session must be authenticated by scanning the QR at https://openwa-app.fly.dev/
- API command endpoints (/sendText etc.) only mount after QR scan — 404 before that is expected
- Fly token stored at /app/openwa-deploy/.flytoken (flyctl in /root/.fly/bin)

## Bug Fix (Jun 2026)
- 502 reported: machine crash-looped (exit_code=1) — Chrome + WhatsApp Web too heavy for 1GB RAM
- Fix: VM memory bumped to 2GB (`flyctl machine update --vm-memory 2048`); fly.toml updated to memory="2gb"
- Verified: root URL returns 200 consistently (testing agent + 3 stability probes over 60s)
- Regression test left at /app/backend/tests/test_openwa_gateway.py (user paused further testing-agent runs until they confirm)

## Backlog
- P1: Webhook configuration (WA_WEBHOOK) if user wants inbound message forwarding
- P2: Dedicated IPv4, custom domain
