# Incidents History

Retrieve an interactive, paginated list of past emergency incidents stored in the system.

***

**Endpoint:** `GET /api/incidents/`

**Query Parameters:**

| Parameter | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `type` | `string` | Filter by incident type (e.g., Fire, Traffic) | No |
| `severity` | `string` | Filter by severity level (e.g., High, Critical) | No |
| `page` | `integer` | Page number for pagination | No |

**Response (200 OK):**

```json
{
  "count": 125,
  "next": "http://localhost:8000/api/incidents/?page=2",
  "previous": null,
  "results": [
    {
      "id": "INC-1045",
      "incident_type": "Fire",
      "location": "123 Main St, Springfield",
      "lat": 40.123,
      "lng": -75.456,
      "time": "2024-03-15T14:30:00Z",
      "severity": "High",
      "confidence": "0.85",
      "status": "Active"
    }
  ]
}
```
