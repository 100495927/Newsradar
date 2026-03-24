class RSSFeed:
    # RSS
    def __init__(self, fuente, titulo, link, entradas):
        self._fuente = fuente
        self._titulo = titulo
        self._link = link
        self._entradas = []

        for entrada in entradas:
            p = self._fuente.parser(entrada)
            entrada_parseada = p.generar()
            self._entradas.append(entrada_parseada)

    def __str__(self):
        return f"""
        {self._titulo}
        {self._link}
        """

    @property
    def entradas(self) -> tuple:
        return tuple(self._entradas)


__all__ = ["RSSFeed"]
