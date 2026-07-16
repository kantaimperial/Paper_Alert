"""Picks the macOS (launchd) or Windows (Task Scheduler) auto-run backend."""

import platform

if platform.system() == "Windows":
    from src.scheduler_windows import (
        ROOT_DIR,
        WEEKDAY_LABELS,
        WEEKDAY_ORDER,
        current_schedule,
        install_schedule,
        is_installed,
        python_executable,
        uninstall_schedule,
    )
else:
    from src.scheduler_macos import (
        ROOT_DIR,
        WEEKDAY_LABELS,
        WEEKDAY_ORDER,
        current_schedule,
        install_schedule,
        is_installed,
        python_executable,
        uninstall_schedule,
    )

__all__ = [
    "ROOT_DIR",
    "WEEKDAY_LABELS",
    "WEEKDAY_ORDER",
    "current_schedule",
    "install_schedule",
    "is_installed",
    "python_executable",
    "uninstall_schedule",
]
