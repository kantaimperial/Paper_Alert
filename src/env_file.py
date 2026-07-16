"""Writes .env with the credentials the app's pipeline reads at import time."""

from src.config import GEMINI_MODEL_DEFAULT, ROOT_DIR

ENV_FILE = ROOT_DIR / ".env"


def save_env(
    gemini_api_key: str,
    gmail_address: str,
    gmail_app_password: str,
    gemini_model: str = GEMINI_MODEL_DEFAULT,
) -> None:
    content = (
        "# Japanese abstract translation/summary runs via the Gemini API (free tier).\n"
        "# Get a key at https://aistudio.google.com/apikey\n"
        f"GEMINI_API_KEY={gemini_api_key}\n"
        "# Model used for summarization. Flash-Lite models tend to have more\n"
        "# generous free-tier rate limits than full Flash models.\n"
        f"GEMINI_MODEL={gemini_model}\n"
        "\n"
        "# Gmail account used to send the alert\n"
        f"GMAIL_ADDRESS={gmail_address}\n"
        "# Generate at https://myaccount.google.com/apppasswords (requires 2-Step Verification enabled)\n"
        f"GMAIL_APP_PASSWORD={gmail_app_password}\n"
    )
    ENV_FILE.write_text(content)
