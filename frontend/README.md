# Istikshaf — Frontend Desktop Web Application

Istikshaf is an AI-assisted electricity grid-loss detection and inspection-prioritization desktop web application for Pakistan's electricity distribution companies (DISCOs).

The frontend is built using React 18, Vite, TypeScript, Tailwind CSS, TanStack Query, Apache ECharts, Lucide React, and React Three Fiber.

---

## 🚀 Quick Start

### 1. Installation
```bash
cd frontend
npm install --legacy-peer-deps
```

### 2. Development Server
Start the local Vite dev server at `http://localhost:5173`:
```bash
npm run dev
```

### 3. Run Tests
Execute the Vitest test suite:
```bash
npm run test
```

### 4. Build Production Bundle
Type-check and compile the production bundle:
```bash
npm run build
```

---

## ⚙️ Environment Variables & Backend Integration

Set environment variables in `.env`:

```env
# Fast-API Backend Base URL
VITE_API_BASE_URL=http://localhost:8000/api

# Standalone Mock Mode (true = deterministic rich mocks, false = live FastAPI client)
VITE_USE_MOCK_API=true
```

### Fast-API Integration Notes
When `VITE_USE_MOCK_API=false`, the frontend connects to the Python FastAPI backend running at `http://localhost:8000`. Ensure that FastAPI configures CORS to permit requests from `http://localhost:5173`.

---

## 🗺️ Application Route Map

### Public Routes
- `/` — Landing Page (Hero 3D Grid Canvas, Capabilities, Responsible AI Framework)
- `/workspaces` — Prototype Role Selection

### Operator / Analyst Workspace
- `/analyst` — Grid Loss Operations Overview
- `/analyst/grid` — Grid Topology Explorer (Feeders → PMTs → Consumers)
- `/analyst/investigations` — Inspection Prioritization Queue
- `/analyst/investigations/:consumerId` — Consumer Anomaly & TreeSHAP Evidence (e.g., `C-08124`)
- `/analyst/comparison` — Monthly Billing vs Hourly Smart-Meter Pipeline Comparison
- `/analyst/job-cards` — Operational Job-Cards List
- `/analyst/job-cards/:jobCardId` — Printable Job-Card Detail (A4 Print Mode)

### Field Inspector / Supervisor Workspace
- `/field` — Field Overview & Workload Summary
- `/field/jobs/:jobCardId` — Site Checklist & Inspection Findings Form Submission

### Admin Workspace
- `/admin` — System Telemetry, PAI-EAS Endpoint Status, Data Sources, User Access, Audit Log

---

## 🔒 Responsible AI & Terminology Compliance

Istikshaf is strictly an **inspection support system**. All scores and findings are presented with non-punitive terminology:
- Calibrated anomaly risk (e.g. "91% calibrated anomaly risk")
- Unaccounted residual
- Recommended for review
- Evidence strength & field verification required

Never uses accusatory language ("theft", "guilty", "criminal", "chance of theft").
