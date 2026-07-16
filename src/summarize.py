import re
import time

import requests

from src.config import GEMINI_API_KEY, GEMINI_MODEL
from src.models import Paper

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"

# Free tier allows ~20 requests/minute; space calls out to stay under that.
MIN_REQUEST_INTERVAL = 3.5

_last_request_at = 0.0

SYSTEM_PROMPTS = {
    "ja": (
        "あなたは無機材料化学の専門家です。与えられた論文のタイトルと要旨を読み、"
        "同業の研究者が一目で要点を掴めるように、日本語で1〜2文・80文字程度に"
        "要約してください。要旨の文章をそのまま訳すのではなく、「何をやって・"
        "何が新しく分かったか」だけに絞り込んでください。専門用語はそのまま"
        "使って構いません。要約以外の文章（前置きや後書き）は出力しないでください。"
    ),
    "en": (
        "You are an expert in inorganic materials chemistry. Read the given paper's "
        "title and abstract, and write a 1-2 sentence summary a fellow researcher "
        "could grasp at a glance. Do not just paraphrase the abstract sentence by "
        "sentence - distill it down to what was done and what's newly shown. "
        "Technical terms may be used as-is. Output only the summary, with no "
        "preamble or closing remarks."
    ),
}


def _throttle() -> None:
    global _last_request_at
    wait = MIN_REQUEST_INTERVAL - (time.monotonic() - _last_request_at)
    if wait > 0:
        time.sleep(wait)
    _last_request_at = time.monotonic()


def _retry_delay_seconds(response) -> float:
    # Gemini's 429 body includes "Please retry in 40.8s"; honor that instead
    # of guessing, with a safe fallback if the message format ever changes.
    try:
        message = response.json().get("error", {}).get("message", "")
    except ValueError:
        message = ""
    match = re.search(r"retry in ([\d.]+)s", message)
    return float(match.group(1)) + 2 if match else 60.0


def _request_gemini(paper: Paper, system_prompt: str):
    _throttle()
    return requests.post(
        GEMINI_URL,
        headers={"x-goog-api-key": GEMINI_API_KEY},
        json={
            "model": GEMINI_MODEL,
            "system_instruction": system_prompt,
            "input": f"タイトル: {paper.title}\n\n要旨:\n{paper.abstract}",
        },
        timeout=60,
    )


def summarize_paper(paper: Paper, language: str = "ja") -> str:
    """Return a short summary of the paper's abstract, via the Gemini API."""
    if not paper.abstract:
        return "(要旨なし)" if language == "ja" else "(no abstract)"
    system_prompt = SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS["ja"])
    try:
        response = _request_gemini(paper, system_prompt)
        if response.status_code == 429:
            # Still over the free-tier rate limit despite throttling; wait out
            # the window the API tells us to, once, before giving up.
            time.sleep(_retry_delay_seconds(response))
            response = _request_gemini(paper, system_prompt)
        response.raise_for_status()
        data = response.json()
        for step in data.get("steps", []):
            if step.get("type") == "model_output":
                texts = [
                    block["text"]
                    for block in step.get("content", [])
                    if block.get("type") == "text"
                ]
                if texts:
                    return "".join(texts).strip()
        return "(要約失敗: レスポンスを解析できませんでした)"
    except requests.RequestException as exc:
        return f"(要約失敗: Gemini APIへのリクエストが失敗しました - {exc})"
