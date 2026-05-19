# tasks.py -- JARVIS Compact Task Core (v3)
import os, sys, subprocess, webbrowser, time, urllib.parse, json, platform, re
from datetime import datetime
from typing import Optional, List
from skills.img import generate_image

IS_WIN = platform.system() == "Windows"
IS_TRX = "TERMUX_VERSION" in os.environ or os.path.exists("/data/data/com.termux")

APP_REG = {
    "youtube": {"p": "com.google.android.youtube", "w": "https://youtube.com", "t": ["yt", "video", "music"]},
    "chrome": {"p": "com.android.chrome", "w": "chrome", "t": ["browser", "internet", "web"]},
    "whatsapp": {"p": "com.whatsapp", "w": "https://web.whatsapp.com", "t": ["wa", "whats app"]},
    "telegram": {"p": "org.telegram.messenger", "w": "https://web.telegram.org", "t": ["tg"]},
    "spotify": {"p": "com.spotify.music", "w": "spotify", "t": ["music", "song"]},
    "gallery": {"p": "com.google.android.apps.photos", "w": "photos", "t": ["photos", "gallery", "pictures"]},
    "camera": {"p": "com.android.camera", "w": "camera", "t": ["camera", "photo"]},
    "files": {"p": "com.google.android.documentsui", "w": "explorer", "t": ["files", "file manager", "storage", "explorer"]},
    "calculator": {"p": "com.android.calculator2", "w": "calc", "t": ["calc", "calculate"]},
    "settings": {"p": "com.android.settings", "w": "settings", "t": ["setting", "preferences"]},
    "maps": {"p": "com.google.android.apps.maps", "w": "https://maps.google.com", "t": ["map", "navigation", "gps"]},
    "gmail": {"p": "com.google.android.gm", "w": "https://mail.google.com", "t": ["email", "mail"]},
    "clock": {"p": "com.google.android.deskclock", "w": "clock", "t": ["alarm", "timer", "stopwatch"]},
    "contacts": {"p": "com.google.android.contacts", "w": "contacts", "t": ["contact", "phonebook"]},
    "phone": {"p": "com.google.android.dialer", "w": "phone", "t": ["dialer", "call"]},
    "play store": {"p": "com.android.vending", "w": "playstore", "t": ["playstore", "app store"]},
    "instagram": {"p": "com.instagram.android", "w": "https://instagram.com", "t": ["ig", "insta"]},
    "facebook": {"p": "com.facebook.katana", "w": "https://facebook.com", "t": ["fb", "meta"]},
    "twitter": {"p": "com.twitter.android", "w": "https://twitter.com", "t": ["x", "tweet"]},
    "linkedin": {"p": "com.linkedin.android", "w": "https://linkedin.com", "t": ["linked"]},
    "netflix": {"p": "com.netflix.mediaclient", "w": "https://netflix.com", "t": ["netflix"]},
    "prime video": {"p": "com.amazon.avod.thirdpartyclient", "w": "https://primevideo.com", "t": ["prime", "amazon video"]},
    "notepad": {"p": "com.socialnmobile.dictapps.notepad.color.note", "w": "notepad", "t": ["notes", "notepad"]},
}

def _run(cmds):
    try:
        r = subprocess.run(cmds, capture_output=True, text=True, timeout=3)
        if r.returncode != 0:
            print(f"[tasks] _run failed ({r.returncode}): {r.stderr[:200]}")
        return r
    except subprocess.TimeoutExpired:
        print(f"[tasks] _run timeout: {cmds[0]}")
        return None
    except Exception as e:
        print(f"[tasks] _run exception: {e}")
        return None

def open_app(n: str):
    q = n.lower().strip()
    info = next((v for k, v in APP_REG.items() if q in [k] + v.get("t", [])), {"w": q, "p": q})
    pkg = info.get("p", q)
    if IS_TRX:
        _run(["am", "start", "--user", "0", "-p", pkg])
    else:
        w = info.get("w", q)
        if w.startswith("http"):
            webbrowser.open(w)
        else:
            subprocess.Popen(["cmd", "/c", "start", w], shell=False)
    return f"Opening {n}."

def close_app(n: str):
    q = n.lower().strip()
    info = next((v for k, v in APP_REG.items() if q in [k] + v.get("t", [])), {"p": q})
    pkg = info.get("p", q)
    if IS_TRX:
        _run(["am", "force-stop", pkg])
    elif IS_WIN:
        _run(["taskkill", "/IM", f"{pkg.split('.')[0]}.exe", "/F"])
    return f"Closed {n}."

def open_any_app(n: str):
    return open_app(n)

def play_yt(q: str):
    url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(q)}"
    if IS_TRX:
        _run(["am", "start", "--user", "0", "-a", "android.intent.action.VIEW", "-d", url])
    else:
        webbrowser.open(url)
    return f"Playing {q}."

def search(q: str):
    from core.config import SERP_API_KEY
    import requests
    res = ""
    try:
        r = requests.get("https://serpapi.com/search", params={"q": q, "api_key": SERP_API_KEY}, timeout=5).json()
        res = r.get("answer_box", {}).get("answer") or r.get("organic_results", [{}])[0].get("snippet", "")
    except Exception:
        pass
    webbrowser.open(f"https://google.com/search?q={q}")
    return res if res else f"Searched for {q}."

def get_realtime_data(q: str):
    from core.config import SERP_API_KEY
    import requests
    try:
        r = requests.get("https://serpapi.com/search", params={"q": q, "api_key": SERP_API_KEY, "num": 3}, timeout=8).json()
        answer = r.get("answer_box", {}).get("answer")
        if answer:
            return str(answer)
        kg = r.get("knowledge_graph", {})
        if kg.get("description"):
            return kg["description"]
        results = r.get("organic_results", [])
        if results:
            snippets = [r.get("snippet", "") for r in results[:3] if r.get("snippet")]
            if snippets:
                return " | ".join(snippets)
        return f"No real-time results found for '{q}'."
    except Exception as e:
        return f"Search error: {e}"

def take_shot():
    from core.config import NOTES_DIR
    p = os.path.join(NOTES_DIR, f"s_{int(time.time())}.png")
    if IS_TRX:
        _run(["termux-screenshot", "-f", p])
    return f"Screenshot: {p}"

def get_time():
    return datetime.now().strftime("%I:%M %p, %A %B %d, %Y")

def lock():
    return lock_screen()

def lock_screen():
    if IS_TRX:
        for cmd in (["/system/bin/input", "keyevent", "26"], ["input", "keyevent", "26"]):
            r = _run(cmd)
            if r and r.returncode == 0:
                return "Screen locked."
        return "Screen lock may require INJECT_EVENTS permission. Try granting Termux special access in Settings."
    return "Lock screen is not available on this device."

def shutdown():
    return "Shutdown is not available on Android."

def restart():
    return "Restart is not available on Android."

def cancel_shutdown():
    return "Shutdown control is not available on Android."

def write_note(t):
    from core.config import NOTES_DIR
    filepath = os.path.join(NOTES_DIR, f"note_{int(time.time())}.txt")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(t)
    return f"Note saved to {filepath}."

def get_battery_status():
    if IS_TRX:
        try:
            result = subprocess.run(["termux-battery-status"], capture_output=True, text=True, timeout=3)
            data = json.loads(result.stdout)
            pct = data.get("percentage", "?")
            status = data.get("status", "unknown")
            return f"Battery: {pct}% ({status})"
        except Exception:
            return "Battery info unavailable on this device."
    elif IS_WIN:
        try:
            result = subprocess.run(["powershell", "-Command", "(Get-WmiObject Win32_Battery).EstimatedChargeRemaining"], capture_output=True, text=True, timeout=5)
            pct = result.stdout.strip()
            if pct:
                return f"Battery: {pct}%"
            return "No battery detected (desktop PC)."
        except Exception:
            return "No battery detected (desktop PC)."
    return "Battery status not available."

def get_system_info():
    info = {"OS": f"{platform.system()} {platform.release()}", "Machine": platform.machine(), "Hostname": platform.node(), "Python": platform.python_version(), "CPU Cores": os.cpu_count()}
    parts = [f"{k}: {v}" for k, v in info.items()]
    return " | ".join(parts)

def get_time_date():
    return get_time()

def get_news(topic: str = ""):
    from core.config import NEWS_API_KEY
    import requests
    try:
        params = {"apiKey": NEWS_API_KEY, "language": "en", "pageSize": 5}
        if topic:
            params["q"] = topic
            url = "https://newsapi.org/v2/everything"
        else:
            params["country"] = "in"
            url = "https://newsapi.org/v2/top-headlines"
        r = requests.get(url, params=params, timeout=8).json()
        articles = r.get("articles", [])
        if not articles:
            return "No news articles found."
        headlines = []
        for i, a in enumerate(articles[:5], 1):
            title = a.get("title", "No title")
            headlines.append(f"{i}. {title}")
        return "Latest News:\n" + "\n".join(headlines)
    except Exception as e:
        return f"News fetch error: {e}"

def control_volume(direction: str = ""):
    d = direction.lower().strip()
    if IS_TRX:
        if "down" in d or "low" in d:
            _run(["termux-volume", "music", "5"])
            return "Volume decreased."
        else:
            _run(["termux-volume", "music", "12"])
            return "Volume increased."
    return "Volume control not available."

def control_brightness(direction: str = ""):
    d = direction.lower().strip()
    if IS_TRX:
        if "down" in d or "low" in d or "decrease" in d or "dim" in d:
            _run(["termux-brightness", "50"])
            return "Brightness decreased."
        else:
            _run(["termux-brightness", "200"])
            return "Brightness increased."
    return "Brightness control not available."

def toggle_wifi(state: str = ""):
    s = state.lower().strip()
    if IS_TRX:
        if "off" in s or "disable" in s:
            _run(["termux-wifi-enable", "false"])
            return "WiFi disabled."
        else:
            _run(["termux-wifi-enable", "true"])
            return "WiFi enabled."
    return "WiFi control not available."

def toggle_bluetooth(state: str = ""):
    s = state.lower().strip()
    if IS_TRX:
        if "off" in s or "disable" in s:
            _run(["am", "start", "-a", "android.bluetooth.adapter.action.REQUEST_DISABLE"])
            return "Bluetooth disable requested."
        else:
            _run(["am", "start", "-a", "android.bluetooth.adapter.action.REQUEST_ENABLE"])
            return "Bluetooth enable requested."
    return "Bluetooth control not available."

def open_website(url: str):
    if not url.startswith("http"):
        url = f"https://{url}"
    if IS_TRX:
        _run(["am", "start", "--user", "0", "-a", "android.intent.action.VIEW", "-d", url])
    else:
        webbrowser.open(url)
    return f"Opening {url}."

def open_gallery():
    if IS_TRX:
        _run(["am", "start", "-a", "android.intent.action.VIEW", "-t", "image/*"])
    return "Opening gallery."

def access_storage():
    if IS_TRX:
        _run(["am", "start", "-a", "android.intent.action.VIEW", "-d", "content://com.android.externalstorage.documents/root/primary"])
    return "Opening file manager."

def take_photo():
    if IS_TRX:
        from core.config import NOTES_DIR
        p = os.path.join(NOTES_DIR, f"photo_{int(time.time())}.jpg")
        _run(["termux-camera-photo", "-c", "0", p])
        return f"Photo saved to {p}."
    return "Camera not available."

def generate_image_task(prompt: str):
    if not prompt or str(prompt).lower() in ["none", "null", ""]:
        return json.dumps({"status": "error", "message": "No image description provided."})
    try:
        filepath, image_url = generate_image(prompt)
        if filepath and image_url:
            return json.dumps({"status": "success", "message": f"Image generated: {prompt}", "url": image_url, "filepath": filepath})
        elif filepath:
            return json.dumps({"status": "success", "message": f"Image generated and saved to {filepath}", "filepath": filepath})
        else:
            return json.dumps({"status": "error", "message": "Image generation failed. API may be temporarily unavailable."})
    except Exception as e:
        return json.dumps({"status": "error", "message": f"Image generation error: {e}"})

def understand_screen():
    screenshot_result = take_shot()
    return f"Screen captured. {screenshot_result} (Vision analysis requires active vision model connection.)"

def call_contact(n: str):
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    contact_file = os.path.join(root_dir, "personal_details", "contact.txt")
    number = None
    contact_name = None
    if os.path.exists(contact_file):
        try:
            with open(contact_file, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
            for line in lines:
                line = line.strip()
                if line.startswith("- "):
                    part = line[2:].strip()
                    if ":" in part:
                        nm, val = part.split(":", 1)
                        nm = nm.strip()
                        val = val.strip()
                        if nm and val and val.lower() != "[not set]" and re.search(rf"{n}", nm, re.IGNORECASE):
                            contact_name = nm
                            number = val
                            break
            if not number:
                for line in lines:
                    if ":" in line:
                        nm, val = line.split(":", 1)
                        nm = nm.strip()
                        val = val.strip()
                        if val and val.lower() != "[not set]" and re.search(rf"{n}", nm, re.IGNORECASE):
                            contact_name = nm
                            number = val
                            break
        except Exception:
            pass
    if not number:
        return f"Contact '{n}' not found or number not set."
    try:
        if IS_TRX:
            subprocess.run(["am", "start", "--user", "0", "-a", "android.intent.action.CALL", "-d", f"tel:{number}"], capture_output=True)
        else:
            webbrowser.open(f"tel:{number}")
    except Exception as e:
        return f"Failed to initiate call: {e}"
    return f"Calling {contact_name or n} ({number})..."

NOTIF_FRIENDLY = {
    "com.whatsapp": "WhatsApp", "com.instagram.android": "Instagram", "com.google.android.gm": "Gmail",
    "com.google.android.gm.lite": "Gmail Lite", "com.facebook.katana": "Facebook", "com.twitter.android": "Twitter",
    "com.telegram.messenger": "Telegram", "com.android.systemui": "System", "com.google.android.apps.maps": "Maps",
    "com.google.android.youtube": "YouTube", "com.google.android.dialer": "Phone", "com.android.phone": "Phone",
    "com.google.android.apps.photos": "Photos",
}

def read_notifications(max_count: int = 10):
    if not IS_TRX:
        return "Notifications reading is available on Android only."
    try:
        r = subprocess.run(["termux-notification-list"], capture_output=True, text=True, timeout=3)
        if r.returncode != 0 or not r.stdout.strip():
            return "No notifications found."
        items = json.loads(r.stdout)
        if not items:
            return "No notifications found."
        lines = []
        for item in items[:max_count]:
            pkg = item.get("packageName", "")
            title = (item.get("title") or "").strip()
            content = (item.get("content") or "").strip()
            label = NOTIF_FRIENDLY.get(pkg, pkg.split(".")[-1] if "." in pkg else pkg)
            parts = [f"{label}"]
            if title:
                parts.append(title)
            if content:
                parts.append(f"({content})")
            lines.append(": ".join(parts))
        return "Notifications: " + " | ".join(lines)
    except json.JSONDecodeError:
        return "Unable to parse notifications."
    except subprocess.TimeoutExpired:
        return "Notification service timed out."
    except Exception as e:
        return f"Notification error: {e}"

def search_and_read(q: str):
    return get_realtime_data(q)

def send_sms(t: str):
    parts = t.split("|", 1) if "|" in t else t.split(" ", 1)
    number = parts[0].strip()
    message = parts[1].strip() if len(parts) > 1 else ""
    if not number or not message:
        return "Usage: send sms [number]|[message]"
    if IS_TRX:
        subprocess.run(["termux-sms-send", "-n", number, message], capture_output=True, timeout=3)
        return f"SMS sent to {number}."
    return "SMS sending is available on Android only."

def read_sms(target: str = ""):
    if not IS_TRX:
        return "SMS reading is available on Android only."
    try:
        count = 5
        if target and target.strip().isdigit():
            count = int(target.strip())
        r = subprocess.run(["termux-sms-inbox", "-l", str(count)], capture_output=True, text=True, timeout=3)
        if r.returncode != 0 or not r.stdout.strip():
            return "No SMS messages found."
        msgs = json.loads(r.stdout)
        if not msgs:
            return "No SMS messages."
        lines = []
        for m in msgs[:count]:
            sender = m.get("number", "Unknown")
            body = (m.get("body") or "").strip()[:80]
            received = m.get("received", "")
            lines.append(f"{sender}: {body}")
        return "SMS: " + " | ".join(lines)
    except Exception as e:
        return f"SMS inbox error: {e}"

def get_contacts(_=None):
    if not IS_TRX:
        return "Contacts are available on Android only."
    try:
        r = subprocess.run(["termux-contact-list"], capture_output=True, text=True, timeout=3)
        if r.returncode != 0 or not r.stdout.strip():
            return "No contacts found."
        contacts = json.loads(r.stdout)
        if not contacts:
            return "No contacts found."
        lines = [f"{c.get('name', '?')}: {c.get('number', '?')}" for c in contacts[:20]]
        return "Contacts: " + " | ".join(lines)
    except Exception as e:
        return f"Contacts error: {e}"

def media_control(cmd: str = "play"):
    c = cmd.lower().strip()
    valid = {"play", "pause", "next", "previous", "stop", "info"}
    if c not in valid:
        return f"Invalid media command: {c}. Use: {', '.join(sorted(valid))}"
    if not IS_TRX:
        return "Media control is available on Android only."
    _run(["termux-media-player", c])
    return f"Media {c}."

def share_content(text: str):
    if not IS_TRX:
        return "Share is available on Android only."
    try:
        r = subprocess.run(["termux-share", "-a", "share", text], capture_output=True, text=True, timeout=3)
        return f"Shared: {text[:50]}..."
    except Exception as e:
        return f"Share error: {e}"

def get_wifi_info(_=None):
    if not IS_TRX:
        return "WiFi info is available on Android only."
    try:
        r = subprocess.run(["termux-wifi-connectioninfo"], capture_output=True, text=True, timeout=3)
        if r.returncode != 0 or not r.stdout.strip():
            return "No WiFi connection."
        info = json.loads(r.stdout)
        ssid = info.get("ssid", "?")
        signal = info.get("rssi", 0)
        ip = info.get("ip", "?")
        speed = info.get("link_speed_mbps", "?")
        return f"WiFi: {ssid} | Signal: {signal} dBm | IP: {ip} | Speed: {speed} Mbps"
    except Exception as e:
        return f"WiFi info error: {e}"

def set_wallpaper(target: str = ""):
    if not IS_TRX:
        return "Wallpaper setting is available on Android only."
    if not target:
        return "Provide a file path or URL for the wallpaper."
    local_path = target
    if target.startswith("http"):
        import tempfile
        import requests as req
        try:
            local_path = os.path.join(tempfile.gettempdir(), f"wp_{int(time.time())}.jpg")
            resp = req.get(target, timeout=10)
            with open(local_path, "wb") as f:
                f.write(resp.content)
        except Exception as e:
            return f"Wallpaper download error: {e}"
    _run(["termux-wallpaper", "-f", local_path])
    return f"Wallpaper set from {target[:60]}."

def get_call_log(target: str = ""):
    if not IS_TRX:
        return "Call log is available on Android only."
    try:
        count = 5
        if target and target.strip().isdigit():
            count = int(target.strip())
        r = subprocess.run(["termux-call-log", "-l", str(count)], capture_output=True, text=True, timeout=3)
        if r.returncode != 0 or not r.stdout.strip():
            return "No call log entries."
        data = json.loads(r.stdout)
        if not data:
            return "No call log entries."
        if isinstance(data, dict):
            data = [data]
        lines = []
        for c in data[:count]:
            number = c.get("number", "?")
            name = c.get("name", "") or ""
            call_type = c.get("type", "?")
            duration = c.get("duration", "?")
            entry = f"{name or number} ({call_type}, {duration}s)"
            lines.append(entry)
        return "Call log: " + " | ".join(lines)
    except Exception as e:
        return f"Call log error: {e}"

def get_location(_=None):
    if not IS_TRX:
        return "Location is available on Android only."
    try:
        r = subprocess.run(["termux-location", "-p", "gps"], capture_output=True, text=True, timeout=4)
        if r.returncode != 0 or not r.stdout.strip():
            r = subprocess.run(["termux-location", "-p", "network"], capture_output=True, text=True, timeout=3)
        if r.returncode != 0 or not r.stdout.strip():
            return "Location unavailable."
        loc = json.loads(r.stdout)
        lat = loc.get("latitude", "?")
        lon = loc.get("longitude", "?")
        alt = loc.get("altitude", "?")
        acc = loc.get("accuracy", "?")
        provider = loc.get("provider", "?")
        return f"Location: {lat}, {lon} (+/-{acc}m, {provider})"
    except Exception as e:
        return f"Location error: {e}"

open_application = open_app
play_youtube = play_yt
search_google = search
take_screenshot = take_shot
shutdown_computer = shutdown
restart_computer = restart
close_application = close_app
