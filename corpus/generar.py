"""Genera el corpus de corpus/: expedientes sintéticos con su resultado esperado.

Uso, desde cualquier directorio: python corpus/generar.py

Cada caso es una entrada según docs/modelo-datos.md y un resultado esperado,
escrito a mano aquí a partir de docs/especificacion-calculo.md, no copiado
del cálculo. Antes de escribir nada, el script calcula cada caso con el
código de src/ y lo compara con lo esperado. Si alguno no coincide, termina
con error y no escribe ningún fichero.

Los datos son sintéticos y deterministas: cada ejecución produce exactamente
los mismos ficheros. Los identificadores dicen «FICTICIO» y las descripciones
«ficticio»; no hay nombres, NIF ni ningún dato que recuerde a una entidad o
persona real.

Por cada caso se escriben NN-nombre.json (la entrada) y
NN-nombre.esperado.json (qué demuestra y el resultado), y un README.md con la
lista. A = 2027-07-10 en todos los casos (sujeto con `actividad = "otra"`).
"""

import json
import sys
from dataclasses import dataclass
from pathlib import Path

DIRECTORIO = Path(__file__).resolve().parent
# Usa siempre el código de src/, no una versión instalada del paquete.
sys.path.insert(0, str(DIRECTORIO.parent / "src"))

from plazos.calculo import REGIMENES  # noqa: E402
from plazos.carga import cargar  # noqa: E402
from plazos.cli import codigo_de_salida  # noqa: E402
from plazos.salida import como_dict, informe  # noqa: E402

# Estados, con nombres cortos para que las expectativas se lean de un vistazo.
PNI = "plazo_no_iniciado"
CONS = "en_conservacion"
RESTR = "acceso_restringido"
ELIM = "eliminacion_exigida"
PRORR = "conservacion_prorrogada"
FACULT = "conservacion_facultativa_77_4"
SUPR = "supresion_exigida"
SIN = "sin_regla"
INDET = "indeterminado"

LEY, AMLR, T1, T2, T3, T4 = REGIMENES


# --- Construcción de las entradas --------------------------------------------


def hecho(tipo, inicio=None, terminacion=None, ejecucion=None):
    return {
        "tipo": tipo,
        "fecha_inicio": inicio,
        "fecha_terminacion": terminacion,
        "fecha_ejecucion": ejecucion,
        "fecha_negativa": None,
        "objeto_negativa": None,
    }


def expediente(numero, referencia, hecho_inicial, documento, prorrogas=(), pendiente=False):
    """Entrada con un solo documento, de un sujeto obligado ficticio."""
    return {
        "version_modelo": 2,
        "fecha_referencia": referencia,
        "sujeto": {"naturaleza": "sujeto_obligado", "actividad": "otra"},
        "expediente": {
            "id": f"EXP-FICTICIO-{numero:02d}",
            "hecho_inicial": hecho_inicial,
            "documentos": [documento],
            "prorrogas_autoridad": [
                {"autoridad": "Autoridad ficticia", "fecha_requerimiento": r, "fecha_fin": f} for r, f in prorrogas
            ],
            "procedimiento_judicial_pendiente_2027_07_10": pendiente,
        },
    }


def documento(categoria, fecha, descripcion, **campos):
    return {
        "id": "DOC-FICTICIO-1",
        "categoria": categoria,
        "descripcion": f"Documento ficticio: {descripcion}",
        "fecha_documento": fecha,
        **campos,
    }


# --- Resultado esperado ------------------------------------------------------


def lec(norma, estado, inicio=None, restringido=None, vence=None, prorroga=None, facultativa=None):
    """Una lectura: norma, estado y solo las fechas que tiene."""
    fechas = {
        "inicio": inicio,
        "acceso_restringido_desde": restringido,
        "vencimiento": vence,
        "fin_prorroga": prorroga,
        "fin_conservacion_facultativa": facultativa,
    }
    return {"norma": norma, "estado": estado, **{k: v for k, v in fechas.items() if v}}


def linea(primero, *cambios):
    """Línea temporal: el estado inicial y cada (fecha, estado) en que cambia."""
    return [[None, primero], *[[fecha, estado] for fecha, estado in cambios]]


def reg(lecturas, linea_temporal, avisos=()):
    return {"lecturas": lecturas, "avisos": sorted(avisos), "linea_temporal": linea_temporal}


def resultado(codigo, estados, regimenes):
    """Resultado de un expediente con un solo documento. `estados` en el orden de REGIMENES."""
    estados = dict(zip(REGIMENES, estados))
    return {
        "codigo_salida": codigo,
        "estados": estados,
        "transicion_coincide": len({estados[t] for t in (T1, T2, T3, T4)}) == 1,
        "regimenes": regimenes,
    }


def resumen(inf):
    """Lo que se compara de cada caso: estados, lecturas, avisos y línea temporal, sin mensajes ni citas."""
    datos = como_dict(inf)
    (doc,) = datos["documentos"]
    return {
        "codigo_salida": codigo_de_salida(inf),
        "estados": {r: doc["regimenes"][r]["estado"] for r in REGIMENES},
        "transicion_coincide": doc["comparacion"]["transicion_coincide"],
        "regimenes": {
            r: reg(
                {
                    l["id"]: lec(
                        l["norma"],
                        l["estado"],
                        l["inicio"],
                        l["acceso_restringido_desde"],
                        l["vencimiento"],
                        l["fin_prorroga"],
                        l["fin_conservacion_facultativa"],
                    )
                    for l in datos_r["lecturas"]
                },
                [[t["desde"], t["estado"]] for t in datos_r["linea_temporal"]],
                [a["codigo"] for a in datos_r["avisos"]],
            )
            for r, datos_r in doc["regimenes"].items()
        },
    }


# --- Los casos ---------------------------------------------------------------


@dataclass(frozen=True)
class Caso:
    nombre: str
    demuestra: str
    entrada: dict
    esperado: dict


def _caso_01():
    # Relación terminada el 2028-01-01 (≥ A). Ley: R = 2033-01-02, V = 2038-01-01.
    # AMLR: V = 2033-01-01. Con F ≥ A, T-1 a T-3 son el AMLR y T-4 toma la Ley (D-24).
    ley = lec("ley", CONS, "2028-01-01", "2033-01-02", "2038-01-01")
    amlr = lec("amlr", CONS, "2028-01-01", vence="2033-01-01")
    linea_ley = linea(PNI, ("2028-01-01", CONS), ("2033-01-02", RESTR), ("2038-01-02", ELIM))
    linea_amlr = linea(PNI, ("2028-01-01", CONS), ("2033-01-02", SUPR))
    return Caso(
        "01-mismo-estado-en-los-seis",
        "Diligencia debida de una relación terminada el 2028-01-01, a fecha 2030-01-01. Los seis regímenes dan "
        "en_conservacion: la Ley vence el 2038-01-01 y el AMLR el 2033-01-01, y los dos plazos están en curso. "
        "Código 0, aunque la línea temporal muestra que divergen desde el 2033-01-02: el código solo mira la "
        "fecha de referencia (§9.3).",
        expediente(1, "2030-01-01", hecho("relacion_de_negocios", "2020-01-01", "2028-01-01"),
                   documento("diligencia_debida", "2020-01-01", "copia de un documento de identidad inventado")),
        resultado(0, [CONS] * 6, {
            LEY: reg({"DD": ley}, linea_ley),
            AMLR: reg({"77.3": amlr}, linea_amlr),
            T1: reg({"DD": amlr}, linea_amlr),
            T2: reg({"77.3": amlr}, linea_amlr),
            T3: reg({"DD": amlr}, linea_amlr),
            T4: reg({"DD": ley}, linea_ley),
        }),
    )


def _caso_02():
    # Relación terminada el 2029-06-30 (≥ A). Ley: R = 2034-07-01, V = 2039-06-30.
    # AMLR: V = 2034-06-30, supresión desde 2034-07-01.
    ley = lec("ley", RESTR, "2029-06-30", "2034-07-01", "2039-06-30")
    amlr = lec("amlr", SUPR, "2029-06-30", vence="2034-06-30")
    linea_ley = linea(PNI, ("2029-06-30", CONS), ("2034-07-01", RESTR), ("2039-07-01", ELIM))
    linea_amlr = linea(PNI, ("2029-06-30", CONS), ("2034-07-01", SUPR))
    return Caso(
        "02-restringido-en-la-ley-suprimido-en-el-amlr",
        "Diligencia debida de una relación terminada el 2029-06-30, a fecha 2035-01-01. El mismo día "
        "(2034-07-01) en que la Ley pasa a acceso restringido (quinto año, D-4), el AMLR exige suprimir (V + 1, "
        "D-2). T-1 a T-3 siguen el AMLR porque el plazo empieza después de A; T-4 mantiene la Ley.",
        expediente(2, "2035-01-01", hecho("relacion_de_negocios", "2022-02-01", "2029-06-30"),
                   documento("diligencia_debida", "2022-02-01", "declaración inventada del cliente")),
        resultado(1, [RESTR, SUPR, SUPR, SUPR, SUPR, RESTR], {
            LEY: reg({"DD": ley}, linea_ley),
            AMLR: reg({"77.3": amlr}, linea_amlr, ["D-10"]),
            T1: reg({"DD": amlr}, linea_amlr, ["D-10"]),
            T2: reg({"77.3": amlr}, linea_amlr, ["D-10"]),
            T3: reg({"DD": amlr}, linea_amlr, ["D-10"]),
            T4: reg({"DD": ley}, linea_ley),
        }),
    )


def _caso_03():
    # Relación terminada el 2021-10-31 (< A): el plazo de la Ley está en curso el 2027-07-10.
    # Ley: R = 2026-11-01, V = 2031-10-31. AMLR: V = 2026-10-31.
    # T-3: vence el primero de 2031-10-31 y 2032-07-10: la Ley (D-23), sin restricción.
    ley = lec("ley", RESTR, "2021-10-31", "2026-11-01", "2031-10-31")
    amlr = lec("amlr", SUPR, "2021-10-31", vence="2026-10-31")
    linea_ley = linea(PNI, ("2021-10-31", CONS), ("2026-11-01", RESTR), ("2031-11-01", ELIM))
    return Caso(
        "03-plazo-en-curso-el-10-de-julio-de-2027",
        "Diligencia debida de una relación terminada el 2021-10-31, cuyo plazo de la Ley sigue en curso el "
        "2027-07-10. A fecha 2028-06-30 las lecturas de la transición no coinciden: T-1 y T-4 mantienen la Ley "
        "(acceso restringido), T-2 aplica el AMLR desde H y exige suprimir desde A, y T-3 cuenta desde A con el "
        "límite de la Ley y vuelve a en_conservacion sin restricción. T-1 y T-4 no pueden diferir aquí: para un "
        "plazo que empezó antes de A, las dos son la Ley (§4.2).",
        expediente(3, "2028-06-30", hecho("relacion_de_negocios", "2015-03-01", "2021-10-31"),
                   documento("diligencia_debida", "2015-03-01", "contrato inventado")),
        resultado(1, [RESTR, SUPR, RESTR, SUPR, CONS, RESTR], {
            LEY: reg({"DD": ley}, linea_ley),
            AMLR: reg({"77.3": amlr}, linea(PNI, ("2021-10-31", CONS), ("2026-11-01", SUPR)), ["D-10"]),
            T1: reg({"DD": ley}, linea_ley),
            T2: reg({"77.3": amlr},
                    linea(PNI, ("2021-10-31", CONS), ("2026-11-01", RESTR), ("2027-07-10", SUPR)), ["D-10"]),
            T3: reg({"DD": lec("ley", CONS, "2021-10-31", vence="2031-10-31")},
                    linea(PNI, ("2021-10-31", CONS), ("2026-11-01", RESTR), ("2027-07-10", CONS), ("2031-11-01", ELIM))),
            T4: reg({"DD": ley}, linea_ley),
        }),
    )


def _caso_04():
    # Relación viva, operación ejecutada el 2015-05-20. Referencia 2026-01-01 (< A).
    # OP-1: V = 2025-05-20, eliminación desde 2025-05-21. OP-2: sin terminación, plazo no iniciado.
    # Sin terminación no hay R. AMLR: sin H, plazo no iniciado, con aviso D-20.
    ley = {"OP-1": lec("ley", ELIM, "2015-05-20", vence="2025-05-20"), "OP-2": lec("ley", PNI)}
    linea_ley = linea(PNI, ("2015-05-20", INDET))
    return Caso(
        "04-operacion-en-relacion-viva",
        "Operación ejecutada el 2015-05-20 dentro de una relación que sigue viva, a fecha 2026-01-01. Con la "
        "letra de la Ley (OP-1, art. 25.1.b) la operación ya debía eliminarse el 2025-05-21; con el RD (OP-2, "
        "art. 29.1) su plazo no ha empezado, porque cuenta desde la terminación. La Ley queda indeterminado "
        "(D-6), y T-1 a T-4 con ella, porque es antes de A. La línea temporal no cambia al pasar de "
        "en_conservacion a eliminacion_exigida en OP-1: el estado del régimen sigue siendo indeterminado (D-26).",
        expediente(4, "2026-01-01", hecho("relacion_de_negocios", "2010-03-01"),
                   documento("operaciones", "2015-05-20", "orden de transferencia inventada",
                             fecha_ejecucion_operacion="2015-05-20")),
        resultado(1, [INDET, PNI, INDET, INDET, INDET, INDET], {
            LEY: reg(ley, linea_ley),
            AMLR: reg({"77.3": lec("amlr", PNI)}, linea(PNI), ["D-20"]),
            T1: reg(ley, linea_ley),
            T2: reg(ley, linea(PNI, ("2015-05-20", INDET), ("2027-07-10", PNI))),
            T3: reg(ley, linea_ley),
            T4: reg(ley, linea_ley),
        }),
    )


def _caso_05():
    # Relación terminada el 2022-03-31: R = 2027-04-01. Examen especial: apertura 2021-01-10,
    # cierre 2021-02-15, decisión 2021-02-20, comunicación 2021-02-25. Referencia 2031-02-18.
    fechas = {
        "EE-1": ("2021-01-10", "2031-01-10"),
        "EE-2": ("2021-02-15", "2031-02-15"),
        "EE-3": ("2021-02-20", "2031-02-20"),
        "EE-4": ("2021-02-25", "2031-02-25"),
        "EE-5": ("2022-03-31", "2032-03-31"),
    }
    vencidas = {"EE-1", "EE-2"}  # V < 2031-02-18
    ley = {k: lec("ley", ELIM if k in vencidas else RESTR, i, "2027-04-01", v) for k, (i, v) in fechas.items()}
    # T-3: todas empiezan antes de A y la Ley vence antes que A + 5 años: plazo de la Ley, sin restricción (D-23).
    t3 = {k: lec("ley", ELIM if k in vencidas else CONS, i, vence=v) for k, (i, v) in fechas.items()}
    amlr = lec("amlr", SUPR, "2022-03-31", vence="2027-03-31")
    linea_ley = linea(PNI, ("2021-01-10", INDET), ("2022-03-31", CONS), ("2027-04-01", RESTR),
                      ("2031-01-11", INDET), ("2032-04-01", ELIM))
    return Caso(
        "05-examen-especial-cinco-lecturas",
        "Examen especial (apertura 2021-01-10, cierre 2021-02-15, decisión 2021-02-20, comunicación 2021-02-25) "
        "de una relación terminada el 2022-03-31, a fecha 2031-02-18. El RD 25.4 no dice desde cuándo cuentan "
        "los diez años: EE-1 y EE-2 ya exigen eliminar, EE-3 a EE-5 siguen en acceso restringido, y la Ley da "
        "indeterminado. El AMLR cuenta desde la terminación y exige suprimir desde el 2027-04-01.",
        expediente(5, "2031-02-18", hecho("relacion_de_negocios", "2018-06-01", "2022-03-31"),
                   documento("examen_especial", "2021-01-10", "expediente de examen especial inventado",
                             fecha_apertura="2021-01-10", fecha_cierre="2021-02-15",
                             fecha_decision_comunicacion="2021-02-20", fecha_comunicacion="2021-02-25")),
        resultado(1, [INDET, SUPR, INDET, SUPR, INDET, INDET], {
            LEY: reg(ley, linea_ley),
            AMLR: reg({"77.3": amlr}, linea(PNI, ("2022-03-31", CONS), ("2027-04-01", SUPR)), ["D-10"]),
            T1: reg(ley, linea_ley),
            T2: reg({"77.3": amlr},
                    linea(PNI, ("2021-01-10", INDET), ("2022-03-31", CONS), ("2027-04-01", RESTR), ("2027-07-10", SUPR)),
                    ["D-10"]),
            T3: reg(t3, linea(PNI, ("2021-01-10", INDET), ("2022-03-31", CONS), ("2027-04-01", RESTR),
                              ("2027-07-10", CONS), ("2031-01-11", INDET), ("2032-04-01", ELIM))),
            T4: reg(ley, linea_ley),
        }),
    )


def _caso_06():
    # Operación ocasional del 2028-02-01: R = 2033-02-02. Análisis de riesgo del 2028-01-15, sustituido
    # el 2029-01-15. Referencia 2030-06-01.
    # CI-1: V = 2038-01-15. CI-2: V = 2039-01-15. CI-3: V = 2038-02-01.
    ley = {
        "CI-1": lec("ley", CONS, "2028-01-15", "2033-02-02", "2038-01-15"),
        "CI-2": lec("ley", CONS, "2029-01-15", "2033-02-02", "2039-01-15"),
        "CI-3": lec("ley", CONS, "2028-02-01", "2033-02-02", "2038-02-01"),
    }
    amlr = {
        "SR-1": lec("ninguna", SIN),
        **{f"SR-2/{k}": v for k, v in ley.items()},
        "SR-3": lec("amlr", CONS, "2028-02-01", vence="2033-02-01"),
    }
    sin_regla = {k: lec("ninguna", SIN) for k in ley}
    linea_ley = linea(PNI, ("2028-01-15", INDET), ("2029-01-15", CONS), ("2033-02-02", RESTR),
                      ("2038-01-16", INDET), ("2039-01-16", ELIM))
    linea_sin_regla = linea(PNI, ("2027-07-10", SIN))
    return Caso(
        "06-control-interno-sin-regla-en-el-amlr",
        "Análisis de riesgo del 2028-01-15, sustituido el 2029-01-15, en el expediente de una operación "
        "ocasional del 2028-02-01, a fecha 2030-06-01. La Ley (RD 29.2) lo conserva diez años con las lecturas "
        "CI-1 a CI-3, que hoy coinciden. El art. 77.1 del AMLR no lo incluye: sin_regla (D-17), con las "
        "lecturas SR-1 a SR-3. T-1 a T-3 quedan en sin_regla desde A; T-4 sigue la Ley.",
        expediente(6, "2030-06-01", hecho("operacion_ocasional", ejecucion="2028-02-01"),
                   documento("comunicacion_control_interno", "2028-01-15", "análisis de riesgo inventado",
                             subtipo="analisis_riesgo", fecha_fin_vigencia="2029-01-15")),
        resultado(1, [CONS, SIN, SIN, SIN, SIN, CONS], {
            LEY: reg(ley, linea_ley),
            AMLR: reg(amlr, linea(SIN)),
            T1: reg(sin_regla, linea_sin_regla),
            T2: reg(amlr, linea_sin_regla),
            T3: reg(sin_regla, linea_sin_regla),
            T4: reg(ley, linea_ley),
        }),
    )


def _caso_07():
    # Relación terminada el 2028-09-30. Ley: R = 2033-10-01, V = 2038-09-30.
    # AMLR: V = 2033-09-30; requerimiento del 2033-05-01 (≤ V, D-11) hasta el 2036-12-31, por debajo
    # del límite V + 5 años = 2038-09-30 (D-12): prórroga hasta el 2036-12-31.
    ley = lec("ley", RESTR, "2028-09-30", "2033-10-01", "2038-09-30")
    amlr = lec("amlr", PRORR, "2028-09-30", vence="2033-09-30", prorroga="2036-12-31")
    linea_ley = linea(PNI, ("2028-09-30", CONS), ("2033-10-01", RESTR), ("2038-10-01", ELIM))
    linea_amlr = linea(PNI, ("2028-09-30", CONS), ("2033-10-01", PRORR), ("2037-01-01", SUPR))
    return Caso(
        "07-prorroga-de-la-autoridad",
        "Diligencia debida de una relación terminada el 2028-09-30, con un requerimiento de la autoridad del "
        "2033-05-01 para conservarla hasta el 2036-12-31, a fecha 2035-06-01. En el AMLR, conservación "
        "prorrogada del 2033-10-01 al 2036-12-31 (art. 77.3, D-11, D-12); en la Ley, que no tiene prórroga, "
        "acceso restringido hasta el 2038-09-30. T-4 elimina por la Ley el 2038-10-01, porque la Ley acaba "
        "después que la prórroga (D-24). Como la línea temporal proyecta los hechos de hoy (D-25), la prórroga "
        "aparece aunque se requirió después de empezar el plazo.",
        expediente(7, "2035-06-01", hecho("relacion_de_negocios", "2023-01-01", "2028-09-30"),
                   documento("diligencia_debida", "2023-01-01", "justificante inventado de actividad"),
                   prorrogas=[("2033-05-01", "2036-12-31")]),
        resultado(1, [RESTR, PRORR, PRORR, PRORR, PRORR, RESTR], {
            LEY: reg({"DD": ley}, linea_ley),
            AMLR: reg({"77.3": amlr}, linea_amlr),
            T1: reg({"DD": amlr}, linea_amlr),
            T2: reg({"77.3": amlr}, linea_amlr),
            T3: reg({"DD": amlr}, linea_amlr),
            T4: reg({"DD": ley}, linea_ley),
        }),
    )


def _caso_08():
    # Relación terminada el 2019-11-30, procedimiento judicial pendiente el 2027-07-10. Referencia 2033-03-01.
    # Ley: R = 2024-12-01, V = 2029-11-30. AMLR: V = 2024-11-30; art. 77.4: facultativa desde el 2027-07-10
    # hasta el 2032-07-10 (PA-1) o el 2037-07-10 (PA-2).
    # T-3: la Ley vence el 2029-11-30, antes que A + 5 años: eliminación sin art. 77.4 (D-23).
    ley = lec("ley", ELIM, "2019-11-30", "2024-12-01", "2029-11-30")
    amlr = {
        "PA-1": lec("amlr", SUPR, "2019-11-30", vence="2024-11-30", facultativa="2032-07-10"),
        "PA-2": lec("amlr", FACULT, "2019-11-30", vence="2024-11-30", facultativa="2037-07-10"),
    }
    linea_ley = linea(PNI, ("2019-11-30", CONS), ("2024-12-01", RESTR), ("2029-12-01", ELIM))
    return Caso(
        "08-procedimiento-judicial-pendiente",
        "Diligencia debida de una relación terminada el 2019-11-30, relacionada con un procedimiento judicial "
        "pendiente el 2027-07-10, a fecha 2033-03-01. El AMLR ya exigía suprimir desde el 2024-12-01, pero el "
        "art. 77.4 permite conservar desde el 2027-07-10: hasta el 2032-07-10 sin período adicional (PA-1) o "
        "hasta el 2037-07-10 con él (PA-2). Hoy PA-1 exige suprimir y PA-2 permite conservar: indeterminado "
        "(D-13). La Ley, sin excepción judicial, exige eliminar desde el 2029-12-01, y T-3 también (D-23).",
        expediente(8, "2033-03-01", hecho("relacion_de_negocios", "2012-09-01", "2019-11-30"),
                   documento("diligencia_debida", "2012-09-01", "copia inventada de escritura"),
                   pendiente=True),
        resultado(1, [ELIM, INDET, ELIM, INDET, ELIM, ELIM], {
            LEY: reg({"DD": ley}, linea_ley),
            AMLR: reg(amlr, linea(PNI, ("2019-11-30", CONS), ("2024-12-01", SUPR), ("2027-07-10", FACULT),
                                  ("2032-07-11", INDET), ("2037-07-11", SUPR)), ["D-10"]),
            T1: reg({"DD": ley}, linea_ley),
            T2: reg(amlr, linea(PNI, ("2019-11-30", CONS), ("2024-12-01", RESTR), ("2027-07-10", FACULT),
                                ("2032-07-11", INDET), ("2037-07-11", SUPR)), ["D-10"]),
            T3: reg({"DD": lec("ley", ELIM, "2019-11-30", vence="2029-11-30")},
                    linea(PNI, ("2019-11-30", CONS), ("2024-12-01", RESTR), ("2027-07-10", CONS), ("2029-12-01", ELIM))),
            T4: reg({"DD": ley}, linea_ley),
        }),
    )


CASOS = [_caso_01(), _caso_02(), _caso_03(), _caso_04(), _caso_05(), _caso_06(), _caso_07(), _caso_08()]


# --- Autoverificación y escritura --------------------------------------------


def comprobar(caso):
    """Calcula el caso y devuelve las diferencias con lo esperado (vacío si coincide)."""
    carga = cargar(json.dumps(caso.entrada, ensure_ascii=False))
    if carga.errores:
        return [f"la entrada no es válida: {[e.codigo for e in carga.errores]}"]
    obtenido = resumen(informe(carga))
    diferencias = [
        f"{clave}: se esperaba {caso.esperado[clave]!r} y se obtuvo {obtenido[clave]!r}"
        for clave in ("codigo_salida", "estados", "transicion_coincide")
        if obtenido[clave] != caso.esperado[clave]
    ]
    for regimen in REGIMENES:
        for parte in ("lecturas", "avisos", "linea_temporal"):
            esperado = caso.esperado["regimenes"][regimen][parte]
            calculado = obtenido["regimenes"][regimen][parte]
            if calculado != esperado:
                diferencias.append(f"{regimen}.{parte}: se esperaba {esperado!r} y se obtuvo {calculado!r}")
    return diferencias


def ficheros(caso):
    """Los dos ficheros de un caso: nombre → contenido."""
    esperado = {"caso": caso.nombre, "demuestra": caso.demuestra, "resultado": caso.esperado}
    return {f"{caso.nombre}.json": _json(caso.entrada), f"{caso.nombre}.esperado.json": _json(esperado)}


def readme():
    lineas = [
        "# Corpus",
        "",
        "Expedientes sintéticos con su resultado esperado. Lo genera `corpus/generar.py`, que comprueba cada "
        "caso con el código de `src/` antes de escribirlo. No se edita a mano.",
        "",
        "```",
        "python corpus/generar.py",
        "```",
        "",
        "Cada caso tiene la entrada (`NN-nombre.json`, según `docs/modelo-datos.md`) y el resultado esperado "
        "(`NN-nombre.esperado.json`): el estado del documento en los seis regímenes en la fecha de referencia, "
        "sus lecturas con sus fechas, los avisos y la línea temporal de cada régimen. Los resultados esperados "
        "están escritos a mano en `generar.py` a partir de `docs/especificacion-calculo.md`. El código de salida "
        "es el de `plazos-conservacion` (§9.3): 0 si los seis regímenes dan el mismo estado y ninguno es "
        "`indeterminado`; 1 si no.",
        "",
        "| Caso | Referencia | " + " | ".join(REGIMENES) + " | Código |",
        "|---|---|" + "---|" * len(REGIMENES) + "---|",
    ]
    for caso in CASOS:
        r = caso.esperado
        fila = [caso.nombre, caso.entrada["fecha_referencia"], *(r["estados"][g] for g in REGIMENES),
                str(r["codigo_salida"])]
        lineas.append("| " + " | ".join(fila) + " |")
    lineas += ["", "## Qué demuestra cada caso", ""]
    for caso in CASOS:
        lineas += [f"**{caso.nombre}.** {caso.demuestra}", ""]
    return "\n".join(lineas).rstrip("\n") + "\n"


def _json(datos):
    return json.dumps(datos, ensure_ascii=False, indent=2) + "\n"


def main():
    fallos = [(caso.nombre, diferencias) for caso in CASOS if (diferencias := comprobar(caso))]
    if fallos:
        for nombre, diferencias in fallos:
            print(f"{nombre}:", *diferencias, sep="\n  ", file=sys.stderr)
        sys.exit(f"{len(fallos)} caso(s) no dan el resultado esperado: no se escribe nada")
    for caso in CASOS:
        for nombre, contenido in ficheros(caso).items():
            (DIRECTORIO / nombre).write_text(contenido, encoding="utf-8", newline="\n")
        print(f"Escrito corpus/{caso.nombre}.json y .esperado.json")
    (DIRECTORIO / "README.md").write_text(readme(), encoding="utf-8", newline="\n")
    print("Escrito corpus/README.md")


if __name__ == "__main__":
    main()
