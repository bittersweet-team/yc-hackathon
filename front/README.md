# Demo Hunters - Frontend

**Create product demo videos with one click**

## What it does
Submit your product URL → Get demo videos delivered to your email

## Quick Start
```bash
npm install
npm run dev
```

## Features
- 🔐 Email & Google authentication
- 📝 Submit product URL and description
- 📊 View demo generation history
- 🎥 Track video processing status
- 📧 Get notified when videos are ready

## Tech Stack
- React/Next.js
- Tailwind CSS
- Supabase Auth
- Backend API integration

## Environment Variables
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key

DEMO_HUNTERS_API_URL=http://127.0.0.1:8000
```

## Project Structure
```
/components   - Reusable UI components
/pages        - Application routes
/services     - API client functions
/styles       - Global styles
```
