# Demo Hunters - Backend

**AI-powered demo video generation service**

## What it does
Processes product URLs � Generates demo videos � Manages delivery pipeline

## Quick Start
```bash
pip install -r requirements.txt
python main.py
```

## API Endpoints
```
POST /api/demo     - Submit new demo request (requires auth)
GET  /api/demos    - List all demos (requires auth)
GET  /api/demo/:id - Get demo status (requires auth)
DELETE /api/demo/:id - Delete demo (requires auth)
GET  /health       - Health check endpoint
```

## Features
- Screen recording of product websites
- Automatic short-form video generation
- Email delivery with AgentMail
- Full async processing pipeline
- Video storage in Supabase

## Tech Stack
- Python/FastAPI
- Recording API (custom)
- Klap API (short-form video generation)
- AgentMail (email delivery)
- Supabase (Auth, Database, Storage, Task Queue)

## Environment Variables
```
PORT=8000
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_service_key
SUPABASE_JWT_SECRET=your_jwt_secret
RECORDING_API_URL=your_recording_api
KLAP_API_KEY=your_klap_key
AGENTMAIL_API_KEY=your_agentmail_key
```

## Project Structure
```
/api        - API route handlers
/models     - Database & AI models
/services   - Video generation logic
/utils      - Helper functions
/workers    - Background job processors
```

## Async Processing Flow
1. User submits product URL + description (with email auth)
2. Call recording API to capture product demo video
3. Store long-form video in Supabase Storage
4. Call Klap API to generate short-form videos
5. Store short-form videos in Supabase Storage
6. Call AgentMail to send videos to user's email
7. Update demo status in database

## Authentication
- Handled by Supabase on frontend
- JWT token verification for API access
- User email extracted from token for video delivery
