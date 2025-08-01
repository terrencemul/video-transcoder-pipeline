# Video Transcoder Pipeline - Webhook Test Script (PowerShell)
# =============================================================

$server = "http://66.42.87.222:3000"

Write-Host "Video Transcoder Pipeline - Webhook Test Script" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Test health endpoint
Write-Host "Testing server health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$server/health" -Method Get
    Write-Host "✓ Server is healthy!" -ForegroundColor Green
    Write-Host "  Status: $($health.status)"
    Write-Host "  Message: $($health.message)"
    Write-Host ""
} catch {
    Write-Host "✗ Server is not responding!" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Red
    exit 1
}

# Check for test video
$testVideo = "test-video.mp4"
if (-not (Test-Path $testVideo)) {
    Write-Host "ERROR: $testVideo not found in current directory" -ForegroundColor Red
    Write-Host "Please place a test video file named '$testVideo' in this directory" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Menu
Write-Host "Select webhook to test:" -ForegroundColor Cyan
Write-Host "1. Short Form (9:16 - TikTok, Reels, Shorts)" -ForegroundColor White
Write-Host "2. Long Form (16:9 and 9:16 - YouTube, Facebook)" -ForegroundColor White
Write-Host "3. Listings (16:9 - Property Tours)" -ForegroundColor White
Write-Host "4. Test All Endpoints" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter your choice (1-4)"

function Upload-Video {
    param(
        [string]$endpoint,
        [string]$category
    )
    
    Write-Host "`nTesting $category Video Upload..." -ForegroundColor Yellow
    
    try {
        # Create form data
        $form = @{
            video = Get-Item -Path $testVideo
        }
        
        # Send request
        $response = Invoke-RestMethod -Uri "$server/webhook/video-upload/$endpoint" `
                                     -Method Post `
                                     -Form $form
        
        Write-Host "✓ Upload successful!" -ForegroundColor Green
        Write-Host "  Success: $($response.success)" -ForegroundColor Gray
        Write-Host "  Message: $($response.message)" -ForegroundColor Gray
        Write-Host "  Filename: $($response.filename)" -ForegroundColor Gray
        
        return $true
    } catch {
        Write-Host "✗ Upload failed!" -ForegroundColor Red
        Write-Host "  Error: $_" -ForegroundColor Red
        return $false
    }
}

switch ($choice) {
    "1" { 
        Upload-Video -endpoint "short-form" -category "Short Form"
    }
    "2" { 
        Upload-Video -endpoint "long-form" -category "Long Form"
    }
    "3" { 
        Upload-Video -endpoint "listings" -category "Listings"
    }
    "4" {
        Write-Host "`nTesting All Endpoints..." -ForegroundColor Cyan
        
        $results = @()
        $results += Upload-Video -endpoint "short-form" -category "Short Form"
        Start-Sleep -Seconds 1
        
        $results += Upload-Video -endpoint "long-form" -category "Long Form"
        Start-Sleep -Seconds 1
        
        $results += Upload-Video -endpoint "listings" -category "Listings"
        
        Write-Host "`n=== Test Summary ===" -ForegroundColor Cyan
        Write-Host "Short Form: $(if($results[0]){'✓ Passed'}else{'✗ Failed'})" -ForegroundColor $(if($results[0]){'Green'}else{'Red'})
        Write-Host "Long Form: $(if($results[1]){'✓ Passed'}else{'✗ Failed'})" -ForegroundColor $(if($results[1]){'Green'}else{'Red'})
        Write-Host "Listings: $(if($results[2]){'✓ Passed'}else{'✗ Failed'})" -ForegroundColor $(if($results[2]){'Green'}else{'Red'})
    }
    default {
        Write-Host "Invalid choice. Please run the script again." -ForegroundColor Red
    }
}

Write-Host "`nTest completed!" -ForegroundColor Green
Read-Host "Press Enter to exit"
