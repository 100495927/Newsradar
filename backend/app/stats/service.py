from collections import Counter
import re
from ..store import alerts_col, notifications_col, sources_col

# Lista de palabras a ignorar en la nube (Stopwords)
STOPWORDS = {"el", "la", "los", "las", "de", "que", "en", "un", "una", "y", "del", "con", "para", "como"}

def get_global_stats():
    """Realiza agregaciones en la DB para el Dashboard Global."""
    return {
        "n_fuentes": sources_col.count_documents({}),
        "n_noticias": notifications_col.count_documents({}),
        "n_alertas": alerts_col.count_documents({}),
        "alertas_por_categoria": list(alerts_col.aggregate([
            {"$unwind": "$categories"},
            {"$group": {"_id": "$categories.label", "total": {"$sum": 1}}}
        ]))
    }

def get_feed_stats(feed_id: str):
    """Calcula rendimiento específico de un RSS."""
    return {
        "feed_id": feed_id,
        "n_noticias": notifications_col.count_documents({"feed_id": feed_id}),
        "n_alertas": alerts_col.count_documents({"source_id": feed_id})
    }

def get_word_cloud_data(categoria: str):
    """Procesa noticias para generar una nube de palabras."""
    noticias = list(notifications_col.find({"category": categoria}, {"title": 1, "description": 1}))
    texto_completo = " ".join([n.get("title", "") + " " + n.get("description", "") for n in noticias])
    
    palabras = re.findall(r'\w+', texto_completo.lower())
    palabras_filtradas = [w for w in palabras if w not in STOPWORDS and len(w) > 3]
    
    conteo = Counter(palabras_filtradas).most_common(50)
    return [{"word": word, "value": count} for word, count in conteo]