#!/usr/bin/env python3
"""
generate_json.py — Gera data/articles.json para o GitHub Pages.
Chamado pelo GitHub Actions a cada 15 minutos.
"""

import json
import datetime
import pathlib
import logging

from scraper import run_all, dedupe
from rss_reader import fetch_all_rss

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S',
)
log = logging.getLogger(__name__)


def main() -> None:
    pathlib.Path('data').mkdir(exist_ok=True)

    log.info("── Feeds RSS ───────────────────────────────────────")
    rss_arts = fetch_all_rss()
    log.info(f"RSS: {len(rss_arts)} artigos")

    log.info("── Scraping (fontes sem RSS) ───────────────────────")
    scraped = run_all()
    log.info(f"Scraping: {len(scraped)} artigos")

    all_articles = dedupe(rss_arts + scraped)
    log.info(f"Total único: {len(all_articles)} artigos")

    now = datetime.datetime.utcnow()

    payload = {
        "generated_at": now.isoformat() + "Z",
        "generated_at_br": now.strftime("%d/%m/%Y %H:%M") + " UTC",
        "total": len(all_articles),
        "articles": [
            {
                "source":      a.source,
                "group":       a.group,
                "title":       a.title,
                "link":        a.link,
                "date":        a.date.isoformat() if a.date else None,
                "description": a.description,
            }
            for a in sorted(
                all_articles,
                key=lambda a: a.date or datetime.datetime.min,
                reverse=True,
            )
        ],
    }

    out = pathlib.Path('data/articles.json')
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    log.info(f"Salvo: {out} ({len(all_articles)} artigos)")


if __name__ == '__main__':
    main()
