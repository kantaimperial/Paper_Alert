import requests


def get_abstract_by_doi(doi: str) -> str:
    """Best-effort fetch of an abstract for a paper found elsewhere (e.g.
    Crossref) that lacks one, using Semantic Scholar's DOI lookup."""
    if not doi:
        return ""
    url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}"
    try:
        resp = requests.get(url, params={"fields": "abstract"}, timeout=15)
        if resp.ok:
            return resp.json().get("abstract") or ""
    except requests.RequestException:
        pass
    return ""
