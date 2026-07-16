import json

from src.config import STATE_FILE, STATE_DIR


def load_last_run() -> str | None:
    if not STATE_FILE.exists():
        return None
    return json.loads(STATE_FILE.read_text()).get("last_run")


def save_last_run(date_str: str) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps({"last_run": date_str}))
