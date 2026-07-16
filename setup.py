"""Interactive wizard that creates profile.yaml."""

from pathlib import Path

from src.profile import PROFILE_FILE, Profile, save_profile

DEFAULT_FLAGSHIP_JOURNALS = [
    "Nature",
    "Science",
    "Nature Materials",
    "Nature Chemistry",
    "Nature Energy",
    "Nature Communications",
    "Nature Nanotechnology",
    "Science Advances",
]


def _prompt_list(message: str, default: list | None = None) -> list:
    default_hint = f" [Enterで既定値: {', '.join(default)}]" if default else ""
    raw = input(f"{message}{default_hint}\n> ").strip()
    if not raw:
        return list(default) if default else []
    return [item.strip() for item in raw.split(",") if item.strip()]


def main() -> None:
    print("=== paper-alert セットアップ ===")
    print("キーワード・重視する雑誌・メールアドレスを設定します。")
    print()

    if PROFILE_FILE.exists():
        overwrite = input(f"{PROFILE_FILE.name} は既に存在します。上書きしますか？ [y/N] > ").strip().lower()
        if overwrite != "y":
            print("中止しました。")
            return

    recipient_email = input("アラートを受け取るメールアドレス: ").strip()

    print()
    print("アラートしたいキーワードをカンマ区切りで入力してください（元素名・分子名・応用分野など）。")
    print("例: perovskite, organic semiconductor, charge transport")
    keywords = _prompt_list("キーワード")

    print()
    print("Nature/Science系(最上位誌)だけに使う、より広い一致条件を追加できます（任意）。")
    print("例: semiconductor, nanomaterials")
    broad_terms = _prompt_list("広い一致条件（空欄でスキップ）")

    print()
    print("Nature/Science系の監視対象誌をカンマ区切りで入力してください。")
    flagship_journals = _prompt_list("Nature/Science系の雑誌", default=DEFAULT_FLAGSHIP_JOURNALS)

    print()
    print("あなたの専門分野のトップジャーナル（ACS/RSC/Wileyなど）をカンマ区切りで入力してください。")
    print("例: Journal of the American Chemical Society, Advanced Materials, Chemical Science")
    priority_journals = _prompt_list("専門分野の雑誌")

    profile = Profile(
        recipient_email=recipient_email,
        keywords=keywords,
        broad_terms=broad_terms,
        flagship_journals=flagship_journals,
        priority_journals=priority_journals,
    )
    save_profile(profile)

    print()
    print(f"✓ {PROFILE_FILE.name} を作成しました。")
    print()
    print("次の手順:")
    print("  1. .env.example を .env にコピーし、GEMINI_API_KEY と Gmailアプリパスワードを設定")
    print("     (Geminiキーは https://aistudio.google.com/apikey で無料発行)")
    print("  2. python main.py で実行")


if __name__ == "__main__":
    main()
