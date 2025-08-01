# Deploy to Vultr Server (66.42.87.222)

## SSH Connection & Deployment Commands

### 1. Connect to Your Vultr Server
```bash
ssh root@66.42.87.222
# or if you have a different user:
# ssh your-username@66.42.87.222
```

### 2. Clone Repository
```bash
cd /var/www
git clone https://github.com/terrencemul/video-transcoder-pipeline.git
cd video-transcoder-pipeline/video-pipeline
```

### 3. Install System Dependencies
```bash
# Update system
apt update && apt upgrade -y

# Install Python and pip
apt install python3 python3-pip -y

# Install FFmpeg
apt install ffmpeg -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
apt install nodejs -y
```

### 4. Install Python Dependencies
```bash
pip3 install -r requirements.txt
```

### 5. Create Webhook Server
```bash
# Initialize Node.js project
npm init -y
npm install express multer

# Create webhook server
cat > webhook-server.js << 'EOF'
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
  const pythonProcess = spawn('python3', ['main.py', '--input', req.file.path]);
  
  pythonProcess.stdout.on('data', (data) => {
    console.log(`Transcoder: ${data}`);
  });
  
  res.json({ 
    success: true, 
    message: 'Short form video uploaded and processing started',
    filename: req.file.filename
  });
});

app.post('/webhook/video-upload/long-form', upload.single('video'), (req, res) => {
  console.log('✅ Long form video uploaded:', req.file.filename);
  
  const pythonProcess = spawn('python3', ['main.py', '--input', req.file.path]);
  
  pythonProcess.stdout.on('data', (data) => {
    console.log(`Transcoder: ${data}`);
  });
  
  res.json({ 
    success: true, 
    message: 'Long form video uploaded and processing started',
    filename: req.file.filename
  });
});

app.post('/webhook/video-upload/listings', upload.single('video'), (req, res) => {
  console.log('✅ Listings video uploaded:', req.file.filename);
  
  const pythonProcess = spawn('python3', ['main.py', '--input', req.file.path]);
  
  pythonProcess.stdout.on('data', (data) => {
    console.log(`Transcoder: ${data}`);
  });
  
  res.json({ 
    success: true, 
    message: 'Listings video uploaded and processing started',
    filename: req.file.filename
  });
});

// Health check
app.get('/health', (req, res) => {
  res.json({ 
    status: 'OK', 
    message: 'Video transcoder webhook server running',
    server: '66.42.87.222'
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 Video transcoder webhook server running on 66.42.87.222:${PORT}`);
});
EOF
```

### 6. Setup Environment
```bash
# Copy and configure environment
cp .env.example .env

# Make sure directories exist
mkdir -p input/short_form_9_16
mkdir -p input/long_form_16_9_or_9_16  
mkdir -p input/listings_16_9
mkdir -p processing
mkdir -p output
```

### 7. Test the Setup
```bash
# Test Python transcoder
python3 test_setup.py

# Start webhook server (test mode)
node webhook-server.js
```

### 8. Production Setup with PM2
```bash
# Install PM2 for production
npm install -g pm2

# Start webhook server with PM2
pm2 start webhook-server.js --name "video-webhook"

# Setup PM2 to start on boot
pm2 startup
pm2 save

# Check status
pm2 status
```

### 9. Configure Firewall (if needed)
```bash
# Allow port 3000
ufw allow 3000
ufw status
```

## n8n Integration URLs

Once deployed, your n8n workflows can use these endpoints:

### Webhook URLs:
- **Short Form**: `http://66.42.87.222:3000/webhook/video-upload/short-form`
- **Long Form**: `http://66.42.87.222:3000/webhook/video-upload/long-form`
- **Listings**: `http://66.42.87.222:3000/webhook/video-upload/listings`

### Health Check:
- `http://66.42.87.222:3000/health`

## n8n HTTP Request Node Settings:
- **Method**: POST
- **URL**: `http://66.42.87.222:3000/webhook/video-upload/short-form`
- **Body Content Type**: Form-Data
- **Body Parameters**:
  - Name: `video`
  - Value: `{{ $binary.data }}`

## Test Deployment:
```bash
# Test from your local machine
curl http://66.42.87.222:3000/health

# Test video upload
curl -X POST \
  -F "video=@test-video.mp4" \
  http://66.42.87.222:3000/webhook/video-upload/short-form
```

## Directory Structure on Server:
```
/var/www/video-transcoder-pipeline/video-pipeline/
├── input/
│   ├── short_form_9_16/      # Videos from n8n short-form
│   ├── long_form_16_9_or_9_16/  # Videos from n8n long-form
│   └── listings_16_9/        # Videos from n8n listings
├── output/                   # Final transcoded videos
├── webhook-server.js         # Running on port 3000
└── main.py                   # Python transcoder
```

Your Vultr server will now automatically:
1. Receive videos from n8n
2. Process them with face detection
3. Create both 16:9 and 9:16 versions
4. Name them for platform delivery
