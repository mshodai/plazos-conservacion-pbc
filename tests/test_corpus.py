"""El corpus de corpus/: cada caso da el resultado que documenta.

Se comprueba de cuatro formas: el resultado calculado coincide con el
.esperado.json de cada caso; la línea de órdenes devuelve el código de salida
esperado sobre el fichero real; los ficheros son exactamente los que genera
corpus/generar.py; y el script falla sin escribir si una expectativa no se
cumple.
"""

import copy
import importlib.util
import json
from pathlib import Path

import pytest

from plazos.carga import cargar_fichero
from plazos.cli import main as cli
from plazos.salida import informe

CORPUS = Path(__file__).resolve().parent.parent / "corpus"


def _generador():
    spec = importlib.util.spec_from_file_location("corpus_generar", CORPUS / "generar.py")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


G = _generador()
ESPERADOS = sorted(CORPUS.glob("*.esperado.json"))
IDS = [p.name.removesuffix(".esperado.json") for p in ESPERADOS]


def test_estan_todos_los_casos():
    assert IDS == [c.nombre for c in G.CASOS]
    assert len(ESPERADOS) == 8


@pytest.mark.parametrize("esperado", ESPERADOS, ids=IDS)
def test_cada_caso_da_su_resultado(esperado):
    datos = json.loads(esperado.read_text(encoding="utf-8"))
    carga = cargar_fichero(CORPUS / f"{datos['caso']}.json")
    assert carga.valida, carga.errores
    assert G.resumen(informe(carga)) == datos["resultado"]


@pytest.mark.parametrize("esperado", ESPERADOS, ids=IDS)
def test_la_linea_de_ordenes_da_el_codigo_esperado(esperado, capsys):
    datos = json.loads(esperado.read_text(encoding="utf-8"))
    assert cli([str(CORPUS / f"{datos['caso']}.json")]) == datos["resultado"]["codigo_salida"]
    assert cli([str(CORPUS / f"{datos['caso']}.json"), "--json"]) == datos["resultado"]["codigo_salida"]
    capsys.readouterr()


def test_los_ficheros_son_los_que_genera_el_script():
    """Reproducible: si alguien edita un fichero a mano o cambia generar.py sin regenerar, falla."""
    generados = {"README.md": G.readme()}
    for caso in G.CASOS:
        generados.update(G.ficheros(caso))
    en_disco = {p.name: p.read_text(encoding="utf-8") for p in CORPUS.iterdir() if p.suffix in (".json", ".md")}
    assert en_disco == generados


def test_generar_dos_veces_da_lo_mismo():
    assert _generador().readme() == G.readme()
    assert [_generador().ficheros(c) for c in _generador().CASOS] == [G.ficheros(c) for c in G.CASOS]


def test_el_script_falla_sin_escribir_si_una_expectativa_no_se_cumple(tmp_path, monkeypatch):
    caso = G.CASOS[6]  # prórroga
    esperado = copy.deepcopy(caso.esperado)
    # Una lista nueva: en el caso, el AMLR y T-1 a T-3 comparten la misma.
    linea = [list(tramo) for tramo in esperado["regimenes"]["amlr"]["linea_temporal"]]
    linea[2][0] = "2033-10-02"
    esperado["regimenes"]["amlr"]["linea_temporal"] = linea
    mal = G.Caso(caso.nombre, caso.demuestra, caso.entrada, esperado)
    (diferencia,) = G.comprobar(mal)
    assert diferencia.startswith("amlr.linea_temporal: se esperaba")

    monkeypatch.setattr(G, "DIRECTORIO", tmp_path)
    monkeypatch.setattr(G, "CASOS", [G.CASOS[0], mal])
    with pytest.raises(SystemExit):
        G.main()
    assert list(tmp_path.iterdir()) == []


def test_una_entrada_no_valida_es_un_fallo():
    caso = G.CASOS[0]
    entrada = copy.deepcopy(caso.entrada)
    entrada["regimen"] = "amlr"
    assert G.comprobar(G.Caso(caso.nombre, caso.demuestra, entrada, caso.esperado)) == [
        "la entrada no es válida: ['ERR-01']"
    ]


def test_estan_los_casos_pedidos():
    """Cada caso cubre lo que su nombre dice, en la fecha de referencia."""
    por_nombre = {c.nombre[3:]: c.esperado for c in G.CASOS}
    estados = {n: e["estados"] for n, e in por_nombre.items()}

    assert len(set(estados["mismo-estado-en-los-seis"].values())) == 1
    assert (estados["restringido-en-la-ley-suprimido-en-el-amlr"]["ley_10_2010"],
            estados["restringido-en-la-ley-suprimido-en-el-amlr"]["amlr"]) == ("acceso_restringido", "supresion_exigida")
    transicion = [estados["plazo-en-curso-el-10-de-julio-de-2027"][t] for t in ("T-1", "T-2", "T-3", "T-4")]
    assert len(set(transicion)) == 3
    assert set(por_nombre["operacion-en-relacion-viva"]["regimenes"]["ley_10_2010"]["lecturas"]) == {"OP-1", "OP-2"}
    assert set(por_nombre["examen-especial-cinco-lecturas"]["regimenes"]["ley_10_2010"]["lecturas"]) == {
        f"EE-{n}" for n in range(1, 6)
    }
    assert estados["control-interno-sin-regla-en-el-amlr"]["amlr"] == "sin_regla"
    assert estados["prorroga-de-la-autoridad"]["amlr"] == "conservacion_prorrogada"
    assert set(por_nombre["procedimiento-judicial-pendiente"]["regimenes"]["amlr"]["lecturas"]) == {"PA-1", "PA-2"}


def test_los_datos_son_sinteticos():
    """Identificadores «FICTICIO» y descripciones «ficticio», sin datos de personas ni entidades."""
    for caso in G.CASOS:
        expediente = caso.entrada["expediente"]
        assert "FICTICIO" in expediente["id"]
        for doc in expediente["documentos"]:
            assert "FICTICIO" in doc["id"]
            assert doc["descripcion"].startswith("Documento ficticio:")
        for prorroga in expediente["prorrogas_autoridad"]:
            assert prorroga["autoridad"] == "Autoridad ficticia"
