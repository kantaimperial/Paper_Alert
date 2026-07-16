import re


def _term_matches(text_low: str, term: str) -> bool:
    # word-boundary match for short terms (e.g. element symbols like Bi,
    # Pb) to avoid matching them inside unrelated words; plain substring
    # for multi-word phrases and longer single words.
    if len(term) <= 2:
        return bool(re.search(rf"\b{re.escape(term.lower())}\b", text_low))
    return term.lower() in text_low


def _contains_any(text: str, terms: list) -> bool:
    text_low = text.lower()
    return any(_term_matches(text_low, term) for term in terms)


def match_priority(text: str, keywords: list) -> bool:
    """Medium match used for priority_journals: any keyword."""
    return _contains_any(text, keywords)


def match_flagship(text: str, keywords: list, broad_terms: list) -> bool:
    """Broad match used for flagship_journals: keywords plus broader terms."""
    return match_priority(text, keywords) or _contains_any(text, broad_terms)


def relevance_score(text: str, keywords: list) -> int:
    """Count of distinct keywords matched in text, used to rank matches."""
    text_low = text.lower()
    return sum(1 for term in keywords if _term_matches(text_low, term))


def dedupe(papers: list) -> list:
    seen = set()
    result = []
    for paper in papers:
        key = paper.dedup_key()
        if key in seen:
            continue
        seen.add(key)
        result.append(paper)
    return result
