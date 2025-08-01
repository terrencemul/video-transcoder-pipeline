const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');
const https = require('https');
const http = require('http');
const { URL } = require('url');

const app = express();

// Middleware for JSON parsing
app.use(express.json());

// Configure multer for file uploads (keeping backward compatibility)
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

// Helper function to download video from URL with redirect support
function downloadVideo(videoUrl, destination, redirectCount = 0) {
  return new Promise((resolve, reject) => {
    if (redirectCount > 5) {
      reject(new Error('Too many redirects'));
      return;
    }

    try {
      const url = new URL(videoUrl);
      const protocol = url.protocol === 'https:' ? https : http;
      
      const file = fs.createWriteStream(destination);
      
      const request = protocol.get(videoUrl, (response) => {
        // Handle redirects (301, 302, 303, 307, 308)
        if (response.statusCode >= 300 && response.statusCode < 400 && response.headers.location) {
          // Clean up the file stream
          file.close();
          fs.unlink(destination, () => {});
          
          // Follow the redirect
          const redirectUrl = response.headers.location;
          console.log(`↪️  Following redirect to: ${redirectUrl}`);
          
          // Resolve relative URLs
          const newUrl = redirectUrl.startsWith('http') 
            ? redirectUrl 
            : new URL(redirectUrl, videoUrl).toString();
          
          // Recursively download from the new URL
          return downloadVideo(newUrl, destination, redirectCount + 1)
            .then(resolve)
            .catch(reject);
        }
        
        // Check for successful response
        if (response.statusCode !== 200) {
          file.close();
          fs.unlink(destination, () => {});
          reject(new Error(`Failed to download: ${response.statusCode}`));
          return;
        }
        
        // Pipe the response to the file
        response.pipe(file);
        
        file.on('finish', () => {
          file.close();
          console.log(`✅ Download complete: ${path.basename(destination)}`);
          resolve(destination);
        });
        
        file.on('error', (err) => {
          fs.unlink(destination, () => {});
          reject(err);
        });
      });
      
      request.on('error', (err) => {
        file.close();
        fs.unlink(destination, () => {}); // Delete the file on error
        reject(err);
      });
      
      request.setTimeout(60000, () => { // Increased to 60 seconds for large videos
        request.destroy();
        file.close();
        fs.unlink(destination, () => {});
        reject(new Error('Download timeout'));
      });
      
    } catch (error) {
      reject(error);
    }
  });
}

// Helper function to get filename from URL or generate one
function getFilenameFromUrl(videoUrl) {
  try {
    const url = new URL(videoUrl);
    const pathname = url.pathname;
    let filename = path.basename(pathname);
    
    // Clean up filename - remove query parameters
    filename = filename.split('?')[0];
    
    // Check for common video extensions
    const videoExtensions = ['.mp4', '.mov', '.avi', '.webm', '.mkv', '.flv', '.wmv'];
    const hasVideoExtension = videoExtensions.some(ext => filename.toLowerCase().endsWith(ext));
    
    // If no filename or no video extension, generate one
    if (!filename || !hasVideoExtension) {
      // Try to extract from query parameters (some services use ?filename=video.mp4)
      const urlParams = new URLSearchParams(url.search);
      const paramFilename = urlParams.get('filename') || urlParams.get('file') || urlParams.get('name');
      
      if (paramFilename && videoExtensions.some(ext => paramFilename.toLowerCase().endsWith(ext))) {
        filename = paramFilename;
      } else {
        filename = 'video.mp4';
      }
    }
    
    // Sanitize filename - remove special characters
    filename = filename.replace(/[^a-zA-Z0-9._-]/g, '_');
    
    return `${Date.now()}_${filename}`;
  } catch (error) {
    return `${Date.now()}_video.mp4`;
  }
}

// Process video from URL
async function processVideoFromUrl(req, res, category) {
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
    console.log(`⬇️  Downloading video from: ${videoUrl}`);
    console.log(`📁 Saving to: ${downloadPath}`);
    
    try {
      await downloadVideo(videoUrl, downloadPath);
      console.log(`✅ Video downloaded successfully`);
      
      // Verify file exists and has size
      const stats = fs.statSync(downloadPath);
      console.log(`📊 File size: ${(stats.size / 1024 / 1024).toFixed(2)} MB`);
    } catch (downloadError) {
      console.error(`❌ Download failed: ${downloadError.message}`);
      throw downloadError;
    }
    
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

// Process uploaded video file
function processVideoFromUpload(req, res, category) {
  if (!req.file) {
    return res.status(400).json({
      success: false,
      error: 'No video file uploaded'
    });
  }
  
  console.log(`✅ ${category} video uploaded:`, req.file.filename);
  
  // Trigger Python transcoder
  const pythonProcess = spawn('python3', ['main.py', '--input', req.file.path]);
  
  pythonProcess.stdout.on('data', (data) => {
    console.log(`Transcoder: ${data}`);
  });
  
  pythonProcess.stderr.on('data', (data) => {
    console.error(`Transcoder Error: ${data}`);
  });
  
  res.json({ 
    success: true, 
    message: `${category} video uploaded and processing started`,
    filename: req.file.filename
  });
}

// Webhook endpoints - handle both URL and file upload
app.post('/webhook/video-upload/short-form', upload.single('video'), async (req, res) => {
  // Check if it's a URL submission or file upload
  if (req.body.videoUrl) {
    await processVideoFromUrl(req, res, 'short_form_9_16');
  } else {
    processVideoFromUpload(req, res, 'Short form');
  }
});

app.post('/webhook/video-upload/long-form', upload.single('video'), async (req, res) => {
  if (req.body.videoUrl) {
    await processVideoFromUrl(req, res, 'long_form_16_9_or_9_16');
  } else {
    processVideoFromUpload(req, res, 'Long form');
  }
});

app.post('/webhook/video-upload/listings', upload.single('video'), async (req, res) => {
  if (req.body.videoUrl) {
    await processVideoFromUrl(req, res, 'listings_16_9');
  } else {
    processVideoFromUpload(req, res, 'Listings');
  }
});

// Health check
app.get('/health', (req, res) => {
  res.json({ 
    status: 'OK', 
    message: 'Video transcoder webhook server running (URL + Upload mode)',
    server: '66.42.87.222',
    modes: ['url-download', 'file-upload']
  });
});

// Error handling middleware
app.use((error, req, res, next) => {
  if (error instanceof multer.MulterError) {
    if (error.code === 'LIMIT_FILE_SIZE') {
      return res.status(400).json({
        success: false,
        error: 'File too large. Maximum size is 500MB.'
      });
    }
  }
  console.error('Server error:', error);
  res.status(500).json({
    success: false,
    error: 'Internal server error'
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 Video transcoder webhook server running on 66.42.87.222:${PORT}`);
  console.log(`📡 Modes: URL Download (JSON) + File Upload (multipart/form-data)`);
  console.log(`✅ Ready to receive videos!`);
});
