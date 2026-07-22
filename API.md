# Quantoryx — REST API Documentation Reference

The **Quantoryx REST API** provides programmatic access to the underlying quantitative research, simulation, and analysis engine. This API is self-contained and operates entirely on local datasets.

## Interactive Documentation Interfaces
Once the server is running, the interactive documentation interfaces can be accessed at the following local endpoints:
* **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **ReDoc UI:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## Endpoint Index

### System Diagnostics
* [`GET /api/health`](#get-apihealth) — Retrieve service operational uptime and timestamp parameters.
* [`GET /api/version`](#get-apiversion) — Retrieve framework metadata version indicators.
* [`GET /api/status`](#get-apistatus) — Retrieve system constants and active environment statuses.

### Simulation & Analysis
* [`POST /api/backtest`](#post-apibacktest) — Simulate a single-strategy backtest run.
* [`POST /api/optimize`](#post-apioptimize) — Run parameter optimization sweeps on price histories.
* [`POST /api/walk-forward`](#post-apiwalk-forward) — Run rolling walk-forward validation slices.
* [`POST /api/paper-trading`](#post-apipaper-trading) — Run step-by-step account leverage/spread simulators.
* [`POST /api/ai-analysis`](#post-apiai-analysis) — Nominate a champion model using cognitive selections.

### Analytics & Reports
* [`GET /api/dashboard`](#get-apidashboard) — Retrieve aggregated session overview metrics.
* [`GET /api/portfolio`](#get-apiportfolio) — Retrieve cash history and drawdown equity curves.
* [`GET /api/reports`](#get-apireports) — Index output files and document locations.
* [`GET /api/strategies`](#get-apistrategies) — Inspect registered strategy parameter profiles.
* [`GET /api/market-regime`](#get-apimarket-regime) — Inspect historical market regime distribution densities.
* [`GET /api/system-health`](#get-apisystem-health) — Run comprehensive code, validation, and directory health audits.

---

## System Diagnostics

### GET `/api/health`
Checks the active server health and uptime metrics.

* **Response (200 OK):**
  ```json
  {
    "status": "OK",
    "timestamp": "2026-07-22T12:00:00Z",
    "uptime_seconds": 124.55
  }
