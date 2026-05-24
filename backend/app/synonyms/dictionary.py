from __future__ import annotations

import unicodedata

# Fallback dictionary for when ConceptNet returns no results.
# Covers common Spanish news/current-affairs vocabulary.
FALLBACK: dict[str, list[str]] = {
    # Economía
    "economia": ["finanzas", "mercado", "PIB", "inflación", "bolsa", "inversión"],
    "finanzas": ["economía", "mercado", "inversión", "capital", "banca"],
    "mercado": ["bolsa", "comercio", "oferta", "demanda", "intercambio"],
    "bolsa": ["mercado de valores", "acciones", "cotización", "inversión", "Wall Street"],
    "inversion": ["capital", "financiación", "ahorro", "rentabilidad", "fondo"],
    "inflacion": ["precios", "IPC", "carestía", "poder adquisitivo", "deflación"],
    "desempleo": ["paro", "desocupación", "empleo", "ERTE", "contratación"],
    "paro": ["desempleo", "desocupación", "subsidio", "ERTE", "trabajo"],
    "trabajo": ["empleo", "laboral", "ocupación", "profesión", "oficio"],
    "empresa": ["compañía", "corporación", "negocio", "firma", "sociedad"],
    "banca": ["banco", "finanzas", "crédito", "préstamo", "entidad financiera"],
    "impuesto": ["tributo", "tasa", "gravamen", "hacienda", "fiscalidad"],
    "deuda": ["crédito", "préstamo", "déficit", "endeudamiento", "pasivo"],
    "exportacion": ["comercio exterior", "ventas internacionales", "exportaciones", "intercambio"],
    "importacion": ["comercio exterior", "compras internacionales", "aduanas", "aranceles"],

    # Política
    "politica": ["gobierno", "parlamento", "elecciones", "partido", "legislación"],
    "gobierno": ["ejecutivo", "administración", "ministros", "gabinete", "política"],
    "elecciones": ["votaciones", "comicios", "sufragio", "urnas", "candidatos"],
    "partido": ["formación política", "candidatura", "coalición", "agrupación"],
    "congreso": ["parlamento", "cámara", "diputados", "legislativo", "asamblea"],
    "senado": ["cámara alta", "senadores", "legislativo", "parlamento"],
    "presidente": ["jefe de gobierno", "mandatario", "primer ministro", "ejecutivo"],
    "ministro": ["secretario de estado", "consejero", "titular", "cartera"],
    "ley": ["norma", "legislación", "decreto", "reglamento", "regulación"],
    "democracia": ["república", "sistema político", "elecciones", "ciudadanos"],
    "corrupcion": ["fraude", "soborno", "malversación", "escándalo", "irregularidad"],
    "transparencia": ["rendición de cuentas", "acceso a la información", "anticorrupción"],
    "diplomacia": ["relaciones exteriores", "embajada", "negociación", "tratado"],
    "referendum": ["consulta popular", "plebiscito", "votación", "sufragio"],

    # Internacional
    "guerra": ["conflicto", "armado", "ejército", "paz", "ataque", "ofensiva"],
    "conflicto": ["guerra", "tensión", "crisis", "enfrentamiento", "disputa"],
    "paz": ["cese al fuego", "armisticio", "negociación", "acuerdo", "reconciliación"],
    "onu": ["Naciones Unidas", "organismo internacional", "multilateral", "seguridad global"],
    "otan": ["alianza atlántica", "aliados", "defensa colectiva", "militares"],
    "ue": ["Unión Europea", "Europa", "Bruselas", "instituciones europeas"],
    "tratado": ["acuerdo", "pacto", "convenio", "alianza", "negociación"],
    "sanciones": ["embargo", "restricciones", "medidas", "penalizaciones"],
    "refugiados": ["migrantes", "desplazados", "asilo", "diáspora", "exiliados"],
    "inmigracion": ["migración", "refugiados", "fronteras", "asilo", "extranjeros"],

    # Sociedad
    "sociedad": ["ciudadanos", "comunidad", "población", "bienestar social", "colectivo"],
    "educacion": ["enseñanza", "escuelas", "universidad", "formación", "aprendizaje"],
    "sanidad": ["salud", "sistema sanitario", "hospitales", "médicos", "enfermedad"],
    "salud": ["sanidad", "medicina", "epidemia", "hospital", "bienestar"],
    "vivienda": ["inmobiliario", "alquiler", "hipoteca", "habitación", "hogar"],
    "alquiler": ["arrendamiento", "vivienda", "renta", "inquilino", "propietario"],
    "pensiones": ["jubilación", "retiro", "prestación", "seguridad social", "vejez"],
    "familia": ["hogar", "padres", "hijos", "núcleo familiar", "parentesco"],
    "mujer": ["feminismo", "igualdad", "género", "derechos", "emancipación"],
    "violencia": ["agresión", "maltrato", "crimen", "delito", "brutalidad"],
    "igualdad": ["equidad", "paridad", "derechos", "justicia social", "discriminación"],
    "racismo": ["discriminación", "xenofobia", "intolerancia", "odio", "prejuicio"],
    "pobreza": ["exclusión social", "desigualdad", "precariedad", "marginalidad"],

    # Tecnología
    "tecnologia": ["innovación", "software", "digital", "ciberseguridad", "datos"],
    "inteligencia artificial": ["IA", "machine learning", "automatización", "algoritmo"],
    "ciberseguridad": ["hacking", "ciberataque", "vulnerabilidad", "malware", "privacidad"],
    "internet": ["red", "web", "digital", "conectividad", "banda ancha"],
    "redes sociales": ["Twitter", "Facebook", "Instagram", "plataformas digitales"],
    "startup": ["empresa emergente", "emprendimiento", "innovación", "tecnológica"],
    "datos": ["información", "big data", "privacidad", "base de datos", "analytics"],
    "robot": ["automatización", "inteligencia artificial", "máquina", "industria 4.0"],

    # Medio ambiente
    "medio ambiente": ["cambio climático", "sostenibilidad", "ecología", "contaminación"],
    "cambio climatico": ["calentamiento global", "CO2", "emisiones", "efecto invernadero"],
    "energia": ["petróleo", "gas", "renovable", "electricidad", "combustible"],
    "renovable": ["solar", "eólica", "energía verde", "sostenible", "limpia"],
    "contaminacion": ["polución", "emisiones", "toxicidad", "residuos", "medio ambiente"],
    "sequía": ["escasez de agua", "aridez", "desertificación", "lluvia"],
    "inundacion": ["riada", "desbordamiento", "catástrofe natural", "lluvia torrencial"],
    "incendio": ["fuego", "llamas", "forestal", "emergencia", "evacuación"],

    # Justicia y seguridad
    "justicia": ["tribunal", "ley", "juicio", "sentencia", "derecho"],
    "tribunal": ["juzgado", "corte", "juicio", "magistrado", "sala"],
    "policia": ["fuerzas de seguridad", "agentes", "orden público", "cuerpo policial"],
    "crimen": ["delito", "robo", "asesinato", "violencia", "delincuencia"],
    "prision": ["cárcel", "reclusión", "condena", "penitenciaría", "recluso"],
    "terrorismo": ["atentado", "yihadismo", "extremismo", "ataque terrorista"],
    "narcotráfico": ["drogas", "cartel", "tráfico", "crimen organizado"],

    # Cultura y deporte
    "cultura": ["arte", "entretenimiento", "cine", "música", "literatura"],
    "deporte": ["fútbol", "competición", "atletas", "olimpiadas", "liga"],
    "futbol": ["liga", "Champions", "goles", "equipos", "partido", "entrenador"],
    "olimpiadas": ["juegos olímpicos", "atletas", "medallas", "deporte", "competición"],
    "cine": ["película", "director", "actor", "festival", "producción"],
    "musica": ["canción", "artista", "álbum", "concierto", "banda"],

    # Ciencia y salud pública
    "ciencia": ["investigación", "descubrimiento", "estudio", "laboratorio", "innovación"],
    "vacuna": ["inmunización", "dosis", "campana de vacunación", "protección", "anticuerpos"],
    "pandemia": ["epidemia", "virus", "contagio", "cuarentena", "brote"],
    "cancer": ["tumor", "oncología", "quimioterapia", "tratamiento", "enfermedad"],
    "hospital": ["clínica", "sanatorio", "centro médico", "urgencias", "médicos"],
    "medicamento": ["fármaco", "tratamiento", "droga", "pastilla", "terapia"],

    # Religión
    "religion": ["iglesia", "fe", "creencia", "papa", "islam", "catolicismo"],
    "iglesia": ["catolicismo", "papa", "obispo", "diócesis", "parroquia"],
    "islam": ["musulmán", "mezquita", "corán", "ramadán", "yihad"],
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
