"""Registers/unregisters the periodic run as a macOS launchd LaunchAgent."""

import os
import plistlib
import subprocess
import sys
from pathlib import Path

from src.config import ROOT_DIR

LABEL = "com.paperalert.run"
LAUNCH_AGENTS_DIR = Path.home() / "Library" / "LaunchAgents"
PLIST_PATH = LAUNCH_AGENTS_DIR / f"{LABEL}.plist"
LOG_DIR = ROOT_DIR / "logs"

# launchd Weekday: 0 and 7 are Sunday, 1 is Monday, ... 6 is Saturday.
WEEKDAY_LABELS = {1: "月", 2: "火", 3: "水", 4: "木", 5: "金", 6: "土", 0: "日"}
WEEKDAY_ORDER = [1, 2, 3, 4, 5, 6, 0]


def _calendar_interval(frequency: str, hour: int, minute: int, weekdays: list[int] | None):
    if frequency == "daily":
        return {"Hour": hour, "Minute": minute}
    if frequency == "weekly":
        if not weekdays:
            raise ValueError("weekly frequency requires at least one weekday")
        return [{"Weekday": wd, "Hour": hour, "Minute": minute} for wd in weekdays]
    raise ValueError(f"unknown frequency: {frequency}")


def python_executable() -> str:
    venv_python = ROOT_DIR / "venv" / "bin" / "python3"
    return str(venv_python) if venv_python.exists() else sys.executable


def build_plist(frequency: str, hour: int, minute: int, weekdays: list[int] | None = None) -> dict:
    return {
        "Label": LABEL,
        "ProgramArguments": [python_executable(), str(ROOT_DIR / "main.py")],
        "WorkingDirectory": str(ROOT_DIR),
        "StartCalendarInterval": _calendar_interval(frequency, hour, minute, weekdays),
        "StandardOutPath": str(LOG_DIR / "paper-alert.log"),
        "StandardErrorPath": str(LOG_DIR / "paper-alert.err.log"),
    }


def is_installed() -> bool:
    return PLIST_PATH.exists()


def current_schedule() -> dict | None:
    """Returns {"frequency", "hour", "minute", "weekdays"} for the installed job, or None."""
    if not PLIST_PATH.exists():
        return None
    with open(PLIST_PATH, "rb") as f:
        plist = plistlib.load(f)
    interval = plist.get("StartCalendarInterval")
    if isinstance(interval, list):
        return {
            "frequency": "weekly",
            "hour": interval[0].get("Hour", 9),
            "minute": interval[0].get("Minute", 0),
            "weekdays": [entry.get("Weekday", 0) for entry in interval],
        }
    return {
        "frequency": "daily",
        "hour": interval.get("Hour", 9),
        "minute": interval.get("Minute", 0),
        "weekdays": [],
    }


def install_schedule(frequency: str, hour: int, minute: int, weekdays: list[int] | None = None) -> Path:
    uninstall_schedule()
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    LAUNCH_AGENTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(PLIST_PATH, "wb") as f:
        plistlib.dump(build_plist(frequency, hour, minute, weekdays), f)
    subprocess.run(
        ["launchctl", "bootstrap", f"gui/{os.getuid()}", str(PLIST_PATH)],
        check=True,
    )
    return PLIST_PATH


def uninstall_schedule() -> None:
    if not PLIST_PATH.exists():
        return
    # Fails harmlessly if the job isn't currently loaded (e.g. after a reboot).
    subprocess.run(
        ["launchctl", "bootout", f"gui/{os.getuid()}/{LABEL}"],
        check=False,
    )
    PLIST_PATH.unlink()
