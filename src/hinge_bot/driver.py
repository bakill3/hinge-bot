"""Appium driver factory: capability builder + ADB device detection."""

from __future__ import annotations

import logging
import subprocess
import sys
from typing import Optional

from appium import webdriver
from appium.options.android import UiAutomator2Options

from hinge_bot.config import BotConfig

logger = logging.getLogger("hinge_bot")


def detect_device_udid() -> Optional[str]:
    """Run adb devices and return the UDID of the first online device. Returns None on failure."""
    try:
        result = subprocess.run(
            ["adb", "devices"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except FileNotFoundError:
        logger.error(
            "'adb' not found in PATH. "
            "Install Android SDK Platform Tools and make sure adb is on your PATH."
        )
        return None
    except subprocess.TimeoutExpired:
        logger.error("'adb devices' timed out after 10 seconds.")
        return None

    online = [
        line.split("\t")[0].strip()
        for line in result.stdout.splitlines()[1:]  # skip header
        if line.strip().endswith("\tdevice")
    ]

    if not online:
        logger.error(
            "No online ADB devices found.\n"
            "adb devices output:\n%s\n"
            "Make sure your emulator or device is running and recognised by ADB.\n"
            "Try: adb devices",
            result.stdout.strip(),
        )
        return None

    if len(online) > 1:
        logger.warning(
            "Multiple devices online: %s. Using first: %s. Pass --udid to pick one.",
            online,
            online[0],
        )

    logger.debug("Detected device UDID: %s", online[0])
    return online[0]


def build_driver(config: BotConfig) -> webdriver.Remote:
    """Resolve device UDID, build capabilities and return an active driver. Exits 1 if no device."""
    udid = config.device_udid or detect_device_udid()
    if not udid:
        logger.error(
            "No device UDID available. "
            "Set DEVICE_UDID in .env, add device_udid to your profile YAML, "
            "or pass --udid on the command line."
        )
        sys.exit(1)

    logger.info("Targeting device: %s", udid)

    options = UiAutomator2Options()
    options.platform_name = config.platform_name
    options.device_name = udid
    options.udid = udid
    options.app_package = config.app_package
    options.app_activity = config.app_activity
    options.automation_name = config.automation_name
    options.no_reset = True
    options.new_command_timeout = config.timeouts.new_command

    logger.info("Connecting to Appium at %s", config.appium_server_url)
    try:
        driver = webdriver.Remote(
            command_executor=config.appium_server_url,
            options=options,
        )
    except Exception as exc:
        logger.error(
            "Failed to start Appium session: %s\n"
            "Is the Appium server running? Try: appium --base-path /wd/hub",
            exc,
        )
        raise

    driver.implicitly_wait(config.timeouts.implicit)
    logger.info("Session started. session_id=%s", driver.session_id)
    return driver
