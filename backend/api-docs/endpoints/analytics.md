# Analytics

Fetch aggregated metrics and statistical data used to power the frontend administrator dashboards.

***

**Endpoint:** `GET /api/analytics/statistics/`

**Response (200 OK):**

Returns aggregated counts grouped by incident type and derived severity score.

```json
{
  "by_type": {
    "Fire": 45,
    "EMS": 120,
    "Traffic": 85
  },
  "by_severity": {
    "Critical": 12,
    "High": 58,
    "Medium": 130,
    "Low": 50
  }
}
```
