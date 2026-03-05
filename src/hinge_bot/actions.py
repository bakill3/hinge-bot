"""High-level bot actions: scroll, like, pass."""

from __future__ import annotations

import logging

from appium.webdriver.webdriver import WebDriver

from hinge_bot.config import BotConfig
from hinge_bot.selectors import get_selectors
from hinge_bot.utils import find_element_with_fallbacks, save_artifacts, wait_seconds

logger = logging.getLogger("hinge_bot")


def scroll_profile(driver: WebDriver, config: BotConfig, dry_run: bool = False) -> None:
    """Scroll down to reveal more of the current profile card."""
    if dry_run:
        logger.info("[dry-run] Would scroll profile.")
        return

    size = driver.get_window_size()
    start_y = int(size["height"] * 0.75)
    end_y = int(size["height"] * 0.35)
    x = int(size["width"] * 0.5)
    driver.swipe(x, start_y, x, end_y, duration=600)
    wait_seconds(*config.wait_ranges.short)
    logger.debug("Scrolled profile.")


def like_profile(
    driver: WebDriver,
    config: BotConfig,
    run_id: str,
    dry_run: bool = False,
) -> bool:
    """Click Like then confirm Send Like if it appears. Returns False if Like button missing."""
    selectors = get_selectors(config.locale)

    like_el = find_element_with_fallbacks(
        driver,
        selectors["like_button"],
        timeout=config.timeouts.explicit,
    )

    if like_el is None:
        logger.warning("Like button not found. Saving debug artifacts.")
        save_artifacts(driver, run_id, label="like_button_missing")
        return False

    if dry_run:
        logger.info("[dry-run] Would click Like.")
        return True

    like_el.click()
    logger.info("Liked profile.")
    wait_seconds(*config.wait_ranges.short)

    # "Send Like" is optional, use a shorter timeout
    confirm_timeout = max(config.timeouts.explicit // 2, 3)
    send_el = find_element_with_fallbacks(
        driver,
        selectors["send_like_button"],
        timeout=confirm_timeout,
    )
    if send_el is not None:
        send_el.click()
        logger.info("Send Like confirmed.")
        wait_seconds(*config.wait_ranges.short)
    else:
        logger.debug("No Send Like confirmation required.")

    return True


def pass_profile(
    driver: WebDriver,
    config: BotConfig,
    run_id: str,
    dry_run: bool = False,
) -> bool:
    """Click Pass. Falls back to swipe left if button not found. Returns False on fallback."""
    selectors = get_selectors(config.locale)

    pass_el = find_element_with_fallbacks(
        driver,
        selectors["pass_button"],
        timeout=config.timeouts.explicit,
    )

    if pass_el is None:
        logger.warning("Pass button not found. Saving debug artifacts and swiping left.")
        save_artifacts(driver, run_id, label="pass_button_missing")
        if not dry_run:
            _swipe_left(driver)
        else:
            logger.info("[dry-run] Would swipe left.")
        return False

    if dry_run:
        logger.info("[dry-run] Would click Pass.")
        return True

    pass_el.click()
    logger.info("Passed profile.")
    wait_seconds(*config.wait_ranges.short)
    return True


def _swipe_left(driver: WebDriver) -> None:
    size = driver.get_window_size()
    start_x = int(size["width"] * 0.8)
    end_x = int(size["width"] * 0.2)
    y = int(size["height"] * 0.5)
    driver.swipe(start_x, y, end_x, y, duration=500)
    logger.debug("Swiped left.")
