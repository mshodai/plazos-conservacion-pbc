"""Funciones auxiliares de los tests. No contiene tests."""

import json

from plazos.carga import cargar


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


def relacion(terminacion, inicio=None):
    return hecho("relacion_de_negocios", fecha_inicio=inicio, fecha_terminacion=terminacion)


def ocasional(ejecucion):
    return hecho("operacion_ocasional", fecha_ejecucion=ejecucion)


def negativa(fecha, objeto="relacion_de_negocios"):
    return hecho("negativa", fecha_negativa=fecha, objeto_negativa=objeto)


def diligencia(id_, fecha):
    return {"id": id_, "categoria": "diligencia_debida", "fecha_documento": fecha}


def operacion(id_, fecha, ejecucion=None):
    doc = {"id": id_, "categoria": "operaciones", "fecha_documento": fecha}
    if ejecucion:
        doc["fecha_ejecucion_operacion"] = ejecucion
    return doc


def examen(id_, apertura, cierre=None, decision=None, comunicacion=None):
    return {
        "id": id_,
        "categoria": "examen_especial",
        "fecha_documento": apertura,
        "fecha_apertura": apertura,
        "fecha_cierre": cierre,
        "fecha_decision_comunicacion": decision,
        "fecha_comunicacion": comunicacion,
    }


def comunicacion(id_, subtipo, fecha, fin_vigencia=None, examen_especial_id=None):
    doc = {"id": id_, "categoria": "comunicacion_control_interno", "subtipo": subtipo, "fecha_documento": fecha}
    doc["fecha_fin_vigencia"] = fin_vigencia
    if examen_especial_id:
        doc["examen_especial_id"] = examen_especial_id
    return doc


def fondos(id_, aplicacion, fin_proyecto=None):
    return {
        "id": id_,
        "categoria": "aplicacion_fondos",
        "fecha_documento": aplicacion,
        "proyecto": "P",
        "fecha_aplicacion": aplicacion,
        "fecha_fin_proyecto": fin_proyecto,
    }


def entrada(fecha_referencia, hecho_inicial, documentos, naturaleza="sujeto_obligado", actividad="otra",
            prorrogas=(), pendiente=False):
    """Entrada validada con `plazos.carga`."""
    datos = {
        "version_modelo": 2,
        "fecha_referencia": fecha_referencia,
        "sujeto": {"naturaleza": naturaleza, "actividad": actividad},
        "expediente": {
            "id": "E",
            "hecho_inicial": hecho_inicial,
            "documentos": list(documentos),
            "prorrogas_autoridad": [
                {"autoridad": a, "fecha_requerimiento": r, "fecha_fin": f} for a, r, f in prorrogas
            ],
            "procedimiento_judicial_pendiente_2027_07_10": pendiente,
        },
    }
    resultado = cargar(json.dumps(datos))
    assert resultado.valida, resultado.errores
    return resultado.entrada
