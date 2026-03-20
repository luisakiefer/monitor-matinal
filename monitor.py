#!/usr/bin/env python3
"""
monitor.py — Monitor Matinal · Ponto de entrada unificado
Combina RSS + scraping e exporta para XLSX.

Uso:
  python monitor.py               # RSS + scraping → XLSX
  python monitor.py --rss-only    # só feeds RSS
  python monitor.py --scrape-only # só scraping (sem RSS)
  python monitor.py --out arquivo.xlsx
"""

import sys
import logging
import datetime
import argparse

from scraper import Article, dedupe, export_xlsx
from rss_reader import fetch_all_rss
from scraper import run_all as run_scraper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S',
)
log = logging.getLogger(__name__)

BANNER = """\
╔══════════════════════════════════════════════════════╗
║       Matinal · Monitor de Notícias                 ║
║       RSS + Scraping → XLSX                         ║
╚══════════════════════════════════════════════════════╝"""


def main() -> None:
    parser = argparse.ArgumentParser(description='Monitor Matinal — coleta unificada')
    parser.add_argument('--rss-only',    action='store_true', help='Apenas feeds RSS')
    parser.add_argument('--scrape-only', action='store_true', help='Apenas scraping')
    parser.add_argument('--out', metavar='ARQUIVO.xlsx',
                        help='Caminho de saída (padrão: matinal-YYYY-MM-DD.xlsx)')
    args = parser.parse_args()

    print(BANNER)
    print()

    all_articles: list[Article] = []

    # ── 1. Feeds RSS ─────────────────────────────────────────────────────────
    if not args.scrape_only:
        print("── Buscando feeds RSS ──────────────────────────────────")
        rss_arts = fetch_all_rss()
        print(f"   RSS: {len(rss_arts)} artigos coletados\n")
        all_articles.extend(rss_arts)

    # ── 2. Scraping (fontes sem RSS) ─────────────────────────────────────────
    if not args.rss_only:
        print("── Scraping (fontes sem RSS) ───────────────────────────")
        scraped = run_scraper()
        print(f"   Scraping: {len(scraped)} artigos coletados\n")
        all_articles.extend(scraped)

    # ── 3. Deduplicação global ───────────────────────────────────────────────
    before = len(all_articles)
    all_articles = dedupe(all_articles)
    dupes = before - len(all_articles)

    # ── 4. Resumo ────────────────────────────────────────────────────────────
    print("── Resultado ───────────────────────────────────────────")
    print(f"   Total coletado:     {before}")
    print(f"   Duplicatas removidas: {dupes}")
    print(f"   Artigos únicos:     {len(all_articles)}")
    print(f"   Fontes:             {len(set(a.source for a in all_articles))}")
    print()

    if not all_articles:
        print("Nenhum artigo coletado. Verifique a conexão.")
        sys.exit(1)

    # ── 5. Export XLSX ───────────────────────────────────────────────────────
    date_str  = datetime.datetime.now().strftime('%Y-%m-%d')
    filepath  = args.out or f'matinal-monitor-{date_str}.xlsx'
    print("── Exportando planilha ─────────────────────────────────")
    path = export_xlsx(all_articles, filepath)
    print(f"   Planilha salva: {path}")
    print()
    print("Pronto.")


if __name__ == '__main__':
    main()
