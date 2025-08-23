# Demo Hunters Backend - Setup Guide

## Prerequisites
- Python 3.9+
- Supabase account
- Klap API key
- AgentMail API key
- Recording API service

## Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your credentials:
```bash
cp .env.example .env
```

Edit `.env` with your actual values:
```env
PORT=8000
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_service_role_key
SUPABASE_JWT_SECRET=your_jwt_secret
RECORDING_API_URL=https://your-recording-api.com
KLAP_API_KEY=your_klap_api_key
AGENTMAIL_API_KEY=your_agentmail_api_key
```

### 3. Setup Supabase Database

Run the SQL schema in your Supabase SQL editor:
```sql
-- Copy contents of supabase_schema.sql
```

This creates:
- `demos` table for storing demo requests
- `task_queue` table for background job processing
- Storage bucket for videos
- RLS policies for security
- Helper functions and triggers

### 4. Start the Server
```bash
python main.py
# or
./start.sh
```

The server will start on http://localhost:8000 with:
- API documentation at http://localhost:8000/docs
- Health check at http://localhost:8000/health
- Integrated task worker for background processing

## API Endpoints

### Demos (All require Bearer token authentication)
- `POST /api/demo` - Submit new demo request
- `GET /api/demos` - List user's demos
- `GET /api/demo/{id}` - Get demo status
- `DELETE /api/demo/{id}` - Delete demo

### Public Endpoints
- `GET /health` - Health check and system status
- `GET /` - API info
- `GET /docs` - Swagger API documentation

### Authentication
Authentication is handled by Supabase on the frontend. The backend only verifies JWT tokens sent in the Authorization header:
```
Authorization: Bearer <supabase_access_token>
```

## Processing Flow

1. User submits product URL via API
2. Request is saved to database with `pending` status
3. Task is added to `task_queue` table
4. Background worker picks up task
5. Recording API captures product demo video
6. Video is stored in Supabase Storage
7. Klap API generates short-form videos
8. AgentMail sends videos to user's email
9. Demo status updated to `completed`

## Monitoring

Check the health endpoint for system status:
```bash
curl http://localhost:8000/health
```

Response includes:
- Service status
- Task queue metrics
- Worker status

## Troubleshooting

### Task Worker Issues
- Check logs for worker errors
- Verify database connection
- Check `task_queue` table for stuck tasks

### Video Generation Issues
- Verify API keys are correct
- Check external service status
- Review error_message in demos table

### Email Delivery Issues
- Verify AgentMail API key
- Check user email address
- Review AgentMail logs

## Development

### Run with auto-reload
```bash
uvicorn main:app --reload --port 8000
```

### Check task queue
```sql
SELECT * FROM task_queue ORDER BY created_at DESC;
```

### Check demo status
```sql
SELECT * FROM demos ORDER BY created_at DESC;
```