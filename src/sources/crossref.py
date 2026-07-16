import requests

from src.config import CROSSREF_MAILTO
from src.models import Paper

BASE_URL = "https://api.crossref.org/works"


def search_journal(
    journal: str, keywords: list, date_from: str, date_to: str, tier: int, rows: int = 60
) -> list:
    # Crossref's bibliographic query is a plain relevance search (no boolean
    # operators), so we just hand it every keyword we care about and rely on
    # src.filtering to apply the real match afterwards.
    bibliographic_query = " ".join(keywords)
    params = {
        "query.bibliographic": bibliographic_query,
        "query.container-title": journal,
        "filter": f"from-pub-date:{date_from},until-pub-date:{date_to},type:journal-article",
        "rows": rows,
        "mailto": CROSSREF_MAILTO,
    }
    resp = requests.get(BASE_URL, params=params, timeout=30)
    resp.raise_for_status()
    items = resp.json().get("message", {}).get("items", [])

    papers = []
    for item in items:
        container = item.get("container-title") or [""]
        title = item.get("title") or [""]
        authors = [
            f"{a.get('given', '')} {a.get('family', '')}".strip()
            for a in item.get("author", [])
        ]
        date_parts = (
            item.get("published-print", item.get("published-online", {})).get(
                "date-parts", [[]]
            )[0]
        )
        published = "-".join(f"{p:02d}" if i else str(p) for i, p in enumerate(date_parts))
        papers.append(
            Paper(
                source="crossref",
                tier=tier,
                title=title[0] if title else "",
                authors=authors,
                venue=container[0] if container else journal,
                published=published,
                doi=item.get("DOI", ""),
                url=item.get("URL", ""),
                abstract=_clean_abstract(item.get("abstract", "")),
            )
        )
    return papers


def _clean_abstract(raw: str) -> str:
    # Crossref abstracts are JATS XML; strip tags for a plain-text version.
    import re

    return re.sub(r"<[^>]+>", " ", raw).strip()
