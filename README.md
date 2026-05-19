# JARVIS — AI Productivity Assistant

<p align="center">
  <img src="assets/banner.png" alt="JARVIS" width="600"/>
</p>

<p align="center">
  <strong>Voice-controlled AI assistant for Android & PC</strong><br>
  Open apps • Generate images • Research topics • Control devices • Chat with LLM
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Android-34-green?logo=android" alt="Android">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Flask-2.3+-lightgrey?logo=flask" alt="Flask">
  <img src="https://img.shields.io/badge/Groq-LLM-orange?logo=groq" alt="Groq">
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License">
</p>

---

## Overview

JARVIS is a **voice-controlled AI productivity assistant** that runs on both Android (via a WebView APK) and PC (via a web browser). It uses **Groq LLM** for natural language understanding and routes commands to specialized agents for tasks, research, image generation, coding, and more.

The backend runs as a Flask server (on your device via Termux or on a PC) and serves a **solar-system-themed web UI**. The Android APK wraps this UI in a WebView with a Kotlin-to-JavaScript bridge for native device control (WiFi, Bluetooth, flashlight, app launching, etc.).

---

## Features

### 🎯 Task Automation
- Open/close apps (YouTube, Chrome, WhatsApp, Telegram, Spotify, etc.)
- Control volume, brightness, WiFi, Bluetooth
- Take screenshots, photos, open gallery/files
- Send SMS, read notifications, check call logs
- Get battery status, system info, time, weather, news
- Control media playback, share content, set wallpaper
- Get GPS location, WiFi connection info

### 🧠 Multi-Agent AI
| Agent | Description |
|-------|-------------|
| **Chat** | General conversation, advice, questions |
| **Task** | Device/app control, system operations |
| **Research** | Deep multi-source information gathering |
| **Search** | Quick facts, news, weather, real-time data |
| **Coding** | Write, debug, explain, refactor code |
| **Image** | Generate images via SeaArt AI |
| **Reasoning** | Math, planning, pros/cons, analysis |

### 🎨 Features
- Voice input via Web Speech API (browser) or Termux STT (Android)
- Text-to-speech responses (Android TTS or browser SpeechSynthesis)
- Real-time solar system animated background
- Image generation with prompt enhancement
- Auto-skill learning (remembers successful command patterns)
- Knowledge base with search
- Chat history and session management

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Android Device                     │
│                                                       │
│  ┌──────────────────┐      ┌──────────────────────┐  │
│  │   Android APK     │      │   Termux (or PC)     │  │
│  │   (WebView)       │◄────►│   Flask Backend      │  │
│  │                   │ HTTP │   :8001              │  │
│  │  ┌─────────────┐  │      │                      │  │
│  │  │ Web UI      │  │      │  ┌────────────────┐  │  │
│  │  │ index.html  │  │      │  │  Orchestrator  │  │  │
│  │  │ script.js   │  │      │  │  (router)      │  │  │
│  │  └──────┬──────┘  │      │  └───────┬────────┘  │  │
│  │         │         │      │          │           │  │
│  │  ┌──────┴──────┐  │      │  ┌───────┴────────┐  │  │
│  │  │JarvisBridge │  │      │  │  Chat  Task     │  │  │
│  │  │ (Kotlin/JS) │  │      │  │  Image Research │  │  │
│  │  │ openApp()   │  │      │  │  Coding Search  │  │  │
│  │  │ wifi()      │  │      │  │  Reasoning      │  │  │
│  │  │ speak()     │  │      │  └────────────────┘  │  │
│  │  └─────────────┘  │      │                      │  │
│  └──────────────────┘      └──────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### How Commands Flow
1. **Voice/Text Input** → Captured by Web UI (Speech API) or typed
2. **HTTP POST `/chat`** → Sent to Flask backend
3. **Orchestrator** → Classifies intent (keyword + LLM routing)
4. **Specialized Agent** → Executes the task
5. **Response** → Returned as JSON with reply text + metadata
6. **Android Bridge** → Frontend calls Kotlin methods for device actions
7. **TTS** → Response spoken aloud via Android TTS

---

## Quick Start

### Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.10+ |
| Groq API Key | [Get one free](https://console.groq.com) |
| Android SDK (for APK build) | 34+ (platform android-36) |
| JDK (for APK build) | 17+ |
| Termux (Android backend) | Latest from F-Droid |

### 1️⃣ Get a Groq API Key

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up and create an API key
3. You'll use this key in the next step

### 2️⃣ Start the Backend

#### Option A: Termux (Android — Recommended)

```bash
# Install dependencies
pkg update && pkg upgrade
pkg install python git termux-api
pip install flask requests

# Clone or copy the project
cd ~
# Copy the project to your Termux home directory

# Set your API key
export GROQ_CHAT_API_KEY='gsk_your_key_here'

# Start the server
cd backend
python app_productivity.py
```

#### Option B: PC (Windows/Linux)

```bash
# Install Python dependencies
cd backend
pip install -r requirements.txt

# Set your API key
export GROQ_CHAT_API_KEY='gsk_your_key_here'
# On Windows: set GROQ_CHAT_API_KEY=gsk_your_key_here

# Start the server
python app_productivity.py
```

The server will start on **http://127.0.0.1:8001**

### 3️⃣ Open the Web Interface

**Option A: Android APK** → Install the APK and open it (auto-connects to local backend)
**Option B: Browser** → Open `http://127.0.0.1:8001` in Chrome/Edge

Tap the **orb** to activate voice, or type in the chat box.

### 4️⃣ Try Commands

| Command | Response |
|---------|----------|
| "Hello" | Chat conversation |
| "Open YouTube" | Opens YouTube app |
| "What time is it?" | Current time |
| "Generate an image of a sunset" | Creates AI image |
| "Search latest news" | Fetches news headlines |
| "Turn on WiFi" | Enables WiFi |
| "What's my battery status?" | Battery info |
| "Calculate 15% of 340" | Math reasoning |

---

## Building the APK

### On Linux (with Android SDK)

```bash
# Set up SDK
export ANDROID_HOME=/opt/android-sdk
export PATH=$PATH:$ANDROID_HOME/platform-tools

# Build
cd android
bash gradlew assembleDebug --no-daemon
```

Output: `android/app/build/outputs/apk/debug/app-debug.apk`

### On Windows

```powershell
cd android
.\gradlew.bat assembleDebug --no-daemon
```

### Notes
- Requires JDK 17+ and Android SDK with platform **android-36** and build-tools **36.0.0**
- The APK connects to `http://127.0.0.1:8001` — the backend must be running on the same device
- Install via `adb install -r app-debug.apk` or tap the APK in a file manager

---

## Configuration

### Backend Config (`backend/config_productivity.py`)

| Setting | Default | Description |
|---------|---------|-------------|
| `PORT` | 8001 | Flask server port |
| `GROQ_CHAT_API_KEY` | — | Groq API key (also via env var) |
| `GROQ_CHAT_MODEL` | llama-3.3-70b-versatile | LLM model |
| `NOTES_DIR` | ./notes | Where notes/screenshots are saved |
| `NEWS_API_KEY` | — | (Optional) NewsAPI key |
| `SERP_API_KEY` | — | (Optional) SerpAPI key |

### Android Config

| Setting | Location | Description |
|---------|----------|-------------|
| `BACKEND_URL` | `MainActivity.kt:30` | Backend URL (default: `http://127.0.0.1:8001`) |
| `PKG_MAP` | `script.js:221-230` | App name → Android package mapping |
| `ANDROID_TASK_MAP` | `script.js:232-242` | Task → Android bridge method mapping |

---

## Project Structure

```
JARVIS-Productivity/
├── README.md
├── rbuild.md                     # Build documentation & error log
├── android/                      # Android APK source
│   ├── app/
│   │   └── src/main/
│   │       ├── AndroidManifest.xml
│   │       ├── java/com/jarvis/productivity/
│   │       │   ├── MainActivity.kt
│   │       │   ├── JarvisBridge.kt
│   │       │   ├── JarvisService.kt
│   │       │   └── BootReceiver.kt
│   │       └── res/
│   ├── gradle/wrapper/
│   ├── build.gradle.kts
│   ├── gradle.properties
│   └── local.properties
├── backend/                      # Python Flask backend
│   ├── app_productivity.py       # Main Flask application
│   ├── config_productivity.py    # Configuration
│   ├── requirements.txt          # Python dependencies
│   ├── agents/                   # AI agents
│   │   ├── task_agent.py
│   │   ├── chat_agent.py
│   │   ├── image_agent.py
│   │   ├── research_agent.py
│   │   ├── search_agent.py
│   │   ├── coding_agent.py
│   │   └── reasoning_agent.py
│   ├── core/                     # Core engine
│   │   ├── orchestrator.py       # Command routing
│   │   ├── brain.py              # LLM interaction
│   │   ├── config.py             # Shared config
│   │   ├── memory.py             # Chat memory
│   │   ├── auto_skill.py         # Auto-skill learning
│   │   ├── data_center.py        # Knowledge base
│   │   └── llm_adapter.py        # LLM provider adapter
│   ├── skills/                   # Executable skills
│   │   └── tasks.py              # All device/app control functions
│   ├── audio/                    # Voice I/O
│   │   └── voice.py
│   └── web/                      # Web UI
│       ├── index.html
│       ├── script.js
│       └── style.css
├── scripts/                      # Utility scripts
│   ├── build_apk.bat
│   ├── deploy_termux.sh
│   ├── validate_setup.py
│   └── verify_backend.py
└── training_data/                # Training data (user-created)
```

---

## Android Bridge Methods

The `JarvisBridge.kt` exposes these methods to JavaScript via `window.Android`:

| Method | Parameters | Description |
|--------|-----------|-------------|
| `speak` | `text: String` | Speak text via TTS |
| `stopTts` | — | Stop current TTS |
| `toast` | `text: String` | Show a toast message |
| `vibrate` | `ms: Int` | Vibrate device |
| `openApp` | `pkg: String` | Open an app by package name |
| `closeApp` | `pkg: String` | Open app info screen |
| `openUrl` | `url: String` | Open a URL |
| `wifi` | `on: Boolean` | Toggle WiFi |
| `bluetooth` | `on: Boolean` | Toggle Bluetooth |
| `flashlight` | `on: Boolean` | Toggle flashlight |
| `brightness` | `level: Int` | Set screen brightness |
| `ringerMode` | `mode: String` | Set ringer mode |
| `dnd` | `on: Boolean` | Toggle Do Not Disturb |
| `airplane` | `on: Boolean` | Toggle airplane mode |
| `clipboard` / `clipboardRead` | `text: String` | Clipboard access |
| `share` | `text: String` | Share text |
| `mediaPlay` / `mediaNext` / `mediaPrev` | — | Media controls |
| `sendSms` | `number, message` | Send SMS |
| `screenOn` | — | Check if screen is on |
| `deviceInfo` | — | Get device info JSON |

---

## Agent System

JARVIS uses a **routing architecture** with specialized agents:

```
User Input → Orchestrator → Classification (keyword + LLM)
                               │
             ┌─────────────────┼─────────────────┐
             ▼                 ▼                   ▼
        Task Agent      Chat Agent          Image Agent
     (open apps,      (conversation,      (image generation)
      settings,         advice)
      device control)
             │                 │                   │
             ▼                 ▼                   ▼
        skills/tasks.py    brain.py           skills/img.py
        (am start,         (Groq LLM)         (SeaArt API)
         Termux API)
```

Each agent extends `BaseAgent` and implements a `run(query, parameters)` method. The orchestrator classifies the intent, routes to the appropriate agent, and optionally runs a secondary agent.

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web UI |
| `/chat` | POST | Process a command → returns reply + metadata |
| `/agent` | POST | Direct agent call |
| `/agents` | GET | List available agents |
| `/shutdown` | POST | Stop the backend (token: `jarvis_shutdown`) |
| `/health` | GET | Server health check |
| `/status` | GET | System status, battery, time |
| `/history` | GET | Recent chat history |
| `/knowledge/search` | POST | Search knowledge base |
| `/knowledge/stats` | GET | Knowledge base statistics |
| `/auto-skills` | GET | List auto-learned skills |
| `/device/location` | GET | GPS location |
| `/device/tts` | POST | Speak text via Termux TTS |

---

## Troubleshooting

### "Apps won't open / opens Play Store"
- Ensure Termux has the **Termux:API** app installed
- Grant Termux special permissions in Android Settings
- The app must be installed on the device
- Package names in `script.js:PKG_MAP` must match exactly

### "TTS speaks garbled characters"
- The speech cleaning regex removes special characters before speaking
- If you see issues, check `script.js:speak()` function

### "Backend won't start"
- Verify `GROQ_CHAT_API_KEY` is set
- Check that port 8001 is not in use
- Run `pip install -r requirements.txt`

### "Can't build APK"
- JDK 17+ required (`java -version`)
- Android SDK at `/opt/android-sdk` with platform android-36
- Set `ANDROID_HOME` environment variable

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_CHAT_API_KEY` | **Yes** | Groq API key for LLM access |
| `NEWS_API_KEY` | No | NewsAPI key for news agent |
| `SERP_API_KEY` | No | SerpAPI key for search agent |
| `TERMUX_VERSION` | Auto | Set by Termux runtime |

---

## License

MIT License — see [LICENSE](LICENSE) file.

## Acknowledgments

- [Groq](https://groq.com) for the ultra-fast LLM inference
- [Flask](https://flask.palletsprojects.com) for the web framework
- [SeaArt AI](https://seaart.ai) for image generation
- Android Open Source Project for platform APIs

---

<p align="center">
  Made with ❤️ for productivity
</p>
