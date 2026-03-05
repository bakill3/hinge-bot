"""Load config from YAML profiles merged with environment overrides."""

from __future__ import annotations

import os
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Optional

import yaml

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def _find_configs_dir() -> Path:
    # Running from source: src/hinge_bot/config.py -> ../../configs/
    candidate = Path(__file__).parent.parent.parent / "configs"
    if candidate.exists():
        return candidate

    candidate = Path.cwd() / "configs"
    if candidate.exists():
        return candidate

    raise FileNotFoundError(
        "Could not locate configs/ directory. "
        "Expected it adjacent to the project root or in the current directory."
    )


@dataclass
class Timeouts:
    implicit: int = 5       # seconds, driver-level implicit wait
    explicit: int = 10      # seconds, WebDriverWait per element
    page_load: int = 30     # seconds, Appium page-load timeout
    new_command: int = 60   # seconds, Appium new-command timeout


@dataclass
class WaitRanges:
    """Sleep ranges (seconds) between UI interactions."""
    short: tuple[float, float] = (0.5, 1.5)
    medium: tuple[float, float] = (1.5, 3.0)
    long: tuple[float, float] = (3.0, 5.0)


@dataclass
class BotConfig:
    appium_server_url: str = "http://127.0.0.1:4723"
    device_udid: Optional[str] = None
    app_package: str = "co.hinge.app"
    app_activity: str = "co.hinge.app.MainActivity"
    automation_name: str = "UiAutomator2"
    platform_name: str = "Android"
    locale: str = "pt-PT"
    timeouts: Timeouts = field(default_factory=Timeouts)
    wait_ranges: WaitRanges = field(default_factory=WaitRanges)


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge override into base without mutating either."""
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(profile: str = "default", udid: Optional[str] = None) -> BotConfig:
    """
    Build a BotConfig in priority order:
      1. configs/default.yaml
      2. configs/<profile>.yaml
      3. Environment variables (APPIUM_SERVER_URL, DEVICE_UDID, ...)
      4. --udid CLI flag
    """
    configs_dir = _find_configs_dir()

    default_path = configs_dir / "default.yaml"
    if not default_path.exists():
        raise FileNotFoundError(f"Missing required config: {default_path}")

    with default_path.open() as fh:
        data: dict = yaml.safe_load(fh) or {}

    if profile != "default":
        profile_path = configs_dir / f"{profile}.yaml"
        if not profile_path.exists():
            raise FileNotFoundError(
                f"Profile '{profile}' not found. Expected: {profile_path}"
            )
        with profile_path.open() as fh:
            profile_data: dict = yaml.safe_load(fh) or {}
        data = _deep_merge(data, profile_data)

    _ENV_MAP = {
        "APPIUM_SERVER_URL": "appium_server_url",
        "DEVICE_UDID": "device_udid",
        "APP_PACKAGE": "app_package",
        "APP_ACTIVITY": "app_activity",
        "HINGE_LOCALE": "locale",
    }
    for env_key, config_key in _ENV_MAP.items():
        env_val = os.getenv(env_key)
        if env_val is not None:
            data[config_key] = env_val

    if udid is not None:
        data["device_udid"] = udid

    timeouts_raw: dict = data.pop("timeouts", {})
    wait_ranges_raw: dict = data.pop("wait_ranges", {})

    timeouts = Timeouts(**timeouts_raw) if timeouts_raw else Timeouts()

    wait_ranges = WaitRanges(
        short=tuple(wait_ranges_raw.get("short", [0.5, 1.5])),
        medium=tuple(wait_ranges_raw.get("medium", [1.5, 3.0])),
        long=tuple(wait_ranges_raw.get("long", [3.0, 5.0])),
    ) if wait_ranges_raw else WaitRanges()

    known = {f.name for f in fields(BotConfig)} - {"timeouts", "wait_ranges"}
    filtered = {k: v for k, v in data.items() if k in known}

    return BotConfig(timeouts=timeouts, wait_ranges=wait_ranges, **filtered)
