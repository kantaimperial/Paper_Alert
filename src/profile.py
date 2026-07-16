from dataclasses import dataclass, field
from pathlib import Path

import yaml

from src.config import ROOT_DIR

PROFILE_FILE = ROOT_DIR / "profile.yaml"


@dataclass
class Profile:
    recipient_email: str
    keywords: list = field(default_factory=list)
    broad_terms: list = field(default_factory=list)
    flagship_journals: list = field(default_factory=list)
    priority_journals: list = field(default_factory=list)


def load_profile(path: Path = PROFILE_FILE) -> Profile:
    if not path.exists():
        raise FileNotFoundError(
            f"{path} が見つかりません。`python setup.py` を実行してプロファイルを作成してください。"
        )
    data = yaml.safe_load(path.read_text()) or {}
    return Profile(
        recipient_email=data.get("recipient_email", ""),
        keywords=data.get("keywords", []),
        broad_terms=data.get("broad_terms", []),
        flagship_journals=data.get("flagship_journals", []),
        priority_journals=data.get("priority_journals", []),
    )


def save_profile(profile: Profile, path: Path = PROFILE_FILE) -> None:
    data = {
        "recipient_email": profile.recipient_email,
        "keywords": profile.keywords,
        "broad_terms": profile.broad_terms,
        "flagship_journals": profile.flagship_journals,
        "priority_journals": profile.priority_journals,
    }
    path.write_text(yaml.dump(data, allow_unicode=True, sort_keys=False))
