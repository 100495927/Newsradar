from alerts.matcher import clean_descriptors, find_matched_descriptors


def test_descriptor_found_in_title() -> None:
    entry = {"titulo": "La inteligencia artificial crece", "resumen": ""}

    assert find_matched_descriptors(entry, ["artificial"]) == ["artificial"]


def test_descriptor_found_in_summary() -> None:
    entry = {"titulo": "Economia", "resumen": "Sube la inflacion europea"}

    assert find_matched_descriptors(entry, ["inflacion"]) == ["inflacion"]


def test_descriptor_not_found() -> None:
    entry = {"titulo": "Deportes", "resumen": "Resultado local"}

    assert find_matched_descriptors(entry, ["energia"]) == []


def test_multiple_descriptors_and_case_insensitive() -> None:
    entry = {"titulo": "Alerta por ENERGIA", "resumen": "El mercado electrico cambia"}

    assert find_matched_descriptors(entry, ["energia", "Mercado"]) == [
        "energia",
        "Mercado",
    ]


def test_clean_descriptors_removes_empty_and_duplicates() -> None:
    assert clean_descriptors([" IA ", "", "ia", None, "datos"]) == ["IA", "datos"]
