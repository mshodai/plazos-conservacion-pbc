"""Estructuras de datos de la entrada, según docs/modelo-datos.md (versión 2).

Describen la entrada ya validada y no contienen ninguna regla de cálculo. No
hay régimen: es un parámetro del cálculo (modelo, §0). Todas las fechas son
`date`; el texto AAAA-MM-DD solo existe en el JSON.
"""

from dataclasses import dataclass
from datetime import date

VERSION_MODELO = 2

# §2.1
NATURALEZAS = ("sujeto_obligado", "fundacion", "asociacion")
ACTIVIDADES = ("agente_de_futbol", "club_de_futbol_profesional", "otra")

# §3
RELACION_DE_NEGOCIOS = "relacion_de_negocios"
OPERACION_OCASIONAL = "operacion_ocasional"
NEGATIVA = "negativa"
TIPOS_HECHO = (RELACION_DE_NEGOCIOS, OPERACION_OCASIONAL, NEGATIVA)
OBJETOS_NEGATIVA = (RELACION_DE_NEGOCIOS, OPERACION_OCASIONAL)

# §4
DILIGENCIA_DEBIDA = "diligencia_debida"
OPERACIONES = "operaciones"
EXAMEN_ESPECIAL = "examen_especial"
COMUNICACION_CONTROL_INTERNO = "comunicacion_control_interno"
APLICACION_FONDOS = "aplicacion_fondos"
CATEGORIAS = (
    DILIGENCIA_DEBIDA,
    OPERACIONES,
    EXAMEN_ESPECIAL,
    COMUNICACION_CONTROL_INTERNO,
    APLICACION_FONDOS,
)

# §4.4
COMUNICACION_POR_INDICIO = "comunicacion_por_indicio"
SUBTIPOS_CON_VIGENCIA = ("politicas_procedimientos", "analisis_riesgo")
SUBTIPOS = (
    COMUNICACION_POR_INDICIO,
    "comunicacion_sistematica",
    *SUBTIPOS_CON_VIGENCIA,
    "organo_control_interno",
    "otro",
)

# Modelo, §8.1 (V-1).
ERRORES = {
    "ERR-01": "JSON mal formado o con claves repetidas, campo obligatorio ausente, valor de tipo no válido, "
    "`version_modelo` distinto de 2, o campo `regimen` u otro desconocido",
    "ERR-02": "`hecho_inicial` no tiene la fecha que corresponde a su `tipo`, o tiene rellenos campos de otro tipo de hecho",
    "ERR-03": "`tipo = \"negativa\"` sin `objeto_negativa`",
    "ERR-04": "`fecha_inicio` posterior a `fecha_terminacion`",
    "ERR-05": "`tipo = null` en un expediente con documentos que no son `aplicacion_fondos`",
    "ERR-06": "`aplicacion_fondos` con `sujeto.naturaleza = \"sujeto_obligado\"`",
    "ERR-07": "`id` de documento repetido, o `examen_especial_id` que no existe, no es un `examen_especial` "
    "o está en un subtipo que no es `comunicacion_por_indicio`",
    "ERR-08": "`fecha_ejecucion_operacion` ausente o null en una operación de una relación de negocios, "
    "o distinta de `hecho_inicial.fecha_ejecucion` en una operación ocasional",
    "ERR-09": "Un hecho posterior a `fecha_referencia`",
}


@dataclass(frozen=True)
class Sujeto:
    naturaleza: str
    actividad: str


@dataclass(frozen=True)
class HechoInicial:
    """§3. `tipo` es None solo en el caso del §4.5."""

    tipo: str | None
    fecha_inicio: date | None
    fecha_terminacion: date | None
    fecha_ejecucion: date | None
    fecha_negativa: date | None
    objeto_negativa: str | None


@dataclass(frozen=True, kw_only=True)
class Documento:
    """Campos comunes a todas las categorías (§4)."""

    id: str
    fecha_documento: date
    descripcion: str | None = None

    categoria = ""  # la fija cada subclase


@dataclass(frozen=True, kw_only=True)
class DocumentoDiligenciaDebida(Documento):
    categoria = DILIGENCIA_DEBIDA


@dataclass(frozen=True, kw_only=True)
class DocumentoOperacion(Documento):
    """§4.2. `fecha_ejecucion_operacion` solo es obligatoria dentro de una relación."""

    categoria = OPERACIONES
    fecha_ejecucion_operacion: date | None = None


@dataclass(frozen=True, kw_only=True)
class DocumentoExamenEspecial(Documento):
    """§4.3. Las cuatro fechas del RD 25.3."""

    categoria = EXAMEN_ESPECIAL
    fecha_apertura: date
    fecha_cierre: date | None
    fecha_decision_comunicacion: date | None
    fecha_comunicacion: date | None


@dataclass(frozen=True, kw_only=True)
class DocumentoComunicacionControlInterno(Documento):
    """§4.4."""

    categoria = COMUNICACION_CONTROL_INTERNO
    subtipo: str
    examen_especial_id: str | None = None
    fecha_fin_vigencia: date | None = None


@dataclass(frozen=True, kw_only=True)
class DocumentoAplicacionFondos(Documento):
    """§4.5."""

    categoria = APLICACION_FONDOS
    proyecto: str
    fecha_aplicacion: date
    fecha_fin_proyecto: date | None


@dataclass(frozen=True)
class ProrrogaAutoridad:
    """§6: AMLR, art. 77.3, párrafo segundo."""

    autoridad: str
    fecha_requerimiento: date
    fecha_fin: date


@dataclass(frozen=True)
class Expediente:
    id: str
    hecho_inicial: HechoInicial
    documentos: tuple[Documento, ...]
    prorrogas_autoridad: tuple[ProrrogaAutoridad, ...]
    procedimiento_judicial_pendiente_2027_07_10: bool


@dataclass(frozen=True)
class Entrada:
    version_modelo: int
    fecha_referencia: date
    sujeto: Sujeto
    expediente: Expediente


@dataclass(frozen=True)
class Incidencia:
    """Error de validación del §8. `ruta` señala el dato en el JSON, p. ej.
    `expediente.documentos[2].fecha_cierre`."""

    codigo: str
    mensaje: str
    ruta: str = ""


@dataclass(frozen=True)
class ResultadoCarga:
    """La entrada validada, o None si hay algún error.

    El modelo no define avisos, así que solo hay errores.
    """

    entrada: Entrada | None
    errores: tuple[Incidencia, ...]

    @property
    def valida(self) -> bool:
        return not self.errores
