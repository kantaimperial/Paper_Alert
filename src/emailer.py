import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.config import GMAIL_ADDRESS, GMAIL_APP_PASSWORD
from src.models import Paper
from src.summarize import summarize_paper

TIER_LABELS = {1: "Tier 1 (Nature / Science)", 2: "Tier 2 (JACS)", 3: "Tier 3 (その他)"}


def _paper_block(paper: Paper) -> str:
    summary = summarize_paper(paper)
    authors = ", ".join(paper.authors[:5])
    if len(paper.authors) > 5:
        authors += " et al."
    lines = [
        f"■ {paper.title}",
        f"  誌名: {paper.venue}  発行日: {paper.published}",
        f"  著者: {authors}",
    ]
    if paper.doi:
        lines.append(f"  DOI: {paper.doi} (https://doi.org/{paper.doi})")
    if paper.url and paper.url != f"https://doi.org/{paper.doi}":
        lines.append(f"  リンク: {paper.url}")
    lines.append(f"  要約: {summary}")
    return "\n".join(lines) + "\n"


def build_digest(papers: list, date_from: str, date_to: str) -> str:
    lines = [f"論文アラート ({date_from} 〜 {date_to})", f"該当件数: {len(papers)}件", ""]
    for tier in (1, 2, 3):
        tier_papers = [p for p in papers if p.tier == tier]
        if not tier_papers:
            continue
        lines.append(f"--- {TIER_LABELS[tier]} ---")
        lines.append("")
        for paper in tier_papers:
            lines.append(_paper_block(paper))
    return "\n".join(lines)


def send_alert(papers: list, recipient_email: str, date_from: str, date_to: str) -> None:
    body = build_digest(papers, date_from, date_to)

    msg = MIMEMultipart()
    msg["Subject"] = f"[Paper Alert] {len(papers)}件の新着論文 ({date_from} 〜 {date_to})"
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = recipient_email
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.send_message(msg)
