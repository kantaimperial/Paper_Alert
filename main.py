from datetime import date, timedelta

from src.config import LOOKBACK_DAYS_DEFAULT
from src.emailer import send_alert
from src.filtering import dedupe, match_flagship, match_priority
from src.models import Paper
from src.profile import load_profile
from src.sources import crossref, semantic_scholar
from src.state import load_last_run, save_last_run


def run() -> None:
    profile = load_profile()

    today = date.today()
    date_to = today.isoformat()
    last_run = load_last_run()
    date_from = last_run or (today - timedelta(days=LOOKBACK_DAYS_DEFAULT)).isoformat()

    papers: list[Paper] = []
    for journal in profile.flagship_journals:
        papers += crossref.search_journal(journal, profile.keywords, date_from, date_to, tier=1)
    for journal in profile.priority_journals:
        papers += crossref.search_journal(journal, profile.keywords, date_from, date_to, tier=2)

    papers = dedupe(papers)
    matched = []
    for paper in papers:
        text = f"{paper.title} {paper.abstract}"
        if paper.tier == 1:
            is_match = match_flagship(text, profile.keywords, profile.broad_terms)
        else:
            is_match = match_priority(text, profile.keywords)
        if is_match:
            matched.append(paper)

    for paper in matched:
        if not paper.abstract and paper.doi:
            paper.abstract = semantic_scholar.get_abstract_by_doi(paper.doi)

    if matched:
        matched.sort(key=lambda p: (p.tier, p.published))
        send_alert(matched, profile.recipient_email, date_from, date_to)
        print(f"Sent alert for {len(matched)} paper(s).")
    else:
        print("No matching papers found.")

    save_last_run(date_to)


if __name__ == "__main__":
    run()
