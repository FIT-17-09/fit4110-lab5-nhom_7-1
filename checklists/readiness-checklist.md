# Lab 05 Docker Compose Readiness Checklist

**Completion Date:** 2026-06-17  
**Status:** ✅ COMPLETE - All 6 requirements verified

---

## 1. ✅ Database Service Ready

**Requirement:** PostgreSQL service must be running and accepting connections

**Evidence:**
```
localhost:5432 - accepting connections
```

**Details:**
- Service: `fit4110-db-lab05` | Port: 5432 | User: fit4110
- Health Check: `pg_isready -U fit4110 -h localhost` ✅ PASSED
- Container State: Healthy (verified 2026-06-17 09:17)

---

## 2. ✅ AI Service Health Endpoint Responsive

**Requirement:** AI service must expose `/health` endpoint and respond with OK status

**Evidence:**
```json
{
  "status": "ok",
  "service": "ai-service",
  "version": "0.5.0"
}
```

**Details:**
- Service: `fit4110-ai-lab05` | Port: 9000
- Endpoint: `GET /health` → 200 OK
- Status Field: "ok" ✅ PASSED
- Container State: Healthy (verified 2026-06-17 09:17)

---

## 3. ✅ API Service Can Connect to DB and AI Service

**Requirement:** API service must successfully execute requests to both DB and AI service

**Evidence (Newman Test Results):**
```
✓ 2 requests executed
✓ 0 failures
✓ Duration: 181ms
✓ Average response time: 18ms
```

**Test Endpoints:**
- Health: `GET /health` → 200 OK (27ms)
- Create Reading: `POST /readings` → 201 Created (9ms)

**Details:**
- API Service: `fit4110-api-lab05` (port 8000)
- Test Command: `npm run test:compose`
- Reports Generated:
  - `reports/newman-lab05-compose.xml` (JUnit)
  - `reports/newman-lab05-compose.html` (Interactive)

---

## 4. ✅ Environment Variables Configured Correctly

**Requirement:** All services must read required environment variables from `.env`

**Evidence:**
- ✅ `.env` file created from `.env.example`
- ✅ Variables configured: APP_HOST, APP_PORT, POSTGRES_* (all required), AI_SERVICE_URL, SERVICE_VERSION
- ✅ No secrets committed to git (`.env` in `.gitignore`)
- ✅ All 3 services started successfully with `.env`

**Details:**
- Config Template: `.env.example`
- Config Runtime: `.env` (local, not tracked)
- Service Status: All 3 services healthy after `.env` load

---

## 5. ✅ Docker Network (team-internal) Working

**Requirement:** Services must communicate on internal Docker network

**Evidence:**
```
✓ Network fit4110-lab5-nhom_7-1_team-internal  Created
✓ Container fit4110-ai-lab05                   Healthy
✓ Container fit4110-db-lab05                   Healthy
✓ Container fit4110-api-lab05                  Started
```

**Details:**
- Network: `team-internal` (internal only)
- DNS Resolution: ✅ Services reachable by hostname
- Service-to-Service: ✅ All 3 connected and communicating
- Full Logs: `reports/compose-logs.txt`

---

## 6. ✅ Version/Tag Correct (v0.1.0-team-iot)

**Requirement:** API service must report version v0.1.0-team-iot

**Evidence (API Health Response):**
```json
{
  "status": "ok",
  "service": "iot-ingestion",
  "version": "v0.1.0-team-iot"
}
```

**Details:**
- Image Tag: `fit4110/api:v0.1.0-team-iot` ✅ CORRECT
- Docker Build: `naming to docker.io/fit4110/api:v0.1.0-team-iot`
- Health Report: `version: v0.1.0-team-iot` ✅ VERIFIED

---

## Summary

| Item | Status | Evidence |
|------|--------|----------|
| Database Ready | ✅ | pg_isready response |
| AI Health | ✅ | /health endpoint 200 OK |
| API↔DB/AI Connection | ✅ | 2/2 Newman tests passed |
| Environment Variables | ✅ | .env configured, all services started |
| Network Configuration | ✅ | team-internal network active |
| Version Tag | ✅ | v0.1.0-team-iot reported |

**Overall Status:** 🟢 **READY FOR SUBMISSION**

All 6 Lab 05 Docker Compose readiness requirements have been verified.

---

## Test Artifacts

- `reports/compose-logs.txt` — Full Docker Compose logs
- `reports/newman-lab05-compose.xml` — Newman JUnit report
- `reports/newman-lab05-compose.html` — Newman HTML report
- `checklists/readiness-checklist.md` — This file
