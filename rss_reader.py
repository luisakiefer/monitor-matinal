#!/usr/bin/env python3
"""
rss_reader.py — Leitor dos feeds RSS do Monitor Matinal
Busca os mesmos feeds do monitor-matinal.html e retorna Articles.
"""

import datetime
import time
import logging
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Optional
from urllib.parse import unquote

import requests
from bs4 import BeautifulSoup

from scraper import Article, HEADERS, TIMEOUT, DELAY, dedupe

log = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Fontes RSS — espelho exato do SOURCES em monitor-matinal.html
# ─────────────────────────────────────────────────────────────────────────────

RSS_SOURCES: list[dict] = [
    # ── RS ───────────────────────────────────────────────────────────────────
    {
        'id': 'ghz', 'name': 'GZH', 'group': 'RS', 'color': '#d32f2f',
        'feeds': [
            'https://gauchazh.clicrbs.com.br/rss/noticias.xml',
            'https://gauchazh.clicrbs.com.br/rss/ultimas-noticias.xml',
        ],
    },
    {
        'id': 'correio', 'name': 'Correio do Povo', 'group': 'RS', 'color': '#1565c0',
        'feeds': ['https://www.correiodopovo.com.br/feed'],
    },
    {
        'id': 'jc', 'name': 'Jornal do Comércio', 'group': 'RS', 'color': '#2e7d32',
        'feeds': ['https://www.jornaldocomercio.com/_conteudo/rss/geral.xml'],
    },
    {
        'id': 'osul', 'name': 'O Sul', 'group': 'RS', 'color': '#6a1b9a',
        'feeds': ['https://www.osul.com.br/feed/'],
    },
    {
        'id': 'sul21', 'name': 'Sul21', 'group': 'RS', 'color': '#00838f',
        'feeds': ['https://sul21.com.br/feed/'],
    },
    {
        'id': 'matinal', 'name': 'Matinal', 'group': 'RS', 'color': '#42c8dc',
        'feeds': ['https://www.matinal.org/rss/'],
    },
    {
        'id': 'bdf', 'name': 'Brasil de Fato RS', 'group': 'RS', 'color': '#c62828',
        'feeds': ['https://www.brasildefato.com.br/rss2.xml'],
    },
    {
        'id': 'extraclasse', 'name': 'Extraclasse', 'group': 'RS', 'color': '#e65100',
        'feeds': ['https://www.extraclasse.org.br/feed/'],
    },
    {
        'id': 'agorars', 'name': 'Agora RS', 'group': 'RS', 'color': '#0277bd',
        'feeds': ['https://agorars.com/feed/'],
    },
    {
        'id': 'gaucha', 'name': 'Rádio Gaúcha', 'group': 'RS', 'color': '#f9a825',
        'feeds': ['https://gauchazh.clicrbs.com.br/rss/radiogaucha.xml'],
    },
    # ── Nacional ─────────────────────────────────────────────────────────────
    {
        'id': 'g1', 'name': 'G1 RS', 'group': 'Nacional', 'color': '#1a73e8',
        'feeds': ['https://g1.globo.com/rss/g1/rs/'],
    },
    {
        'id': 'folha', 'name': 'Folha de S.Paulo', 'group': 'Nacional', 'color': '#37474f',
        'feeds': ['https://feeds.folha.uol.com.br/emcimadahora/rss091.xml'],
    },
    {
        'id': 'uol', 'name': 'UOL', 'group': 'Nacional', 'color': '#4527a0',
        'feeds': ['https://rss.uol.com.br/feed/noticias.xml'],
    },
    {
        'id': 'metropoles', 'name': 'Metrópoles', 'group': 'Nacional', 'color': '#ad1457',
        'feeds': ['https://www.metropoles.com/feed'],
    },
    {
        'id': 'cnn', 'name': 'CNN Brasil', 'group': 'Nacional', 'color': '#b71c1c',
        'feeds': ['https://www.cnnbrasil.com.br/feed/'],
    },
    {
        'id': 'r7', 'name': 'R7', 'group': 'Nacional', 'color': '#558b2f',
        'feeds': ['https://noticias.r7.com/feed.xml'],
    },
    {
        'id': 'gnews', 'name': 'Google News RS', 'group': 'Nacional', 'color': '#1a73e8',
        'feeds': [
            'https://news.google.com/rss/search?q=Porto+Alegre+RS&hl=pt-BR&gl=BR&ceid=BR:pt-419'
        ],
    },
]

# Namespaces comuns em feeds RSS/Atom
NS = {
    'dc':      'http://purl.org/dc/elements/1.1/',
    'content': 'http://purl.org/rss/1.0/modules/content/',
    'media':   'http://search.yahoo.com/mrss/',
    'atom':    'http://www.w3.org/2005/Atom',
}


def _parse_date(s: str) -> Optional[datetime.datetime]:
    if not s:
        return None
    # RFC 2822 (RSS padrão)
    try:
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(s.strip())
        # Converte para UTC sem tzinfo (para o Excel)
        return dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)
    except Exception:
        pass
    # ISO 8601 (Atom / alguns RSS modernos)
    for fmt in ('%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d %H:%M:%S'):
        try:
            return datetime.datetime.strptime(s.strip()[:19], fmt[:len(s.strip()[:19])])
        except Exception:
            pass
    return None


def _strip_html(s: str) -> str:
    if not s:
        return ''
    return BeautifulSoup(s, 'html.parser').get_text(separator=' ', strip=True)


def fetch_feed(source: dict, feed_url: str) -> list[Article]:
    """Busca um feed RSS/Atom e retorna lista de Articles."""
    articles: list[Article] = []
    try:
        r = requests.get(feed_url, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        root = ET.fromstring(r.content)
    except Exception as e:
        log.warning(f"  Feed {source['name']} ({feed_url}): {e}")
        return []

    # ── RSS 2.0 ──────────────────────────────────────────────────────────────
    for item in root.findall('.//item'):
        title = _strip_html(item.findtext('title') or '')
        link  = (item.findtext('link') or '').strip()
        # <link> em RSS pode vir como elemento vazio com atributo href (raro mas existe)
        if not link:
            link_el = item.find('link')
            if link_el is not None:
                link = link_el.get('href', '')
        pub  = (item.findtext('pubDate')
                or item.findtext(f'{{{NS["dc"]}}}date')
                or '')
        desc = _strip_html(
            item.findtext('description')
            or item.findtext(f'{{{NS["content"]}}}encoded')
            or ''
        )[:300]
        date = _parse_date(pub)
        if title and link:
            articles.append(Article(
                source=source['name'],
                title=title,
                link=link,
                date=date,
                description=desc,
                group=source['group'],
            ))

    # ── Atom ─────────────────────────────────────────────────────────────────
    if not articles:
        atom_ns = NS['atom']
        for entry in root.findall(f'{{{atom_ns}}}entry'):
            title = _strip_html(entry.findtext(f'{{{atom_ns}}}title') or '')
            link_el = entry.find(f'{{{atom_ns}}}link[@rel="alternate"]')
            if link_el is None:
                link_el = entry.find(f'{{{atom_ns}}}link')
            link = link_el.get('href', '') if link_el is not None else ''
            pub  = (entry.findtext(f'{{{atom_ns}}}published')
                    or entry.findtext(f'{{{atom_ns}}}updated')
                    or '')
            desc = _strip_html(
                entry.findtext(f'{{{atom_ns}}}summary')
                or entry.findtext(f'{{{atom_ns}}}content')
                or ''
            )[:300]
            date = _parse_date(pub)
            if title and link:
                articles.append(Article(
                    source=source['name'],
                    title=title,
                    link=link,
                    date=date,
                    description=desc,
                    group=source['group'],
                ))

    return articles


def fetch_all_rss() -> list[Article]:
    """Busca todos os feeds RSS e retorna lista unificada sem duplicatas."""
    all_articles: list[Article] = []
    total = sum(len(s['feeds']) for s in RSS_SOURCES)
    done  = 0

    for src in RSS_SOURCES:
        for feed_url in src['feeds']:
            done += 1
            log.info(f"[{done}/{total}] RSS {src['name']} …")
            arts = fetch_feed(src, feed_url)
            log.info(f"  → {len(arts)} item(s)")
            all_articles.extend(arts)
            if done < total:
                time.sleep(DELAY / 2)

    return dedupe(all_articles)


if __name__ == '__main__':
    import json
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s [%(levelname)s] %(message)s')
    arts = fetch_all_rss()
    print(f"\nTotal RSS: {len(arts)} artigos de {len(RSS_SOURCES)} fontes")
