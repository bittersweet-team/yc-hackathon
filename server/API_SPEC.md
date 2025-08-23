# Demo Hunters API Specification

## Base URL
```
http://localhost:8000
```

## Authentication
All protected endpoints require Supabase JWT token in Authorization header:
```
Authorization: Bearer <supabase_access_token>
```

## Endpoints

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "Demo Hunters Backend",
  "version": "1.0.0",
  "task_queue": {
    "pending": 2,
    "processing": 1,
    "worker_running": true
  }
}
```

---

### Submit Demo Request
```http
POST /api/demo
Authorization: Bearer <token>
Content-Type: application/json
```

**Request:**
```json
{
  "product_url": "https://example.com",
  "description": "SaaS platform for team collaboration",
  "email": "user@example.com"  // optional, uses token email if not provided
}
```

**Response:**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "product_url": "https://example.com",
  "description": "SaaS platform for team collaboration",
  "status": "pending",
  "long_video_url": null,
  "short_video_urls": [],
  "error_message": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Status Values:**
- `pending` - Request received
- `recording` - Recording product demo
- `processing` - Processing video
- `generating` - Generating shorts
- `sending` - Sending email
- `completed` - Success
- `failed` - Error occurred

---

### List User's Demos
```http
GET /api/demos
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "product_url": "https://example.com",
    "description": "SaaS platform",
    "status": "completed",
    "long_video_url": "https://storage.url/video.mp4",
    "short_video_urls": [
      "https://storage.url/short1.mp4",
      "https://storage.url/short2.mp4"
    ],
    "error_message": null,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

---

### Get Demo Status
```http
GET /api/demo/{demo_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "product_url": "https://example.com",
  "description": "SaaS platform",
  "status": "processing",
  "long_video_url": "https://storage.url/video.mp4",
  "short_video_urls": [],
  "error_message": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

---

### Delete Demo
```http
DELETE /api/demo/{demo_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "message": "Demo deleted successfully"
}
```

---

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Invalid authentication token"
}
```

### 404 Not Found
```json
{
  "detail": "Demo not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Processing Workflow

1. **Submit** - User submits product URL
2. **Queue** - Task added to database queue
3. **Record** - Capture product demo video (45s)
4. **Store** - Save to Supabase Storage
5. **Generate** - Create shorts via Klap API
6. **Export** - Export top 3 shorts
7. **Deliver** - Send videos via AgentMail
8. **Complete** - Update status to completed

---

## Rate Limits
- No explicit rate limits
- Processing limited by external API quotas
- One active recording per user recommended

---

## Webhooks
Not implemented. Use polling on `/api/demo/{id}` for status updates.
