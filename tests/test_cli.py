"""Línea de órdenes plazos-conservacion: códigos de salida y --json."""

import json
import re
import tomllib
from pathlib import Path

import pytest

from ayudas import diligencia, relacion
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


def test_d27_indeterminado_devuelve_1(tmp_path):
    """Antes de A los seis regímenes podrían coincidir en «indeterminado»: también es 1."""
    doc = {"id": "O", "categoria": "operaciones", "fecha_documento": "2014-04-01", "fecha_ejecucion_operacion": "2014-04-01"}
    entrada = datos("2025-01-01", relacion(None, "2012-01-01"), [doc])
    assert main([escribir(tmp_path, entrada)]) == 1


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
