#!/usr/bin/env python3
"""
test.py - checks that your ESP32-S3 + MicroPython setup works (runs on your PC).

Usage:
    python test.py              auto-detect the port
    python test.py COM5         use a specific port

Put this file in the same folder as run.py.
Close any REPL / serial monitor first, since only one program can use the port.
"""

import importlib.util
import subprocess
import sys

from run import find_port  # reuse the port detection from run.py

PASS, FAIL, INFO = "[PASS]", "[FAIL]", "[INFO]"
results = []


def record(ok, name, detail=""):
    results.append(ok)
    print(f"{PASS if ok else FAIL} {name}" + (f" - {detail}" if detail else ""))


def board_exec(port, code, timeout=20):
    """Run a snippet of Python on the board, return (ok, output)."""
    try:
        p = subprocess.run(
            [sys.executable, "-m", "mpremote", "connect", port, "exec", code], # type: ignore
            capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return False, "timed out (is the port busy or the board not in REPL?)"
    out = (p.stdout + p.stderr).strip() # type: ignore
    return p.returncode == 0, out


def main():
    port = sys.argv[1] if len(sys.argv) > 1 else find_port()

    # 1. Tools installed
    for mod in ("esptool", "mpremote", "serial"):
        found = importlib.util.find_spec(mod) is not None
        record(found, f"{mod} installed", "" if found else f"run: python -m pip install {'pyserial' if mod == 'serial' else mod}")

    # 2. Port found
    record(bool(port), "serial port found", port or "plug in the board or pass a port, e.g. python test.py COM5")
    if not port:
        return finish()

    # 3. Board responds
    ok, out = board_exec(port, "print('hello from esp32')")
    record(ok and "hello from esp32" in out, "board responds", out.splitlines()[-1] if out else "")
    if not ok:
        print(f"{INFO} If this fails: check the cable, close other serial programs, or reflash MicroPython.")
        return finish()

    # 4. MicroPython + ESP32-S3
    ok, out = board_exec(port, "import sys, os; print(sys.implementation.name); print(os.uname().machine); print(os.uname().release)")
    lines = out.splitlines()
    record(ok and "micropython" in out.lower(), "MicroPython firmware", lines[-1] if lines else "")
    record(ok and "esp32s3" in out.lower().replace("-", ""), "chip is ESP32-S3", " | ".join(lines[1:2]))

    # 5. Memory
    ok, out = board_exec(port, "import gc; gc.collect(); print(gc.mem_free())")
    try:
        free = int(out.splitlines()[-1])
        record(free > 20000, "free RAM", f"{free:,} bytes")
    except (ValueError, IndexError):
        record(False, "free RAM", out)

    # 6. Filesystem write/read/delete
    code = (
        "f = open('_t.txt', 'w'); f.write('ok'); f.close();"
        "print(open('_t.txt').read());"
        "import os; os.remove('_t.txt')"
    )
    ok, out = board_exec(port, code)
    record(ok and out.splitlines()[-1:] == ["ok"], "filesystem read/write", out.splitlines()[-1] if out else "")

    # 7. Import from board filesystem (like main.py importing other files)
    code = (
        "open('_mod.py','w').write('VALUE = 42\\n');"
        "import _mod; print(_mod.VALUE);"
        "import os, sys; os.remove('_mod.py'); sys.modules.pop('_mod', None)"
    )
    ok, out = board_exec(port, code)
    record(ok and out.splitlines()[-1:] == ["42"], "importing a module from the board", out.splitlines()[-1] if out else "")

    # 8. Info only: files on the board
    ok, out = board_exec(port, "import os; print(os.listdir())")
    if ok:
        print(f"{INFO} files on board: {out}")

    finish()


def finish():
    passed, total = sum(results), len(results)
    print(f"\n{passed}/{total} checks passed")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()