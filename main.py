import argparse
from datetime import date, timedelta

from src.config import LOOKBACK_DAYS_DEFAULT
from src.emailer import send_alert
from src.filtering import dedupe, match_flagship, match_priority, relevance_score
from src.models import Paper
from src.profile import load_profile
from src.sources import arxiv, crossref, semantic_scholar
from src.state import load_last_run, save_last_run


def run(date_from: str | None = None, save_state: bool = True) -> None:
    profile = load_profile()

    today = date.today()
    date_to = today.isoformat()
    if date_from is None:
        last_run = load_last_run()
        date_from = last_run or (today - timedelta(days=LOOKBACK_DAYS_DEFAULT)).isoformat()

    papers: list[Paper] = []
    for journal in profile.flagship_journals:
        papers += crossref.search_journal(journal, profile.keywords, date_from, date_to, tier=1)
    for journal in profile.priority_journals:
        papers += crossref.search_journal(journal, profile.keywords, date_from, date_to, tier=2)
    if profile.include_arxiv:
        papers += arxiv.search(profile.keywords, date_from, date_to, tier=3)
    if profile.include_chemrxiv:
        papers += crossref.search_chemrxiv(profile.keywords, date_from, date_to, tier=3)

    papers = dedupe(papers)
    matched = []
    for paper in papers:
        text = f"{paper.title} {paper.abstract}"
        if paper.tier == 1:
            is_match = match_flagship(text, profile.keywords, profile.broad_terms)
        else:
            is_match = match_priority(text, profile.keywords)
        if is_match:
            paper.relevance = relevance_score(text, profile.keywords)
            matched.append(paper)

    # arXiv/ChemRxiv aren't a curated list like the watched journals, so they
    # can vastly outnumber journal matches; cap each to its own allowance
    # (keeping the most relevant ones) before combining with journal matches.
    journal_matches = [p for p in matched if p.source not in ("arxiv", "chemrxiv")]
    arxiv_matches = sorted(
        (p for p in matched if p.source == "arxiv"), key=lambda p: -p.relevance
    )[: profile.max_arxiv_papers]
    chemrxiv_matches = sorted(
        (p for p in matched if p.source == "chemrxiv"), key=lambda p: -p.relevance
    )[: profile.max_chemrxiv_papers]
    matched = journal_matches + arxiv_matches + chemrxiv_matches
    matched.sort(key=lambda p: (p.tier, -p.relevance))
    matched = matched[: profile.max_total_papers]

    for paper in matched:
        if not paper.abstract and paper.doi:
            paper.abstract = semantic_scholar.get_abstract_by_doi(paper.doi)

    if matched:
        send_alert(matched, profile.recipient_email, date_from, date_to, profile.summary_language)
        print(f"Sent alert for {len(matched)} paper(s).")
    else:
        print("No matching papers found.")

    if save_state:
        save_last_run(date_to)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--since",
        metavar="YYYY-MM-DD",
        help="Search from this date instead of state/last_run.json (for test runs).",
    )
    parser.add_argument(
        "--no-save-state",
        action="store_true",
        help="Don't update state/last_run.json after this run (for test runs).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    run(date_from=args.since, save_state=not args.no_save_state)
