"""La salida: el estado de cada documento en los seis regímenes y dónde difieren.

`informe` calcula los seis regímenes sobre una entrada ya cargada y añade dos
cosas que el cálculo no da por sí solo:

- la **línea temporal** de cada régimen: en qué fechas cambia el estado del
  documento, calculada evaluando el estado en cada fecha en que puede cambiar;
- la **comparación**: qué regímenes dan estados distintos en la fecha de
  referencia y en qué periodos de la línea temporal difieren.

`texto` y `como_json` lo presentan, según el §9 de la especificación. Las
decisiones de la especificación se citan como «D-n»; el resto de comentarios
son de formato.
"""

import json
from dataclasses import dataclass, replace
from datetime import date, timedelta

from plazos.calculo import (
    ACCESO_RESTRINGIDO,
    AMLR,
    ELIMINACION_EXIGIDA,
    FECHA_77_4,
    FIN_PA,
    INDETERMINADO,
    LEY,
    PLAZO_AMLR,
    REGIMENES,
    SUPRESION_EXIGIDA,
    TRANSICION,
    Lectura,
    ResultadoDocumento,
    calcular,
    calcular_regimen,
    sumar_anios,
)
from plazos.modelo import Entrada, Incidencia, ResultadoCarga

UN_DIA = timedelta(days=1)

# D-28: los estados que exigen hacer algo con el documento.
ESTADOS_QUE_EXIGEN_ACTUAR = frozenset({ELIMINACION_EXIGIDA, SUPRESION_EXIGIDA, ACCESO_RESTRINGIDO})

ADVERTENCIA = (
    "Resultado de un cálculo bajo las lecturas que declara la especificación "
    "(docs/especificacion-calculo.md), no una determinación jurídica. Donde la norma no fija "
    "un dato, el cálculo da todas las lecturas y no elige; las decisiones propias se citan como D-n."
)

# D-25: la línea temporal es una proyección de los hechos conocidos, no una predicción.
NOTA_LINEA_TEMPORAL = (
    "La línea temporal es una proyección de los hechos que constan hoy en la entrada, no una "
    "predicción: aplica esos hechos a todas las fechas, sin tener en cuenta cuándo se conoció "
    "cada uno ni hechos futuros, como una prórroga nueva o la terminación de una relación que "
    "sigue viva. Si cambia un hecho, cambia la línea temporal."
)


# --- Estructuras del informe -------------------------------------------------


@dataclass(frozen=True)
class Tramo:
    """Periodo con un mismo estado. `desde` None: desde siempre; `hasta` None: en adelante."""

    desde: date | None
    hasta: date | None
    estado: str

    def contiene(self, fecha: date) -> bool:
        return (self.desde is None or self.desde <= fecha) and (self.hasta is None or fecha <= self.hasta)


@dataclass(frozen=True)
class PeriodoDistinto:
    """Periodo en que los seis regímenes no dan el mismo estado."""

    desde: date | None
    hasta: date | None
    estados: dict[str, str]

    @property
    def ley_y_amlr_difieren(self) -> bool:
        return self.estados[LEY] != self.estados[AMLR]

    @property
    def transicion_difiere(self) -> bool:
        return len({self.estados[t] for t in TRANSICION}) > 1


@dataclass(frozen=True)
class Activador:
    """D-28: una lectura de un régimen que da un estado que exige actuar."""

    regimen: str
    lectura: str | None
    estado: str


@dataclass(frozen=True)
class InformeDocumento:
    resultado: ResultadoDocumento
    lineas: dict[str, tuple[Tramo, ...]]
    periodos_distintos: tuple[PeriodoDistinto, ...]

    @property
    def id(self) -> str:
        return self.resultado.documento_id

    @property
    def estados(self) -> dict[str, str]:
        return {r: self.resultado.estado(r) for r in REGIMENES}

    @property
    def estados_distintos(self) -> bool:
        return len(set(self.estados.values())) > 1

    @property
    def ley_y_amlr_difieren(self) -> bool:
        return self.estados[LEY] != self.estados[AMLR]

    @property
    def grupos(self) -> dict[str, tuple[str, ...]]:
        """Estado → regímenes que lo dan, en el orden de REGIMENES."""
        grupos: dict[str, list[str]] = {}
        for regimen, estado in self.estados.items():
            grupos.setdefault(estado, []).append(regimen)
        return {estado: tuple(regimenes) for estado, regimenes in grupos.items()}

    @property
    def hay_indeterminado(self) -> bool:
        return INDETERMINADO in self.estados.values()

    @property
    def activadores(self) -> tuple[Activador, ...]:
        """D-28: cada régimen y lectura que da un estado que exige actuar, en el orden de REGIMENES."""
        activadores = []
        for regimen, res in self.resultado.regimenes.items():
            if res.lecturas:
                activadores += [
                    Activador(regimen, l.id, l.estado) for l in res.lecturas if l.estado in ESTADOS_QUE_EXIGEN_ACTUAR
                ]
            elif res.estado in ESTADOS_QUE_EXIGEN_ACTUAR:
                activadores.append(Activador(regimen, None, res.estado))
        return tuple(activadores)

    @property
    def exige_actuar(self) -> bool:
        """D-28: alguna lectura de algún régimen da un estado que exige actuar."""
        return bool(self.activadores)


@dataclass(frozen=True)
class Informe:
    errores: tuple[Incidencia, ...]
    expediente_id: str | None = None
    fecha_referencia: date | None = None
    fecha_aplicacion_amlr: date | None = None
    documentos: tuple[InformeDocumento, ...] = ()

    @property
    def valida(self) -> bool:
        return not self.errores

    @property
    def exige_actuar(self) -> bool:
        """D-28: en algún documento, alguna lectura exige actuar."""
        return any(d.exige_actuar for d in self.documentos)


# --- Construcción ------------------------------------------------------------


def informe(carga: ResultadoCarga) -> Informe:
    if not carga.valida:
        return Informe(errores=carga.errores)
    entrada = carga.entrada
    resultado = calcular(entrada)
    documentos = []
    for doc, res in zip(entrada.expediente.documentos, resultado.documentos):
        fechas = fechas_de_cambio(entrada, doc, resultado.fecha_aplicacion_amlr)
        lineas = {r: linea_temporal(entrada, doc, r, fechas) for r in REGIMENES}
        documentos.append(InformeDocumento(res, lineas, periodos_distintos(lineas)))
    return Informe(
        errores=(),
        expediente_id=entrada.expediente.id,
        fecha_referencia=entrada.fecha_referencia,
        fecha_aplicacion_amlr=resultado.fecha_aplicacion_amlr,
        documentos=tuple(documentos),
    )


def _fechas_de(lecturas) -> set[date]:
    """Fechas en que puede cambiar el estado de alguna de las lecturas (§2.2, §3.2)."""
    fechas = set()
    for lectura in lecturas:
        fechas |= {f for f in (lectura.inicio, lectura.acceso_restringido_desde) if f}
        fechas |= {f + UN_DIA for f in (lectura.vencimiento, lectura.fin_prorroga, lectura.fin_conservacion_facultativa) if f}
    return fechas


def fechas_de_cambio(entrada: Entrada, doc, a: date) -> list[date]:
    """Todas las fechas en que puede cambiar el estado del documento en algún régimen (§9.2).

    Son las fechas de las lecturas (inicio, restricción y el día siguiente a
    cada fin) y las fijas de la transición: A, A + 5 años + 1 (T-3) y las del
    art. 77.4. Las lecturas de un régimen dependen de la fecha en que se
    evalúan (T-n cambia de la Ley al AMLR en A), así que se repite con las
    fechas nuevas hasta que no aparece ninguna.
    """
    fechas = {a, sumar_anios(a, PLAZO_AMLR) + UN_DIA, FECHA_77_4} | {f + UN_DIA for f in FIN_PA.values()}
    pendientes = {entrada.fecha_referencia} | fechas
    evaluadas = set()
    while pendientes:
        fecha = pendientes.pop()
        evaluadas.add(fecha)
        en_fecha = replace(entrada, fecha_referencia=fecha)
        for regimen in REGIMENES:
            nuevas = _fechas_de(calcular_regimen(en_fecha, doc, regimen).lecturas) - fechas
            fechas |= nuevas
            pendientes |= nuevas - evaluadas
    return sorted(fechas)


def linea_temporal(entrada: Entrada, doc, regimen: str, fechas: list[date]) -> tuple[Tramo, ...]:
    """Los tramos de estado del documento en un régimen, del pasado al futuro
    (D-25). Son los del estado del régimen, no los de cada lectura (D-26).

    `fechas` son las de `fechas_de_cambio`: entre dos seguidas el estado no cambia.
    """
    tramos: list[Tramo] = []

    def estado_en(fecha):
        return calcular_regimen(replace(entrada, fecha_referencia=fecha), doc, regimen).estado

    # Antes de la primera fecha de cambio, el estado no cambia.
    actual = Tramo(None, None, estado_en(fechas[0] - UN_DIA))
    for fecha in fechas:
        estado = estado_en(fecha)
        if estado != actual.estado:
            tramos.append(replace(actual, hasta=fecha - UN_DIA))
            actual = Tramo(fecha, None, estado)
    tramos.append(actual)
    return tuple(tramos)


def periodos_distintos(lineas: dict[str, tuple[Tramo, ...]]) -> tuple[PeriodoDistinto, ...]:
    """Los periodos en que los seis regímenes no dan el mismo estado."""
    cortes = sorted({t.desde for tramos in lineas.values() for t in tramos if t.desde is not None})
    inicios = [None, *cortes]
    periodos: list[PeriodoDistinto] = []
    for i, desde in enumerate(inicios):
        hasta = inicios[i + 1] - UN_DIA if i + 1 < len(inicios) else None
        muestra = desde if desde is not None else (cortes[0] - UN_DIA if cortes else date(2000, 1, 1))
        estados = {r: next(t.estado for t in tramos if t.contiene(muestra)) for r, tramos in lineas.items()}
        if len(set(estados.values())) == 1:
            continue
        if periodos and periodos[-1].estados == estados and _consecutivos(periodos[-1].hasta, desde):
            periodos[-1] = replace(periodos[-1], hasta=hasta)
        else:
            periodos.append(PeriodoDistinto(desde, hasta, estados))
    return tuple(periodos)


def _consecutivos(hasta, desde):
    return hasta is not None and desde is not None and hasta + UN_DIA == desde


# --- JSON --------------------------------------------------------------------


def _fecha(valor):
    return valor.isoformat() if valor else None


def _lectura_dict(lectura: Lectura):
    return {
        "id": lectura.id,
        "norma": lectura.norma,
        "estado": lectura.estado,
        "cita": lectura.cita,
        "inicio": _fecha(lectura.inicio),
        "vencimiento": _fecha(lectura.vencimiento),
        "acceso_restringido_desde": _fecha(lectura.acceso_restringido_desde),
        "fin_prorroga": _fecha(lectura.fin_prorroga),
        "fin_conservacion_facultativa": _fecha(lectura.fin_conservacion_facultativa),
    }


def _tramo_dict(tramo: Tramo):
    return {"desde": _fecha(tramo.desde), "hasta": _fecha(tramo.hasta), "estado": tramo.estado}


def como_dict(inf: Informe) -> dict:
    return {
        "advertencia": ADVERTENCIA,
        "valida": inf.valida,
        "errores": [{"codigo": e.codigo, "mensaje": e.mensaje, "ruta": e.ruta} for e in inf.errores],
        "expediente": inf.expediente_id,
        "fecha_referencia": _fecha(inf.fecha_referencia),
        "fecha_aplicacion_amlr": _fecha(inf.fecha_aplicacion_amlr),
        "nota_linea_temporal": NOTA_LINEA_TEMPORAL if inf.valida else None,
        "exige_actuar": {
            "valor": inf.exige_actuar,
            "activado_por": [
                {"documento": d.id, **_activador_dict(a)} for d in inf.documentos for a in d.activadores
            ],
        }
        if inf.valida
        else None,
        "documentos": [
            {
                "id": d.id,
                "categoria": d.resultado.categoria,
                "exige_actuar": {
                    "valor": d.exige_actuar,
                    "activado_por": [_activador_dict(a) for a in d.activadores],
                },
                "comparacion": {
                    "estados_distintos": d.estados_distintos,
                    "ley_y_amlr_difieren": d.ley_y_amlr_difieren,
                    "transicion_coincide": d.resultado.transicion_coincide,
                    "grupos": [{"estado": e, "regimenes": list(rs)} for e, rs in d.grupos.items()],
                    "periodos_distintos": [
                        {
                            "desde": _fecha(p.desde),
                            "hasta": _fecha(p.hasta),
                            "ley_y_amlr_difieren": p.ley_y_amlr_difieren,
                            "transicion_difiere": p.transicion_difiere,
                            "estados": p.estados,
                        }
                        for p in d.periodos_distintos
                    ],
                },
                "regimenes": {
                    r: {
                        "estado": res.estado,
                        "lecturas": [_lectura_dict(l) for l in res.lecturas],
                        "avisos": [{"codigo": a.codigo, "mensaje": a.mensaje} for a in res.avisos],
                        "linea_temporal": [_tramo_dict(t) for t in d.lineas[r]],
                    }
                    for r, res in d.resultado.regimenes.items()
                },
            }
            for d in inf.documentos
        ],
    }


def como_json(inf: Informe) -> str:
    return json.dumps(como_dict(inf), ensure_ascii=False, indent=2)


# --- Texto -------------------------------------------------------------------

ANCHO_REGIMEN = max(len(r) for r in REGIMENES)


def _periodo(desde, hasta) -> str:
    if desde is None and hasta is None:
        return "siempre"
    if desde is None:
        return f"hasta el {hasta}"
    if hasta is None:
        return f"desde el {desde}"
    return f"del {desde} al {hasta}"


def _activador_dict(a: Activador) -> dict:
    return {"regimen": a.regimen, "lectura": a.lectura, "estado": a.estado}


def _exige_actuar_texto(doc: InformeDocumento) -> list[str]:
    """D-28: qué régimen y qué lectura exigen actuar, para que el código 1 se explique en el informe."""
    if not doc.exige_actuar:
        return ["  No: ninguna lectura de ningún régimen exige actuar (D-28)."]
    lineas = ["  Sí (D-28). Lo exigen:"]
    por_regimen: dict[str, list[str]] = {}
    for a in doc.activadores:
        por_regimen.setdefault(a.regimen, []).append(f"{a.lectura}: {a.estado}" if a.lectura else a.estado)
    for regimen, lecturas in por_regimen.items():
        estado = doc.estados[regimen]
        nota = "" if estado in ESTADOS_QUE_EXIGEN_ACTUAR else f" (estado del régimen: {estado})"
        lineas.append(f"    {regimen:<{ANCHO_REGIMEN}}  {'; '.join(lecturas)}{nota}")
    return lineas


def _lectura_texto(lectura: Lectura) -> str:
    fechas = [
        ("inicio", lectura.inicio),
        ("restringido desde", lectura.acceso_restringido_desde),
        ("vence", lectura.vencimiento),
        ("prórroga hasta", lectura.fin_prorroga),
        ("facultativa hasta", lectura.fin_conservacion_facultativa),
    ]
    detalle = " · ".join(f"{nombre} {valor}" for nombre, valor in fechas if valor)
    return f"{lectura.id}: {lectura.estado}" + (f" ({detalle})" if detalle else "") + f" — {lectura.cita}"


def _linea_texto(tramos, referencia) -> str:
    """«plazo_no_iniciado → 2020-03-15 en_conservacion → …», con ◀ en el tramo de la referencia."""
    partes = []
    for tramo in tramos:
        marca = " ◀" if tramo.contiene(referencia) else ""
        partes.append((f"{tramo.desde} " if tramo.desde else "") + tramo.estado + marca)
    return " → ".join(partes)


def _estados_texto(estados: dict[str, str]) -> str:
    grupos: dict[str, list[str]] = {}
    for regimen, estado in estados.items():
        grupos.setdefault(estado, []).append(regimen)
    return "; ".join(f"{', '.join(rs)}: {estado}" for estado, rs in grupos.items())


def texto(inf: Informe) -> str:
    lineas: list[str] = []
    if not inf.valida:
        lineas.append(f"La entrada no es válida ({len(inf.errores)} errores):")
        for e in inf.errores:
            lineas.append(f"  {e.codigo}  {e.ruta or '(raíz)'}: {e.mensaje}")
        return "\n".join(lineas) + "\n"

    lineas += [
        f"Expediente {inf.expediente_id}",
        f"Fecha de referencia: {inf.fecha_referencia} · AMLR aplicable desde el {inf.fecha_aplicacion_amlr}",
        "",
        ADVERTENCIA,
    ]
    if not inf.documentos:
        lineas += ["", "El expediente no tiene documentos."]

    for doc in inf.documentos:
        ref = inf.fecha_referencia
        lineas += ["", f"== Documento {doc.id} ({doc.resultado.categoria})", ""]

        lineas.append(f"Estado el {ref}:")
        for regimen, estado in doc.estados.items():
            lineas.append(f"  {regimen:<{ANCHO_REGIMEN}}  {estado}")

        lineas += ["", "Dónde difieren:"]
        if not doc.estados_distintos:
            lineas.append(f"  Los seis regímenes coinciden el {ref}.")
        else:
            if doc.ley_y_amlr_difieren:
                lineas.append(f"  La Ley y el AMLR dan estados distintos el {ref}.")
            if not doc.resultado.transicion_coincide:
                lineas.append(
                    "  T-1 a T-4 no coinciden: el estado depende de cómo se resuelva la transición (S-1, D-21)."
                )
            lineas.append(f"  {_estados_texto(doc.estados)}")
        if doc.hay_indeterminado:
            lineas.append("  «indeterminado»: las lecturas de ese régimen dan estados distintos (D-6).")
        if doc.periodos_distintos:
            lineas.append("  Periodos con estados distintos:")
            for p in doc.periodos_distintos:
                # Antes de A, `amlr` es solo comparativo: el AMLR no es aplicable (D-20).
                antes = " (AMLR aún no aplicable)" if p.hasta is not None and p.hasta < inf.fecha_aplicacion_amlr else ""
                lineas.append(f"    {_periodo(p.desde, p.hasta)}{antes}: {_estados_texto(p.estados)}")
        else:
            lineas.append("  Los seis regímenes coinciden en toda la línea temporal.")

        lineas += ["", f"Exige actuar el {ref}:"]
        lineas += _exige_actuar_texto(doc)

        lineas += ["", "Línea temporal (◀ fecha de referencia):"]
        for regimen in REGIMENES:
            lineas.append(f"  {regimen:<{ANCHO_REGIMEN}}  {_linea_texto(doc.lineas[regimen], ref)}")

        lineas += ["", "Lecturas:"]
        mostradas: dict[tuple, str] = {}
        for regimen, res in doc.resultado.regimenes.items():
            # Para no repetir: T-n antes de A son la Ley, y T-2 desde A es el AMLR.
            clave = res.lecturas
            if clave in mostradas:
                lineas.append(f"  {regimen}: las mismas que {mostradas[clave]}")
                continue
            mostradas[clave] = regimen
            if not res.lecturas:
                lineas.append(f"  {regimen}: sin lecturas")
                continue
            lineas.append(f"  {regimen}:")
            lineas += [f"    {_lectura_texto(l)}" for l in res.lecturas]

        avisos = [(r, a) for r, res in doc.resultado.regimenes.items() for a in res.avisos]
        if avisos:
            lineas += ["", "Avisos:"]
            vistos: dict = {}
            for regimen, aviso in avisos:
                vistos.setdefault(aviso, []).append(regimen)
            for aviso, regimenes in vistos.items():
                lineas.append(f"  {aviso.codigo} ({', '.join(regimenes)}): {aviso.mensaje}")

    lineas += ["", NOTA_LINEA_TEMPORAL]
    return "\n".join(lineas) + "\n"
