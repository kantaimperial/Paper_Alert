import xml.etree.ElementTree as ET

import requests

from src.models import Paper

BASE_URL = "https://export.arxiv.org/api/query"

NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
}


def search(keywords: list, date_from: str, date_to: str, tier: int, max_results: int = 50) -> list:
    # arXiv has no separate relevance-ranking step like Crossref, so we OR all
    # keywords together and rely on src.filtering for the real match, same as
    # the Crossref sources.
    keyword_query = " OR ".join(f'all:"{kw}"' for kw in keywords)
    date_range = f"submittedDate:[{date_from.replace('-', '')}0000 TO {date_to.replace('-', '')}2359]"
    search_query = f"({keyword_query}) AND {date_range}"

    params = {
        "search_query": search_query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    resp = requests.get(BASE_URL, params=params, timeout=30)
    resp.raise_for_status()
    root = ET.fromstring(resp.text)

    papers = []
    for entry in root.findall("atom:entry", NS):
        title = (entry.findtext("atom:title", default="", namespaces=NS) or "").strip()
        summary = (entry.findtext("atom:summary", default="", namespaces=NS) or "").strip()
        published = (entry.findtext("atom:published", default="", namespaces=NS) or "")[:10]
        url = entry.findtext("atom:id", default="", namespaces=NS) or ""
        doi = entry.findtext("arxiv:doi", default="", namespaces=NS) or ""
        authors = [
            (author.findtext("atom:name", default="", namespaces=NS) or "").strip()
            for author in entry.findall("atom:author", NS)
        ]
        papers.append(
            Paper(
                source="arxiv",
                tier=tier,
                title=title,
                authors=authors,
                venue="arXiv",
                published=published,
                doi=doi,
                url=url,
                abstract=summary,
            )
        )
    return papers
