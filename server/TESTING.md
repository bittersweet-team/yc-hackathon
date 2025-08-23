# Testing Guide

## Mock Mode Setup

The backend is configured to run in mock mode for testing without real recording API.

### 1. Sample Video Setup

Place a sample video file at:
```
server/res/sample.mp4
```

If no sample.mp4 is found, the system will use a public Big Buck Bunny video as fallback.

### 2. Configuration

In your `.env` file:
```env
USE_MOCK_RECORDING=true  # Enable mock mode
RECORDING_API_URL=mock   # Or set to "mock"
```

## Test Endpoints

The API includes test endpoints for verifying each service:

### Check Test Configuration
```bash
curl http://localhost:8000/api/test/status
```

### Test Mock Recording
```bash
curl -X POST http://localhost:8000/api/test/recording
```

Response:
```json
{
  "success": true,
  "message": "Mock recording successful",
  "data": {
    "video_url": "https://..."
  }
}
```

### Test Klap API
```bash
curl -X POST http://localhost:8000/api/test/klap \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"}'
```

### Test AgentMail
```bash
curl -X POST http://localhost:8000/api/test/agentmail \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

## Integration Test Script

Run the full integration test:
```bash
python test_integration.py
```

This will:
1. Upload sample video (mock recording)
2. Submit to Klap API for short generation
3. Send test email via AgentMail

## Test Flow

### Complete Demo Test

1. Start the server:
```bash
python main.py
```

2. Create a test demo (requires auth token):
```bash
curl -X POST http://localhost:8000/api/demo \
  -H "Authorization: Bearer <your_supabase_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "product_url": "https://example.com",
    "description": "Test product demo",
    "email": "your-email@example.com"
  }'
```

3. Check demo status:
```bash
curl http://localhost:8000/api/demo/{demo_id} \
  -H "Authorization: Bearer <your_supabase_token>"
```

## Monitoring

Watch server logs to track processing:
- Mock recording upload
- Klap API submission
- Short video generation
- AgentMail delivery

## Troubleshooting

### Recording Issues
- Verify `sample.mp4` exists in `server/res/`
- Check Supabase Storage bucket permissions
- Fallback URL will be used if upload fails

### Klap API Issues
- Verify API key is valid
- Check video URL is accessible
- Processing may take 5-10 minutes

### AgentMail Issues
- Verify API key is valid
- Check email format
- Review server logs for errors

## Production Mode

To switch to production:
1. Set `USE_MOCK_RECORDING=false` in `.env`
2. Provide real `RECORDING_API_URL`
3. Ensure all API keys are production keys