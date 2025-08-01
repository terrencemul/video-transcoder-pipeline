@echo off
echo ====================================
echo Video Transcoder - Quick Server Update
echo ====================================
echo.

echo This will update your Vultr server with the latest webhook fixes.
echo Server: 66.42.87.222
echo.
pause

echo.
echo Connecting to server and updating...
echo.

ssh root@66.42.87.222 "cd /var/www/video-transcoder-pipeline/video-pipeline && git pull origin main && cp webhook-server-fixed.js webhook-server.js && pm2 restart video-webhook && echo 'Update complete!' && pm2 status"

echo.
echo ====================================
echo Update finished!
echo ====================================
echo.
echo Test the server with:
echo curl http://66.42.87.222:3000/health
echo.
pause
