const express = require('express');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');
const https = require('https');
const http = require('http');
const { URL } = require('url');

const app = express();
app.use(express.json());

// Helper function to download video from URL
function downloadVideo(videoUrl, destination) {
  return new Promise((resolve, reject) => {
    const url = new URL(videoUrl);
    const protocol = url.protocol === 'https:' ? https : http;
    
    const file = fs.createWriteStream(destination);
    
    protocol.get(videoUrl, (response) => {
      if (response.statusCode !== 200) {
        reject(new Error(`Failed to download: ${response.statusCode}`));
        return;
      }
      
      response.pipe(file);
      
      file.on('finish', () => {
        file.close();
        resolve(destination);
      });
    }).on('error', (err) => {
      fs.unlink(destination, () => {}); // Delete the file on error
      reject(err);
    });
  });
}

// Helper function to get filename from URL or generate one
function getFilenameFromUrl(videoUrl) {
  try {
    const url = new URL(videoUrl);
    const pathname = url.pathname;
    const filename = path.basename(pathname);
    
    // If no filename in URL or no extension, generate one
    if (!filename || !filename.includes('.')) {
      return `${Date.now()}_video.mp4`;
    }
    
    return `${Date.now()}_${filename}`;
  } catch (error) {
    return `${Date.now()}_video.mp4`;
  }
}

// Process video endpoint
async function processVideo(req, res, category) {
  try {
    const { videoUrl } = req.body;
    
    if (!videoUrl) {
      return res.status(400).json({
        success: false,
        error: 'No video URL provided'
      });
    }
    
    console.log(`📥 Received ${category} video URL:`, videoUrl);
    
    // Create upload directory
    const uploadPath = path.join(__dirname, 'input', category);
    fs.mkdirSync(uploadPath, { recursive: true });
    
    // Generate filename and download path
    const filename = getFilenameFromUrl(videoUrl);
    const downloadPath = path.join(uploadPath, filename);
    
    // Download video
    console.log(`⬇️  Downloading video to: ${downloadPath}`);
    await downloadVideo(videoUrl, downloadPath);
    console.log(`✅ Video downloaded successfully`);
    
    // Trigger Python transcoder
    const pythonProcess = spawn('python3', ['main.py', '--input', downloadPath]);
    
    pythonProcess.stdout.on('data', (data) => {
      console.log(`Transcoder: ${data}`);
    });
    
    pythonProcess.stderr.on('data', (data) => {
      console.error(`Transcoder Error: ${data}`);
    });
    
    res.json({
      success: true,
      message: `${category} video downloaded and processing started`,
      filename: filename,
      videoUrl: videoUrl
    });
    
  } catch (error) {
    console.error(`❌ Error processing ${category} video:`, error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
}

// Webhook endpoints for URL-based videos
app.post('/webhook/video-upload/short-form', (req, res) => {
  processVideo(req, res, 'short_form_9_16');
});

app.post('/webhook/video-upload/long-form', (req, res) => {
  processVideo(req, res, 'long_form_16_9_or_9_16');
});

app.post('/webhook/video-upload/listings', (req, res) => {
  processVideo(req, res, 'listings_16_9');
});

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'OK',
    message: 'Video transcoder webhook server running (URL mode)',
    server: '66.42.87.222'
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 Video transcoder webhook server running on 66.42.87.222:${PORT}`);
  console.log(`📡 Mode: URL Download (expecting JSON with videoUrl)`);
});
