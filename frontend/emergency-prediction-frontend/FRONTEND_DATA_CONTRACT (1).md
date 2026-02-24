# Frontend Data Contract — Backend Implementation Guide

> **Purpose**: This document shows the **exact JSON structures** the frontend components expect. Backend developers should implement their API responses to match these contracts so frontend integration is smooth.
>
> **How to use**: For each endpoint below, match your API response to the **"Backend must return"** section. If the current response differs, the **"Current response"** section shows what you're returning now and the **"Transform needed"** section explains the gap.

---

## Endpoint 1: `GET /api/analytics/statistics/`

**Used by**: Dashboard StatCards, IncidentChart (Pie), SeverityChart (Bar)

### Backend must return

```json
{
  "total_incidents": 1245,
  "critical_count": 5,
  "by_type": [
    { "name": "EMS",     "value": 120, "color": "#dc2626" },
    { "name": "Fire",    "value": 80,  "color": "#ef4444" },
    { "name": "Traffic", "value": 45,  "color": "#f97316" }
  ],
  "by_severity": {
    "low": 50,
    "medium": 30,
    "high": 15,
    "critical": 5
  }
}
```

### How each frontend component uses this

**StatCards** (in `Dashboard.jsx`):
```js
// StatCard "Total Incidents"  →  response.total_incidents
// StatCard "Critical Alerts"  →  response.critical_count
// StatCard "Active Dispatches" →  hardcoded (no backend data — keep as demo)
// StatCard "Units Available"   →  hardcoded (no backend data — keep as demo)
```

**IncidentChart.jsx** (Donut/Pie chart):
```js
// Reads: response.by_type
// Expected array shape:
[
  { "name": "EMS",     "value": 120, "color": "#dc2626" },
  { "name": "Fire",    "value": 80,  "color": "#ef4444" },
  { "name": "Traffic", "value": 45,  "color": "#f97316" }
]
// Recharts PieChart uses: dataKey="value", fills from entry.color
// Center text shows sum of all values as "Total"
```

> ⚠️ **Important**: The frontend currently says "Medical" and "Rescue" — these **do not exist** in the 911 dataset. The correct types are **EMS**, **Fire**, **Traffic**. The frontend will be updated to match.

**SeverityChart.jsx** — see Endpoint 2 below (needs its own endpoint)

### Current backend response

```json
{
  "by_type":     { "EMS": 120, "Fire": 80, "Traffic": 45 },
  "by_severity": { "Low": 50, "Medium": 30, "High": 15, "Critical": 5 }
}
```

### Transform needed

| Field | Current | Needed | Change |
|---|---|---|---|
| `total_incidents` | Not returned | `1245` (integer) | Add: sum of all incident counts |
| `critical_count` | Not returned | `5` (integer) | Add: count of severity="Critical" |
| `by_type` | `{key: count}` dict | `[{name, value, color}]` array | Restructure + add color mapping |

**Color mapping for backend** (hardcode these):
```python
TYPE_COLORS = {
    "EMS":     "#dc2626",
    "Fire":    "#ef4444",
    "Traffic": "#f97316",
}
```

---

## Endpoint 2: `GET /api/analytics/severity-by-day/`

**Used by**: SeverityChart.jsx (Stacked Bar chart)  
**Status**: ❌ This endpoint does **not exist yet** — needs to be created

### Backend must return

```json
[
  { "day": "Mon", "low": 9,  "medium": 9,  "high": 12, "critical": 1 },
  { "day": "Tue", "low": 12, "medium": 18, "high": 3,  "critical": 5 },
  { "day": "Wed", "low": 16, "medium": 16, "high": 5,  "critical": 1 },
  { "day": "Thu", "low": 11, "medium": 10, "high": 6,  "critical": 3 },
  { "day": "Fri", "low": 6,  "medium": 8,  "high": 8,  "critical": 2 },
  { "day": "Sat", "low": 23, "medium": 8,  "high": 6,  "critical": 2 },
  { "day": "Sun", "low": 19, "medium": 15, "high": 11, "critical": 2 }
]
```

### How the frontend uses this

```js
// SeverityChart.jsx — Recharts BarChart
// XAxis:   dataKey="day"
// Bar 1:   dataKey="low"      name="Low"      fill="#22c55e"
// Bar 2:   dataKey="medium"   name="Medium"   fill="#f59e0b"
// Bar 3:   dataKey="high"     name="High"     fill="#f97316"
// Bar 4:   dataKey="critical" name="Critical" fill="#ef4444"
```

### Implementation hint

```python
# In analytics/views.py — new view
from django.db.models.functions import ExtractWeekDay
from collections import defaultdict

class SeverityByDayView(APIView):
    def get(self, request):
        DAY_NAMES = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        qs = Incident.objects.values('severity') \
            .annotate(dow=ExtractWeekDay('timestamp')) \
            .values('dow', 'severity') \
            .annotate(count=Count('id'))
        
        result = {d: {"day": d, "low": 0, "medium": 0, "high": 0, "critical": 0} 
                  for d in DAY_NAMES}
        for row in qs:
            day_name = DAY_NAMES[row['dow'] - 1]  # Django: 1=Sun, 7=Sat
            result[day_name][row['severity'].lower()] = row['count']
        
        # Return in Mon→Sun order
        ordered = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
        return Response([result[d] for d in ordered])
```

---

## Endpoint 3: `GET /api/analytics/hourly/`

**Used by**: TrafficChart.jsx (24h Area chart)  
**Status**: ❌ This endpoint does **not exist yet** — needs to be created

### Backend must return

```json
[
  { "time": "00:00", "calls": 45 },
  { "time": "01:00", "calls": 12 },
  { "time": "02:00", "calls": 48 },
  ...
  { "time": "23:00", "calls": 35 }
]
```

24 objects, one per hour (00:00 through 23:00).

### How the frontend uses this

```js
// TrafficChart.jsx — Recharts AreaChart
// XAxis:  dataKey="time"     (string "HH:00")
// Area:   dataKey="calls"    (integer count)
// Shows every 3rd label on x-axis (interval={2})
```

### Implementation hint

```python
# In analytics/views.py — new view
from django.db.models.functions import ExtractHour

class HourlyCallsView(APIView):
    def get(self, request):
        qs = Incident.objects.annotate(hour=ExtractHour('timestamp')) \
            .values('hour') \
            .annotate(calls=Count('id')) \
            .order_by('hour')
        
        # Ensure all 24 hours present
        hour_map = {row['hour']: row['calls'] for row in qs}
        result = [
            {"time": f"{h:02d}:00", "calls": hour_map.get(h, 0)}
            for h in range(24)
        ]
        return Response(result)
```

---

## Endpoint 4: `GET /api/incidents/`

**Used by**: RecentIncidents.jsx (Dashboard table), History.jsx (full page table)

### Backend must return (per incident)

```json
{
  "results": [
    {
      "id": 1001,
      "type": "Fire",
      "location": "Main St & 5th Ave",
      "timestamp": "2026-02-12T08:23:00Z",
      "severity": "Critical",
      "confidence": "94%",
      "status": "Dispatched"
    }
  ],
  "count": 145518,
  "next": "http://localhost:8000/api/incidents/?page=2",
  "previous": null
}
```

### How each frontend component uses this

**RecentIncidents.jsx** (Dashboard — last 5 incidents):

```js
// Table columns:
//   ID         →  "INC-" + response.id     (frontend adds prefix)
//   Type       →  response.type            ("EMS" | "Fire" | "Traffic")
//   Location   →  response.location        (human-readable string)
//   Severity   →  response.severity        ("Critical" | "High" | "Medium" | "Low")
//   Confidence →  response.confidence      ("94%" format string)
//   Status     →  response.status          ("Dispatched" | "Active" | "Resolved" | "Closed")
```

**History.jsx** (Full table with search, filters, pagination):

```js
// Same fields but:
//   incident_type  →  response.type          (frontend key is "incident_type")
//   time           →  response.timestamp     (frontend formats to locale string)
//   severity       →  response.severity      (UPPERCASE in display: "CRITICAL")
// 
// Filters:  search by text, filter by severity dropdown
// Pagination: configurable rows per page (10, 25, 50, 100, All)
```

### Current backend response

```json
{
  "results": [
    {
      "id": 1,
      "type": "Fire",
      "severity": "High",
      "latitude": 40.1,
      "longitude": -75.3,
      "timestamp": "2016-01-01T14:00:00Z",
      "description": "...",
      "created_at": "2026-02-23T..."
    }
  ]
}
```

### Fields missing from backend Incident model

| Frontend needs | Backend has | Action needed |
|---|---|---|
| `location` (string) | `latitude` + `longitude` (floats) | **Option A**: Add `location` field to model and populate from `addr`/`twp` during data load. **Option B**: Return `twp` (township name) as location. **Option C**: Frontend formats as "40.1, -75.3" |
| `confidence` (string %) | ❌ Not in model | Add `confidence` field (CharField) OR omit from listing (it's really only relevant for predictions) |
| `status` | ❌ Not in model | Add `status` field with choices: `Dispatched`, `Active`, `Resolved`, `Closed` — default to "Resolved" for historical data |

> **Recommendation**: Add `location` (populated from `twp` column during data load) and `status` (default "Resolved" for loaded data). Skip `confidence` for historical incidents — it only makes sense for new predictions.

---

## Endpoint 5: `POST /api/predictions/predict/`

**Used by**: Newincident.jsx (Prediction form)

### Frontend will send

```json
{
  "type": "Fire",
  "hour": 14,
  "lat": 40.1,
  "lng": -75.3,
  "month": 2,
  "day_of_week": 0
}
```

| Field | Type | Values | Source |
|---|---|---|---|
| `type` | string | `"EMS"`, `"Fire"`, `"Traffic"` | User selects from dropdown |
| `hour` | int | 0–23 | Extracted from current time |
| `lat` | float | ~40.0–40.3 (Montgomery County) | From location picker / geocoding |
| `lng` | float | ~-75.0–-75.6 (Montgomery County) | From location picker / geocoding |
| `month` | int | 1–12 | Extracted from current date |
| `day_of_week` | int | 0–6 (Mon=0, Sun=6) | Extracted from current date |

### Backend must return

```json
{
  "severity": "High",
  "confidence": 0.85,
  "recommended_response": "Dispatch 2 Units — Priority"
}
```

| Field | Type | Values |
|---|---|---|
| `severity` | string | `"Critical"`, `"High"`, `"Medium"`, `"Low"` (Titlecase) |
| `confidence` | float | 0.0–1.0 (NOT null, NOT a string like "85%") |
| `recommended_response` | string | Human-readable dispatch recommendation |

### How the frontend displays the result

```js
// Result panel shows:
//   Severity badge:  colored pill (red=Critical, orange=High, green=otherwise)
//                    Text: response.severity.toUpperCase()
//
//   AI Confidence:   Large number display
//                    Text: Math.round(response.confidence * 100) + "%"
//
//   Recommended Response:  Text block
//                          Text: response.recommended_response
//
//   Action buttons:  "Confirm & Dispatch" + "Ignore"
```

### Current backend response

```json
{
  "severity": "Critical",
  "confidence": null
}
```

### Gaps to fix

| Field | Current | Needed | Fix |
|---|---|---|---|
| `confidence` | `null` (always) | `0.85` (float) | Use `predict_proba()` if classifier, or pseudo-confidence if regressor |
| `recommended_response` | Not returned | `"Dispatch 3+ Units"` | Add mapping in `ml_service.py` + update serializer |

**Recommended response mapping** (add to backend):
```python
RESPONSE_MAP = {
    "Critical": "Dispatch 3+ Units — Immediate Response",
    "High":     "Dispatch 2 Units — Priority Response",
    "Medium":   "Dispatch 1 Unit — Standard Response",
    "Low":      "Monitor — No Dispatch Needed"
}
```

---

## Summary: All Endpoints at a Glance

| # | Endpoint | Method | Status | Used By |
|---|---|---|---|---|
| 1 | `/api/analytics/statistics/` | GET | ⚠️ Exists — needs restructure | StatCards, IncidentChart |
| 2 | `/api/analytics/severity-by-day/` | GET | ❌ Needs creation | SeverityChart |
| 3 | `/api/analytics/hourly/` | GET | ❌ Needs creation | TrafficChart |
| 4 | `/api/incidents/` | GET | ⚠️ Exists — missing fields | RecentIncidents, History |
| 5 | `/api/predictions/predict/` | POST | ⚠️ Exists — response incomplete | Newincident |

### Type Values (use everywhere consistently)

```
"EMS"      — Emergency Medical Services
"Fire"     — Fire incidents
"Traffic"  — Traffic accidents
```

> ❌ NOT "Medical", NOT "Rescue" — these do not exist in the 911 dataset

### Severity Values (use everywhere consistently)

```
"Critical"  — Most urgent (red)
"High"      — Urgent (orange)
"Medium"    — Standard (amber/yellow)
"Low"       — Non-urgent (green)
```

> Always Titlecase when returning from backend. Frontend handles case conversion for display.
