"""Validaciones del §8 de docs/modelo-datos.md, una a una.

Cada test parte de una entrada mínima válida (una relación de negocios
terminada con un documento de diligencia debida) y cambia solo lo necesario
para provocar el error.
"""

import json
from datetime import date

import pytest

from plazos.carga import cargar, cargar_fichero
from plazos.modelo import ERRORES


def base():
    return {
        "version_modelo": 2,
        "fecha_referencia": "2030-01-01",
        "sujeto": {"naturaleza": "sujeto_obligado", "actividad": "otra"},
        "expediente": {
            "id": "E",
            "hecho_inicial": hecho("relacion_de_negocios", fecha_inicio="2015-01-01", fecha_terminacion="2020-03-15"),
            "documentos": [diligencia("D1")],
            "prorrogas_autoridad": [],
            "procedimiento_judicial_pendiente_2027_07_10": False,
        },
    }


def hecho(tipo, **fechas):
    datos = {
        "tipo": tipo,
        "fecha_inicio": None,
        "fecha_terminacion": None,
        "fecha_ejecucion": None,
        "fecha_negativa": None,
        "objeto_negativa": None,
    }
    datos.update(fechas)
    return datos


def diligencia(id_, fecha="2015-01-01"):
    return {"id": id_, "categoria": "diligencia_debida", "fecha_documento": fecha}


def operacion(id_, **campos):
    return {"id": id_, "categoria": "operaciones", "fecha_documento": "2016-01-01", **campos}


def examen(id_, **campos):
    datos = {
        "id": id_,
        "categoria": "examen_especial",
        "fecha_documento": "2018-01-01",
        "fecha_apertura": "2018-01-01",
        "fecha_cierre": "2018-02-01",
        "fecha_decision_comunicacion": "2018-02-01",
        "fecha_comunicacion": None,
    }
    datos.update(campos)
    return datos


def comunicacion(id_, subtipo, **campos):
    return {"id": id_, "categoria": "comunicacion_control_interno", "fecha_documento": "2018-02-02", "subtipo": subtipo, **campos}


def fondos(id_, **campos):
    datos = {
        "id": id_,
        "categoria": "aplicacion_fondos",
        "fecha_documento": "2019-01-01",
        "proyecto": "P1",
        "fecha_aplicacion": "2019-01-01",
        "fecha_fin_proyecto": None,
    }
    datos.update(campos)
    return datos


def cargar_dict(datos):
    return cargar(json.dumps(datos, ensure_ascii=False))


def codigos(resultado):
    return [e.codigo for e in resultado.errores]


def rutas(resultado):
    return {(e.codigo, e.ruta) for e in resultado.errores}


# --- Entrada válida ----------------------------------------------------------


def test_base_valida():
    resultado = cargar_dict(base())
    assert resultado.valida, resultado.errores
    assert resultado.entrada.fecha_referencia == date(2030, 1, 1)
    assert resultado.entrada.expediente.hecho_inicial.fecha_terminacion == date(2020, 3, 15)


def test_hay_nueve_codigos():
    assert sorted(ERRORES) == [f"ERR-0{n}" for n in range(1, 10)]


def test_cargar_fichero(tmp_path):
    ruta = tmp_path / "entrada.json"
    ruta.write_text(json.dumps(base()), encoding="utf-8")
    assert cargar_fichero(ruta).valida


# --- ERR-01: estructura y tipos ----------------------------------------------


def test_err01_regimen():
    datos = base()
    datos["regimen"] = "amlr"
    resultado = cargar_dict(datos)
    assert rutas(resultado) == {("ERR-01", "regimen")}
    assert resultado.entrada is None


def test_err01_campo_desconocido():
    datos = base()
    datos["expediente"]["prorroga_nacional_77_4"] = True
    assert rutas(cargar_dict(datos)) == {("ERR-01", "expediente.prorroga_nacional_77_4")}


def test_err01_campo_de_otra_categoria():
    datos = base()
    datos["expediente"]["documentos"][0]["fecha_apertura"] = "2015-01-01"
    assert rutas(cargar_dict(datos)) == {("ERR-01", "expediente.documentos[0].fecha_apertura")}


@pytest.mark.parametrize("campo", ["version_modelo", "fecha_referencia", "sujeto", "expediente"])
def test_err01_falta_campo_raiz(campo):
    datos = base()
    del datos[campo]
    assert ("ERR-01", campo) in rutas(cargar_dict(datos))


@pytest.mark.parametrize("campo", ["fecha_inicio", "objeto_negativa"])
def test_err01_falta_campo_del_hecho(campo):
    datos = base()
    del datos["expediente"]["hecho_inicial"][campo]
    assert rutas(cargar_dict(datos)) == {("ERR-01", f"expediente.hecho_inicial.{campo}")}


@pytest.mark.parametrize("valor", ["2020-3-15", "15/03/2020", "20200315", "2023-02-29", 20200315, None])
def test_err01_fecha_mal_formada(valor):
    datos = base()
    datos["fecha_referencia"] = valor
    assert codigos(cargar_dict(datos)) == ["ERR-01"]


@pytest.mark.parametrize("valor", [1, "2", 2.0, True])
def test_err01_version(valor):
    datos = base()
    datos["version_modelo"] = valor
    assert rutas(cargar_dict(datos)) == {("ERR-01", "version_modelo")}


@pytest.mark.parametrize(
    "ruta, valor",
    [
        (("sujeto", "naturaleza"), "empresa"),
        (("sujeto", "actividad"), None),
        (("expediente", "procedimiento_judicial_pendiente_2027_07_10"), "no"),
        (("expediente", "documentos"), {}),
        (("expediente", "hecho_inicial", "tipo"), "otra"),
    ],
)
def test_err01_valor_no_valido(ruta, valor):
    datos = base()
    destino = datos
    for clave in ruta[:-1]:
        destino = destino[clave]
    destino[ruta[-1]] = valor
    assert rutas(cargar_dict(datos)) == {("ERR-01", ".".join(ruta))}


def test_err01_json_mal_formado():
    resultado = cargar('{"version_modelo": 2,')
    assert codigos(resultado) == ["ERR-01"]
    assert resultado.entrada is None


def test_err01_clave_repetida():
    texto = json.dumps(base())
    texto = texto.replace('"version_modelo": 2', '"version_modelo": 2, "version_modelo": 2')
    assert codigos(cargar(texto)) == ["ERR-01"]


def test_err01_raiz_no_es_objeto():
    assert codigos(cargar("[]")) == ["ERR-01"]


def test_err01_fecha_fin_vigencia_obligatoria_en_politicas():
    datos = base()
    datos["expediente"]["documentos"].append(comunicacion("C1", "politicas_procedimientos"))
    assert rutas(cargar_dict(datos)) == {("ERR-01", "expediente.documentos[1].fecha_fin_vigencia")}


def test_err01_no_da_errores_derivados():
    """Una fecha mal formada no provoca además ERR-02 ni ERR-09."""
    datos = base()
    datos["expediente"]["hecho_inicial"] = hecho("operacion_ocasional", fecha_ejecucion="mañana")
    assert rutas(cargar_dict(datos)) == {("ERR-01", "expediente.hecho_inicial.fecha_ejecucion")}


# --- ERR-02: fechas del hecho inicial ----------------------------------------


def test_relacion_viva_es_valida():
    datos = base()
    datos["expediente"]["hecho_inicial"] = hecho("relacion_de_negocios", fecha_inicio="2015-01-01")
    assert cargar_dict(datos).valida


@pytest.mark.parametrize("tipo, fecha", [("operacion_ocasional", "fecha_ejecucion"), ("negativa", "fecha_negativa")])
def test_err02_falta_la_fecha_del_tipo(tipo, fecha):
    datos = base()
    datos["expediente"]["hecho_inicial"] = hecho(tipo, objeto_negativa="relacion_de_negocios" if tipo == "negativa" else None)
    assert rutas(cargar_dict(datos)) == {("ERR-02", f"expediente.hecho_inicial.{fecha}")}


def test_err02_fecha_de_otro_tipo():
    datos = base()
    datos["expediente"]["hecho_inicial"]["fecha_ejecucion"] = "2020-03-15"
    assert rutas(cargar_dict(datos)) == {("ERR-02", "expediente.hecho_inicial.fecha_ejecucion")}


def test_err02_fecha_inicio_sin_relacion():
    datos = base()
    datos["expediente"]["hecho_inicial"] = hecho("operacion_ocasional", fecha_inicio="2020-01-01", fecha_ejecucion="2020-03-15")
    assert rutas(cargar_dict(datos)) == {("ERR-02", "expediente.hecho_inicial.fecha_inicio")}


def test_err02_objeto_negativa_sin_negativa():
    datos = base()
    datos["expediente"]["hecho_inicial"]["objeto_negativa"] = "relacion_de_negocios"
    assert rutas(cargar_dict(datos)) == {("ERR-02", "expediente.hecho_inicial.objeto_negativa")}


def test_err02_tipo_nulo_con_fechas():
    datos = base()
    datos["sujeto"]["naturaleza"] = "fundacion"
    datos["expediente"]["hecho_inicial"] = hecho(None, fecha_terminacion="2020-03-15")
    datos["expediente"]["documentos"] = [fondos("F1")]
    assert rutas(cargar_dict(datos)) == {("ERR-02", "expediente.hecho_inicial.fecha_terminacion")}


# --- ERR-03: negativa sin objeto ---------------------------------------------


def test_negativa_valida_sin_regimen():
    """§0, principio 3: una negativa se admite aunque la Ley no la use."""
    datos = base()
    datos["expediente"]["hecho_inicial"] = hecho("negativa", fecha_negativa="2028-05-10", objeto_negativa="relacion_de_negocios")
    resultado = cargar_dict(datos)
    assert resultado.valida, resultado.errores
    assert resultado.entrada.expediente.hecho_inicial.fecha_negativa == date(2028, 5, 10)


def test_err03():
    datos = base()
    datos["expediente"]["hecho_inicial"] = hecho("negativa", fecha_negativa="2028-05-10")
    assert rutas(cargar_dict(datos)) == {("ERR-03", "expediente.hecho_inicial.objeto_negativa")}


# --- ERR-04: inicio posterior a terminación ----------------------------------


def test_err04():
    datos = base()
    datos["expediente"]["hecho_inicial"]["fecha_inicio"] = "2021-01-01"
    assert rutas(cargar_dict(datos)) == {("ERR-04", "expediente.hecho_inicial.fecha_inicio")}


def test_inicio_igual_a_terminacion_es_valido():
    datos = base()
    datos["expediente"]["hecho_inicial"]["fecha_inicio"] = "2020-03-15"
    assert cargar_dict(datos).valida


# --- ERR-05: tipo null -------------------------------------------------------


def test_tipo_nulo_con_fondos_es_valido():
    datos = base()
    datos["sujeto"]["naturaleza"] = "asociacion"
    datos["expediente"]["hecho_inicial"] = hecho(None)
    datos["expediente"]["documentos"] = [fondos("F1"), fondos("F2", fecha_fin_proyecto="2020-01-01")]
    resultado = cargar_dict(datos)
    assert resultado.valida, resultado.errores
    assert resultado.entrada.expediente.hecho_inicial.tipo is None


def test_err05():
    datos = base()
    datos["sujeto"]["naturaleza"] = "fundacion"
    datos["expediente"]["hecho_inicial"] = hecho(None)
    datos["expediente"]["documentos"] = [fondos("F1"), diligencia("D1")]
    assert rutas(cargar_dict(datos)) == {("ERR-05", "expediente.hecho_inicial.tipo")}


# --- ERR-06: aplicación de fondos en un sujeto obligado ----------------------


def test_err06():
    datos = base()
    datos["expediente"]["documentos"].append(fondos("F1"))
    assert rutas(cargar_dict(datos)) == {("ERR-06", "sujeto.naturaleza")}


# --- ERR-07: ids y referencias -----------------------------------------------


def test_err07_id_repetido():
    datos = base()
    datos["expediente"]["documentos"].append(diligencia("D1"))
    assert rutas(cargar_dict(datos)) == {("ERR-07", "expediente.documentos[1].id")}


def test_referencia_a_examen_especial_valida():
    datos = base()
    datos["expediente"]["documentos"] += [
        examen("X1"),
        comunicacion("C1", "comunicacion_por_indicio", examen_especial_id="X1", fecha_fin_vigencia=None),
    ]
    resultado = cargar_dict(datos)
    assert resultado.valida, resultado.errores


@pytest.mark.parametrize("referencia", ["NO-EXISTE", "D1"])
def test_err07_referencia_no_valida(referencia):
    datos = base()
    datos["expediente"]["documentos"].append(
        comunicacion("C1", "comunicacion_por_indicio", examen_especial_id=referencia)
    )
    assert rutas(cargar_dict(datos)) == {("ERR-07", "expediente.documentos[1].examen_especial_id")}


def test_err07_referencia_con_otro_subtipo():
    datos = base()
    datos["expediente"]["documentos"] += [examen("X1"), comunicacion("C1", "otro", examen_especial_id="X1")]
    assert rutas(cargar_dict(datos)) == {("ERR-07", "expediente.documentos[2].examen_especial_id")}


# --- ERR-08: operación sin fecha de ejecución --------------------------------


@pytest.mark.parametrize("campos", [{}, {"fecha_ejecucion_operacion": None}])
def test_err08(campos):
    datos = base()
    datos["expediente"]["documentos"].append(operacion("O1", **campos))
    assert rutas(cargar_dict(datos)) == {("ERR-08", "expediente.documentos[1].fecha_ejecucion_operacion")}


def test_operacion_ocasional_sin_fecha_de_operacion_es_valida():
    datos = base()
    datos["expediente"]["hecho_inicial"] = hecho("operacion_ocasional", fecha_ejecucion="2016-01-01")
    datos["expediente"]["documentos"] = [operacion("O1")]
    assert cargar_dict(datos).valida


# --- ERR-09: hechos posteriores a la fecha de referencia ---------------------


def test_err09_varias_fechas():
    datos = base()
    datos["fecha_referencia"] = "2019-01-01"
    datos["expediente"]["documentos"].append(examen("X1", fecha_cierre="2019-06-01"))
    assert rutas(cargar_dict(datos)) == {
        ("ERR-09", "expediente.hecho_inicial.fecha_terminacion"),
        ("ERR-09", "expediente.documentos[1].fecha_cierre"),
    }


def test_hecho_igual_a_la_referencia_es_valido():
    datos = base()
    datos["fecha_referencia"] = "2020-03-15"
    assert cargar_dict(datos).valida


def test_err09_no_cuenta_el_fin_de_la_prorroga():
    """§5: `fecha_fin` es el final previsto, no un hecho."""
    datos = base()
    datos["expediente"]["prorrogas_autoridad"] = [
        {"autoridad": "SEPBLAC", "fecha_requerimiento": "2029-11-01", "fecha_fin": "2035-01-01"}
    ]
    resultado = cargar_dict(datos)
    assert resultado.valida, resultado.errores
    (prorroga,) = resultado.entrada.expediente.prorrogas_autoridad
    assert prorroga.fecha_fin == date(2035, 1, 1)


def test_err09_requerimiento_posterior():
    datos = base()
    datos["expediente"]["prorrogas_autoridad"] = [
        {"autoridad": "SEPBLAC", "fecha_requerimiento": "2031-01-01", "fecha_fin": "2035-01-01"}
    ]
    assert rutas(cargar_dict(datos)) == {("ERR-09", "expediente.prorrogas_autoridad[0].fecha_requerimiento")}


# --- Varios errores a la vez -------------------------------------------------


def test_se_recogen_todos_los_errores_ordenados():
    datos = base()
    datos["regimen"] = "ley_10_2010"
    datos["expediente"]["hecho_inicial"]["fecha_inicio"] = "2021-01-01"
    datos["expediente"]["documentos"] += [diligencia("D1"), fondos("F1")]
    assert codigos(cargar_dict(datos)) == ["ERR-01", "ERR-04", "ERR-06", "ERR-07"]
