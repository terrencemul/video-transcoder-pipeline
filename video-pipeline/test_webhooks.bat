@echo off
echo Video Transcoder Pipeline - Webhook Test Script
echo ===============================================
echo.

REM Check if curl is available
where curl >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: curl is not installed or not in PATH
    echo Please install curl or use Windows 10's built-in curl
    pause
    exit /b 1
)

REM Server configuration
set SERVER=http://66.42.87.222:3000

REM Test health endpoint first
echo Testing server health...
curl %SERVER%/health
echo.
echo.

REM Check if test video exists
if not exist "test-video.mp4" (
    echo ERROR: test-video.mp4 not found in current directory
    echo Please place a test video file named "test-video.mp4" in this directory
    pause
    exit /b 1
)

echo Select webhook to test:
echo 1. Short Form (9:16 - TikTok, Reels, Shorts)
echo 2. Long Form (16:9 and 9:16 - YouTube, Facebook)
echo 3. Listings (16:9 - Property Tours)
echo 4. Test All Endpoints
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto short_form
if "%choice%"=="2" goto long_form
if "%choice%"=="3" goto listings
if "%choice%"=="4" goto test_all
goto invalid_choice

:short_form
echo.
echo Testing Short Form Video Upload...
curl -X POST -F "video=@test-video.mp4" %SERVER%/webhook/video-upload/short-form
goto end

:long_form
echo.
echo Testing Long Form Video Upload...
curl -X POST -F "video=@test-video.mp4" %SERVER%/webhook/video-upload/long-form
goto end

:listings
echo.
echo Testing Listings Video Upload...
curl -X POST -F "video=@test-video.mp4" %SERVER%/webhook/video-upload/listings
goto end

:test_all
echo.
echo Testing All Endpoints...
echo.
echo 1. Short Form Upload:
curl -X POST -F "video=@test-video.mp4" %SERVER%/webhook/video-upload/short-form
echo.
echo.
echo 2. Long Form Upload:
curl -X POST -F "video=@test-video.mp4" %SERVER%/webhook/video-upload/long-form
echo.
echo.
echo 3. Listings Upload:
curl -X POST -F "video=@test-video.mp4" %SERVER%/webhook/video-upload/listings
goto end

:invalid_choice
echo Invalid choice. Please run the script again.

:end
echo.
echo.
echo Test completed!
pause
