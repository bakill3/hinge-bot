#!/usr/bin/env bash
# ─── Start Appium server (Linux / macOS) ─────────────────────────────────────
#
# Usage:
#   ./scripts/run_appium.sh            # default port 4723
#   ./scripts/run_appium.sh --port 4724
#
# Requires Node.js + appium installed globally:
#   npm install -g appium
#   appium driver install uiautomator2

set -euo pipefail

if ! command -v appium &>/dev/null; then
  echo "Error: 'appium' not found in PATH."
  echo "Install it with: npm install -g appium"
  exit 1
fi

exec appium --base-path /wd/hub "$@"
