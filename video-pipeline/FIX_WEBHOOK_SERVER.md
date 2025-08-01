# Fix Webhook Server Instructions

## Issue Identified
The webhook server is crashing because it's trying to access `req.file.filename` when processing URL-based requests, but `req.file` is undefined for JSON requests.

## Quick Fix via SSH

1. **Connect to server:**
```bash
ssh root@66.42.87.222
# Password: _bT7Sb(nh)+c3V-o
```

2. **Navigate to project:**
```bash
cd /var/www/video-transcoder-pipeline/video-pipeline
```

3. **Stop the current server:**
```bash
pm2 stop video-webhook
```

4. **Create the fixed webhook server:**
```bash
# Copy the content from webhook-server-fixed.js
nano webhook-server-fixed.js
# Paste the content and save (Ctrl+X, Y, Enter)
```

5. **Replace the current server:**
```bash
cp webhook-server-fixed.js webhook-server.js
```

6. **Restart PM2:**
```bash
pm2 restart video-webhook
pm2 save
```

7. **Check logs:**
```bash
pm2 logs video-webhook --lines 20
```

## Alternative: Push Update via Git

1. **From your local machine:**
```bash
cd c:\Users\terre\Ahoyhomes_Git_Repo_Local\video-pipeline
git add webhook-server-fixed.js
git commit -m "Fix webhook server to handle both URL and file uploads"
git push origin main
```

2. **On the server:**
```bash
cd /var/www/video-transcoder-pipeline/video-pipeline
git pull origin main
cp webhook-server-fixed.js webhook-server.js
pm2 restart video-webhook
```

## Test Commands

### Test Health Endpoint:
```bash
curl http://66.42.87.222:3000/health
```

### Test URL-based Upload:
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"videoUrl":"https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4"}' \
  http://66.42.87.222:3000/webhook/video-upload/short-form
```

### Test File Upload:
```bash
curl -X POST \
  -F "video=@test-video.mp4" \
  http://66.42.87.222:3000/webhook/video-upload/short-form
```

## What the Fix Does

1. **Dual Mode Support**: The fixed server supports both:
   - JSON requests with `videoUrl` parameter
   - File uploads via multipart/form-data

2. **Error Handling**: Properly checks if request contains URL or file before processing

3. **Better Logging**: More detailed console output for debugging

4. **Timeout Protection**: 30-second timeout for URL downloads

## Expected Response

### For URL submission:
```json
{
  "success": true,
  "message": "short_form_9_16 video downloaded and processing started",
  "filename": "1733088000000_video.mp4",
  "videoUrl": "https://example.com/video.mp4"
}
```

### For file upload:
```json
{
  "success": true,
  "message": "Short form video uploaded and processing started",
  "filename": "1733088000000_test-video.mp4"
}
```
