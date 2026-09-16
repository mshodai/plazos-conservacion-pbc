"""La salida: línea temporal, periodos distintos, JSON y texto."""

import json
from datetime import date

from ayudas import diligencia, entrada, relacion
from plazos.calculo import (
    ACCESO_RESTRINGIDO,
    AMLR,
    ELIMINACION_EXIGIDA,
    EN_CONSERVACION,
    LEY,
    PLAZO_NO_INICIADO,
    REGIMENES,
    SUPRESION_EXIGIDA,
    T2,
    T3,
)
from plazos.carga import cargar
from plazos.modelo import ResultadoCarga
from plazos.salida import Tramo, como_dict, como_json, informe, texto


def d(texto):
    return date.fromisoformat(texto)


def informe_ejemplo1(ref="2028-01-01"):
    """Ejemplo 1 de la especificación: relación terminada el 2020-03-15."""
    ent = entrada(ref, relacion("2020-03-15"), [diligencia("DNI", "2019-01-01")])
    return informe(ResultadoCarga(ent, ()))


def tramos(inf, regimen):
    return [(t.desde, t.hasta, t.estado) for t in inf.documentos[0].lineas[regimen]]


# --- Línea temporal ----------------------------------------------------------


def test_linea_temporal_ley():
    assert tramos(informe_ejemplo1(), LEY) == [
        (None, d("2020-03-14"), PLAZO_NO_INICIADO),
        (d("2020-03-15"), d("2025-03-15"), EN_CONSERVACION),
        (d("2025-03-16"), d("2030-03-15"), ACCESO_RESTRINGIDO),
        (d("2030-03-16"), None, ELIMINACION_EXIGIDA),
    ]


def test_linea_temporal_amlr():
    assert tramos(informe_ejemplo1(), AMLR) == [
        (None, d("2020-03-14"), PLAZO_NO_INICIADO),
        (d("2020-03-15"), d("2025-03-15"), EN_CONSERVACION),
        (d("2025-03-16"), None, SUPRESION_EXIGIDA),
    ]


def test_linea_temporal_de_la_transicion_cambia_en_a():
    inf = informe_ejemplo1()
    assert tramos(inf, T2)[2:] == [
        (d("2025-03-16"), d("2027-07-09"), ACCESO_RESTRINGIDO),
        (d("2027-07-10"), None, SUPRESION_EXIGIDA),
    ]
    assert tramos(inf, T3)[2:] == [
        (d("2025-03-16"), d("2027-07-09"), ACCESO_RESTRINGIDO),
        (d("2027-07-10"), d("2030-03-15"), EN_CONSERVACION),  # D-23: sin restricción, vence por la Ley
        (d("2030-03-16"), None, ELIMINACION_EXIGIDA),
    ]


def test_la_linea_temporal_no_depende_de_la_fecha_de_referencia():
    for regimen in REGIMENES:
        assert tramos(informe_ejemplo1("2021-01-01"), regimen) == tramos(informe_ejemplo1("2035-01-01"), regimen)


def test_la_linea_coincide_con_el_calculo_en_la_referencia():
    for ref in ("2020-03-15", "2025-03-15", "2025-03-16", "2027-07-09", "2027-07-10", "2030-03-16"):
        doc = informe_ejemplo1(ref).documentos[0]
        for regimen in REGIMENES:
            (tramo,) = [t for t in doc.lineas[regimen] if t.contiene(d(ref))]
            assert tramo.estado == doc.resultado.estado(regimen), (ref, regimen)


def test_tramo_contiene():
    assert Tramo(None, d("2020-01-01"), "x").contiene(d("1900-01-01"))
    assert not Tramo(d("2020-01-02"), None, "x").contiene(d("2020-01-01"))


# --- Periodos distintos ------------------------------------------------------


def test_periodos_distintos():
    periodos = informe_ejemplo1().documentos[0].periodos_distintos
    assert [(p.desde, p.hasta) for p in periodos] == [
        (d("2025-03-16"), d("2027-07-09")),
        (d("2027-07-10"), d("2030-03-15")),
        (d("2030-03-16"), None),
    ]
    antes_de_a, transicion, final = periodos
    assert antes_de_a.ley_y_amlr_difieren and not antes_de_a.transicion_difiere
    assert transicion.transicion_difiere
    assert final.estados[LEY] == ELIMINACION_EXIGIDA and final.estados[AMLR] == SUPRESION_EXIGIDA


def test_sin_diferencias():
    ent = entrada("2026-01-01", relacion(None, "2020-01-01"), [diligencia("D", "2020-01-01")])
    doc = informe(ResultadoCarga(ent, ())).documentos[0]
    assert not doc.estados_distintos
    assert doc.periodos_distintos == ()
    assert all(tramos == ((Tramo(None, None, PLAZO_NO_INICIADO)),) for tramos in doc.lineas.values())


# --- JSON --------------------------------------------------------------------


def test_json():
    datos = json.loads(como_json(informe_ejemplo1()))
    assert datos["valida"] and datos["errores"] == []
    assert (datos["fecha_referencia"], datos["fecha_aplicacion_amlr"]) == ("2028-01-01", "2027-07-10")
    (doc,) = datos["documentos"]
    assert set(doc["regimenes"]) == set(REGIMENES)
    assert doc["regimenes"][LEY]["estado"] == ACCESO_RESTRINGIDO
    assert doc["regimenes"][LEY]["lecturas"][0]["vencimiento"] == "2030-03-15"
    assert doc["regimenes"][LEY]["linea_temporal"][1] == {
        "desde": "2020-03-15", "hasta": "2025-03-15", "estado": EN_CONSERVACION,
    }
    comparacion = doc["comparacion"]
    assert comparacion["estados_distintos"] and comparacion["ley_y_amlr_difieren"]
    assert not comparacion["transicion_coincide"]
    assert {g["estado"]: g["regimenes"] for g in comparacion["grupos"]} == {
        ACCESO_RESTRINGIDO: ["ley_10_2010", "T-1", "T-4"],
        SUPRESION_EXIGIDA: ["amlr", "T-2"],
        EN_CONSERVACION: ["T-3"],
    }
    assert len(comparacion["periodos_distintos"]) == 3


def test_json_con_errores():
    datos = como_dict(informe(cargar("{}")))
    assert not datos["valida"]
    assert {e["codigo"] for e in datos["errores"]} == {"ERR-01"}
    assert datos["documentos"] == []


# --- Texto -------------------------------------------------------------------


def test_texto():
    salida = texto(informe_ejemplo1())
    assert "== Documento DNI (diligencia_debida)" in salida
    assert "La Ley y el AMLR dan estados distintos el 2028-01-01." in salida
    assert "T-1 a T-4 no coinciden" in salida
    assert (
        "ley_10_2010  plazo_no_iniciado → 2020-03-15 en_conservacion → "
        "2025-03-16 acceso_restringido ◀ → 2030-03-16 eliminacion_exigida"
    ) in salida
    assert "del 2025-03-16 al 2027-07-09 (AMLR aún no aplicable):" in salida
    assert "T-1: las mismas que ley_10_2010" in salida
    assert "D-10 (amlr, T-2)" in salida
    assert "no una determinación jurídica" in salida


def test_texto_con_errores():
    salida = texto(informe(cargar('{"regimen": "amlr"}')))
    assert salida.startswith("La entrada no es válida")
    assert "ERR-01  regimen:" in salida


def test_d25_la_nota_dice_que_es_una_proyeccion():
    salida = texto(informe_ejemplo1())
    assert "proyección de los hechos que constan hoy en la entrada, no una predicción" in salida
    assert "no una predicción" in como_dict(informe_ejemplo1())["nota_linea_temporal"]
