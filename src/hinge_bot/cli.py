"""CLI entrypoint. Run hinge-bot --help for usage."""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
import urllib.error
import urllib.request

from hinge_bot.actions import like_profile, pass_profile, scroll_profile
from hinge_bot.config import load_config
from hinge_bot.driver import build_driver, detect_device_udid
from hinge_bot.utils import make_run_id, save_artifacts, setup_logging, wait_seconds

logger = logging.getLogger("hinge_bot")

_PROFILES = ["default", "avd", "memu"]


def cmd_doctor(args: argparse.Namespace) -> int:
    """Check adb, device and Appium. Exits 0 if all pass, 1 if any fail."""
    all_ok = True

    # 1. adb
    try:
        result = subprocess.run(
            ["adb", "version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        first_line = result.stdout.splitlines()[0] if result.stdout else "(no output)"
        print(f"[OK]   adb found: {first_line}")
    except FileNotFoundError:
        print("[FAIL] adb not found. Install Android SDK Platform Tools and add to PATH.")
        all_ok = False
    except Exception as exc:
        print(f"[FAIL] adb error: {exc}")
        all_ok = False

    # 2. online device
    udid = detect_device_udid()
    if udid:
        print(f"[OK]   Device online: {udid}")
    else:
        print("[FAIL] No ADB device online. Start your emulator or connect a device.")
        all_ok = False

    # 3. Appium reachability
    try:
        config = load_config(profile=args.profile)
    except FileNotFoundError as exc:
        print(f"[FAIL] Config error: {exc}")
        return 1

    status_url = config.appium_server_url.rstrip("/") + "/status"
    try:
        with urllib.request.urlopen(status_url, timeout=5):
            print(f"[OK]   Appium reachable at {config.appium_server_url}")
    except urllib.error.URLError as exc:
        print(
            f"[FAIL] Appium not reachable at {config.appium_server_url}: {exc.reason}\n"
            "       Start the server with: appium --base-path /wd/hub"
        )
        all_ok = False
    except Exception as exc:
        print(f"[FAIL] Appium check error: {exc}")
        all_ok = False

    return 0 if all_ok else 1


def cmd_run(args: argparse.Namespace) -> int:
    """Run the bot loop until Ctrl-C. With --dry-run, logs actions without clicking."""
    try:
        config = load_config(profile=args.profile, udid=args.udid)
    except FileNotFoundError as exc:
        logger.error("Config error: %s", exc)
        return 1

    run_id = make_run_id()
    logger.info(
        "Starting run. run_id=%s  profile=%s  dry_run=%s",
        run_id, args.profile, args.dry_run,
    )

    driver = build_driver(config)
    count = 0

    try:
        while True:
            scroll_profile(driver, config, dry_run=args.dry_run)

            liked = like_profile(driver, config, run_id, dry_run=args.dry_run)
            if not liked:
                pass_profile(driver, config, run_id, dry_run=args.dry_run)

            count += 1
            logger.info("Profiles processed: %d", count)
            wait_seconds(*config.wait_ranges.medium)

    except KeyboardInterrupt:
        logger.info("Stopped by user after %d profile(s).", count)
        return 0

    except Exception as exc:
        logger.exception("Unexpected error after %d profile(s): %s", count, exc)
        try:
            save_artifacts(driver, run_id, label="crash")
        except Exception:
            pass
        return 1

    finally:
        logger.info("Closing Appium session.")
        try:
            driver.quit()
        except Exception as exc:
            logger.warning("driver.quit() failed: %s", exc)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hinge-bot",
        description="Cross-platform Hinge automation bot.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  hinge-bot doctor\n"
            "  hinge-bot run --profile avd\n"
            "  hinge-bot run --profile memu --udid 127.0.0.1:21503\n"
            "  hinge-bot run --profile avd --dry-run --log-level DEBUG\n"
        ),
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        metavar="LEVEL",
        help="Logging verbosity (default: INFO)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # doctor
    doctor = subparsers.add_parser(
        "doctor",
        help="Check adb, device, and Appium connectivity",
    )
    doctor.add_argument(
        "--profile",
        default="default",
        choices=_PROFILES,
        help="Config profile to use for Appium URL check (default: default)",
    )

    # run
    run = subparsers.add_parser(
        "run",
        help="Start the bot",
    )
    run.add_argument(
        "--profile",
        default="default",
        choices=_PROFILES,
        help="Config profile (default: default)",
    )
    run.add_argument(
        "--udid",
        default=None,
        metavar="UDID",
        help="Device UDID. Overrides config and auto-detection.",
    )
    run.add_argument(
        "--dry-run",
        action="store_true",
        help="Log every action without sending any click or swipe",
    )

    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    setup_logging(args.log_level)

    dispatch = {
        "doctor": cmd_doctor,
        "run": cmd_run,
    }
    sys.exit(dispatch[args.command](args))


if __name__ == "__main__":
    main()
