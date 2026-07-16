from dataclasses import dataclass, field


@dataclass
class Paper:
    source: str  # "semantic_scholar" | "arxiv" | "crossref"
    tier: int  # 1 = Nature/Science family, 2 = JACS, 3 = keyword match elsewhere
    title: str
    authors: list = field(default_factory=list)
    venue: str = ""
    published: str = ""  # YYYY-MM-DD
    doi: str = ""
    url: str = ""
    abstract: str = ""

    def dedup_key(self) -> str:
        if self.doi:
            return f"doi:{self.doi.lower()}"
        return f"title:{self.title.strip().lower()}"
