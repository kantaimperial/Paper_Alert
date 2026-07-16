import requests

from src.config import GEMINI_API_KEY
from src.models import Paper

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"
GEMINI_MODEL = "gemini-3.5-flash"

SYSTEM_PROMPT = (
    "あなたは無機材料化学の専門家です。与えられた論文のタイトルと要旨を読み、"
    "日本語で3〜4文に要約してください。何が新しいか・なぜ重要かが伝わるように"
    "書いてください。専門用語はそのまま使って構いません。"
    "要約以外の文章（前置きや後書き）は出力しないでください。"
)


def summarize_paper(paper: Paper) -> str:
    """Return a short Japanese summary of the paper's abstract, via the Gemini API."""
    if not paper.abstract:
        return "(要旨なし)"
    try:
        response = requests.post(
            GEMINI_URL,
            headers={"x-goog-api-key": GEMINI_API_KEY},
            json={
                "model": GEMINI_MODEL,
                "system_instruction": SYSTEM_PROMPT,
                "input": f"タイトル: {paper.title}\n\n要旨:\n{paper.abstract}",
            },
            timeout=60,
        )
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
        return f"(要約失敗: Gemini APIに接続できませんでした - {exc})"
