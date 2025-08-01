# n8n Curl Commands for Video Transcoder Pipeline

## Test Commands for Each Video Category

These curl commands simulate how n8n would send videos to your webhook endpoints.

### 1. Short Form Videos (9:16 aspect ratio)
```bash
# For videos that need to be in 9:16 format (TikTok, Instagram Reels, YouTube Shorts)
curl -X POST \
  -F "video=@your-video.mp4" \
  http://66.42.87.222:3000/webhook/video-upload/short-form
```

### 2. Long Form Videos (16:9 or 9:16)
```bash
# For regular videos that may need both aspect ratios
curl -X POST \
  -F "video=@your-video.mp4" \
  http://66.42.87.222:3000/webhook/video-upload/long-form
```

### 3. Listings Videos (16:9 aspect ratio)
```bash
# For property listing videos that should be in 16:9 format
curl -X POST \
  -F "video=@your-video.mp4" \
  http://66.42.87.222:3000/webhook/video-upload/listings
```

## Complete Test Examples

### Test with a sample video file:
```bash
# First, create a test video or use an existing one
# Then run one of these commands:

# Short Form Test
curl -X POST \
  -H "Content-Type: multipart/form-data" \
  -F "video=@C:/Users/terre/test-video.mp4" \
  http://66.42.87.222:3000/webhook/video-upload/short-form

# Long Form Test
curl -X POST \
  -H "Content-Type: multipart/form-data" \
  -F "video=@C:/Users/terre/test-video.mp4" \
  http://66.42.87.222:3000/webhook/video-upload/long-form

# Listings Test
curl -X POST \
  -H "Content-Type: multipart/form-data" \
  -F "video=@C:/Users/terre/test-video.mp4" \
  http://66.42.87.222:3000/webhook/video-upload/listings
```

## n8n HTTP Request Node Configuration

For each category, configure your n8n HTTP Request node as follows:

### Short Form Videos (TikTok, Reels, Shorts)
```json
{
  "method": "POST",
  "url": "http://66.42.87.222:3000/webhook/video-upload/short-form",
  "sendBody": true,
  "bodyContentType": "multipart-form-data",
  "bodyParameters": {
    "parameters": [
      {
        "name": "video",
        "value": "={{ $binary.data }}",
        "parameterType": "formBinaryData",
        "dataPropertyName": "data"
      }
    ]
  }
}
```

### Long Form Videos (YouTube, Facebook)
```json
{
  "method": "POST",
  "url": "http://66.42.87.222:3000/webhook/video-upload/long-form",
  "sendBody": true,
  "bodyContentType": "multipart-form-data",
  "bodyParameters": {
    "parameters": [
      {
        "name": "video",
        "value": "={{ $binary.data }}",
        "parameterType": "formBinaryData",
        "dataPropertyName": "data"
      }
    ]
  }
}
```

### Listings Videos (Property Tours)
```json
{
  "method": "POST",
  "url": "http://66.42.87.222:3000/webhook/video-upload/listings",
  "sendBody": true,
  "bodyContentType": "multipart-form-data",
  "bodyParameters": {
    "parameters": [
      {
        "name": "video",
        "value": "={{ $binary.data }}",
        "parameterType": "formBinaryData",
        "dataPropertyName": "data"
      }
    ]
  }
}
```

## Webhook Response Examples

### Successful Upload Response:
```json
{
  "success": true,
  "message": "Short form video uploaded and processing started",
  "filename": "1733086800000_test-video.mp4"
}
```

### Health Check:
```bash
curl http://66.42.87.222:3000/health
```

Response:
```json
{
  "status": "OK",
  "message": "Video transcoder webhook server running",
  "server": "66.42.87.222"
}
```

## Testing from Windows Command Prompt

If you're testing from Windows, use these commands:

```cmd
# Short Form
curl -X POST -F "video=@C:\path\to\your\video.mp4" http://66.42.87.222:3000/webhook/video-upload/short-form

# Long Form
curl -X POST -F "video=@C:\path\to\your\video.mp4" http://66.42.87.222:3000/webhook/video-upload/long-form

# Listings
curl -X POST -F "video=@C:\path\to\your\video.mp4" http://66.42.87.222:3000/webhook/video-upload/listings
```

## Video Processing Flow

1. **Upload**: Video is uploaded to the appropriate input folder based on the endpoint
2. **Processing**: Python transcoder automatically processes the video
3. **Face Detection**: For 16:9 to 9:16 conversion, face detection centers the crop
4. **Output**: Processed videos are saved to the output folder with platform-specific naming

## Output File Naming Convention

The transcoder will create files with names like:
- `shortform_9_16_[original_name].mp4`
- `longform_16_9_[original_name].mp4`
- `longform_9_16_[original_name].mp4`
- `listings_16_9_[original_name].mp4`

## Monitoring Processing

To monitor video processing on the server:
```bash
# SSH into server
ssh root@66.42.87.222

# Check PM2 logs
pm2 logs video-webhook

# Check specific folders
ls -la /var/www/video-transcoder-pipeline/video-pipeline/input/short_form_9_16/
ls -la /var/www/video-transcoder-pipeline/video-pipeline/output/
```

## Troubleshooting

If uploads fail, check:
1. Server is accessible: `curl http://66.42.87.222:3000/health`
2. File size is under 500MB
3. Video format is supported (mp4, mov, avi)
4. PM2 process is running: `pm2 status` (on server)
