import requests
import bs4
from dataclasses import dataclass, field
from pathlib import Path

LOCALIZACION_JSON_IPTC = Path(__file__).parent / "iptc_categorias.json"


@dataclass
class IPTCCategoriaDescripcion:
    idioma: str
    nombre: str
    descripcion: str

    def a_json(self) -> dict[str, str]:
        return {
            "idioma": self.idioma,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
        }

    def __hash__(self):
        return hash(self.idioma)

    def __eq__(self, other):
        return self.idioma == other.idioma


@dataclass
class IPTCCategoria:
    id: int
    id_padre: int | None
    nivel: int | None
    descripciones: set[IPTCCategoriaDescripcion] = field(default_factory=set)
    subcategorias: set["IPTCCategoria"] = field(default_factory=set)

    def generar_niveles(self):
        if not self.nivel:
            return
        for subcategoria in self.subcategorias:
            subcategoria.nivel = self.nivel + 1
            subcategoria.generar_niveles()

    def a_json(self) -> dict:
        d = {
            "id": self.id,
            "id_padre": self.id_padre,
            "nivel": self.nivel,
            "descripciones": [],
            "subcategorias": [],
        }
        for descripcion in self.descripciones:
            d["descripciones"].append(descripcion.a_json())
        for subcat in self.subcategorias:
            d["subcategorias"].append(subcat.a_json())
        return d

    def a_mongo(self) -> dict:
        d = {
            "_id": self.id,
            "id_padre": self.id_padre,
            "nivel": self.nivel,
            "descripciones": [],
            "subcategorias": [],
        }
        for descripcion in self.descripciones:
            d["descripciones"].append(descripcion.a_json())
        for subcat in self.subcategorias:
            d["subcategorias"].append(subcat.id)
        return d

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return self.id == other.id


def generar_listado_iptc_leng(url, lenguaje) -> dict[int, IPTCCategoria]:
    response = requests.get(url)
    response.encoding = "utf-8"
    response.raise_for_status()

    soup = bs4.BeautifulSoup(response.text, "html.parser")

    tabla = soup.find("table", {"class": "treetable"})
    if not tabla:
        raise Exception("No se encontro la tabla")

    categorias = tabla.select("tbody tr")
    hashmap_categorias: dict[int, IPTCCategoria] = {}

    # Parsear HTML
    for categoria in categorias:
        id = int(str(categoria.get("data-tt-id", "medtop:-1")).split(":")[1])
        id_padre = (
            int(str(categoria.get("data-tt-parent-id", "medtop:-1")).split(":")[1])
            if categoria.get("data-tt-parent-id")
            else None
        )
        if not id_padre:
            nivel = 1
        else:
            nivel = None
        celdas = categoria.select("td")
        nombre = celdas[1].text
        descripcion = celdas[2].text
        obj_desc = IPTCCategoriaDescripcion(
            idioma=lenguaje, nombre=nombre, descripcion=descripcion
        )
        obj = IPTCCategoria(
            id=id,
            id_padre=id_padre,
            nivel=nivel,
        )
        obj.descripciones.add(obj_desc)
        hashmap_categorias[id] = obj

    return hashmap_categorias


def generar_listado_iptc():
    hashmap_es = generar_listado_iptc_leng(
        "https://www.iptc.org/std/NewsCodes/treeview/mediatopic/mediatopic-es.html",
        "es",
    )
    hashmap_en_us = generar_listado_iptc_leng(
        "https://www.iptc.org/std/NewsCodes/treeview/mediatopic/mediatopic-en-US.html",
        "en-US",
    )
    hashmap_en_gb = generar_listado_iptc_leng(
        "https://www.iptc.org/std/NewsCodes/treeview/mediatopic/mediatopic-en-GB.html",
        "en-GB",
    )

    ids = set(hashmap_es.keys())
    hashmap_general = hashmap_es

    for cat in ids:
        es_desc = hashmap_es[cat].descripciones
        en_us_desc = hashmap_en_us[cat].descripciones
        en_gb_desc = hashmap_en_gb[cat].descripciones
        hashmap_general[cat].descripciones = es_desc | en_us_desc | en_gb_desc

    # Actualizar subcategorias
    for _, categoria in hashmap_general.items():
        if categoria.id_padre:
            hashmap_general[categoria.id_padre].subcategorias.add(categoria)

    # Actualizar niveles
    for _, categoria in hashmap_general.items():
        if categoria.nivel == 1:
            categoria.generar_niveles()

    with open(LOCALIZACION_JSON_IPTC, "w", encoding="utf-8") as f:
        lista_cats = []
        for cats in hashmap_general.values():
            lista_cats.append(cats.a_mongo())

        import json

        json.dump(lista_cats, f, ensure_ascii=False)


__all__ = ["IPTCCategoria"]

if __name__ == "__main__":
    generar_listado_iptc()
