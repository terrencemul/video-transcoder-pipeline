# Video Transcoder Pipeline - URL Webhook Test Script
# ===================================================

$server = "http://66.42.87.222:3000"

Write-Host "Video Transcoder Pipeline - URL Webhook Test Script" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
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

# Sample video URLs
$sampleUrls = @{
    "BigBuckBunny" = "https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4"
    "Custom" = ""
}

Write-Host "Select video URL option:" -ForegroundColor Cyan
Write-Host "1. Use sample video URL (Big Buck Bunny)" -ForegroundColor White
Write-Host "2. Enter custom video URL" -ForegroundColor White
Write-Host ""

$urlChoice = Read-Host "Enter your choice (1-2)"

$videoUrl = ""
switch ($urlChoice) {
    "1" { 
        $videoUrl = $sampleUrls["BigBuckBunny"]
        Write-Host "Using sample video URL: $videoUrl" -ForegroundColor Gray
    }
    "2" { 
        $videoUrl = Read-Host "Enter video URL"
        Write-Host "Using custom video URL: $videoUrl" -ForegroundColor Gray
    }
    default {
        Write-Host "Invalid choice. Using sample video URL." -ForegroundColor Yellow
        $videoUrl = $sampleUrls["BigBuckBunny"]
    }
}

Write-Host ""
Write-Host "Select webhook to test:" -ForegroundColor Cyan
Write-Host "1. Short Form (9:16 - TikTok, Reels, Shorts)" -ForegroundColor White
Write-Host "2. Long Form (16:9 and 9:16 - YouTube, Facebook)" -ForegroundColor White
Write-Host "3. Listings (16:9 - Property Tours)" -ForegroundColor White
Write-Host "4. Test All Endpoints" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter your choice (1-4)"

function Send-VideoUrl {
    param(
        [string]$endpoint,
        [string]$category,
        [string]$url
    )
    
    Write-Host "`nTesting $category Video URL..." -ForegroundColor Yellow
    
    try {
        # Create JSON body
        $body = @{
            videoUrl = $url
        } | ConvertTo-Json
        
        # Send request
        $response = Invoke-RestMethod -Uri "$server/webhook/video-upload/$endpoint" `
                                     -Method Post `
                                     -ContentType "application/json" `
                                     -Body $body
        
        Write-Host "✓ Request successful!" -ForegroundColor Green
        Write-Host "  Success: $($response.success)" -ForegroundColor Gray
        Write-Host "  Message: $($response.message)" -ForegroundColor Gray
        Write-Host "  Filename: $($response.filename)" -ForegroundColor Gray
        Write-Host "  Video URL: $($response.videoUrl)" -ForegroundColor Gray
        
        return $true
    } catch {
        Write-Host "✗ Request failed!" -ForegroundColor Red
        Write-Host "  Error: $_" -ForegroundColor Red
        
        # Try to parse error response
        try {
            $errorResponse = $_.ErrorDetails.Message | ConvertFrom-Json
            Write-Host "  Server Error: $($errorResponse.error)" -ForegroundColor Red
        } catch {}
        
        return $false
    }
}

switch ($choice) {
    "1" { 
        Send-VideoUrl -endpoint "short-form" -category "Short Form" -url $videoUrl
    }
    "2" { 
        Send-VideoUrl -endpoint "long-form" -category "Long Form" -url $videoUrl
    }
    "3" { 
        Send-VideoUrl -endpoint "listings" -category "Listings" -url $videoUrl
    }
    "4" {
        Write-Host "`nTesting All Endpoints..." -ForegroundColor Cyan
        
        $results = @()
        $results += Send-VideoUrl -endpoint "short-form" -category "Short Form" -url $videoUrl
        Start-Sleep -Seconds 2
        
        $results += Send-VideoUrl -endpoint "long-form" -category "Long Form" -url $videoUrl
        Start-Sleep -Seconds 2
        
        $results += Send-VideoUrl -endpoint "listings" -category "Listings" -url $videoUrl
        
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
Write-Host "Note: Videos are being downloaded and processed on the server." -ForegroundColor Yellow
Write-Host "Check server logs for processing status: pm2 logs video-webhook" -ForegroundColor Yellow
Read-Host "Press Enter to exit"
