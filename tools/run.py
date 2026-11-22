#!/usr/bin/env python3
"""
run.py - helper for ESP32-S3 + MicroPython (runs on your PC, not on the board).

Wraps esptool and mpremote so you don't have to remember the commands.

Usage:
    python run.py ports                      list serial ports
    python run.py erase                      erase the board's flash
    python run.py flash firmware.bin         flash MicroPython firmware
    python run.py upload                     upload project files to the board
    python run.py run lcd.py                 run a file (mounts the current folder)
    python run.py run lcd.py --no-mount      run a file without mounting
    python run.py repl                       open the REPL
    python run.py ls                         list files on the board
    python run.py reset                      reboot the board
    python run.py rm main.py                 delete a file on the board

Options:
    -p COM5 / --port COM5                    choose a port (otherwise auto-detect)
    --baud 460800                            flash baud rate (flash command)
    --mount-dir DIR                          folder to mount for 'run' (default: .)
    --no-mount                               'run' without mounting anything

About 'run':
    'run' mounts your PC folder on the board while the script runs, so imports
    such as 'from lib.lcd1602 import LCD1602' are read from your computer.
    Nothing is copied to the board's flash. Run it from your project folder
    (the one that contains lib/), not from tools/.

Requires: pip install esptool mpremote
"""

import argparse
import os
import sys
import subprocess

try:
    from serial.tools import list_ports
except ImportError:
    sys.exit("pyserial is missing. Run: python -m pip install esptool mpremote")

CHIP = "esp32s3"

# Things that should NOT be uploaded to the board
SKIP = {
    "run.py", "test.py", "README.md", "__pycache__", ".git", ".vscode",
    ".venv", "venv", "env", "node_modules", ".gitignore", ".micropico",
    "typings", "tools",
}
SKIP_EXT = {".bin", ".md", ".pyc", ".txt", ".zip"}


# ---------------------------------------------------------------- helpers
def find_port():
    """Guess the ESP32-S3 port. Ignores Bluetooth virtual COM ports."""
    candidates = []
    for p in list_ports.comports():
        desc = (p.description or "").lower()
        if "bluetooth" in desc:
            continue
        score = 0
        if p.vid == 0x303A:  # Espressif native USB
            score += 10
        if "usb serial" in desc or "usb jtag" in desc or "cp210" in desc or "ch340" in desc:
            score += 5
        candidates.append((score, p.device))
    if not candidates:
        return None
    candidates.sort(reverse=True)
    return candidates[0][1]


def sh(cmd):
    """Print and run a command, return its exit code."""
    print("> " + " ".join(cmd))
    return subprocess.call(cmd)


def esptool(port, *args):
    return sh([sys.executable, "-m", "esptool", "--chip", CHIP, "--port", port, *args]) # type: ignore


def mpremote(port, *args):
    return sh([sys.executable, "-m", "mpremote", "connect", port, *args]) # type: ignore


def need_port(args):
    port = args.port or find_port()
    if not port:
        sys.exit("No serial port found. Plug in the board or pass --port COM5")
    print(f"Using port: {port}")
    return port


# --------------------------------------------------------------- commands
def cmd_ports(args):
    ports = list(list_ports.comports())
    if not ports:
        print("No serial ports found.")
        return 1
    for p in ports:
        print(f"{p.device:8} {p.description}")
    guess = find_port()
    print(f"\nLikely ESP32-S3 port: {guess}")
    return 0


def cmd_erase(args):
    port = need_port(args)
    return esptool(port, "erase-flash")


def cmd_flash(args):
    port = need_port(args)
    if not os.path.isfile(args.firmware): # type: ignore
        sys.exit(f"Firmware file not found: {args.firmware}")
    return esptool(port, "--baud", str(args.baud), "write-flash", "0", args.firmware)


def cmd_upload(args):
    port = need_port(args)
    root = os.path.abspath(args.folder) # type: ignore
    entries = sorted(os.listdir(root))
    failed = 0
    for name in entries:
        ext = os.path.splitext(name)[1].lower() # type: ignore
        if name in SKIP or ext in SKIP_EXT:
            continue
        path = os.path.join(root, name) # type: ignore
        if os.path.isdir(path): # pyright: ignore[reportAttributeAccessIssue]
            rc = mpremote(port, "cp", "-r", path, ":")
        else:
            rc = mpremote(port, "cp", path, f":{name}")
        if rc != 0:
            failed += 1
    if failed:
        print(f"\n{failed} upload(s) failed.")
        return 1
    print("\nUpload done. Run 'python run.py reset' to start main.py.")
    return 0


def cmd_run(args):
    port = need_port(args)
    if not os.path.isfile(args.file): # type: ignore
        sys.exit(f"File not found: {args.file}")
    if args.no_mount: # type: ignore
        return mpremote(port, "run", args.file)
    mount_dir = args.mount_dir # type: ignore
    if not os.path.isdir(mount_dir): # type: ignore
        sys.exit(f"Mount folder not found: {mount_dir}")
    print(f"Mounting {os.path.abspath(mount_dir)} (nothing is uploaded)") # type: ignore
    return mpremote(port, "mount", mount_dir, "run", args.file)


def cmd_repl(args):
    port = need_port(args)
    return mpremote(port, "repl")


def cmd_ls(args):
    port = need_port(args)
    return mpremote(port, "ls")


def cmd_reset(args):
    port = need_port(args)
    return mpremote(port, "reset")


def cmd_rm(args):
    port = need_port(args)
    return mpremote(port, "rm", f":{args.file}")


# ------------------------------------------------------------------- main
def build_parser():
    ap = argparse.ArgumentParser(description="ESP32-S3 MicroPython helper")
    ap.add_argument("-p", "--port", help="serial port, e.g. COM5 (default: auto-detect)")
    sub = ap.add_subparsers(dest="command", required=True)

    sub.add_parser("ports", help="list serial ports").set_defaults(func=cmd_ports)
    sub.add_parser("erase", help="erase flash").set_defaults(func=cmd_erase)

    f = sub.add_parser("flash", help="flash firmware .bin")
    f.add_argument("firmware", help="path to the .bin file")
    f.add_argument("--baud", type=int, default=460800)
    f.set_defaults(func=cmd_flash)

    u = sub.add_parser("upload", help="upload project files to the board")
    u.add_argument("folder", nargs="?", default=".", help="project folder (default: .)")
    u.set_defaults(func=cmd_upload)

    r = sub.add_parser("run", help="run a file (mounts the project folder, no upload)")
    r.add_argument("file", nargs="?", default="main.py")
    r.add_argument("--mount-dir", default=".", help="folder to mount (default: .)")
    r.add_argument("--no-mount", action="store_true", help="run without mounting")
    r.set_defaults(func=cmd_run)

    sub.add_parser("repl", help="open the REPL").set_defaults(func=cmd_repl)
    sub.add_parser("ls", help="list files on the board").set_defaults(func=cmd_ls)
    sub.add_parser("reset", help="reboot the board").set_defaults(func=cmd_reset)

    d = sub.add_parser("rm", help="delete a file on the board")
    d.add_argument("file")
    d.set_defaults(func=cmd_rm)
    return ap


def main():
    args = build_parser().parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()