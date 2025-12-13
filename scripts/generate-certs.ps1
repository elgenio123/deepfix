# Generate self-signed TLS certificates for development/testing
# For production, use Let's Encrypt or your organization's CA

param(
    [string]$Domain = "localhost"
)

$ErrorActionPreference = "Stop"

$CertDir = "traefik/certs"

Write-Host "Generating self-signed certificate for: $Domain" -ForegroundColor Green

# Create directory if it doesn't exist
if (-not (Test-Path $CertDir)) {
    New-Item -ItemType Directory -Path $CertDir -Force | Out-Null
}

# Generate certificate using PowerShell
$cert = New-SelfSignedCertificate `
    -DnsName $Domain, "localhost", "127.0.0.1" `
    -CertStoreLocation "Cert:\CurrentUser\My" `
    -KeyAlgorithm RSA `
    -KeyLength 2048 `
    -NotAfter (Get-Date).AddYears(1) `
    -FriendlyName "DeepFix Development Certificate" `
    -KeyUsage DigitalSignature, KeyEncipherment `
    -KeyExportPolicy Exportable

try {
    $keyPath = Join-Path $CertDir "server.key"
    $crtPath = Join-Path $CertDir "server.crt"
    
    # Export certificate to PEM format
    $certBase64 = [Convert]::ToBase64String($cert.RawData)
    $certPEM = "-----BEGIN CERTIFICATE-----`n"
    for ($i = 0; $i -lt $certBase64.Length; $i += 64) {
        $certPEM += $certBase64.Substring($i, [Math]::Min(64, $certBase64.Length - $i)) + "`n"
    }
    $certPEM += "-----END CERTIFICATE-----"
    $certPEM | Out-File -FilePath $crtPath -Encoding ASCII -NoNewline
    
    # Export private key - use PFX export method
    $securePassword = ConvertTo-SecureString -String "temp123" -Force -AsPlainText
    $pfxPath = Join-Path $CertDir "temp.pfx"
    Export-PfxCertificate -Cert $cert -FilePath $pfxPath -Password $securePassword | Out-Null
    
    # Try to use certutil or openssl to extract key
    # First, try if we have certutil with base64 encoding
    $certThumbprint = $cert.Thumbprint
    
    # Use a workaround: export as base64 and use external tool if available
    Write-Host "Attempting to extract private key..." -ForegroundColor Yellow
    
    # Check for Git Bash or WSL
    $gitBash = Get-Command "bash" -ErrorAction SilentlyContinue
    if ($gitBash) {
        # Try to use openssl via bash
        $opensslScript = @"
openssl pkcs12 -in '$pfxPath' -nodes -nocerts -out '$keyPath' -passin pass:temp123 2>&1
openssl pkcs12 -in '$pfxPath' -clcerts -nokeys -out '$crtPath' -passin pass:temp123 2>&1
"@
        $opensslScript | bash
        if (Test-Path $keyPath) {
            Remove-Item $pfxPath -Force
            Write-Host "Certificate generated successfully using OpenSSL via Git Bash/WSL!" -ForegroundColor Green
        } else {
            throw "Failed to extract key"
        }
    } else {
        # Fallback: Create a simple note and suggest manual steps
        Write-Host "OpenSSL not available. Creating certificate file only." -ForegroundColor Yellow
        Write-Host "To complete setup, you need to extract the private key manually:" -ForegroundColor Yellow
        Write-Host "1. Install OpenSSL (via Git for Windows, Chocolatey, or WSL)" -ForegroundColor Yellow
        Write-Host "2. Run: openssl pkcs12 -in $pfxPath -nodes -nocerts -out $keyPath -passin pass:temp123" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Or use the bash script: bash scripts/generate-certs.sh" -ForegroundColor Yellow
        
        # Keep the PFX for now
        Write-Host ""
        Write-Host "Certificate file created: $crtPath" -ForegroundColor Green
        Write-Host "Temporary PFX file: $pfxPath (password: temp123)" -ForegroundColor Yellow
        Write-Host "You can extract the key later using OpenSSL." -ForegroundColor Yellow
    }
    
    # Set permissions (Windows)
    if (Test-Path $keyPath) {
        icacls $keyPath /inheritance:r /grant:r "${env:USERNAME}:(R)" 2>&1 | Out-Null
    }
    icacls $crtPath /inheritance:r /grant:r "${env:USERNAME}:(R)" 2>&1 | Out-Null
    
    Write-Host ""
    Write-Host "WARNING: Self-signed certificates are for testing only." -ForegroundColor Yellow
    Write-Host "For production, use Let's Encrypt or a trusted CA."
    
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host "You may need to install OpenSSL or use WSL/Git Bash." -ForegroundColor Yellow
    exit 1
} finally {
    # Remove certificate from store
    Remove-Item "Cert:\CurrentUser\My\$($cert.Thumbprint)" -Force -ErrorAction SilentlyContinue
}
