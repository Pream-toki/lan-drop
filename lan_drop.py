"""Share a folder on your LAN. Tray starts/stops a tiny HTTP server."""

from __future__ import annotations

import json
import os
import socket
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pystray
from PIL import Image, ImageDraw

APP_DIR = Path(__file__).resolve().parent
CONFIG_PATH = APP_DIR / "config.json"
URL_FILE = APP_DIR / "share_url.txt"
STARTUP_NAME = "LanDrop.vbs"

httpd: ThreadingHTTPServer | None = None
http_thread: threading.Thread | None = None
state = {"url": "stopped"}


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        CONFIG_PATH.write_text(
            json.dumps({"folder": str(Path.home() / "Downloads"), "port": 8765}, indent=2),
            encoding="utf-8",
        )
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"folder": str(Path.home() / "Downloads"), "port": 8765}


def save_config(data: dict) -> None:
    CONFIG_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def startup_path() -> Path:
    return (
        Path(os.environ.get("APPDATA", ""))
        / "Microsoft/Windows/Start Menu/Programs/Startup"
        / STARTUP_NAME
    )


def set_startup(icon, want: bool) -> None:
    p = startup_path()
    script = Path(__file__).resolve()
    try:
        if want:
            p.write_text(
                'Set sh = CreateObject("WScript.Shell")\n'
                f'sh.CurrentDirectory = "{script.parent}"\n'
                f'sh.Run "pythonw ""{script}""", 0, False\n',
                encoding="ascii",
            )
        elif p.exists():
            p.unlink()
        cfg = load_config()
        cfg["start_with_windows"] = want
        save_config(cfg)
        icon.update_menu()
    except OSError:
        pass


def lan_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def stop_server() -> None:
    global httpd
    if httpd is not None:
        try:
            httpd.shutdown()
        except Exception:
            pass
        httpd = None
    state["url"] = "stopped"


def start_server() -> None:
    global httpd, http_thread
    stop_server()
    cfg = load_config()
    folder = Path(cfg.get("folder") or (Path.home() / "Downloads"))
    folder.mkdir(parents=True, exist_ok=True)
    port = int(cfg.get("port") or 8765)
    handler = partial(SimpleHTTPRequestHandler, directory=str(folder))
    httpd = ThreadingHTTPServer(("0.0.0.0", port), handler)
    http_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    http_thread.start()
    url = f"http://{lan_ip()}:{port}/"
    state["url"] = url
    URL_FILE.write_text(
        f"Sharing {folder}\n{url}\n\nSame wifi only. Stop from the tray when you are done.\n",
        encoding="utf-8",
    )


def open_url(_i=None, _item=None) -> None:
    if not URL_FILE.exists():
        URL_FILE.write_text("Not sharing yet. Tray -> Start sharing.\n", encoding="utf-8")
    try:
        os.startfile(str(URL_FILE))
    except OSError:
        pass


def open_cfg(_i=None, _item=None) -> None:
    load_config()
    try:
        os.startfile(str(CONFIG_PATH))
    except OSError:
        pass


def do_start(icon, _item=None) -> None:
    try:
        start_server()
    except OSError as e:
        state["url"] = f"fail: {e}"
    try:
        icon.update_menu()
    except Exception:
        pass


def do_stop(icon, _item=None) -> None:
    stop_server()
    try:
        icon.update_menu()
    except Exception:
        pass


def quit_app(icon, _item=None) -> None:
    stop_server()
    icon.stop()


def menu(icon):
    sharing = httpd is not None
    return pystray.Menu(
        pystray.MenuItem(state["url"], None, enabled=False),
        pystray.MenuItem("Start sharing", do_start, enabled=not sharing),
        pystray.MenuItem("Stop sharing", do_stop, enabled=sharing),
        pystray.MenuItem("Show URL / folder", open_url),
        pystray.MenuItem("Settings (folder, port)", open_cfg),
        pystray.MenuItem(
            "Start with Windows",
            lambda i, _: set_startup(i, not startup_path().exists()),
            checked=lambda _: startup_path().exists(),
        ),
        pystray.MenuItem("Quit", quit_app),
    )


def icon_img():
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((10, 14, 54, 50), 8, fill=(40, 130, 100, 255))
    d.polygon([(32, 10), (48, 26), (16, 26)], fill=(40, 130, 100, 255))
    return img


def main() -> None:
    load_config()
    icon = pystray.Icon("LanDrop", icon_img(), "LAN drop", menu=pystray.Menu(lambda: menu(icon)))
    icon.run()


if __name__ == "__main__":
    main()
