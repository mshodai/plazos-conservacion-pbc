"""Línea de órdenes plazos-conservacion: códigos de salida y --json."""

import json
import re
import tomllib
from pathlib import Path

import pytest

from ayudas import diligencia, examen, relacion
from plazos.cli import main

RAIZ = Path(__file__).resolve().parent.parent


def datos(ref, hecho_inicial, documentos):
    return {
        "version_modelo": 2,
        "fecha_referencia": ref,
        "sujeto": {"naturaleza": "sujeto_obligado", "actividad": "otra"},
        "expediente": {
            "id": "E",
            "hecho_inicial": hecho_inicial,
            "documentos": documentos,
            "prorrogas_autoridad": [],
            "procedimiento_judicial_pendiente_2027_07_10": False,
        },
    }


def escribir(tmp_path, contenido, nombre="entrada.json"):
    ruta = tmp_path / nombre
    if isinstance(contenido, bytes):
        ruta.write_bytes(contenido)
    else:
        ruta.write_text(contenido if isinstance(contenido, str) else json.dumps(contenido), encoding="utf-8")
    return str(ruta)


COINCIDEN = datos("2026-01-01", relacion(None, "2020-01-01"), [diligencia("D", "2020-01-01")])
DIFIEREN = datos("2028-01-01", relacion("2020-03-15"), [diligencia("D", "2019-01-01")])


def test_coinciden_devuelve_0(tmp_path, capsys):
    assert main([escribir(tmp_path, COINCIDEN)]) == 0
    assert "Los seis regímenes coinciden el 2026-01-01." in capsys.readouterr().out


def test_difieren_devuelve_1(tmp_path, capsys):
    assert main([escribir(tmp_path, DIFIEREN)]) == 1
    assert "La Ley y el AMLR dan estados distintos" in capsys.readouterr().out


def test_indeterminado_con_eliminacion_devuelve_1(tmp_path):
    """D-28: antes de A, OP-1 exige eliminar y OP-2 no ha empezado: una lectura exige actuar."""
    doc = {"id": "O", "categoria": "operaciones", "fecha_documento": "2014-04-01", "fecha_ejecucion_operacion": "2014-04-01"}
    entrada = datos("2025-01-01", relacion(None, "2012-01-01"), [doc])
    assert main([escribir(tmp_path, entrada)]) == 1


def test_examen_especial_de_relacion_viva_devuelve_0(tmp_path, capsys):
    """D-28: con la Ley, EE-1 a EE-4 dan en_conservacion y EE-5 plazo_no_iniciado (indeterminado);
    con el AMLR, plazo_no_iniciado. Los regímenes discrepan, pero en todas las lecturas hay que
    conservar: ninguna exige actuar. Con D-27, retirada, daba 1."""
    doc = examen("EE", "2021-01-10", "2021-02-15", "2021-02-20", "2021-02-25")
    entrada = datos("2023-01-01", relacion(None, "2018-06-01"), [doc])
    assert main([escribir(tmp_path, entrada)]) == 0
    salida = capsys.readouterr().out
    assert "ley_10_2010  indeterminado" in salida
    assert "amlr         plazo_no_iniciado" in salida
    assert main([escribir(tmp_path, entrada), "--json"]) == 0
    datos_json = json.loads(capsys.readouterr().out)
    assert datos_json["exige_actuar"] == {"valor": False, "activado_por": []}
    assert datos_json["documentos"][0]["exige_actuar"] == {"valor": False, "activado_por": []}


def test_acceso_restringido_exige_actuar(capsys):
    """D-28: en el caso 07 del corpus, la Ley da acceso_restringido y el AMLR conservacion_prorrogada.
    Solo el acceso restringido exige actuar (Ley 25.1), y basta para el 1."""
    assert main([str(RAIZ / "corpus" / "07-prorroga-de-la-autoridad.json"), "--json"]) == 1
    datos_json = json.loads(capsys.readouterr().out)
    activado_por = datos_json["exige_actuar"]["activado_por"]
    assert datos_json["exige_actuar"]["valor"] is True
    assert {(a["regimen"], a["estado"]) for a in activado_por} == {
        ("ley_10_2010", "acceso_restringido"),
        ("T-4", "acceso_restringido"),
    }
    estados = {r: v["estado"] for r, v in datos_json["documentos"][0]["regimenes"].items()}
    assert set(estados.values()) == {"acceso_restringido", "conservacion_prorrogada"}


def test_sin_regla_con_una_lectura_que_exige_actuar(tmp_path, capsys):
    """D-28, lectura literal: el caso 06 en 2035. El AMLR da «sin_regla» como estado, pero su
    lectura SR-3 (art. 77.3 por extensión) ya exige suprimir. El informe dice qué régimen y qué
    lectura dan el 1."""
    entrada = json.loads((RAIZ / "corpus" / "06-control-interno-sin-regla-en-el-amlr.json").read_text(encoding="utf-8"))
    entrada["fecha_referencia"] = "2035-01-01"
    assert main([escribir(tmp_path, entrada), "--json"]) == 1
    documento = json.loads(capsys.readouterr().out)["documentos"][0]
    assert documento["regimenes"]["amlr"]["estado"] == "sin_regla"
    assert {"regimen": "amlr", "lectura": "SR-3", "estado": "supresion_exigida"} in documento["exige_actuar"]["activado_por"]
    assert main([escribir(tmp_path, entrada)]) == 1
    salida = capsys.readouterr().out
    assert "SR-3: supresion_exigida" in salida
    assert "(estado del régimen: sin_regla)" in salida


def test_ejemplo_del_modelo(tmp_path, capsys):
    texto = (RAIZ / "docs" / "modelo-datos.md").read_text(encoding="utf-8")
    ejemplo = re.search(r"```json\n(.*?)\n```", texto, re.DOTALL).group(1)
    assert main([escribir(tmp_path, ejemplo), "--json"]) == 1
    salida = json.loads(capsys.readouterr().out)
    assert [d["id"] for d in salida["documentos"]] == ["DOC-1", "DOC-2", "DOC-3", "DOC-4"]


def test_json(tmp_path, capsys):
    assert main([escribir(tmp_path, DIFIEREN), "--json"]) == 1
    salida = json.loads(capsys.readouterr().out)
    assert salida["documentos"][0]["regimenes"]["amlr"]["estado"] == "supresion_exigida"


def test_entrada_no_valida_devuelve_2(tmp_path, capsys):
    invalida = dict(DIFIEREN, regimen="amlr")
    assert main([escribir(tmp_path, invalida)]) == 2
    assert "ERR-01" in capsys.readouterr().out
    assert main([escribir(tmp_path, invalida), "--json"]) == 2
    assert json.loads(capsys.readouterr().out)["valida"] is False


def test_json_mal_formado_devuelve_2(tmp_path):
    assert main([escribir(tmp_path, "{")]) == 2


@pytest.mark.parametrize(
    "ruta, mensaje",
    [
        (lambda tmp: str(tmp / "no-existe.json"), "no existe el fichero"),
        (lambda tmp: str(tmp), "es un directorio"),
        (lambda tmp: escribir(tmp, "{}".encode("utf-16")), "no está codificado en UTF-8"),
    ],
)
def test_fichero_ilegible_devuelve_2(tmp_path, capsys, ruta, mensaje):
    assert main([ruta(tmp_path)]) == 2
    assert mensaje in capsys.readouterr().err


def test_uso_incorrecto_devuelve_2(capsys):
    with pytest.raises(SystemExit) as salida:
        main([])
    assert salida.value.code == 2


def test_ayuda(capsys):
    with pytest.raises(SystemExit) as salida:
        main(["--help"])
    assert salida.value.code == 0
    ayuda = capsys.readouterr().out
    assert ayuda.startswith("uso: plazos-conservacion")
    assert "códigos de salida" in ayuda


def test_punto_de_entrada_declarado():
    proyecto = tomllib.loads((RAIZ / "pyproject.toml").read_text(encoding="utf-8"))
    assert proyecto["project"]["scripts"] == {"plazos-conservacion": "plazos.cli:main"}
