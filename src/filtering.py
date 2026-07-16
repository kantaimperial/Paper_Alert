import re


def _contains_any(text: str, terms: list) -> bool:
    text_low = text.lower()
    for term in terms:
        # word-boundary match for short terms (e.g. element symbols like Bi,
        # Pb) to avoid matching them inside unrelated words; plain substring
        # for multi-word phrases and longer single words.
        if len(term) <= 2:
            if re.search(rf"\b{re.escape(term.lower())}\b", text_low):
                return True
        elif term.lower() in text_low:
            return True
    return False


def match_priority(text: str, keywords: list) -> bool:
    """Medium match used for priority_journals: any keyword."""
    return _contains_any(text, keywords)


def match_flagship(text: str, keywords: list, broad_terms: list) -> bool:
    """Broad match used for flagship_journals: keywords plus broader terms."""
    return match_priority(text, keywords) or _contains_any(text, broad_terms)


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
