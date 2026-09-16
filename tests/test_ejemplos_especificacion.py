"""Los ocho ejemplos del §8 de docs/especificacion-calculo.md, con sus fechas."""

from datetime import date

import pytest

from ayudas import (
    comunicacion,
    diligencia,
    entrada,
    examen,
    negativa,
    ocasional,
    operacion,
    relacion,
)
from plazos.calculo import (
    ACCESO_RESTRINGIDO,
    AMLR,
    CONSERVACION_FACULTATIVA_77_4,
    CONSERVACION_PRORROGADA,
    ELIMINACION_EXIGIDA,
    EN_CONSERVACION,
    INDETERMINADO,
    LEY,
    PLAZO_NO_INICIADO,
    SIN_REGLA,
    SUPRESION_EXIGIDA,
    T1,
    T2,
    T3,
    T4,
    calcular,
)


def d(texto):
    return date.fromisoformat(texto)


def lecturas(resultado_regimen):
    return {l.id: l for l in resultado_regimen.lecturas}


def estados(doc):
    return {r: doc.estado(r) for r in (LEY, AMLR, T1, T2, T3, T4)}


# --- Ejemplo 1 ---------------------------------------------------------------


def ejemplo1(ref):
    return calcular(entrada(ref, relacion("2020-03-15"), [diligencia("DNI", "2019-01-01")])).documento("DNI")


def test_ejemplo1_fechas():
    doc = ejemplo1("2028-01-01")
    (ley,) = doc.regimenes[LEY].lecturas
    assert (ley.inicio, ley.acceso_restringido_desde, ley.vencimiento) == (d("2020-03-15"), d("2025-03-16"), d("2030-03-15"))
    (amlr,) = doc.regimenes[AMLR].lecturas
    assert (amlr.inicio, amlr.vencimiento, amlr.acceso_restringido_desde) == (d("2020-03-15"), d("2025-03-15"), None)
    assert ejemplo1("2030-03-15").estado(LEY) == ACCESO_RESTRINGIDO
    assert ejemplo1("2030-03-16").estado(LEY) == ELIMINACION_EXIGIDA


def test_ejemplo1_estados_en_2028():
    doc = ejemplo1("2028-01-01")
    assert estados(doc) == {
        LEY: ACCESO_RESTRINGIDO,
        AMLR: SUPRESION_EXIGIDA,
        T1: ACCESO_RESTRINGIDO,
        T2: SUPRESION_EXIGIDA,
        T3: EN_CONSERVACION,
        T4: ACCESO_RESTRINGIDO,
    }
    (t3,) = doc.regimenes[T3].lecturas
    assert t3.vencimiento == d("2030-03-15")
    assert not doc.transicion_coincide


# --- Ejemplo 2 ---------------------------------------------------------------


def test_ejemplo2_bisiesto():
    doc = calcular(
        entrada("2033-03-01", ocasional("2028-02-29"), [operacion("O", "2028-02-29", "2028-02-29")])
    ).documento("O")
    ley = lecturas(doc.regimenes[LEY])
    assert {l.vencimiento for l in ley.values()} == {d("2038-02-28")}
    assert {l.acceso_restringido_desde for l in ley.values()} == {d("2033-03-01")}
    assert doc.regimenes[AMLR].lecturas[0].vencimiento == d("2033-02-28")
    assert estados(doc) == {
        LEY: ACCESO_RESTRINGIDO,
        AMLR: SUPRESION_EXIGIDA,
        T1: SUPRESION_EXIGIDA,
        T2: SUPRESION_EXIGIDA,
        T3: SUPRESION_EXIGIDA,
        T4: ACCESO_RESTRINGIDO,
    }


# --- Ejemplo 3 ---------------------------------------------------------------


def ejemplo3(ref):
    return calcular(entrada(ref, negativa("2028-05-10"), [diligencia("REG", "2028-05-10")])).documento("REG")


def test_ejemplo3_en_2030_coinciden_los_seis():
    doc = ejemplo3("2030-01-01")
    assert set(estados(doc).values()) == {EN_CONSERVACION}
    assert doc.regimenes[AMLR].lecturas[0].vencimiento == d("2033-05-10")
    ley = lecturas(doc.regimenes[LEY])
    assert set(ley) == {"NG-1", "NG-2"}
    assert ley["NG-1"].vencimiento == d("2038-05-10")
    assert ley["NG-1"].acceso_restringido_desde is None  # D-18
    (t4,) = {l.vencimiento for l in doc.regimenes[T4].lecturas}
    assert t4 == d("2038-05-10")


def test_ejemplo3_divergen_desde_2033_05_11():
    assert ejemplo3("2033-05-10").estado(AMLR) == EN_CONSERVACION
    doc = ejemplo3("2033-05-11")
    assert estados(doc) == {
        LEY: EN_CONSERVACION,
        AMLR: SUPRESION_EXIGIDA,
        T1: SUPRESION_EXIGIDA,
        T2: SUPRESION_EXIGIDA,
        T3: SUPRESION_EXIGIDA,
        T4: EN_CONSERVACION,
    }


# --- Ejemplo 4 ---------------------------------------------------------------


def test_ejemplo4_en_2025_la_relacion_sigue_viva():
    """La relación termina el 2026-12-31, así que el 2025-01-01 sigue viva
    (modelo, ERR-09: un hecho no puede ser posterior a la referencia)."""
    doc = calcular(
        entrada("2025-01-01", relacion(None, "2012-01-01"), [operacion("O", "2014-04-01", "2014-04-01")])
    ).documento("O")
    ley = lecturas(doc.regimenes[LEY])
    assert ley["OP-1"].vencimiento == d("2024-04-01")
    assert ley["OP-1"].estado == ELIMINACION_EXIGIDA
    assert ley["OP-2"].estado == PLAZO_NO_INICIADO
    assert doc.estado(LEY) == INDETERMINADO
    assert {doc.estado(t) for t in (T1, T2, T3, T4)} == {INDETERMINADO}
    assert doc.transicion_coincide


def test_ejemplo4_en_2032():
    doc = calcular(
        entrada("2032-06-01", relacion("2026-12-31", "2012-01-01"), [operacion("O", "2014-04-01", "2014-04-01")])
    ).documento("O")
    ley = lecturas(doc.regimenes[LEY])
    assert (ley["OP-1"].estado, ley["OP-2"].estado) == (ELIMINACION_EXIGIDA, ACCESO_RESTRINGIDO)
    assert ley["OP-1"].acceso_restringido_desde is None  # R = 2032-01-01 > V
    assert (ley["OP-2"].vencimiento, ley["OP-2"].acceso_restringido_desde) == (d("2036-12-31"), d("2032-01-01"))
    assert doc.regimenes[AMLR].lecturas[0].vencimiento == d("2031-12-31")

    assert estados(doc) == {
        LEY: INDETERMINADO,
        AMLR: SUPRESION_EXIGIDA,
        T1: INDETERMINADO,
        T2: SUPRESION_EXIGIDA,
        T3: INDETERMINADO,
        T4: INDETERMINADO,
    }
    for t in (T1, T4):
        t_lecturas = lecturas(doc.regimenes[t])
        assert (t_lecturas["OP-1"].estado, t_lecturas["OP-2"].estado) == (ELIMINACION_EXIGIDA, ACCESO_RESTRINGIDO)
    t3 = lecturas(doc.regimenes[T3])
    assert (t3["OP-1"].estado, t3["OP-2"].estado) == (ELIMINACION_EXIGIDA, EN_CONSERVACION)
    assert t3["OP-2"].vencimiento == d("2032-07-10")


# --- Ejemplo 5 ---------------------------------------------------------------


def test_ejemplo5_examen_especial():
    doc = calcular(
        entrada(
            "2029-04-18",
            relacion("2023-09-30"),
            [examen("X", "2019-02-01", "2019-04-15", "2019-04-15", "2019-04-20")],
        )
    ).documento("X")
    ley = lecturas(doc.regimenes[LEY])
    esperado = {
        "EE-1": ("2019-02-01", "2029-02-01", ELIMINACION_EXIGIDA),
        "EE-2": ("2019-04-15", "2029-04-15", ELIMINACION_EXIGIDA),
        "EE-3": ("2019-04-15", "2029-04-15", ELIMINACION_EXIGIDA),
        "EE-4": ("2019-04-20", "2029-04-20", ACCESO_RESTRINGIDO),
        "EE-5": ("2023-09-30", "2033-09-30", ACCESO_RESTRINGIDO),
    }
    assert {k: (str(l.inicio), str(l.vencimiento), l.estado) for k, l in ley.items()} == esperado
    assert ley["EE-5"].acceso_restringido_desde == d("2028-10-01")
    assert doc.estado(LEY) == INDETERMINADO

    (amlr,) = doc.regimenes[AMLR].lecturas
    assert (amlr.inicio, amlr.vencimiento, amlr.estado) == (d("2023-09-30"), d("2028-09-30"), SUPRESION_EXIGIDA)
    assert doc.estado(AMLR) == SUPRESION_EXIGIDA


# --- Ejemplo 6 ---------------------------------------------------------------


def test_ejemplo6_politica_interna():
    """Política aprobada el 2020-01-01 y sustituida el 2026-01-01, en un
    expediente cuya relación sigue viva."""
    doc = calcular(
        entrada(
            "2028-01-01",
            relacion(None, "2019-01-01"),
            [comunicacion("POL", "politicas_procedimientos", "2020-01-01", fin_vigencia="2026-01-01")],
        )
    ).documento("POL")
    ley = lecturas(doc.regimenes[LEY])
    assert (ley["CI-1"].vencimiento, ley["CI-1"].estado) == (d("2030-01-01"), EN_CONSERVACION)
    assert (ley["CI-2"].vencimiento, ley["CI-2"].estado) == (d("2036-01-01"), EN_CONSERVACION)
    assert ley["CI-3"].estado == PLAZO_NO_INICIADO
    assert doc.estado(LEY) == INDETERMINADO
    assert all(l.acceso_restringido_desde is None for l in ley.values())

    amlr = lecturas(doc.regimenes[AMLR])
    assert doc.estado(AMLR) == SIN_REGLA
    assert amlr["SR-1"].estado == SIN_REGLA
    assert {amlr[k].estado for k in ("SR-2/CI-1", "SR-2/CI-2")} == {EN_CONSERVACION}
    assert amlr["SR-2/CI-3"].estado == PLAZO_NO_INICIADO
    assert amlr["SR-3"].estado == PLAZO_NO_INICIADO


# --- Ejemplo 7 ---------------------------------------------------------------


@pytest.mark.parametrize(
    "ref, amlr, ley",
    [
        ("2033-03-01", EN_CONSERVACION, EN_CONSERVACION),
        ("2036-01-01", CONSERVACION_PRORROGADA, ACCESO_RESTRINGIDO),
        ("2038-03-02", SUPRESION_EXIGIDA, ELIMINACION_EXIGIDA),
    ],
)
def test_ejemplo7_prorroga(ref, amlr, ley):
    doc = calcular(
        entrada(ref, relacion("2028-03-01"), [diligencia("D", "2028-01-01")],
                prorrogas=[("SEPBLAC", "2032-11-01", "2040-01-01")])
    ).documento("D")
    assert (doc.estado(AMLR), doc.estado(LEY)) == (amlr, ley)
    (lectura_amlr,) = doc.regimenes[AMLR].lecturas
    assert (lectura_amlr.vencimiento, lectura_amlr.fin_prorroga) == (d("2033-03-01"), d("2038-03-01"))
    assert "D-12" in {a.codigo for a in doc.regimenes[AMLR].avisos}
    (lectura_ley,) = doc.regimenes[LEY].lecturas
    assert (lectura_ley.vencimiento, lectura_ley.acceso_restringido_desde) == (d("2038-03-01"), d("2033-03-02"))


# --- Ejemplo 8 ---------------------------------------------------------------


def test_ejemplo8_procedimiento_judicial_pendiente():
    doc = calcular(
        entrada("2031-06-01", relacion("2021-01-15"), [diligencia("D", "2020-01-01")], pendiente=True)
    ).documento("D")
    amlr = lecturas(doc.regimenes[AMLR])
    assert set(amlr) == {"PA-1", "PA-2"}
    assert {l.vencimiento for l in amlr.values()} == {d("2026-01-15")}
    assert amlr["PA-1"].fin_conservacion_facultativa == d("2032-07-10")
    assert amlr["PA-2"].fin_conservacion_facultativa == d("2037-07-10")
    assert doc.estado(AMLR) == CONSERVACION_FACULTATIVA_77_4

    (ley,) = doc.regimenes[LEY].lecturas
    assert (ley.vencimiento, ley.acceso_restringido_desde) == (d("2031-01-15"), d("2026-01-16"))
    assert doc.estado(LEY) == ELIMINACION_EXIGIDA
