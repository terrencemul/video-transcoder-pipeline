# n8n URL-Based Video Processing Commands

## Webhook Endpoints for URL Videos

Since you're sending video URLs instead of uploading files, here are the updated commands and configurations.

### JSON Payload Format
```json
{
  "videoUrl": "https://example.com/path/to/video.mp4"
}
```

## Test Commands for Each Category

### 1. Short Form Videos (9:16 - TikTok, Reels, Shorts)
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"videoUrl":"https://example.com/video.mp4"}' \
  http://66.42.87.222:3000/webhook/video-upload/short-form
```

### 2. Long Form Videos (16:9 or 9:16)
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"videoUrl":"https://example.com/video.mp4"}' \
  http://66.42.87.222:3000/webhook/video-upload/long-form
```

### 3. Listings Videos (16:9)
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"videoUrl":"https://example.com/video.mp4"}' \
  http://66.42.87.222:3000/webhook/video-upload/listings
```

## n8n HTTP Request Node Configuration

### Short Form Videos
```json
{
  "method": "POST",
  "url": "http://66.42.87.222:3000/webhook/video-upload/short-form",
  "authentication": "none",
  "sendHeaders": true,
  "headerParameters": {
    "parameters": [
      {
        "name": "Content-Type",
        "value": "application/json"
      }
    ]
  },
  "sendBody": true,
  "bodyContentType": "json",
  "bodyParameters": {
    "parameters": [
      {
        "name": "videoUrl",
        "value": "={{ $json.videoUrl }}"
      }
    ]
  }
}
```

### Long Form Videos
```json
{
  "method": "POST",
  "url": "http://66.42.87.222:3000/webhook/video-upload/long-form",
  "authentication": "none",
  "sendHeaders": true,
  "headerParameters": {
    "parameters": [
      {
        "name": "Content-Type",
        "value": "application/json"
      }
    ]
  },
  "sendBody": true,
  "bodyContentType": "json",
  "bodyParameters": {
    "parameters": [
      {
        "name": "videoUrl",
        "value": "={{ $json.videoUrl }}"
      }
    ]
  }
}
```

### Listings Videos
```json
{
  "method": "POST",
  "url": "http://66.42.87.222:3000/webhook/video-upload/listings",
  "authentication": "none",
  "sendHeaders": true,
  "headerParameters": {
    "parameters": [
      {
        "name": "Content-Type",
        "value": "application/json"
      }
    ]
  },
  "sendBody": true,
  "bodyContentType": "json",
  "bodyParameters": {
    "parameters": [
      {
        "name": "videoUrl",
        "value": "={{ $json.videoUrl }}"
      }
    ]
  }
}
```

## Windows Test Commands

```cmd
# Short Form
curl -X POST -H "Content-Type: application/json" -d "{\"videoUrl\":\"https://example.com/video.mp4\"}" http://66.42.87.222:3000/webhook/video-upload/short-form

# Long Form
curl -X POST -H "Content-Type: application/json" -d "{\"videoUrl\":\"https://example.com/video.mp4\"}" http://66.42.87.222:3000/webhook/video-upload/long-form

# Listings
curl -X POST -H "Content-Type: application/json" -d "{\"videoUrl\":\"https://example.com/video.mp4\"}" http://66.42.87.222:3000/webhook/video-upload/listings
```

## Test with Real Video URLs

Here are some example test URLs you can use:

```bash
# Test with a sample video
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"videoUrl":"https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4"}' \
  http://66.42.87.222:3000/webhook/video-upload/short-form
```

## Expected Response

### Success Response:
```json
{
  "success": true,
  "message": "short_form_9_16 video downloaded and processing started",
  "filename": "1733087400000_video.mp4",
  "videoUrl": "https://example.com/video.mp4"
}
```

### Error Response:
```json
{
  "success": false,
  "error": "No video URL provided"
}
```

## Processing Flow

1. **Receive URL**: Webhook receives JSON with video URL
2. **Download Video**: Server downloads video to appropriate input folder
3. **Process Video**: Python transcoder processes the downloaded video
4. **Face Detection**: For 16:9 to 9:16 conversion, uses face detection
5. **Output**: Saves processed videos to output folder

## Monitoring on Server

```bash
# SSH to server
ssh root@66.42.87.222

# Check PM2 logs
pm2 logs video-webhook

# Watch download progress
ls -la /var/www/video-transcoder-pipeline/video-pipeline/input/short_form_9_16/

# Check processed videos
ls -la /var/www/video-transcoder-pipeline/video-pipeline/output/
```

## Update Webhook Server

To update the server to use URL mode:

```bash
# SSH to server
ssh root@66.42.87.222

# Navigate to project
cd /var/www/video-transcoder-pipeline/video-pipeline

# Stop current server
pm2 stop video-webhook

# Replace webhook server with URL version
cp webhook-server-url.js webhook-server.js

# Restart server
pm2 restart video-webhook

# Check logs
pm2 logs video-webhook
```
