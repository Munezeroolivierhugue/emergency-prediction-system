# Predictions

Get an AI-generated severity level and confidence score based on incident parameters.

***

**Endpoint:** `POST /api/predictions/predict/`

**Headers:**
```http
Content-Type: application/json
```
*(Authentication is not required for this endpoint)*

**Request Body:**

| Field | Type | Description | Required | Example |
| :--- | :--- | :--- | :--- | :--- |
| `type` | `string` | Emergency category (Fire, Traffic, EMS) | Yes | "Fire" |
| `hour` | `integer` | Hour of the day (0-23) | Yes | 14 |
| `lat` | `float` | Latitude of the incident | Yes | 40.1 |
| `lng` | `float` | Longitude of the incident | Yes | -75.3 |
| `month` | `integer` | Month of the year (1-12) | No | 1 |
| `day_of_week` | `integer` | Day of the week (0-6) | No | 0 |

**Example Request:**

```json
{
  "type": "Fire",
  "hour": 14,
  "lat": 40.1,
  "lng": -75.3,
  "month": 1,
  "day_of_week": 0
}
```

**Response (200 OK):**

Returns the predicted severity class, confidence percentage, and a recommended response action.

```json
{
  "severity": "Medium",
  "confidence": 0.42,
  "recommended_response": "Dispatch 1 Unit — Standard Response"
}
```

**Response (400 Bad Request):**

Returned if required fields are missing or invalid.

```json
{
  "hour": [
    "Ensure this value is less than or equal to 23."
  ]
}
```
