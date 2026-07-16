"""Registers/unregisters the periodic run as a Windows Task Scheduler task (Windows-only)."""

import json
import subprocess
import sys
from pathlib import Path

from src.config import ROOT_DIR

TASK_NAME = "PaperAlertRun"
STATE_FILE = ROOT_DIR / "state" / "schedule_windows.json"

# schtasks /d expects English 3-letter day codes; 0/1/.../6 = Sun/Mon/.../Sat,
# matching the macOS backend's Weekday numbering for a consistent UI.
WEEKDAY_LABELS = {1: "月", 2: "火", 3: "水", 4: "木", 5: "金", 6: "土", 0: "日"}
WEEKDAY_ORDER = [1, 2, 3, 4, 5, 6, 0]
_SCHTASKS_DAY_CODES = {1: "MON", 2: "TUE", 3: "WED", 4: "THU", 5: "FRI", 6: "SAT", 0: "SUN"}


def python_executable() -> str:
    venv_scripts = ROOT_DIR / "venv" / "Scripts"
    for name in ("pythonw.exe", "python.exe"):
        candidate = venv_scripts / name
        if candidate.exists():
            return str(candidate)
    return sys.executable


def is_installed() -> bool:
    result = subprocess.run(
        ["schtasks", "/query", "/tn", TASK_NAME],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def current_schedule() -> dict | None:
    """Returns {"frequency", "hour", "minute", "weekdays"} for the installed task, or None.

    schtasks' human-readable output is locale-dependent and unreliable to parse, so we
    keep our own record of what we asked for alongside the real task.
    """
    if not is_installed() or not STATE_FILE.exists():
        return None
    return json.loads(STATE_FILE.read_text())


def install_schedule(frequency: str, hour: int, minute: int, weekdays: list[int] | None = None) -> None:
    uninstall_schedule()
    time_str = f"{hour:02d}:{minute:02d}"
    command = f'"{python_executable()}" "{ROOT_DIR / "main.py"}"'

    if frequency == "daily":
        args = ["/sc", "daily"]
    elif frequency == "weekly":
        if not weekdays:
            raise ValueError("weekly frequency requires at least one weekday")
        days = ",".join(_SCHTASKS_DAY_CODES[wd] for wd in weekdays)
        args = ["/sc", "weekly", "/d", days]
    else:
        raise ValueError(f"unknown frequency: {frequency}")

    subprocess.run(
        ["schtasks", "/create", "/tn", TASK_NAME, "/tr", command, "/st", time_str, "/f"] + args,
        check=True,
    )

    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(
        json.dumps({"frequency": frequency, "hour": hour, "minute": minute, "weekdays": weekdays or []})
    )


def uninstall_schedule() -> None:
    subprocess.run(["schtasks", "/delete", "/tn", TASK_NAME, "/f"], capture_output=True)
    if STATE_FILE.exists():
        STATE_FILE.unlink()
