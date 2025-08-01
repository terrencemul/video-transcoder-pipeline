# Simple n8n Webhook Integration (No Auth) - For Testing

## Overview
These are simplified webhook curl commands WITHOUT authorization for easy testing. You can add security later once everything is working.

## Simple Webhook Endpoints (No Auth Required)

### 1. Short Form 9:16 Videos
```bash
curl -X POST \
  -F "video=@/path/to/your/video.mp4" \
  https://your-domain.com/webhook/video-upload/short-form
```

### 2. Long Form Mixed Format Videos
```bash
curl -X POST \
  -F "video=@/path/to/your/video.mp4" \
  https://your-domain.com/webhook/video-upload/long-form
```

### 3. Listings 16:9 Videos
```bash
curl -X POST \
  -F "video=@/path/to/your/video.mp4" \
  https://your-domain.com/webhook/video-upload/listings
```

## Simple Server Implementation (Express.js)

Here's a basic webhook server WITHOUT authentication for testing:

```javascript
const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');

const app = express();

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    // Determine category based on endpoint
    let category = 'unknown';
    if (req.path.includes('short-form')) {
      category = 'short_form_9_16';
    } else if (req.path.includes('long-form')) {
      category = 'long_form_16_9_or_9_16';
    } else if (req.path.includes('listings')) {
      category = 'listings_16_9';
    }
    
    const uploadPath = path.join(__dirname, 'video-pipeline', 'input', category);
    
    // Ensure directory exists
    fs.mkdirSync(uploadPath, { recursive: true });
    cb(null, uploadPath);
  },
  filename: function (req, file, cb) {
    // Use timestamp + original filename
    const filename = `${Date.now()}_${file.originalname}`;
    cb(null, filename);
  }
});

const upload = multer({ 
  storage: storage,
  limits: {
    fileSize: 500 * 1024 * 1024 // 500MB limit
  }
});

// Simple webhook endpoints (NO AUTH)
app.post('/webhook/video-upload/short-form', upload.single('video'), (req, res) => {
  console.log('✅ Short form video uploaded:', req.file.filename);
  res.json({ 
    success: true, 
    message: 'Short form video uploaded successfully',
    filename: req.file.filename,
    category: 'short_form_9_16'
  });
});

app.post('/webhook/video-upload/long-form', upload.single('video'), (req, res) => {
  console.log('✅ Long form video uploaded:', req.file.filename);
  res.json({ 
    success: true, 
    message: 'Long form video uploaded successfully',
    filename: req.file.filename,
    category: 'long_form_16_9_or_9_16'
  });
});

app.post('/webhook/video-upload/listings', upload.single('video'), (req, res) => {
  console.log('✅ Listings video uploaded:', req.file.filename);
  res.json({ 
    success: true, 
    message: 'Listings video uploaded successfully',
    filename: req.file.filename,
    category: 'listings_16_9'
  });
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'OK', message: 'Webhook server is running' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 Webhook server running on port ${PORT}`);
  console.log(`📁 Videos will be saved to: ${path.join(__dirname, 'video-pipeline', 'input')}`);
});
```

## n8n HTTP Request Node Configuration (No Auth)

In your n8n HTTP Request node, use these simple settings:

### Basic Configuration:
- **Method**: POST
- **URL**: `https://your-domain.com/webhook/video-upload/short-form`
- **Body Content Type**: Form-Data

### Body Parameters:
```json
{
  "parameters": [
    {
      "name": "video",
      "value": "={{ $binary.data }}"
    }
  ]
}
```

## Quick Testing

### Test locally first:
1. Save the server code as `webhook-server.js`
2. Install dependencies: `npm install express multer`
3. Run server: `node webhook-server.js`
4. Test with curl on localhost:

```bash
# Test short form upload (localhost)
curl -X POST \
  -F "video=@test-video.mp4" \
  http://localhost:3000/webhook/video-upload/short-form

# Test long form upload (localhost)
curl -X POST \
  -F "video=@test-video.mp4" \
  http://localhost:3000/webhook/video-upload/long-form

# Test listings upload (localhost)
curl -X POST \
  -F "video=@test-video.mp4" \
  http://localhost:3000/webhook/video-upload/listings
```

### Check if server is running:
```bash
curl http://localhost:3000/health
```

## Package.json for the webhook server

Create this `package.json` file:
```json
{
  "name": "video-webhook-server",
  "version": "1.0.0",
  "description": "Simple webhook server for video uploads",
  "main": "webhook-server.js",
  "scripts": {
    "start": "node webhook-server.js",
    "dev": "nodemon webhook-server.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "multer": "^1.4.5-lts.1"
  },
  "devDependencies": {
    "nodemon": "^3.0.1"
  }
}
```

## File Structure After Upload

Videos will be automatically organized:
```
video-pipeline/
├── input/
│   ├── short_form_9_16/
│   │   └── 1722528000000_video1.mp4
│   ├── long_form_16_9_or_9_16/
│   │   └── 1722528001000_video2.mp4
│   └── listings_16_9/
│       └── 1722528002000_video3.mp4
```

## Adding Security Later (Optional)

When you're ready to add security, here's how:

### 1. Simple API Key Method:
Add this to your server:
```javascript
// Middleware to check API key
const checkApiKey = (req, res, next) => {
  const apiKey = req.headers['authorization'];
  const validKey = 'Bearer your-secret-key-here';
  
  if (apiKey !== validKey) {
    return res.status(401).json({ error: 'Invalid API key' });
  }
  next();
};

// Apply to endpoints
app.post('/webhook/video-upload/short-form', checkApiKey, upload.single('video'), ...);
```

### 2. Environment Variable for API Key:
```javascript
const API_KEY = process.env.API_KEY || 'default-test-key';

const checkApiKey = (req, res, next) => {
  const apiKey = req.headers['authorization'];
  const validKey = `Bearer ${API_KEY}`;
  
  if (apiKey !== validKey) {
    return res.status(401).json({ error: 'Invalid API key' });
  }
  next();
};
```

### 3. Then use curl with auth:
```bash
curl -X POST \
  -H "Authorization: Bearer your-secret-key-here" \
  -F "video=@video.mp4" \
  https://your-domain.com/webhook/video-upload/short-form
```

## Next Steps for Testing:

1. **Start simple**: Use the no-auth version first
2. **Test locally**: Use localhost:3000 to verify everything works
3. **Deploy to your domain**: Replace localhost with your actual domain
4. **Test with n8n**: Configure your n8n HTTP Request nodes
5. **Add security later**: Once everything works, add API key authentication

The authorization I mentioned earlier was just a security best practice, but you're absolutely right to skip it for initial testing!
