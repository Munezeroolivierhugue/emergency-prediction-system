# Emergency Severity Prediction API

Welcome to the official developer documentation for the Emergency Severity Prediction API. This API provides machine-learning-powered severity estimations for emergency incidents, historical data retrieval, and analytics.

### Base URL

All endpoints are hosted at:

```
http://localhost:8000/api/
```

### Core Features

*   **Authentication**: JWT-based secure access.
*   **Predictions**: Real-time severity estimation using a trained Random Forest model.
*   **Historical Data**: Query past emergency incidents.
*   **Analytics**: View aggregated statistics for dashboards.

### Data Format

All requests and responses use **JSON**. Please ensure the `Content-Type: application/json` header is included in your requests where applicable.
