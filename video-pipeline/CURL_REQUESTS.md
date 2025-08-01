# Curl Requests for Video Transcoder Pipeline
# Server: 66.42.87.222:3000

## Health Check
```bash
curl http://66.42.87.222:3000/health
```

## Short Form Video Upload (9:16)
```bash
curl -X POST \
  -F "video=@your-video.mp4" \
  http://66.42.87.222:3000/webhook/video-upload/short-form
```

## Long Form Video Upload (Mixed 16:9 or 9:16)
```bash
curl -X POST \
  -F "video=@your-video.mp4" \
  http://66.42.87.222:3000/webhook/video-upload/long-form
```

## Listings Video Upload (16:9)
```bash
curl -X POST \
  -F "video=@your-video.mp4" \
  http://66.42.87.222:3000/webhook/video-upload/listings
```

## Verbose Testing (with response headers)
```bash
# Short form with verbose output
curl -X POST \
  -F "video=@your-video.mp4" \
  -v \
  http://66.42.87.222:3000/webhook/video-upload/short-form

# Long form with verbose output
curl -X POST \
  -F "video=@your-video.mp4" \
  -v \
  http://66.42.87.222:3000/webhook/video-upload/long-form

# Listings with verbose output
curl -X POST \
  -F "video=@your-video.mp4" \
  -v \
  http://66.42.87.222:3000/webhook/video-upload/listings
```

## Expected Response Format
```json
{
  "success": true,
  "message": "Short form video uploaded and processing started",
  "filename": "1722528000000_your-video.mp4"
}
```

## Test with Different Video Formats
```bash
# MP4 file
curl -X POST \
  -F "video=@sample.mp4" \
  http://66.42.87.222:3000/webhook/video-upload/short-form

# MOV file
curl -X POST \
  -F "video=@sample.mov" \
  http://66.42.87.222:3000/webhook/video-upload/long-form

# AVI file
curl -X POST \
  -F "video=@sample.avi" \
  http://66.42.87.222:3000/webhook/video-upload/listings
```

## Progress Monitoring
```bash
# Check server health during processing
watch -n 5 "curl -s http://66.42.87.222:3000/health"

# Monitor server logs (if you have SSH access)
# ssh root@66.42.87.222
# pm2 logs video-webhook
```

## Error Testing
```bash
# Test with no file
curl -X POST \
  http://66.42.87.222:3000/webhook/video-upload/short-form

# Test with invalid endpoint
curl -X POST \
  -F "video=@your-video.mp4" \
  http://66.42.87.222:3000/webhook/video-upload/invalid

# Test with large file (will test 500MB limit)
curl -X POST \
  -F "video=@large-video.mp4" \
  http://66.42.87.222:3000/webhook/video-upload/short-form
```

## n8n Integration Examples

### HTTP Request Node Settings:
```
Method: POST
URL: http://66.42.87.222:3000/webhook/video-upload/short-form
Body Content Type: Form-Data
Body Parameters:
  - Name: video
  - Value: {{ $binary.data }}
```

### Equivalent curl for n8n testing:
```bash
# This simulates what n8n sends
curl -X POST \
  -H "Content-Type: multipart/form-data" \
  -F "video=@video-from-dropbox.mp4" \
  http://66.42.87.222:3000/webhook/video-upload/short-form
```

## Batch Testing Script
```bash
#!/bin/bash
# test-all-endpoints.sh

echo "Testing Video Transcoder Pipeline on 66.42.87.222"
echo "================================================="

# Health check
echo "1. Health Check:"
curl -s http://66.42.87.222:3000/health | jq .
echo ""

# Test video file (replace with your actual video)
VIDEO_FILE="test-video.mp4"

if [ -f "$VIDEO_FILE" ]; then
    echo "2. Testing Short Form Upload:"
    curl -X POST -F "video=@$VIDEO_FILE" http://66.42.87.222:3000/webhook/video-upload/short-form | jq .
    echo ""
    
    echo "3. Testing Long Form Upload:"
    curl -X POST -F "video=@$VIDEO_FILE" http://66.42.87.222:3000/webhook/video-upload/long-form | jq .
    echo ""
    
    echo "4. Testing Listings Upload:"
    curl -X POST -F "video=@$VIDEO_FILE" http://66.42.87.222:3000/webhook/video-upload/listings | jq .
    echo ""
else
    echo "Test video file '$VIDEO_FILE' not found!"
    echo "Please add a test video file or update the VIDEO_FILE variable"
fi

echo "Testing complete!"
```

## Windows CMD Examples
```cmd
# Health check (Windows)
curl http://66.42.87.222:3000/health

# Upload video (Windows)
curl -X POST -F "video=@your-video.mp4" http://66.42.87.222:3000/webhook/video-upload/short-form
```

## PowerShell Examples
```powershell
# Health check
Invoke-RestMethod -Uri "http://66.42.87.222:3000/health" -Method Get

# Upload video (PowerShell)
$form = @{
    video = Get-Item -Path "your-video.mp4"
}
Invoke-RestMethod -Uri "http://66.42.87.222:3000/webhook/video-upload/short-form" -Method Post -Form $form
```

## Response Codes
- **200 OK**: Video uploaded and processing started
- **400 Bad Request**: Missing video file or invalid request
- **413 Payload Too Large**: Video file exceeds 500MB limit
- **500 Internal Server Error**: Server processing error

## File Output Locations
After successful upload and processing, check these directories on your server:
```
/var/www/video-transcoder-pipeline/video-pipeline/output/
├── video_16x9_youtube_googlebusiness_instagram.mp4
└── video_9x16_tiktok_instastories_youtubeshorts_instagram.mp4
```
