# LAN drop

Puts a folder on a tiny web server on **your current wifi**. Phone or another laptop opens the URL and can download those files.

Default folder is Downloads. Default port `8765`.

## Setup

Python 3 → `START.bat` → green share icon.

Tray → **Settings (folder, port)** only if you want a different folder. Do not point this at `C:\` or your whole user profile.

## Use

1. Same wifi as the other device (school wifi guest networks sometimes block device-to-device).
2. **Start sharing**.
3. **Show URL / folder** — open that text file, type the `http://...` address on the other device.
4. When you’re done: **Stop sharing**. Then **Quit** if you don’t need the tray.

**Careful**

- Anyone on that wifi who has the URL can see that folder. Don’t share homework you don’t want copied. Don’t share a folder with logins in it.
- This is not the internet. No port forwarding. If it only works as `127.0.0.1`, the other device is not on your LAN.
- Stop it. Leaving it on in a lab is how random people browse your Downloads.
- Windows Firewall may ask the first time — allow it on **private** networks if you trust this wifi.
- **Start with Windows** is usually a bad idea for this app; keep it off unless you know why.
