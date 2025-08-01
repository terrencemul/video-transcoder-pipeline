# n8n Webhook Integration for Video Transcoder Pipeline

## Overview
This document provides the curl commands and n8n webhook configurations for integrating with the Video Transcoder Pipeline. The webhooks allow n8n workflows to upload videos directly to the appropriate input directories.

## Webhook Endpoints

### 1. Short Form 9:16 Videos
**Endpoint**: `https://your-domain.com/webhook/video-upload/short-form`
**Method**: POST
**Content-Type**: multipart/form-data

#### Curl Command:
```bash
curl -X POST \
  -H "Content-Type: multipart/form-data" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "video=@/path/to/your/video.mp4" \
  -F "source=dropbox" \
  -F "category=short_form_9:16" \
  https://your-domain.com/webhook/video-upload/short-form
```

### 2. Long Form Mixed Format Videos
**Endpoint**: `https://your-domain.com/webhook/video-upload/long-form`
**Method**: POST
**Content-Type**: multipart/form-data

#### Curl Command:
```bash
curl -X POST \
  -H "Content-Type: multipart/form-data" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "video=@/path/to/your/video.mp4" \
  -F "source=dropbox" \
  -F "category=long_form_16:9_or_9:16" \
  https://your-domain.com/webhook/video-upload/long-form
```

### 3. Listings 16:9 Videos
**Endpoint**: `https://your-domain.com/webhook/video-upload/listings`
**Method**: POST
**Content-Type**: multipart/form-data

#### Curl Command:
```bash
curl -X POST \
  -H "Content-Type: multipart/form-data" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "video=@/path/to/your/video.mp4" \
  -F "source=dropbox" \
  -F "category=listings_16:9" \
  https://your-domain.com/webhook/video-upload/listings
```

## n8n Workflow Configuration

### Webhook Node Configuration
```json
{
  "httpMethod": "POST",
  "path": "video-upload/short-form",
  "responseMode": "responseNode",
  "options": {
    "rawBody": false
  }
}
```

### HTTP Request Node (for uploading to your server)
```json
{
  "method": "POST",
  "url": "https://your-domain.com/api/video-upload",
  "sendHeaders": true,
  "headerParameters": {
    "parameters": [
      {
        "name": "Authorization",
        "value": "Bearer YOUR_API_KEY"
      },
      {
        "name": "Content-Type", 
        "value": "multipart/form-data"
      }
    ]
  },
  "sendBody": true,
  "bodyParameters": {
    "parameters": [
      {
        "name": "video",
        "value": "={{ $binary.data }}"
      },
      {
        "name": "category",
        "value": "short_form_9:16"
      },
      {
        "name": "filename",
        "value": "={{ $json.filename }}"
      }
    ]
  }
}
```

## Example n8n Workflow Steps

### 1. Dropbox Trigger → Short Form Processing
```
Dropbox Trigger (short_form_9:16 folder)
    ↓
HTTP Request (upload to webhook)
    ↓
Response (confirmation)
```

### 2. Dropbox Trigger → Long Form Processing  
```
Dropbox Trigger (long_form_16:9_or_9:16 folder)
    ↓
HTTP Request (upload to webhook)
    ↓
Response (confirmation)
```

### 3. Dropbox Trigger → Listings Processing
```
Dropbox Trigger (listings_16:9 folder)
    ↓
HTTP Request (upload to webhook)
    ↓
Response (confirmation)
```

## Server-Side Webhook Handler

You'll need to implement these webhook endpoints on your server. Here's a basic structure:

### Express.js Example
```javascript
const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');

const app = express();

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    const category = req.body.category || 'unknown';
    const uploadPath = path.join(__dirname, 'video-pipeline', 'input', category);
    
    // Ensure directory exists
    fs.mkdirSync(uploadPath, { recursive: true });
    cb(null, uploadPath);
  },
  filename: function (req, file, cb) {
    // Keep original filename or use timestamp
    const filename = req.body.filename || `${Date.now()}_${file.originalname}`;
    cb(null, filename);
  }
});

const upload = multer({ 
  storage: storage,
  limits: {
    fileSize: 500 * 1024 * 1024 // 500MB limit
  },
  fileFilter: function (req, file, cb) {
    // Accept video files only
    const allowedTypes = /mp4|avi|mov|mkv|webm|flv|m4v/;
    const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
    const mimetype = allowedTypes.test(file.mimetype);
    
    if (mimetype && extname) {
      return cb(null, true);
    } else {
      cb(new Error('Only video files are allowed'));
    }
  }
});

// Webhook endpoints
app.post('/webhook/video-upload/short-form', upload.single('video'), (req, res) => {
  console.log('Short form video uploaded:', req.file.path);
  res.json({ 
    success: true, 
    message: 'Video uploaded successfully',
    category: 'short_form_9:16',
    filename: req.file.filename,
    path: req.file.path
  });
});

app.post('/webhook/video-upload/long-form', upload.single('video'), (req, res) => {
  console.log('Long form video uploaded:', req.file.path);
  res.json({ 
    success: true, 
    message: 'Video uploaded successfully',
    category: 'long_form_16:9_or_9:16',
    filename: req.file.filename,
    path: req.file.path
  });
});

app.post('/webhook/video-upload/listings', upload.single('video'), (req, res) => {
  console.log('Listings video uploaded:', req.file.path);
  res.json({ 
    success: true, 
    message: 'Video uploaded successfully',
    category: 'listings_16:9',
    filename: req.file.filename,
    path: req.file.path
  });
});

app.listen(3000, () => {
  console.log('Webhook server running on port 3000');
});
```

## Security Considerations

### API Key Authentication
```bash
# Include API key in all requests
-H "Authorization: Bearer your-secure-api-key-here"
```

### Rate Limiting
Implement rate limiting to prevent abuse:
```javascript
const rateLimit = require('express-rate-limit');

const uploadLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 10, // limit each IP to 10 requests per windowMs
  message: 'Too many upload attempts, please try again later'
});

app.use('/webhook/video-upload/', uploadLimiter);
```

### File Validation
- Check file size limits
- Validate file types
- Scan for malware (optional)
- Verify video integrity

## Testing the Webhooks

### Test with curl (replace with your actual domain):
```bash
# Test short form upload
curl -X POST \
  -H "Authorization: Bearer test-key-123" \
  -F "video=@test-video.mp4" \
  -F "category=short_form_9:16" \
  https://your-domain.com/webhook/video-upload/short-form

# Test long form upload  
curl -X POST \
  -H "Authorization: Bearer test-key-123" \
  -F "video=@test-video.mp4" \
  -F "category=long_form_16:9_or_9:16" \
  https://your-domain.com/webhook/video-upload/long-form

# Test listings upload
curl -X POST \
  -H "Authorization: Bearer test-key-123" \
  -F "video=@test-video.mp4" \
  -F "category=listings_16:9" \
  https://your-domain.com/webhook/video-upload/listings
```

## Integration Flow

1. **n8n Dropbox Trigger**: Detects new video in Dropbox folder
2. **HTTP Request Node**: Sends video to appropriate webhook endpoint
3. **Server Handler**: Receives video and saves to correct input directory
4. **Monitor Mode**: Video transcoder detects new file and processes
5. **Output**: Transcoded videos appear in output directory with platform naming

## Response Format

### Success Response:
```json
{
  "success": true,
  "message": "Video uploaded successfully",
  "category": "short_form_9:16",
  "filename": "video123.mp4",
  "path": "/video-pipeline/input/short_form_9_16/video123.mp4",
  "timestamp": "2025-08-01T12:00:00Z"
}
```

### Error Response:
```json
{
  "success": false,
  "error": "Invalid file type",
  "message": "Only video files are allowed",
  "timestamp": "2025-08-01T12:00:00Z"
}
```

## Deployment Notes

1. **Domain**: Replace `your-domain.com` with your actual domain
2. **SSL**: Use HTTPS for secure file uploads
3. **Storage**: Ensure sufficient disk space for video processing
4. **Monitoring**: Set up logging and error alerting
5. **Backup**: Regular backups of processed videos

## Next Steps

1. Set up your server with the webhook endpoints
2. Configure your domain and SSL certificate
3. Update n8n workflows with your webhook URLs
4. Test the integration with sample videos
5. Set up the video transcoder in monitor mode
6. Monitor logs for successful processing
