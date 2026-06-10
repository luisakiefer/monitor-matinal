#!/usr/bin/env python3
"""
categorization.py — Classificação automática de categoria e localização
Monitor Matinal
"""

# ─────────────────────────────────────────────────────────────────────────────
# CATEGORIAS E PALAVRAS-CHAVE
# ─────────────────────────────────────────────────────────────────────────────

CATEGORY_KEYWORDS = {
    "Política": [
        "câmara", "vereador", "prefeito", "prefeitura", "votação", "lei",
        "legislação", "decisão", "eleição", "político", "governo",
        "executivo", "legislativo", "assembleia", "ALERGS", "deputado",
        "senador", "ministério", "secretário", "governo estadual",
    ],
    "Educação": [
        "escola", "educação", "creche", "universidade", "aluno", "professor",
        "UFRGS", "PUC", "educador", "pedagogia", "aprendizado", "ensino",
        "formação", "bolsa", "currículo", "matrícula", "evasão escolar",
    ],
    "Saúde": [
        "saúde", "hospital", "médico", "SUS", "doença", "epidemia", "COVID",
        "vacinação", "clínica", "enfermeiro", "farmácia", "ambulância",
        "psicologia", "mental", "dengue", "gripe", "pandemia",
    ],
    "Urbanismo": [
        "plano diretor", "zoneamento", "LUOS", "ocupação do solo", "uso do solo",
        "urbanismo", "construção", "prédio", "bairro", "infraestrutura",
        "calçada", "planejamento urbano", "reforma urbana", "segregação", "habitação",
    ],
    "Mobilidade": [
        "transporte", "ônibus", "metrô", "trânsito", "ciclovias", "bicicleta",
        "tráfego", "mobilidade", "TRI", "linhas de ônibus",
        "acessibilidade", "pedestres",
    ],
    "Economia": [
        "economia", "emprego", "desemprego", "comércio", "indústria", "negócio",
        "salário", "renda", "consumo", "preço", "inflação", "financeiro",
        "banco", "crédito", "investimento", "empresa", "turismo",
    ],
    "Meio Ambiente": [
        "enchente", "inundação", "drenagem", "ambiental", "sustentabilidade",
        "CMPC", "celulose", "poluição", "limpeza", "lixo",
        "reciclagem", "parque", "natureza", "rio",
        "lagoa", "Guaíba", "aquecimento global", "clima",
    ],
    "Esporte": [
        "esporte", "futebol", "Grêmio", "Inter", "jogador", "técnico",
        "campeonato", "jogo", "gol", "time", "atleta", "copa",
        "olimpíada", "ginástica", "natação", "corrida",
    ],
    "Tecnologia": [
        "tecnologia", "startup", "inovação", "digital", "internet", "app",
        "software", "programação", "IA", "inteligência artificial", "dados",
        "cibersegurança", "hacker", "plataforma",
    ],
    "Cultura": [
        "cultura", "arte", "artista", "exposição", "teatro", "cinema",
        "música", "concerto", "show", "artesanato", "patrimônio", "histórico",
        "patrimônio histórico", "museu", "biblioteca", "literatura", "poeta",
        "dança", "evento cultural",
    ],
    "Segurança": [
        "segurança", "polícia", "crime", "roubo", "delegacia",
        "presídio", "justiça", "tribunal", "advogado",
        "direito", "sentença", "julgamento", "violência",
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
# LOCALIZAÇÕES E PALAVRAS-CHAVE
# ─────────────────────────────────────────────────────────────────────────────

LOCATION_KEYWORDS = {
    "Porto Alegre": [
        "Porto Alegre", "POA", "capital rio-grandense",
        # Bairros
        "Azenha", "Auxiliadora", "Bom Fim", "Bom Jesus",
        "Cascata", "Cavalhada", "Centro Histórico",
        "Cidade Baixa", "Cidade Nova", "Cristal",
        "Farrapos", "Floresta", "Glória",
        "Higienópolis", "Humaitá", "Itapuã",
        "Jardim Botânico", "Jardim Europa", "Jardim Lindóia",
        "Lami", "Medianeira", "Menino Deus",
        "Moinhos de Vento", "Mont Serrat", "Morro da Cruz",
        "Navegantes", "Nossa Senhora de Fátima",
        "Nonoai", "Passo da Areia", "Petrópolis",
        "Praia de Belas",
        "Restinga", "Rio Branco",
        "Santa Cecília", "Santa Tereza", "Santana",
        "Santo Antônio", "Santos Dumont", "São Cristóvão", "São Geraldo",
        "São João", "Sertório", "Três Figueiras",
        "Tristeza", "Vila Flores",
        "Vila Ipiranga", "Vila Nova",
    ],
    "RM": [  # Região Metropolitana de Porto Alegre
        "região metropolitana", "grande Porto Alegre",
        "Viamão", "Gravataí", "Alvorada", "Cachoeirinha",
        "Esteio", "Sapucaia do Sul", "São Leopoldo",
        "Novo Hamburgo", "Campo Bom", "Sapucaia",
        "Canoas", "Charqueadas", "Eldorado do Sul",
        "Guaíba", "Montenegro", "São Jerônimo",
    ],
    "RS": [
        "Rio Grande do Sul", "gaúcho", "gaúcha",
        "interior do estado", "estado rio-grandense",
        "Caxias do Sul", "Pelotas", "Santa Maria",
        "Passo Fundo", "Lajeado", "Bento Gonçalves",
        "Cruz Alta", "Bagé", "Uruguaiana",
        "Rio Grande", "Santana do Livramento",
        "Serra Gaúcha", "Litoral Gaúcho", "Campanha Gaúcha",
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
# CORES (usadas no HTML)
# ─────────────────────────────────────────────────────────────────────────────

CATEGORY_COLORS = {
    "Política":        "#dc2626",
    "Educação":        "#2563eb",
    "Saúde":           "#16a34a",
    "Urbanismo":       "#ea580c",
    "Mobilidade":      "#7c3aed",
    "Economia":        "#d97706",
    "Meio Ambiente":   "#059669",
    "Esporte":         "#0891b2",
    "Tecnologia":      "#2dd4bf",
    "Cultura":         "#db2777",
    "Segurança":       "#6366f1",
}

LOCATION_COLORS = {
    "Porto Alegre": "#42c8dc",
    "RM":           "#7c3aed",
    "RS":           "#ea580c",
    "Brasil":       "#6b7280",
}

# ─────────────────────────────────────────────────────────────────────────────
# FUNÇÕES DE CLASSIFICAÇÃO
# ─────────────────────────────────────────────────────────────────────────────

def classify_category(title: str, description: str) -> str:
    """Classifica artigo por categoria baseado em keywords."""
    text = f"{title} {description}".lower()
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        count = sum(1 for kw in keywords if kw.lower() in text)
        if count > 0:
            scores[category] = count
    if scores:
        return max(scores.items(), key=lambda x: x[1])[0]
    return "Sem classificação"


def classify_location(title: str, description: str) -> str:
    """Classifica localização com prioridade Porto Alegre > RM > RS > Brasil."""
    text = f"{title} {description}".lower()
    for location in ["Porto Alegre", "RM", "RS"]:
        for kw in LOCATION_KEYWORDS.get(location, []):
            if kw.lower() in text:
                return location
    return "Brasil"


# ─────────────────────────────────────────────────────────────────────────────
# Teste rápido
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        ("Câmara vota novo plano de drenagem em Porto Alegre", "Vereadores aprovaram hoje..."),
        ("Grêmio vence Inter em clássico", "Jogo aconteceu no Beira-Rio"),
        ("UFRGS abre inscrições para bolsas", "Universidade oferece vagas"),
        ("Enchente atinge Canoas e Alvorada", "Região Metropolitana em alerta"),
        ("Governo do RS anuncia investimentos", "Eduardo Leite anunciou pacote"),
    ]
    for title, desc in tests:
        cat = classify_category(title, desc)
        loc = classify_location(title, desc)
        print(f"  [{loc}] [{cat}] {title}")
