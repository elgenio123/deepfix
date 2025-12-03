# DeepFix Production Deployment Verification Script
# This script verifies that all services are running correctly

param(
    [switch]$Detailed
)

Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   DeepFix Production Deployment Verification              ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$allHealthy = $true

# Function to check service status
function Test-Service {
    param(
        [string]$ServiceName,
        [string]$ContainerName,
        [string]$ExpectedStatus = "healthy"
    )
    
    try {
        $status = docker inspect $ContainerName --format='{{.State.Status}}' 2>$null
        $health = docker inspect $ContainerName --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}N/A{{end}}' 2>$null
        
        if ($status -eq "running") {
            if ($health -eq "N/A" -or $health -eq "healthy") {
                Write-Host "✅ $ServiceName" -ForegroundColor Green -NoNewline
                Write-Host " - Status: $status" -ForegroundColor Gray
                if ($health -ne "N/A") {
                    Write-Host "   Health: $health" -ForegroundColor DarkGray
                }
                return $true
            } elseif ($health -eq "starting") {
                Write-Host "⏳ $ServiceName" -ForegroundColor Yellow -NoNewline
                Write-Host " - Status: $status, Health: $health (still starting...)" -ForegroundColor Gray
                return $true
            } else {
                Write-Host "❌ $ServiceName" -ForegroundColor Red -NoNewline
                Write-Host " - Status: $status, Health: $health" -ForegroundColor Gray
                $script:allHealthy = $false
                return $false
            }
        } else {
            Write-Host "❌ $ServiceName" -ForegroundColor Red -NoNewline
            Write-Host " - Status: $status (not running)" -ForegroundColor Gray
            $script:allHealthy = $false
            return $false
        }
    } catch {
        Write-Host "❌ $ServiceName" -ForegroundColor Red -NoNewline
        Write-Host " - Container not found" -ForegroundColor Gray
        $script:allHealthy = $false
        return $false
    }
}

# Check all services
Write-Host "📋 Service Status Check`n" -ForegroundColor Yellow

Test-Service "DeepFix Server" "deepfix-server" | Out-Null
Test-Service "Traefik (Reverse Proxy)" "traefik" | Out-Null
Test-Service "MLflow" "mlflow" | Out-Null
Test-Service "Grafana" "grafana" | Out-Null
Test-Service "Prometheus" "prometheus" | Out-Null
Test-Service "Loki" "loki" | Out-Null
Test-Service "Promtail" "promtail" | Out-Null

Write-Host ""

# Check ports
Write-Host "🌐 Port Status Check`n" -ForegroundColor Yellow

$ports = @(80, 443)
foreach ($port in $ports) {
    try {
        $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Any, $port)
        $listener.Start()
        $listener.Stop()
        Write-Host "❌ Port $port - Not in use (Traefik might not be binding correctly)" -ForegroundColor Red
        $script:allHealthy = $false
    } catch {
        Write-Host "✅ Port $port - In use by Traefik" -ForegroundColor Green
    }
}

Write-Host ""

# Check certificates
Write-Host "🔐 TLS Certificate Check`n" -ForegroundColor Yellow

if (Test-Path "traefik/certs/server.crt" -and Test-Path "traefik/certs/server.key") {
    Write-Host "✅ TLS certificates found" -ForegroundColor Green
    
    if ($Detailed) {
        $certInfo = docker run --rm -v ${PWD}/traefik/certs:/certs alpine/openssl x509 -in /certs/server.crt -noout -subject -dates 2>$null
        Write-Host "   $certInfo" -ForegroundColor DarkGray
    }
} else {
    Write-Host "❌ TLS certificates missing" -ForegroundColor Red
    $script:allHealthy = $false
}

Write-Host ""

# Check volumes
Write-Host "💾 Data Volume Check`n" -ForegroundColor Yellow

$volumes = @("server_logs", "server_mlflow_data")
foreach ($vol in $volumes) {
    if (Test-Path $vol) {
        $size = (Get-ChildItem $vol -Recurse -File | Measure-Object -Property Length -Sum).Sum
        $sizeStr = if ($size -gt 1GB) { "{0:N2} GB" -f ($size / 1GB) } 
                   elseif ($size -gt 1MB) { "{0:N2} MB" -f ($size / 1MB) }
                   elseif ($size -gt 1KB) { "{0:N2} KB" -f ($size / 1KB) }
                   else { "$size bytes" }
        Write-Host "✅ $vol" -ForegroundColor Green -NoNewline
        Write-Host " - Size: $sizeStr" -ForegroundColor Gray
    } else {
        Write-Host "⚠️  $vol" -ForegroundColor Yellow -NoNewline
        Write-Host " - Directory not found (will be created on first use)" -ForegroundColor Gray
    }
}

Write-Host ""

# Network test
Write-Host "🔗 Internal Network Check`n" -ForegroundColor Yellow

try {
    $networkTest = docker compose -f docker-compose.prod.yml exec -T deepfix-server python -c "import socket; s=socket.socket(); s.settimeout(2); s.connect(('mlflow', 5000)); s.close(); print('OK')" 2>$null
    if ($networkTest -match "OK") {
        Write-Host "✅ DeepFix can reach MLflow" -ForegroundColor Green
    } else {
        Write-Host "❌ DeepFix cannot reach MLflow" -ForegroundColor Red
        $script:allHealthy = $false
    }
} catch {
    Write-Host "❌ Network connectivity test failed" -ForegroundColor Red
    $script:allHealthy = $false
}

Write-Host ""

# Final summary
Write-Host "═══════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

if ($allHealthy) {
    Write-Host "✅ All checks passed! Your deployment is healthy.`n" -ForegroundColor Green
    
    Write-Host "🌐 Access your services:" -ForegroundColor Cyan
    Write-Host "   • DeepFix API:  https://localhost/" -ForegroundColor White
    Write-Host "   • MLflow:       https://localhost/mlflow" -ForegroundColor White
    Write-Host "   • Grafana:      https://localhost/grafana (admin/admin)" -ForegroundColor White
    Write-Host "   • Traefik:      https://localhost/dashboard (admin/admin)" -ForegroundColor White
    Write-Host ""
    Write-Host "⚠️  You'll see a certificate warning (self-signed cert). Click Advanced and Proceed to localhost" -ForegroundColor Yellow
    Write-Host ""
    
    exit 0
} else {
    Write-Host "❌ Some checks failed. Please review the output above." -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Troubleshooting tips:" -ForegroundColor Yellow
    Write-Host "   • Check logs: docker compose -f docker-compose.prod.yml logs" -ForegroundColor White
    Write-Host "   • Restart services: docker compose -f docker-compose.prod.yml restart" -ForegroundColor White
    Write-Host "   • View detailed status: docker compose -f docker-compose.prod.yml ps" -ForegroundColor White
    Write-Host ""
    
    exit 1
}

