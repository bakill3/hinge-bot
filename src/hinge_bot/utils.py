"""Shared utilities: logging setup, waits, element finding, artifact capture."""

from __future__ import annotations

import logging
import random
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

if False:  # TYPE_CHECKING, avoids circular import
    from appium.webdriver.webdriver import WebDriver
    from hinge_bot.selectors import Selector

logger = logging.getLogger("hinge_bot")


def setup_logging(level: str = "INFO") -> None:
    """Configure root logger with timestamps and log level."""
    log_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )


def make_run_id() -> str:
    """Generate a unique run identifier for artifact directories."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_id = uuid.uuid4().hex[:6]
    return f"{ts}_{short_id}"


def artifacts_dir() -> Path:
    """Return (and create) the per-session artifacts directory."""
    return Path.cwd() / "artifacts"


def save_artifacts(driver: "WebDriver", run_id: str, label: str = "error") -> None:
    """Save screenshot and page-source XML to artifacts/<run_id>/. Never raises."""
    run_dir = artifacts_dir() / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%H%M%S")

    screenshot_path = run_dir / f"{label}_{ts}.png"
    try:
        driver.save_screenshot(str(screenshot_path))
        logger.info("Screenshot saved: %s", screenshot_path)
    except WebDriverException as exc:
        logger.warning("Could not capture screenshot: %s", exc)

    source_path = run_dir / f"{label}_{ts}.xml"
    try:
        source_path.write_text(driver.page_source, encoding="utf-8")
        logger.info("Page source saved: %s", source_path)
    except WebDriverException as exc:
        logger.warning("Could not capture page source: %s", exc)


def find_element_with_fallbacks(
    driver: "WebDriver",
    selectors: list["Selector"],
    timeout: int = 10,
) -> Optional[WebElement]:
    """Try each Selector in order. Returns first clickable match or None."""
    for sel in selectors:
        logger.debug("Trying selector %s", sel)
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable(sel.as_tuple())
            )
            logger.debug("Found with %s", sel)
            return element
        except TimeoutException:
            logger.debug("Timed out with %s", sel)
        except StaleElementReferenceException:
            logger.debug("Stale element with %s", sel)
        except WebDriverException as exc:
            logger.debug("WebDriver error with %s: %s", sel, exc)

    logger.debug("No selector matched. Tried: %s", [str(s) for s in selectors])
    return None


def wait_seconds(low: float, high: float) -> None:
    """Sleep for a random duration in [low, high] seconds."""
    duration = random.uniform(low, high)
    logger.debug("Waiting %.2fs", duration)
    time.sleep(duration)
