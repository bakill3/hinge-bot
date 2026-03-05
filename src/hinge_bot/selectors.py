"""Centralised UI selectors with locale-aware lookup.

Adding a new language
---------------------
1. Add an entry to _REGISTRY keyed by the BCP-47 locale tag (ex: "fr-FR", "de-DE").
2. Set locale in configs/default.yaml or your profile YAML,
   or export HINGE_LOCALE=fr-FR in .env.
3. Run hinge-bot run --dry-run to verify the selectors are found.

Finding the right accessibility IDs
-------------------------------------
Open Appium Inspector (https://github.com/appium/appium-inspector) with Hinge running.
Inspect the Like, Pass and Send Like buttons and copy the content-desc attribute.
"""

from __future__ import annotations

from dataclasses import dataclass

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.by import By


@dataclass(frozen=True)
class Selector:
    """A single locator strategy + value pair."""
    strategy: str
    value: str

    def as_tuple(self) -> tuple[str, str]:
        return (self.strategy, self.value)

    def __str__(self) -> str:
        return f"({self.strategy!r}, {self.value!r})"


# Registry keyed by BCP-47 locale tag then by action name.
# Each action maps to an ordered list of Selectors tried left-to-right.
_REGISTRY: dict[str, dict[str, list[Selector]]] = {
    # Portuguese (Portugal)
    "pt-PT": {
        "like_button": [
            Selector(AppiumBy.ACCESSIBILITY_ID, "Gostar"),
            Selector(By.XPATH, "//android.widget.Button[@content-desc='Gostar']"),
        ],
        "send_like_button": [
            Selector(AppiumBy.ACCESSIBILITY_ID, "Enviar gosto"),
            Selector(By.XPATH, "//android.widget.Button[@content-desc='Enviar gosto']"),
        ],
        "pass_button": [
            Selector(
                By.XPATH,
                "//android.widget.Button[starts-with(@content-desc,'Ignorar')]",
            ),
        ],
    },
    # English (US)
    "en-US": {
        "like_button": [
            Selector(AppiumBy.ACCESSIBILITY_ID, "Like"),
            Selector(By.XPATH, "//android.widget.Button[@content-desc='Like']"),
        ],
        "send_like_button": [
            Selector(AppiumBy.ACCESSIBILITY_ID, "Send Like"),
            Selector(By.XPATH, "//android.widget.Button[@content-desc='Send Like']"),
        ],
        "pass_button": [
            Selector(
                By.XPATH,
                "//android.widget.Button[starts-with(@content-desc,'Pass')]",
            ),
            Selector(
                By.XPATH,
                "//android.widget.Button[starts-with(@content-desc,'No Thanks')]",
            ),
        ],
    },
    # Add more locales here:
    # "fr-FR": {
    #     "like_button":      [Selector(AppiumBy.ACCESSIBILITY_ID, "Aimer"), ...],
    #     "send_like_button": [Selector(AppiumBy.ACCESSIBILITY_ID, "Envoyer j'aime"), ...],
    #     "pass_button":      [Selector(By.XPATH, "//...[@content-desc='Ignorer']"), ...],
    # },
}

SUPPORTED_LOCALES: frozenset[str] = frozenset(_REGISTRY.keys())


def get_selectors(locale: str = "pt-PT") -> dict[str, list[Selector]]:
    """Return the selector map for locale. Raises ValueError if not registered."""
    if locale not in _REGISTRY:
        available = ", ".join(sorted(_REGISTRY.keys()))
        raise ValueError(
            f"Locale {locale!r} is not registered. "
            f"Available: {available}. "
            f"Add an entry to selectors.py to support it "
            f"(see the module docstring)."
        )
    return _REGISTRY[locale]
