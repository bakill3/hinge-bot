# Hinge Appium Bot 🤖

A fully-automated liking/swiping bot for Hinge, using Appium, Python, and Android emulation (MEmu).  
This project demonstrates anti-ban tactics, custom swipes, and robust automation.

---

## Features

- Automated 'like' and 'ignore' actions on Hinge profiles
- Random swiping and delays for anti-ban
- Easily customizable for future AI integration (e.g. using ChatGPT)

[![Hinge Bot for Windows! - Automate Your Swipes with Appium + Python](https://img.youtube.com/vi/JE7tnCJB74g/0.jpg)](https://www.youtube.com/watch?v=JE7tnCJB74g)

---

## Requirements

- **Windows 10/11**
- [Python 3.8+](https://www.python.org/downloads/)
- [Node.js (LTS)](https://nodejs.org/)
- [MEmu Android Emulator](https://www.memuplay.com/) (or similar)
- [Appium Server](https://appium.io/) (installed via npm)

---

## Quickstart

1. **Clone this repo**
    ```bash
    git clone https://github.com/yourusername/hinge-bot.git
    cd hinge-bot
    ```

2. **Install Python dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3. **Install Appium server**
    ```bash
    npm install -g appium
    ```

4. **Download & set up MEmu**  
    - Install [MEmu](https://www.memuplay.com/)
    - Set up Google Play, install Hinge, log in.

5. **Enable ADB in MEmu**
    - Go to MEmu settings → Others → Enable ADB
    - Make sure you can run:
      ```bash
      adb connect 127.0.0.1:21503
      ```

6. **Start the Appium server** (keep this terminal open)
    ```bash
    appium --base-path /wd/hub
    ```

7. **Run the bot**
    ```bash
    python main.py
    ```

---

## Customization

- All actions and timings are in `main.py`.
- You can add your own anti-ban tactics, delays, or future AI integrations!

---

## Troubleshooting

- **Appium not found:**  
  Double-check Node.js and npm are installed.  
  Try: `npm install -g appium`
- **Device not found:**  
  Make sure ADB is enabled and emulator is running.  
  Run: `adb devices` to verify.
- **Button not found errors:**  
  UI changes frequently, use Appium Inspector to update selectors.

---

## Contributing

PRs and feature requests are welcome!

---

## License

MIT
