# Deploy Video Transcoder Pipeline to Server

## Server Deployment Commands

### 1. Clone Repository on Server
```bash
# SSH into your server first
ssh your-username@your-server-ip

# Clone the repository
git clone https://github.com/terrencemul/video-transcoder-pipeline.git
cd video-transcoder-pipeline/video-pipeline
```

### 2. Install Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install FFmpeg (if not already installed)
# Ubuntu/Debian:
sudo apt update
sudo apt install ffmpeg

# CentOS/RHEL:
sudo yum install ffmpeg
# or
sudo dnf install ffmpeg
```

### 3. Setup Configuration
```bash
# Copy environment configuration
cp .env.example .env

# Edit configuration for server paths
nano .env
```

### 4. Create Webhook Server
Create a simple webhook server that accepts video uploads and triggers the transcoder:

```javascript
// webhook-server.js
const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');

const app = express();

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    let category = 'unknown';
    if (req.path.includes('short-form')) {
      category = 'short_form_9_16';
    } else if (req.path.includes('long-form')) {
      category = 'long_form_16_9_or_9_16';
    } else if (req.path.includes('listings')) {
      category = 'listings_16_9';
    }
    
    const uploadPath = path.join(__dirname, 'input', category);
    fs.mkdirSync(uploadPath, { recursive: true });
    cb(null, uploadPath);
  },
  filename: function (req, file, cb) {
    const filename = `${Date.now()}_${file.originalname}`;
    cb(null, filename);
  }
});

const upload = multer({ 
  storage: storage,
  limits: { fileSize: 500 * 1024 * 1024 } // 500MB
});

// Webhook endpoints
app.post('/webhook/video-upload/short-form', upload.single('video'), (req, res) => {
  console.log('✅ Short form video uploaded:', req.file.filename);
  
  // Trigger Python transcoder
  const pythonProcess = spawn('python', ['main.py', '--input', req.file.path]);
  
  pythonProcess.stdout.on('data', (data) => {
    console.log(`Transcoder output: ${data}`);
  });
  
  res.json({ 
    success: true, 
    message: 'Video uploaded and processing started',
    filename: req.file.filename,
    category: 'short_form_9_16'
  });
});

app.post('/webhook/video-upload/long-form', upload.single('video'), (req, res) => {
  console.log('✅ Long form video uploaded:', req.file.filename);
  
  const pythonProcess = spawn('python', ['main.py', '--input', req.file.path]);
  
  pythonProcess.stdout.on('data', (data) => {
    console.log(`Transcoder output: ${data}`);
  });
  
  res.json({ 
    success: true, 
    message: 'Video uploaded and processing started',
    filename: req.file.filename,
    category: 'long_form_16_9_or_9_16'
  });
});

app.post('/webhook/video-upload/listings', upload.single('video'), (req, res) => {
  console.log('✅ Listings video uploaded:', req.file.filename);
  
  const pythonProcess = spawn('python', ['main.py', '--input', req.file.path]);
  
  pythonProcess.stdout.on('data', (data) => {
    console.log(`Transcoder output: ${data}`);
  });
  
  res.json({ 
    success: true, 
    message: 'Video uploaded and processing started',
    filename: req.file.filename,
    category: 'listings_16_9'
  });
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'OK', message: 'Video transcoder webhook server running' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 Video transcoder webhook server running on port ${PORT}`);
});
```

### 5. Install Node.js Dependencies
```bash
# Create package.json
npm init -y

# Install dependencies
npm install express multer

# Save webhook server
nano webhook-server.js
# (paste the JavaScript code above)
```

### 6. Start the Services
```bash
# Option 1: Start webhook server
node webhook-server.js

# Option 2: Use PM2 for production (recommended)
npm install -g pm2
pm2 start webhook-server.js --name "video-webhook"
pm2 startup
pm2 save
```

### 7. Configure Nginx (if using)
```nginx
# /etc/nginx/sites-available/video-transcoder
server {
    listen 80;
    server_name your-domain.com;
    
    location /webhook/ {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        client_max_body_size 500M;
    }
}
```

### 8. Test the Deployment
```bash
# Test health endpoint
curl http://your-domain.com/health

# Test video upload
curl -X POST \
  -F "video=@test-video.mp4" \
  http://your-domain.com/webhook/video-upload/short-form
```

## n8n Integration

Now your n8n workflows can use these endpoints:

### HTTP Request Node Configuration:
- **URL**: `http://your-domain.com/webhook/video-upload/short-form`
- **Method**: POST
- **Body**: Form-Data
- **Parameters**: 
  - `video`: `{{ $binary.data }}`

### Workflow Example:
```
Dropbox Trigger 
    ↓
HTTP Request (to your server webhook)
    ↓ 
Server processes video automatically
    ↓
Transcoded videos appear in output/ folder
```

## Directory Structure on Server:
```
/var/www/video-transcoder-pipeline/video-pipeline/
├── input/              # Videos from n8n
├── processing/         # Temp processing
├── output/            # Final transcoded videos
├── webhook-server.js  # Node.js webhook server
└── main.py           # Python transcoder
```

Your server is now ready to receive videos from n8n and automatically transcode them!
