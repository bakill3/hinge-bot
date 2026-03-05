# Hinge Bot V2

Cross-platform Hinge automation bot built with Appium and Python.
Runs on Linux, macOS and Windows.

[![Hinge Bot — Automate Your Swipes with Appium + Python](https://img.youtube.com/vi/JE7tnCJB74g/0.jpg)](https://www.youtube.com/watch?v=JE7tnCJB74g)

---

## Disclaimer

This project was built for **educational purposes** to demonstrate mobile UI automation with Appium and Python.

- Works for all genders and orientations, no assumptions are made about who you are or who you are looking for.
- No data is collected, stored or sent anywhere. Everything runs locally on your machine.
- Use it responsibly and in line with [Hinge's Terms of Service](https://hinge.co/terms).
- The author is not responsible for any account restrictions that may result from use.

---

## Project structure

```
hinge-bot/
├── src/hinge_bot/
│   ├── __init__.py
│   ├── __main__.py      # python -m hinge_bot
│   ├── cli.py           # argument parsing + subcommands
│   ├── config.py        # YAML + env config loading
│   ├── driver.py        # Appium driver factory + ADB detection
│   ├── selectors.py     # all locators in one place (locale-aware)
│   ├── actions.py       # like / pass / scroll
│   └── utils.py         # logging, waits, artifact capture
├── configs/
│   ├── default.yaml     # base values
│   ├── avd.yaml         # Android Studio AVD (Linux / macOS / Windows)
│   └── memu.yaml        # MEmu emulator (Windows)
├── scripts/
│   ├── run_appium.sh    # start Appium (Linux / macOS)
│   └── run_appium.ps1   # start Appium (Windows PowerShell)
├── artifacts/           # screenshots + page-source dumps (gitignored)
├── pyproject.toml
├── .env.example
└── .gitignore
```

---

## Prerequisites

| Tool | Where to get it |
|---|---|
| Python 3.10+ | <https://python.org/downloads/> |
| Node.js LTS | <https://nodejs.org/> |
| Android SDK Platform Tools (`adb`) | Android Studio SDK Manager **or** [standalone download](https://developer.android.com/tools/releases/platform-tools) |
| Appium 2.x | `npm install -g appium` |
| UiAutomator2 driver | `appium driver install uiautomator2` |

---

## Setup — Linux (Android Studio AVD)

### 1. Install Android Studio and create an AVD

1. Download [Android Studio](https://developer.android.com/studio).
2. Open **Device Manager** → **Create Virtual Device**.
3. Pick a phone profile (ex: Pixel 6), select an API 30+ system image, finish.
4. Start the emulator. Verify it appears in `adb`:

   ```bash
   adb devices
   # emulator-5554   device
   ```

5. Install Hinge from the Play Store inside the emulator and log in.

### 2. Clone and install the bot

```bash
git clone https://github.com/bakill3/hinge-bot.git
cd hinge-bot
python3 -m venv .venv
```

Activate the venv, pick the line for your shell:

```bash
source .venv/bin/activate        # bash / zsh
source .venv/bin/activate.fish   # fish
```

```bash
pip install -e .
```

### 3. Start Appium

```bash
./scripts/run_appium.sh
# or: appium --base-path /wd/hub
```

Keep this terminal open.

### 4. Verify everything works

```bash
hinge-bot doctor --profile avd
# [OK]   adb found: ...
# [OK]   Device online: emulator-5554
# [OK]   Appium reachable at http://127.0.0.1:4723
```

### 5. Run

```bash
hinge-bot run --profile avd
```

---

## Setup — Windows (MEmu)

### 1. Install MEmu

1. Download and install [MEmu](https://www.memuplay.com/).
2. Open MEmu settings → **Others** → enable **ADB**.
3. Start MEmu, install Hinge, log in.
4. Connect ADB:

   ```powershell
   adb connect 127.0.0.1:21503
   adb devices
   # 127.0.0.1:21503   device
   ```

### 2. Clone and install the bot

```powershell
git clone https://github.com/bakill3/hinge-bot.git
cd hinge-bot
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
```

### 3. Start Appium

```powershell
.\scripts\run_appium.ps1
```

### 4. Verify and run

```powershell
hinge-bot doctor --profile memu
hinge-bot run --profile memu
```

---

## Configuration

### Profiles

Edit the YAML files in `configs/` to change Appium server URL, timeouts, wait ranges, and locale.

| Profile | File | Use when |
|---|---|---|
| `default` | `configs/default.yaml` | base values, good starting point |
| `avd` | `configs/avd.yaml` | Android Studio emulator |
| `memu` | `configs/memu.yaml` | MEmu on Windows |

### Environment overrides

Copy `.env.example` to `.env` and uncomment lines you want to override:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|---|---|---|
| `APPIUM_SERVER_URL` | `http://127.0.0.1:4723` | Appium server URL |
| `DEVICE_UDID` | *(auto-detect)* | ADB device UDID |
| `APP_PACKAGE` | `co.hinge.app` | Target app package |
| `APP_ACTIVITY` | `co.hinge.app.MainActivity` | Launcher activity |
| `HINGE_LOCALE` | `pt-PT` | UI locale for selector resolution |

### Locale / selectors

Selectors are locale-aware. The bot looks up UI button labels for the configured locale.
Two locales are included out of the box:

| Locale | Language |
|---|---|
| `pt-PT` | Portuguese (Portugal), default |
| `en-US` | English (US) |

To switch locale:

```bash
# .env
HINGE_LOCALE=en-US
```

**Adding a new language:** open [src/hinge_bot/selectors.py](src/hinge_bot/selectors.py) and follow the module docstring. Short version:

1. Add an entry to `_REGISTRY` keyed by the BCP-47 locale tag (ex: `"fr-FR"`).
2. Use [Appium Inspector](https://github.com/appium/appium-inspector) to find the `content-desc` of the Like, Pass, and Send Like buttons on your device.
3. Set `HINGE_LOCALE=fr-FR` in `.env` (or in your profile YAML).
4. Run `hinge-bot run --dry-run` to confirm the selectors are found.

---

## CLI reference

```
hinge-bot doctor [--profile default|avd|memu]
hinge-bot run    [--profile default|avd|memu]
                 [--udid <UDID>]
                 [--dry-run]
                 [--log-level DEBUG|INFO|WARNING|ERROR]
```

**`doctor`**: checks adb, device and Appium connectivity before committing to a run.

**`run`**: starts the bot loop.
- `--dry-run` logs every action without clicking or swiping. Useful for verifying selector coverage against a real device.
- `--udid` takes precedence over the profile YAML and environment variables.

Also works as a module:

```bash
python -m hinge_bot run --profile avd --dry-run
```

---

## Debugging

Failed element lookups automatically save a screenshot and page-source XML to
`artifacts/<run-id>/`. To inspect selectors interactively, use
[Appium Inspector](https://github.com/appium/appium-inspector).

To see every selector attempt:

```bash
hinge-bot run --profile avd --log-level DEBUG
```

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `adb not found` | SDK Platform Tools missing | Install via Android Studio SDK Manager or download standalone |
| `No online ADB devices` | Emulator not running / ADB not enabled | Start emulator; on MEmu enable ADB in settings and `adb connect …` |
| `Appium not reachable` | Appium server not started | Run `appium --base-path /wd/hub` in a separate terminal |
| `Like button not found` | Hinge UI changed or wrong locale | Open `artifacts/` for a screenshot; update selectors in `selectors.py` |
| Session hangs silently | `new_command_timeout` too low | Increase `timeouts.new_command` in your profile YAML |

---

## Contributing

PRs and feature requests are welcome!

---

## License

MIT
