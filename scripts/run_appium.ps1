# ─── Start Appium server (Windows PowerShell) ────────────────────────────────
#
# Usage:
#   .\scripts\run_appium.ps1                  # default port 4723
#   .\scripts\run_appium.ps1 --port 4724
#
# Requires Node.js + appium installed globally:
#   npm install -g appium
#   appium driver install uiautomator2

if (-not (Get-Command appium -ErrorAction SilentlyContinue)) {
    Write-Error "appium not found in PATH. Install with: npm install -g appium"
    exit 1
}

appium --base-path /wd/hub @args
