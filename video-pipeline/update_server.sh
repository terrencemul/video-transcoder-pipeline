#!/bin/bash
# Quick script to update webhook server on Vultr

echo "🔄 Updating Video Transcoder Pipeline on Vultr Server..."
echo "================================================"

# Navigate to project directory
cd /var/www/video-transcoder-pipeline/video-pipeline || exit 1

# Pull latest changes from GitHub
echo "📥 Pulling latest changes from GitHub..."
git pull origin main

# Replace webhook server with fixed version
echo "🔧 Updating webhook server..."
cp webhook-server-fixed.js webhook-server.js

# Restart PM2 process
echo "🔄 Restarting webhook server..."
pm2 restart video-webhook

# Save PM2 configuration
pm2 save

# Show status
echo ""
echo "✅ Update complete!"
echo ""
pm2 status

# Show recent logs
echo ""
echo "📋 Recent logs:"
pm2 logs video-webhook --lines 10 --nostream

echo ""
echo "🎉 Webhook server updated successfully!"
echo "Test with: curl http://66.42.87.222:3000/health"
