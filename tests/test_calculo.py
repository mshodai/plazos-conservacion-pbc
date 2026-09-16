"""Reglas de docs/especificacion-calculo.md que los ejemplos del §8 no cubren."""

from datetime import date

import pytest

from ayudas import comunicacion, diligencia, entrada, examen, fondos, hecho, negativa, operacion, relacion
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
    REGIMENES,
    SIN_REGLA,
    SUPRESION_EXIGIDA,
    T1,
    T2,
    T3,
    T4,
    TRANSICION,
    calcular,
    calcular_regimen,
    sumar_anios,
)


def d(texto):
    return date.fromisoformat(texto)


def por_id(regimen):
    return {l.id: l for l in regimen.lecturas}


# --- §1.3: cómputo de fechas -------------------------------------------------


@pytest.mark.parametrize(
    "fecha, anios, esperado",
    [("2020-03-15", 10, "2030-03-15"), ("2028-02-29", 5, "2033-02-28"), ("2028-02-29", 4, "2032-02-29")],
)
def test_d1_sumar_anios(fecha, anios, esperado):
    assert sumar_anios(d(fecha), anios) == d(esperado)


def test_d3_el_dia_de_inicio_ya_esta_en_plazo():
    ent = entrada("2020-03-15", relacion("2020-03-15"), [diligencia("D", "2020-01-01")])
    doc = calcular(ent).documento("D")
    assert doc.estado(LEY) == EN_CONSERVACION


# --- §1.1 y §1.4: forma del resultado ----------------------------------------


def test_seis_regimenes_por_documento():
    ent = entrada("2026-01-01", relacion("2020-03-15"), [diligencia("A", "2019-01-01"), diligencia("B", "2019-01-01")])
    resultado = calcular(ent)
    assert [doc.documento_id for doc in resultado.documentos] == ["A", "B"]
    for doc in resultado.documentos:
        assert tuple(doc.regimenes) == REGIMENES


def test_el_regimen_es_un_parametro():
    ent = entrada("2028-01-01", relacion("2020-03-15"), [diligencia("D", "2019-01-01")])
    (doc,) = ent.expediente.documentos
    assert calcular_regimen(ent, doc, T3).estado == EN_CONSERVACION
    with pytest.raises(ValueError):
        calcular_regimen(ent, doc, "espana")


# --- §2: Ley -----------------------------------------------------------------


def test_d22_relacion_viva_plazo_no_iniciado_sin_restriccion():
    ent = entrada("2040-01-01", relacion(None, "2010-01-01"), [diligencia("D", "2010-01-01")])
    (lectura,) = calcular(ent).documento("D").regimenes[LEY].lecturas
    assert (lectura.estado, lectura.acceso_restringido_desde) == (PLAZO_NO_INICIADO, None)


def test_d9_plazo_que_empieza_despues_de_r():
    """EE-2 con un examen cerrado más de cinco años después de H."""
    ent = entrada("2027-01-01", relacion("2020-01-01"), [examen("X", "2019-01-01", "2026-06-01", "2026-06-01")])
    ley = por_id(calcular(ent).documento("X").regimenes[LEY])
    assert ley["EE-2"].acceso_restringido_desde == d("2026-06-01")
    assert ley["EE-2"].estado == ACCESO_RESTRINGIDO


def test_examen_abierto():
    ent = entrada("2030-01-01", relacion("2020-01-01"), [examen("X", "2019-01-01")])
    ley = por_id(calcular(ent).documento("X").regimenes[LEY])
    assert {k: ley[k].estado for k in ("EE-2", "EE-3", "EE-4")} == dict.fromkeys(("EE-2", "EE-3", "EE-4"), PLAZO_NO_INICIADO)


def test_d7_ee4_sin_comunicacion_usa_la_decision():
    ent = entrada("2030-01-01", relacion("2020-01-01"), [examen("X", "2019-01-01", "2019-02-01", "2019-03-01")])
    assert por_id(calcular(ent).documento("X").regimenes[LEY])["EE-4"].inicio == d("2019-03-01")


def test_d18_negativa_en_examen_y_control_interno():
    ent = entrada(
        "2030-01-01",
        negativa("2025-01-01"),
        [examen("X", "2024-12-01", "2024-12-20", "2024-12-20"), comunicacion("C", "otro", "2024-12-21")],
    )
    resultado = calcular(ent)
    assert set(por_id(resultado.documento("X").regimenes[LEY])) == {"EE-1", "EE-2", "EE-3", "EE-4", "NG-1", "NG-2"}
    assert set(por_id(resultado.documento("C").regimenes[LEY])) == {"CI-1", "NG-1", "NG-2"}


def test_operacion_con_negativa_sin_fecha_de_operacion():
    ent = entrada("2030-01-01", negativa("2025-01-01", "operacion_ocasional"), [operacion("O", "2025-01-01")])
    assert set(por_id(calcular(ent).documento("O").regimenes[LEY])) == {"NG-1", "NG-2"}


def test_d8_fundacion_sin_hecho_inicial():
    ent = entrada("2031-01-01", hecho(None), [fondos("F", "2020-01-01", "2022-06-30")], naturaleza="fundacion")
    doc = calcular(ent).documento("F")
    ley = por_id(doc.regimenes[LEY])
    assert (ley["AF-1"].estado, ley["AF-2"].estado) == (ELIMINACION_EXIGIDA, EN_CONSERVACION)
    assert all(l.acceso_restringido_desde is None for l in ley.values())
    assert doc.estado(LEY) == INDETERMINADO
    amlr = por_id(doc.regimenes[AMLR])
    assert doc.estado(AMLR) == SIN_REGLA
    assert set(amlr) == {"SR-1", "SR-2/AF-1", "SR-2/AF-2"}  # sin SR-3: no hay hecho inicial


# --- §3: AMLR ----------------------------------------------------------------


def test_d19_comunicacion_por_indicio_sigue_el_77_1_b():
    ent = entrada(
        "2030-01-01",
        relacion("2026-01-01"),
        [examen("X", "2025-01-01", "2025-02-01", "2025-02-01", "2025-02-02"),
         comunicacion("C", "comunicacion_por_indicio", "2025-02-02", examen_especial_id="X")],
    )
    doc = calcular(ent).documento("C")
    (lectura,) = doc.regimenes[AMLR].lecturas
    assert (lectura.vencimiento, lectura.estado) == (d("2031-01-01"), EN_CONSERVACION)


def test_d20_aviso_antes_de_la_aplicacion():
    ent = entrada("2026-01-01", relacion("2020-03-15"), [diligencia("D", "2019-01-01")])
    avisos = {a.codigo for a in calcular(ent).documento("D").regimenes[AMLR].avisos}
    assert {"D-20", "D-10"} <= avisos


def test_d11_prorroga_requerida_tarde():
    ent = entrada("2034-01-01", relacion("2028-03-01"), [diligencia("D", "2028-01-01")],
                  prorrogas=[("SEPBLAC", "2033-06-01", "2036-01-01")])
    regimen = calcular(ent).documento("D").regimenes[AMLR]
    assert regimen.estado == SUPRESION_EXIGIDA
    assert "D-11" in {a.codigo for a in regimen.avisos}


def test_d13_antes_del_10_de_julio_de_2027_no_hay_conservacion_facultativa():
    ent = entrada("2027-07-09", relacion("2020-01-01"), [diligencia("D", "2019-01-01")], pendiente=True)
    assert calcular(ent).documento("D").estado(AMLR) == SUPRESION_EXIGIDA
    ent = entrada("2027-07-10", relacion("2020-01-01"), [diligencia("D", "2019-01-01")], pendiente=True)
    assert calcular(ent).documento("D").estado(AMLR) == CONSERVACION_FACULTATIVA_77_4


def test_d13_pa1_y_pa2_divergen_despues_de_2032():
    ent = entrada("2033-01-01", relacion("2020-01-01"), [diligencia("D", "2019-01-01")], pendiente=True)
    doc = calcular(ent).documento("D")
    amlr = por_id(doc.regimenes[AMLR])
    assert (amlr["PA-1"].estado, amlr["PA-2"].estado) == (SUPRESION_EXIGIDA, CONSERVACION_FACULTATIVA_77_4)
    assert doc.estado(AMLR) == INDETERMINADO


# --- §4: transición ----------------------------------------------------------


def test_antes_de_a_los_cuatro_son_la_ley():
    ent = entrada("2026-01-01", relacion("2020-03-15"), [diligencia("D", "2019-01-01")])
    doc = calcular(ent).documento("D")
    assert {doc.estado(t) for t in TRANSICION} == {doc.estado(LEY)}
    assert doc.transicion_coincide


def test_futbol_aplica_desde_2029():
    ent = entrada("2028-01-01", relacion("2020-03-15"), [diligencia("D", "2019-01-01")], actividad="agente_de_futbol")
    resultado = calcular(ent)
    doc = resultado.documento("D")
    assert resultado.fecha_aplicacion_amlr == d("2029-07-10")
    assert doc.estado(T2) == ACCESO_RESTRINGIDO  # todavía la Ley
    assert doc.transicion_coincide


def test_d23_t3_vence_por_el_amlr_con_77_4():
    """F = 2026-01-01 < A: la Ley vencería en 2036, pero A + 5 años es 2032-07-10."""
    ent = entrada("2032-07-11", relacion("2026-01-01"), [diligencia("D", "2025-01-01")], pendiente=True)
    t3 = por_id(calcular(ent).documento("D").regimenes[T3])
    assert {l.vencimiento for l in t3.values()} == {d("2032-07-10")}
    assert (t3["DD/PA-1"].estado, t3["DD/PA-2"].estado) == (SUPRESION_EXIGIDA, CONSERVACION_FACULTATIVA_77_4)


def test_t3_y_t2_dan_sin_regla_en_categorias_sin_regla():
    ent = entrada("2028-01-01", relacion("2020-01-01"), [comunicacion("C", "otro", "2019-06-01")])
    doc = calcular(ent).documento("C")
    assert (doc.estado(T2), doc.estado(T3)) == (SIN_REGLA, SIN_REGLA)
    assert doc.estado(T4) == doc.estado(LEY) == ACCESO_RESTRINGIDO
    assert doc.estado(T1) == ACCESO_RESTRINGIDO  # CI-1 y CI-3 empezaron antes de A


def test_t1_mezcla_ley_y_amlr_por_lectura():
    """EE-1 empieza antes de A (Ley); EE-5, con la relación terminada después, sigue el AMLR."""
    ent = entrada("2034-01-01", relacion("2028-01-01"), [examen("X", "2027-01-01", "2028-02-01", "2028-02-01")])
    t1 = por_id(calcular(ent).documento("X").regimenes[T1])
    assert (t1["EE-1"].norma, t1["EE-1"].estado) == ("ley", ACCESO_RESTRINGIDO)
    assert (t1["EE-5"].norma, t1["EE-5"].estado) == ("amlr", SUPRESION_EXIGIDA)


def test_d24_t4_la_prorroga_del_amlr_supera_a_la_ley():
    """EE-1 abre el 2027-08-01 (≥ A): la Ley vence el 2037-08-01; el AMLR, con
    prórroga, conserva hasta el 2038-01-01."""
    ent = entrada(
        "2037-10-01",
        relacion("2028-01-01"),
        [examen("X", "2027-08-01", "2027-09-01", "2027-09-01")],
        prorrogas=[("SEPBLAC", "2032-06-01", "2038-01-01")],
    )
    t4 = por_id(calcular(ent).documento("X").regimenes[T4])
    assert t4["EE-1"].estado == CONSERVACION_PRORROGADA
    assert t4["EE-5"].estado == ACCESO_RESTRINGIDO  # la Ley aún conserva: 2038-01-01


def test_d23_t3_empate_vence_por_la_ley():
    """F + 10 años = A + 5 años = 2032-07-10: vence por la Ley."""
    ent = entrada("2032-07-11", relacion("2022-07-10"), [diligencia("D", "2022-01-01")], pendiente=True)
    (t3,) = calcular(ent).documento("D").regimenes[T3].lecturas
    assert (t3.norma, t3.vencimiento, t3.estado) == ("ley", d("2032-07-10"), ELIMINACION_EXIGIDA)


def test_d24_t4_los_dos_vencidos():
    """El 2038-01-02 han vencido la Ley y el AMLR con prórroga (2038-01-01).
    EE-1: la Ley acabó antes (2037-08-01), así que manda el AMLR. EE-5: acaban
    el mismo día, así que manda la Ley."""
    ent = entrada(
        "2038-01-02",
        relacion("2028-01-01"),
        [examen("X", "2027-08-01", "2027-09-01", "2027-09-01")],
        prorrogas=[("SEPBLAC", "2032-06-01", "2038-01-01")],
    )
    t4 = por_id(calcular(ent).documento("X").regimenes[T4])
    assert (t4["EE-1"].norma, t4["EE-1"].estado) == ("amlr", SUPRESION_EXIGIDA)
    assert (t4["EE-5"].norma, t4["EE-5"].estado) == ("ley", ELIMINACION_EXIGIDA)
