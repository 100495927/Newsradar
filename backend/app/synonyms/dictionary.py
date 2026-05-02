from __future__ import annotations

import unicodedata

# Fallback dictionary for when ConceptNet returns no results.
# Covers common Spanish news/current-affairs vocabulary.
FALLBACK: dict[str, list[str]] = {
    "economia": ["finanzas", "mercado", "PIB", "inflación", "bolsa", "inversión", "comercio"],
    "finanzas": ["economía", "mercado", "inversión", "capital", "banca", "bolsa"],
    "politica": ["gobierno", "parlamento", "elecciones", "partido", "legislación", "congreso"],
    "gobierno": ["ejecutivo", "administración", "ministros", "gabinete", "política"],
    "elecciones": ["votaciones", "comicios", "sufragio", "urnas", "candidatos"],
    "tecnologia": ["innovación", "software", "digital", "ciberseguridad", "inteligencia artificial", "datos"],
    "inteligencia artificial": ["IA", "machine learning", "automatización", "algoritmo", "deep learning"],
    "ciberseguridad": ["hacking", "ciberataque", "vulnerabilidad", "malware", "phishing", "privacidad"],
    "salud": ["sanidad", "medicina", "epidemia", "hospital", "farmacia", "bienestar"],
    "sanidad": ["salud", "sistema sanitario", "hospitales", "médicos", "enfermedad"],
    "deporte": ["fútbol", "competición", "atletas", "olimpiadas", "liga", "campeonato"],
    "futbol": ["liga", "Champions", "goles", "equipos", "partido", "entrenador"],
    "educacion": ["enseñanza", "escuelas", "universidad", "formación", "aprendizaje", "docentes"],
    "cultura": ["arte", "entretenimiento", "cine", "música", "literatura", "museos"],
    "medio ambiente": ["cambio climático", "sostenibilidad", "ecología", "contaminación", "energía renovable"],
    "clima": ["meteorología", "tiempo", "temperatura", "lluvia", "calentamiento global"],
    "energia": ["petróleo", "gas", "renovable", "electricidad", "combustible", "nuclear"],
    "guerra": ["conflicto", "armado", "ejercito", "paz", "ataque", "defensa"],
    "conflicto": ["guerra", "tensión", "crisis", "enfrentamiento", "disputa"],
    "justicia": ["tribunal", "ley", "juicio", "sentencia", "derecho", "corrupción"],
    "corrupcion": ["fraude", "soborno", "malversación", "escándalo", "irregularidad"],
    "inmigración": ["migración", "refugiados", "fronteras", "asilo", "extranjeros"],
    "inflacion": ["precios", "IPC", "carestía", "poder adquisitivo", "deflación"],
    "desempleo": ["paro", "trabajo", "empleo", "laboral", "ERTE", "contratación"],
    "vivienda": ["inmobiliario", "alquiler", "hipoteca", "precios", "mercado inmobiliario"],
    "sociedad": ["ciudadanos", "comunidad", "población", "bienestar social", "demografía"],
    "religion": ["iglesia", "fe", "creencia", "papa", "islam", "catolicismo"],
    "ciencia": ["investigación", "descubrimiento", "estudio", "laboratorio", "innovación"],
}


def _normalize(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text.lower().strip())
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))


def fallback_lookup(word: str) -> list[str]:
    key = _normalize(word)
    for k, v in FALLBACK.items():
        if _normalize(k) == key:
            return v[:10]
    return []
