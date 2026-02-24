# Authentication

Secure your API requests using JSON Web Tokens (JWT). Most endpoints require an `Authorization: Bearer <token>` header.

***

### Obtain Token

Get access and refresh tokens using your credentials.

**Endpoint:** `POST /api/auth/token/`

**Request Body:**

```json
{
  "username": "your_username",
  "password": "your_password"
}
```

**Response (200 OK):**

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbG...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbG..."
}
```

***

### Refresh Token

Obtain a new access token when the current one expires.

**Endpoint:** `POST /api/auth/token/refresh/`

**Request Body:**

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbG..."
}
```

**Response (200 OK):**

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbG..."
}
```
