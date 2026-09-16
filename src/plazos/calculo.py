"""Cálculo del estado de conservación, según docs/especificacion-calculo.md.

`calcular(entrada)` devuelve, para cada documento, su estado en
`fecha_referencia` en los seis regímenes (D-14): `ley_10_2010`, `amlr` y las
cuatro lecturas de la transición `T-1` a `T-4`. Ninguno es el principal.

La entrada tiene que estar validada (`plazos.carga`). Todas las fechas son
`date`.

Las decisiones de la especificación se citan como «D-n». Los puntos que la
especificación no basta para implementar están marcados con «AMBIGÜEDAD:».
"""

from dataclasses import dataclass, field
from datetime import date, timedelta

from plazos.modelo import (
    COMUNICACION_CONTROL_INTERNO,
    COMUNICACION_POR_INDICIO,
    DILIGENCIA_DEBIDA,
    EXAMEN_ESPECIAL,
    NEGATIVA,
    OPERACION_OCASIONAL,
    OPERACIONES,
    RELACION_DE_NEGOCIOS,
    SUBTIPOS_CON_VIGENCIA,
    Documento,
    Entrada,
    Expediente,
    HechoInicial,
)

# --- Regímenes y estados -----------------------------------------------------

LEY = "ley_10_2010"
AMLR = "amlr"
T1, T2, T3, T4 = "T-1", "T-2", "T-3", "T-4"
TRANSICION = (T1, T2, T3, T4)
REGIMENES = (LEY, AMLR, *TRANSICION)

PLAZO_NO_INICIADO = "plazo_no_iniciado"
EN_CONSERVACION = "en_conservacion"
ACCESO_RESTRINGIDO = "acceso_restringido"
ELIMINACION_EXIGIDA = "eliminacion_exigida"
CONSERVACION_PRORROGADA = "conservacion_prorrogada"
CONSERVACION_FACULTATIVA_77_4 = "conservacion_facultativa_77_4"
SUPRESION_EXIGIDA = "supresion_exigida"
SIN_REGLA = "sin_regla"
INDETERMINADO = "indeterminado"

# Estados en que el documento se sigue conservando.
CONSERVA = (
    PLAZO_NO_INICIADO,
    EN_CONSERVACION,
    ACCESO_RESTRINGIDO,
    CONSERVACION_PRORROGADA,
    CONSERVACION_FACULTATIVA_77_4,
)

# Norma de la que sale cada lectura.
NORMA_LEY = "ley"
NORMA_AMLR = "amlr"
NORMA_NINGUNA = "ninguna"

PLAZO_LEY = 10
PLAZO_AMLR = 5
PRORROGA_MAXIMA = 5  # AMLR 77.3, párrafo segundo
RESTRICCION_LEY = 5  # Ley 25.1, primer párrafo

APLICACION_AMLR = date(2027, 7, 10)  # AMLR 90
APLICACION_AMLR_FUTBOL = date(2029, 7, 10)  # AMLR 90, art. 3.3.n y o
FECHA_77_4 = date(2027, 7, 10)
FIN_PA = {"PA-1": date(2032, 7, 10), "PA-2": date(2037, 7, 10)}  # D-13


# --- Resultado ---------------------------------------------------------------


@dataclass(frozen=True)
class Aviso:
    """Incidencia que no impide el cálculo (§1.4). `codigo` es la decisión que
    la origina (p. ej. «D-12»)."""

    codigo: str
    mensaje: str


@dataclass(frozen=True)
class Lectura:
    """Una lectura de la categoría en un régimen (§1.4)."""

    id: str
    norma: str
    estado: str
    cita: str
    inicio: date | None = None
    vencimiento: date | None = None
    acceso_restringido_desde: date | None = None
    fin_prorroga: date | None = None
    fin_conservacion_facultativa: date | None = None


@dataclass(frozen=True)
class ResultadoRegimen:
    regimen: str
    estado: str
    lecturas: tuple[Lectura, ...]
    avisos: tuple[Aviso, ...] = ()


@dataclass(frozen=True)
class ResultadoDocumento:
    documento_id: str
    categoria: str
    regimenes: dict[str, ResultadoRegimen]

    @property
    def transicion_coincide(self) -> bool:
        """D-21: si T-1 a T-4 dan el mismo estado."""
        return len({self.regimenes[t].estado for t in TRANSICION}) == 1

    def estado(self, regimen: str) -> str:
        return self.regimenes[regimen].estado


@dataclass(frozen=True)
class Resultado:
    fecha_referencia: date
    fecha_aplicacion_amlr: date
    documentos: tuple[ResultadoDocumento, ...]

    def documento(self, id_: str) -> ResultadoDocumento:
        return next(d for d in self.documentos if d.documento_id == id_)


# --- Cómputo de fechas (§1.3) ------------------------------------------------


def sumar_anios(fecha: date, anios: int) -> date:
    """D-1: mismo día y mes, `anios` años después; 29 de febrero → 28."""
    try:
        return fecha.replace(year=fecha.year + anios)
    except ValueError:
        return fecha.replace(year=fecha.year + anios, day=28)


UN_DIA = timedelta(days=1)


def fecha_aplicacion_amlr(entrada: Entrada) -> date:
    """§4.1: A."""
    if entrada.sujeto.actividad in ("agente_de_futbol", "club_de_futbol_profesional"):
        return APLICACION_AMLR_FUTBOL
    return APLICACION_AMLR


def estado_agregado(lecturas) -> str:
    """D-6: el estado común de las lecturas, o `indeterminado` si difieren."""
    estados = {lectura.estado for lectura in lecturas}
    return estados.pop() if len(estados) == 1 else INDETERMINADO


# --- Punto de entrada --------------------------------------------------------


def calcular(entrada: Entrada) -> Resultado:
    """Los seis regímenes para cada documento (D-14)."""
    return Resultado(
        fecha_referencia=entrada.fecha_referencia,
        fecha_aplicacion_amlr=fecha_aplicacion_amlr(entrada),
        documentos=tuple(
            ResultadoDocumento(
                documento_id=doc.id,
                categoria=doc.categoria,
                regimenes={r: calcular_regimen(entrada, doc, r) for r in REGIMENES},
            )
            for doc in entrada.expediente.documentos
        ),
    )


def calcular_regimen(entrada: Entrada, documento: Documento, regimen: str) -> ResultadoRegimen:
    """El estado de un documento en un régimen (§1.1: el régimen es un parámetro)."""
    calculo = _Calculo(entrada)
    if regimen == LEY:
        return calculo.ley(documento)
    if regimen == AMLR:
        return calculo.amlr(documento)
    if regimen in TRANSICION:
        return calculo.transicion(documento, regimen)
    raise ValueError(f"Régimen desconocido: {regimen}")


# --- Cálculo -----------------------------------------------------------------


@dataclass(frozen=True)
class _Inicio:
    """Una lectura de la Ley antes de evaluarla: su id, su fecha de inicio F y su cita."""

    id: str
    fecha: date | None
    cita: str


@dataclass
class _Avisos:
    lista: list[Aviso] = field(default_factory=list)

    def anadir(self, codigo, mensaje):
        aviso = Aviso(codigo, mensaje)
        if aviso not in self.lista:
            self.lista.append(aviso)


class _Calculo:
    def __init__(self, entrada: Entrada):
        self.entrada = entrada
        self.ref = entrada.fecha_referencia
        self.expediente: Expediente = entrada.expediente
        self.hecho: HechoInicial = entrada.expediente.hecho_inicial
        self.a = fecha_aplicacion_amlr(entrada)

    # --- Ley 10/2010 y RD 304/2014 (§2) --------------------------------------

    def h_ley(self) -> date | None:
        """§2.1: H con la Ley. La negativa no da fecha (S-2)."""
        if self.hecho.tipo == RELACION_DE_NEGOCIOS:
            return self.hecho.fecha_terminacion
        if self.hecho.tipo == OPERACION_OCASIONAL:
            return self.hecho.fecha_ejecucion
        return None

    def r_ley(self) -> date | None:
        """§2.2: R = H + 5 años + 1 día (D-4). No existe sin terminación o
        ejecución de una operación ocasional (D-8, D-18)."""
        h = self.h_ley()
        return sumar_anios(h, RESTRICCION_LEY) + UN_DIA if h else None

    def inicios_ley(self, doc: Documento) -> list[_Inicio]:
        """§2.1: las lecturas de la Ley para la categoría del documento."""
        h = self.h_ley()
        negativa = self.hecho.tipo == NEGATIVA
        # D-18: con negativa, las lecturas que usan H se sustituyen por NG-1 y NG-2.
        ng = [
            _Inicio("NG-1", self.hecho.fecha_negativa, "Ley 25.1 (D-18: desde la negativa)"),
            _Inicio("NG-2", doc.fecha_documento, "Ley 25.1 (D-18: desde el documento)"),
        ]

        if doc.categoria == DILIGENCIA_DEBIDA:
            # La especificación no da identificador a la lectura única; se usa «DD».
            return ng if negativa else [_Inicio("DD", h, "Ley 25.1.a; RD 28.1")]

        if doc.categoria == OPERACIONES:
            op1 = doc.fecha_ejecucion_operacion
            if op1 is None and self.hecho.tipo == OPERACION_OCASIONAL:
                # §2.1: en una operación ocasional OP-1 y OP-2 son la misma
                # operación (modelo, V-14), así que sin la fecha propia se usa H.
                op1 = h
            if negativa:
                # AMBIGÜEDAD: D-18 sustituye «las lecturas que usan H», pero OP-1
                # no usa H y con una negativa no suele haber operación. Si el
                # documento trae `fecha_ejecucion_operacion`, se mantiene OP-1;
                # OP-2 se sustituye por NG-1 y NG-2.
                return ([_Inicio("OP-1", op1, "Ley 25.1.b")] if op1 else []) + ng
            return [_Inicio("OP-1", op1, "Ley 25.1.b"), _Inicio("OP-2", h, "RD 29.1")]

        if doc.categoria == EXAMEN_ESPECIAL:
            cita = "RD 25.3 y 25.4"
            inicios = [
                _Inicio("EE-1", doc.fecha_apertura, cita),
                _Inicio("EE-2", doc.fecha_cierre, cita),
                _Inicio("EE-3", doc.fecha_decision_comunicacion, cita),
                # D-7: sin comunicación, la fecha de la decisión.
                _Inicio("EE-4", doc.fecha_comunicacion or doc.fecha_decision_comunicacion, cita + " (D-7)"),
            ]
            return inicios + (ng if negativa else [_Inicio("EE-5", h, "RD 25.4; analogía con Ley 25.1.a y b")])

        if doc.categoria == COMUNICACION_CONTROL_INTERNO:
            inicios = [_Inicio("CI-1", doc.fecha_documento, "RD 29.2")]
            if doc.subtipo in SUBTIPOS_CON_VIGENCIA:
                inicios.append(_Inicio("CI-2", doc.fecha_fin_vigencia, "RD 29.2"))
            # AMBIGÜEDAD: CI-3 aplica «Solo si el expediente tiene hecho
            # inicial». Se lee como `tipo` distinto de null; con una relación
            # viva, H es null y CI-3 da `plazo_no_iniciado`, como EE-5. La otra
            # lectura (exigir H conocida) haría que CI-3 apareciera al terminar
            # la relación. El ejemplo 6 se ha corregido en consecuencia. Con
            # `tipo = null` no puede haber documentos de esta categoría
            # (modelo, ERR-05).
            if self.hecho.tipo is not None:
                inicios += ng if negativa else [_Inicio("CI-3", h, "RD 29.2")]
            return inicios

        return [
            _Inicio("AF-1", doc.fecha_aplicacion, "RD 42.3.d"),
            _Inicio("AF-2", doc.fecha_fin_proyecto, "RD 42.3.d"),
        ]

    def lectura_ley(self, inicio: _Inicio) -> Lectura:
        """§2.2: estado de una lectura de la Ley en la fecha de referencia."""
        f = inicio.fecha
        if f is None:
            return Lectura(inicio.id, NORMA_LEY, PLAZO_NO_INICIADO, inicio.cita)
        v = sumar_anios(f, PLAZO_LEY)
        r = self.r_ley()
        # D-9: si el plazo empieza después de R, la restricción rige desde el inicio.
        restringido = max(r, f) if r is not None and r <= v else None
        if self.ref < f:
            estado = PLAZO_NO_INICIADO
        elif self.ref > v:
            estado = ELIMINACION_EXIGIDA
        elif restringido is not None and self.ref >= restringido:
            estado = ACCESO_RESTRINGIDO
        else:
            estado = EN_CONSERVACION
        return Lectura(inicio.id, NORMA_LEY, estado, inicio.cita, f, v, restringido)

    def ley(self, doc: Documento, regimen: str = LEY) -> ResultadoRegimen:
        lecturas = tuple(self.lectura_ley(i) for i in self.inicios_ley(doc))
        return ResultadoRegimen(regimen, estado_agregado(lecturas), lecturas)

    # --- AMLR (§3) -----------------------------------------------------------

    def h_amlr(self) -> date | None:
        """§3.1: H con el AMLR."""
        return {
            RELACION_DE_NEGOCIOS: self.hecho.fecha_terminacion,
            OPERACION_OCASIONAL: self.hecho.fecha_ejecucion,
            NEGATIVA: self.hecho.fecha_negativa,
        }.get(self.hecho.tipo)

    @staticmethod
    def tiene_regla_amlr(doc: Documento) -> bool:
        """§3.1 y §7."""
        if doc.categoria in (DILIGENCIA_DEBIDA, OPERACIONES, EXAMEN_ESPECIAL):
            return True
        # D-19
        return doc.categoria == COMUNICACION_CONTROL_INTERNO and doc.subtipo == COMUNICACION_POR_INDICIO

    @staticmethod
    def cita_amlr(doc: Documento) -> str:
        letra = {DILIGENCIA_DEBIDA: "a", OPERACIONES: "c"}.get(doc.categoria, "b")
        cita = f"AMLR 77.1.{letra} y 77.3"
        return cita + " (D-19)" if doc.categoria == COMUNICACION_CONTROL_INTERNO else cita

    def prorroga(self, v: date, avisos: _Avisos) -> date | None:
        """D-11 y D-12: fin de la prórroga de la autoridad, o None."""
        limite = sumar_anios(v, PRORROGA_MAXIMA)
        fines = []
        for p in self.expediente.prorrogas_autoridad:
            if p.fecha_requerimiento > v:
                avisos.anadir(
                    "D-11",
                    f"La prórroga requerida por {p.autoridad} el {p.fecha_requerimiento} no se aplica: "
                    f"el plazo venció el {v}",
                )
            else:
                fines.append(p.fecha_fin)
        if not fines:
            return None
        fin = max(fines)
        if fin > limite:
            avisos.anadir("D-12", f"La prórroga hasta el {fin} se recorta al {limite} (vencimiento + 5 años)")
            fin = limite
        # Una prórroga que no pasa del vencimiento no alarga nada.
        return fin if fin > v else None

    def tramo_final_amlr(self, id_, cita, inicio, v, avisos: _Avisos, estado_previo=None) -> list[Lectura]:
        """Estado desde el vencimiento V: prórroga (D-11, D-12) y art. 77.4 (D-13).

        `estado_previo` es el estado si la fecha de referencia no ha llegado a
        V + 1; si es None, se calcula con H = `inicio`.
        """
        p = self.prorroga(v, avisos)
        if estado_previo is not None:
            base = estado_previo
        elif self.ref < inicio:
            base = PLAZO_NO_INICIADO
        elif self.ref <= v:
            base = EN_CONSERVACION
        elif p is not None and self.ref <= p:
            base = CONSERVACION_PRORROGADA
        else:
            base = SUPRESION_EXIGIDA

        if not self.expediente.procedimiento_judicial_pendiente_2027_07_10:
            return [Lectura(id_ or "77.3", NORMA_AMLR, base, cita, inicio, v, fin_prorroga=p)]

        lecturas = []
        for pa, fin in FIN_PA.items():
            estado = base
            # D-13. AMBIGÜEDAD: la especificación no dice qué pasa antes del
            # 2027-07-10. La conservación facultativa empieza ese día (§3.2,
            # columna «Desde»), así que antes se mantiene `supresion_exigida`.
            # También se usa el 2027-07-10 aunque A sea 2029-07-10 (fútbol):
            # el art. 77.4 fija esa fecha.
            if base == SUPRESION_EXIGIDA and FECHA_77_4 <= self.ref <= fin:
                estado = CONSERVACION_FACULTATIVA_77_4
            lecturas.append(
                Lectura(
                    f"{id_}/{pa}" if id_ else pa,
                    NORMA_AMLR,
                    estado,
                    cita + "; 77.4",
                    inicio,
                    v,
                    fin_prorroga=p,
                    fin_conservacion_facultativa=fin,
                )
            )
        return lecturas

    def lecturas_77_3(self, doc: Documento, id_: str, cita: str, avisos: _Avisos) -> list[Lectura]:
        """§3.2: el plazo de 5 años desde H, con prórroga y art. 77.4."""
        h = self.h_amlr()
        if h is None:
            return [Lectura(id_ or "77.3", NORMA_AMLR, PLAZO_NO_INICIADO, cita)]
        return self.tramo_final_amlr(id_, cita, h, sumar_anios(h, PLAZO_AMLR), avisos)

    def amlr(self, doc: Documento, regimen: str = AMLR) -> ResultadoRegimen:
        avisos = _Avisos()
        if self.ref < self.a:
            avisos.anadir("D-20", f"El AMLR no es aplicable el {self.ref}: lo es desde el {self.a}")

        if self.tiene_regla_amlr(doc):
            if self.hecho.tipo is None:
                # §3.1: sin hecho inicial, `indeterminado` sin lecturas. Con el
                # modelo solo lo alcanzaría `aplicacion_fondos` (ERR-05), que
                # no tiene regla, así que no se da en entradas válidas.
                return ResultadoRegimen(regimen, INDETERMINADO, (), tuple(avisos.lista))
            lecturas = tuple(self.lecturas_77_3(doc, "", self.cita_amlr(doc), avisos))
            estado = estado_agregado(lecturas)
        else:
            lecturas = tuple(self.lecturas_sin_regla(doc, avisos))
            # D-17: el estado es `sin_regla` aunque SR-2 o SR-3 den otro. Es
            # una excepción expresa a D-6, que daría `indeterminado`.
            estado = SIN_REGLA

        self.aviso_supresion(lecturas, avisos)
        return ResultadoRegimen(regimen, estado, lecturas, tuple(avisos.lista))

    def lecturas_sin_regla(self, doc: Documento, avisos: _Avisos) -> list[Lectura]:
        """§7.3: SR-1, SR-2 y SR-3."""
        lecturas = [Lectura("SR-1", NORMA_NINGUNA, SIN_REGLA, "AMLR 77.1 (D-17)")]
        # AMBIGÜEDAD: SR-2 es «el cálculo del §2 con sus lecturas CI-n o AF-n»,
        # pero cada lectura tiene un solo estado. Se devuelve una lectura por
        # cada lectura de la Ley, con id «SR-2/CI-1», etc.
        for lectura in (self.lectura_ley(i) for i in self.inicios_ley(doc)):
            lecturas.append(_con_id(lectura, f"SR-2/{lectura.id}", cita=f"{lectura.cita} como Derecho nacional"))
        # AMBIGÜEDAD: SR-3 aplica «por extensión el art. 77.3», y se lee que
        # incluye su segundo párrafo (prórroga) y el art. 77.4. «Solo se
        # calcula si el expediente tiene hecho inicial»: se lee `tipo` distinto
        # de null, como CI-3; con H null da `plazo_no_iniciado`.
        if self.hecho.tipo is not None:
            lecturas += self.lecturas_77_3(doc, "SR-3", "AMLR 77.3 por extensión", avisos)
        return lecturas

    @staticmethod
    def aviso_supresion(lecturas, avisos: _Avisos):
        if any(lectura.estado == SUPRESION_EXIGIDA for lectura in lecturas):
            avisos.anadir(
                "D-10",
                "La supresión del AMLR 77.3 se refiere a los datos personales; "
                "el AMLR no dice qué hacer con el resto de la información",
            )

    # --- Transición (§4) -----------------------------------------------------

    def transicion(self, doc: Documento, regimen: str) -> ResultadoRegimen:
        # §4.3: antes de A, los cuatro dan el resultado de la Ley.
        if self.ref < self.a:
            return self.ley(doc, regimen)
        # §4.2: T-2 aplica desde A el AMLR con V = H + 5 años a todo lo
        # conservado, y a lo posterior a A también; en la fecha de referencia,
        # que es ≥ A, coincide con el régimen `amlr`.
        if regimen == T2:
            return self.amlr(doc, regimen)

        avisos = _Avisos()
        con_regla = self.tiene_regla_amlr(doc)
        lecturas = []
        for inicio in self.inicios_ley(doc):
            iniciado_con_ley = inicio.fecha is not None and inicio.fecha < self.a
            if regimen == T1:
                if iniciado_con_ley:
                    lecturas.append(self.lectura_ley(inicio))
                else:
                    lecturas += self.sustituto_amlr(doc, inicio, con_regla, avisos)
            elif regimen == T3:
                if not con_regla:
                    # §4.2: sin regla en el AMLR, T-3 da `sin_regla` desde A.
                    lecturas.append(self.lectura_sin_regla(inicio))
                elif iniciado_con_ley:
                    lecturas += self.lecturas_t3(doc, inicio, avisos)
                else:
                    lecturas += self.sustituto_amlr(doc, inicio, con_regla, avisos)
            else:  # T4
                if iniciado_con_ley or not con_regla:
                    # §4.2: con F < A, la Ley; sin regla en el AMLR, «siguen la Ley».
                    lecturas.append(self.lectura_ley(inicio))
                else:
                    lecturas += self.lecturas_t4(doc, inicio, avisos)

        lecturas = tuple(lecturas)
        self.aviso_supresion(lecturas, avisos)
        return ResultadoRegimen(regimen, estado_agregado(lecturas), lecturas, tuple(avisos.lista))

    def lectura_sin_regla(self, inicio: _Inicio) -> Lectura:
        # AMBIGÜEDAD: §4.2 dice que las categorías sin regla «quedan en
        # `sin_regla`», sin lecturas SR-n. Se da una lectura `sin_regla` por
        # cada lectura de la Ley, con su mismo id.
        return Lectura(inicio.id, NORMA_NINGUNA, SIN_REGLA, "AMLR 77.1 (D-17)")

    def sustituto_amlr(self, doc, inicio: _Inicio, con_regla, avisos) -> list[Lectura]:
        """Una lectura de la Ley no iniciada antes de A se calcula con el AMLR.

        AMBIGÜEDAD: §4.2 compara «la fecha de inicio de cada lectura» con A,
        pero el AMLR no tiene lecturas por categoría. Cada lectura de la Ley
        con F ≥ A (o sin F) se sustituye por el cálculo del AMLR, con su id de
        la Ley («EE-5», o «EE-5/PA-1» si hay art. 77.4).
        """
        if not con_regla:
            return [self.lectura_sin_regla(inicio)]
        return self.lecturas_77_3(doc, inicio.id, self.cita_amlr(doc), avisos)

    def lecturas_t3(self, doc, inicio: _Inicio, avisos) -> list[Lectura]:
        """§4.2, T-3, F < A: vence el primero de F + 10 años y A + 5 años. Sin restricción."""
        f = inicio.fecha
        v_ley = sumar_anios(f, PLAZO_LEY)
        v_amlr = sumar_anios(self.a, PLAZO_AMLR)
        cita = f"{inicio.cita}; T-3: el primero de F + 10 años y A + 5 años"
        if v_ley <= v_amlr:
            # AMBIGÜEDAD: la especificación no dice cómo se llama el estado
            # después del vencimiento de T-3. Si vence por la Ley, se usa
            # `eliminacion_exigida` (como en el ejemplo 4, OP-1), y la Ley no
            # tiene prórroga ni art. 77.4.
            estado = EN_CONSERVACION if self.ref <= v_ley else ELIMINACION_EXIGIDA
            return [Lectura(inicio.id, NORMA_LEY, estado, cita, f, v_ley)]
        # AMBIGÜEDAD: si vence por A + 5 años, rige el AMLR: después, prórroga
        # (con V = A + 5 años), art. 77.4 y `supresion_exigida`.
        previo = EN_CONSERVACION if self.ref <= v_amlr else None
        return self.tramo_final_amlr(inicio.id, cita, f, v_amlr, avisos, estado_previo=previo)

    def lecturas_t4(self, doc, inicio: _Inicio, avisos) -> list[Lectura]:
        """§4.2, T-4, F ≥ A o sin F: el mayor de los plazos de la Ley y del AMLR.

        AMBIGÜEDAD: la especificación no dice qué estado se da al combinar
        los dos plazos. Mientras la Ley conserve el documento, su estado (con
        la restricción, que «se mantiene»). Cuando la Ley exija eliminarlo, el
        del AMLR si todavía lo conserva (prórroga, art. 77.4). Si los dos han
        vencido, el de la norma cuyo plazo acaba más tarde.
        """
        ley = self.lectura_ley(inicio)
        if ley.estado != ELIMINACION_EXIGIDA:
            return [ley]
        resultado = []
        for amlr in self.lecturas_77_3(doc, inicio.id, self.cita_amlr(doc), avisos):
            if amlr.estado in CONSERVA:
                resultado.append(amlr)
                continue
            fin_amlr = max(d for d in (amlr.vencimiento, amlr.fin_prorroga, amlr.fin_conservacion_facultativa) if d)
            resultado.append(ley if ley.vencimiento >= fin_amlr else amlr)
        return list(dict.fromkeys(resultado))


def _con_id(lectura: Lectura, id_: str, cita: str) -> Lectura:
    return Lectura(
        id_,
        lectura.norma,
        lectura.estado,
        cita,
        lectura.inicio,
        lectura.vencimiento,
        lectura.acceso_restringido_desde,
        lectura.fin_prorroga,
        lectura.fin_conservacion_facultativa,
    )
