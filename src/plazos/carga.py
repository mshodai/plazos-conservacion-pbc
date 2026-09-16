"""Lectura y validación de la entrada, según docs/modelo-datos.md (versión 2).

`cargar` lee el JSON y devuelve un ResultadoCarga con la entrada validada (o
None si hay errores) y los errores del §8 del modelo. No calcula nada, y la
validación no depende del régimen (modelo, §0, principio 3).

Se recogen todos los errores de una pasada, no solo el primero. Un dato mal
formado se anota como ERR-01 y las comprobaciones que dependen de él se
omiten, para no dar errores derivados de otro.

Los puntos que el modelo deja sin decidir para la implementación están
marcados con «AMBIGÜEDAD:».
"""

import json
import re
from datetime import date
from pathlib import Path

from plazos.modelo import (
    ACTIVIDADES,
    APLICACION_FONDOS,
    CATEGORIAS,
    COMUNICACION_CONTROL_INTERNO,
    COMUNICACION_POR_INDICIO,
    DILIGENCIA_DEBIDA,
    EXAMEN_ESPECIAL,
    NATURALEZAS,
    NEGATIVA,
    OBJETOS_NEGATIVA,
    OPERACION_OCASIONAL,
    OPERACIONES,
    RELACION_DE_NEGOCIOS,
    SUBTIPOS,
    SUBTIPOS_CON_VIGENCIA,
    TIPOS_HECHO,
    VERSION_MODELO,
    DocumentoAplicacionFondos,
    DocumentoComunicacionControlInterno,
    DocumentoDiligenciaDebida,
    DocumentoExamenEspecial,
    DocumentoOperacion,
    Entrada,
    Expediente,
    HechoInicial,
    Incidencia,
    ProrrogaAutoridad,
    ResultadoCarga,
    Sujeto,
)

_FECHA = re.compile(r"\d{4}-\d{2}-\d{2}")


class _Invalido:
    """Marca un campo presente pero mal formado (ya anotado como ERR-01).

    Se distingue de None, que es un null válido o un campo opcional ausente.
    """

    def __repr__(self):
        return "INVALIDO"


INVALIDO = _Invalido()


def cargar(texto: str) -> ResultadoCarga:
    """Lee y valida una entrada en JSON."""
    return _Carga().ejecutar(texto)


def cargar_fichero(ruta) -> ResultadoCarga:
    return cargar(Path(ruta).read_text(encoding="utf-8"))


# --- Lectura del JSON --------------------------------------------------------


def _leer_json(texto):
    """Devuelve (datos, claves repetidas). Rechaza NaN e Infinity."""
    repetidas = []

    def objeto(pares):
        resultado = {}
        for clave, valor in pares:
            if clave in resultado:
                repetidas.append(clave)
            resultado[clave] = valor
        return resultado

    def constante(nombre):
        raise ValueError(f"{nombre} no es un número JSON válido")

    datos = json.loads(texto, parse_constant=constante, object_pairs_hook=objeto)
    return datos, repetidas


def _ruta(base, clave):
    return f"{base}.{clave}" if base else clave


def _validos(*valores):
    return all(v is not INVALIDO for v in valores)


def _presente(valor):
    """Tiene un valor válido. Un valor mal formado ya es ERR-01 y no se cuenta."""
    return valor is not None and valor is not INVALIDO


# --- Validación --------------------------------------------------------------


class _Carga:
    def __init__(self):
        self.errores: list[Incidencia] = []
        # Fechas de hechos para ERR-09: (ruta, fecha).
        self.hechos: list[tuple[str, date]] = []

    def error(self, codigo, mensaje, ruta=""):
        self.errores.append(Incidencia(codigo, mensaje, ruta))

    def ejecutar(self, texto):
        try:
            datos, repetidas = _leer_json(texto)
        except ValueError as e:
            # AMBIGÜEDAD: el §8 no tiene código para un JSON mal formado. Se
            # usa ERR-01, el error de estructura.
            self.error("ERR-01", f"El JSON no es válido: {e}")
            return self._resultado(None)

        for clave in repetidas:
            # AMBIGÜEDAD: el modelo no trata las claves repetidas. El módulo
            # json se quedaría en silencio con la última; se rechazan como
            # ERR-01.
            self.error("ERR-01", f"La clave «{clave}» aparece repetida en un mismo objeto")

        if isinstance(datos, dict) and "regimen" in datos:
            # §2: «Un JSON con `regimen` es un error de validación».
            self.error(
                "ERR-01",
                "La entrada no lleva régimen: es un parámetro del cálculo (modelo, §0 y §2)",
                "regimen",
            )
        if not self._objeto(
            datos,
            "",
            ("version_modelo", "fecha_referencia", "sujeto", "expediente"),
            ignorar=("regimen",),
        ):
            return self._resultado(None)

        version = self._version(datos)
        fecha_referencia = self._fecha(datos, "fecha_referencia", "", hecho=False)
        sujeto = self._sujeto(datos)
        expediente = self._expediente(datos, sujeto)

        if isinstance(fecha_referencia, date):
            self._comprobar_hechos_posteriores(fecha_referencia)

        if self.errores:
            return self._resultado(None)
        return self._resultado(Entrada(version, fecha_referencia, sujeto, expediente))

    def _resultado(self, entrada):
        return ResultadoCarga(
            entrada=entrada,
            errores=tuple(sorted(self.errores, key=lambda i: i.codigo)),
        )

    # --- Campos (ERR-01) -----------------------------------------------------

    def _objeto(self, obj, ruta, obligatorios, opcionales=(), ignorar=()):
        """Comprueba que `obj` es un objeto con esos campos. Devuelve si lo es."""
        if not isinstance(obj, dict):
            self.error("ERR-01", "Debe ser un objeto", ruta)
            return False
        for clave in obligatorios:
            if clave not in obj:
                self.error("ERR-01", f"Falta el campo obligatorio «{clave}»", _ruta(ruta, clave))
        for clave in obj:
            if clave not in obligatorios and clave not in opcionales and clave not in ignorar:
                # AMBIGÜEDAD: el §8 solo nombra `regimen` como campo que
                # sobra. Se rechaza cualquier campo desconocido, por la misma
                # razón que `regimen`: un campo que el cálculo no lee, como
                # `prorroga_nacional_77_4` de la versión 1 o una errata, no
                # debe pasar como si sirviera de algo.
                self.error("ERR-01", f"Campo desconocido «{clave}»", _ruta(ruta, clave))
        return True

    def _campo(self, obj, clave, ruta, es_valido, descripcion, nulo):
        """obj[clave]: None si falta o es un null admitido; INVALIDO si está mal.

        La falta de un campo obligatorio ya la anota `_objeto`.
        """
        if clave not in obj:
            return None
        valor = obj[clave]
        if valor is None and nulo:
            return None
        if valor is None or not es_valido(valor):
            self.error("ERR-01", f"«{clave}» debe ser {descripcion}", _ruta(ruta, clave))
            return INVALIDO
        return valor

    def _texto(self, obj, clave, ruta, nulo=False):
        # AMBIGÜEDAD: el modelo no dice si un texto puede estar vacío. Se
        # admite: ningún campo de texto interviene en el cálculo salvo como
        # identificador, y un `id` vacío sigue pudiendo ser único.
        return self._campo(obj, clave, ruta, lambda v: isinstance(v, str), "un texto", nulo)

    def _booleano(self, obj, clave, ruta):
        return self._campo(obj, clave, ruta, lambda v: isinstance(v, bool), "true o false", False)

    def _enumerado(self, obj, clave, ruta, valores, nulo=False):
        descripcion = " o ".join(f"«{v}»" for v in valores) + (" o null" if nulo else "")
        return self._campo(
            obj, clave, ruta, lambda v: isinstance(v, str) and v in valores, descripcion, nulo
        )

    def _fecha(self, obj, clave, ruta, nulo=False, hecho=True):
        """Fecha como `date`. Si `hecho`, se guarda para ERR-09."""
        texto = self._campo(
            obj, clave, ruta, lambda v: isinstance(v, str), "una fecha AAAA-MM-DD", nulo
        )
        if texto is None or texto is INVALIDO:
            return texto
        try:
            # fromisoformat admite también otras formas (20240101, semanas);
            # el modelo pide AAAA-MM-DD (§2).
            if not _FECHA.fullmatch(texto):
                raise ValueError
            fecha = date.fromisoformat(texto)
        except ValueError:
            self.error("ERR-01", f"«{clave}» debe ser una fecha AAAA-MM-DD", _ruta(ruta, clave))
            return INVALIDO
        if hecho:
            self.hechos.append((_ruta(ruta, clave), fecha))
        return fecha

    def _version(self, datos):
        version = self._campo(
            datos,
            "version_modelo",
            "",
            lambda v: isinstance(v, int) and not isinstance(v, bool),
            "un entero",
            False,
        )
        if isinstance(version, int) and version != VERSION_MODELO:
            # AMBIGÜEDAD: el modelo fija la versión 2 pero no dice qué código
            # lleva otra. Se trata como un valor no válido (ERR-01).
            self.error("ERR-01", f"«version_modelo» debe ser {VERSION_MODELO}", "version_modelo")
            return INVALIDO
        return version

    # --- Sujeto (§2.1) -------------------------------------------------------

    def _sujeto(self, datos):
        obj = datos.get("sujeto")
        if not self._objeto(obj, "sujeto", ("naturaleza", "actividad")):
            return None
        naturaleza = self._enumerado(obj, "naturaleza", "sujeto", NATURALEZAS)
        actividad = self._enumerado(obj, "actividad", "sujeto", ACTIVIDADES)
        return Sujeto(naturaleza, actividad)

    # --- Expediente ----------------------------------------------------------

    def _expediente(self, datos, sujeto):
        obj = datos.get("expediente")
        ruta = "expediente"
        if not self._objeto(
            obj,
            ruta,
            (
                "id",
                "hecho_inicial",
                "documentos",
                "prorrogas_autoridad",
                "procedimiento_judicial_pendiente_2027_07_10",
            ),
        ):
            return None
        id_ = self._texto(obj, "id", ruta)
        hecho = self._hecho_inicial(obj)
        documentos = self._documentos(obj, hecho)
        prorrogas = self._prorrogas(obj)
        pendiente = self._booleano(obj, "procedimiento_judicial_pendiente_2027_07_10", ruta)

        validos = [d for d in documentos if d is not None]
        self._comprobar_tipo_nulo(hecho, validos)
        self._comprobar_fondos(sujeto, validos)
        return Expediente(id_, hecho, tuple(validos), tuple(prorrogas), pendiente)

    # --- Hecho inicial (§3) --------------------------------------------------

    CAMPOS_HECHO = (
        "tipo",
        "fecha_inicio",
        "fecha_terminacion",
        "fecha_ejecucion",
        "fecha_negativa",
        "objeto_negativa",
    )

    # Fecha que corresponde a cada tipo (§3: «Solo se rellena la fecha que
    # corresponde al `tipo`; las otras dos van a `null`»).
    FECHA_DEL_TIPO = {
        RELACION_DE_NEGOCIOS: "fecha_terminacion",
        OPERACION_OCASIONAL: "fecha_ejecucion",
        NEGATIVA: "fecha_negativa",
    }

    def _hecho_inicial(self, expediente):
        obj = expediente.get("hecho_inicial")
        ruta = "expediente.hecho_inicial"
        # AMBIGÜEDAD: la tabla del §3 no tiene columna «Obligatorio». Los seis
        # campos se piden siempre, con null cuando no aplican, como en el
        # ejemplo del §1: así un campo olvidado no se confunde con un null.
        if not self._objeto(obj, ruta, self.CAMPOS_HECHO):
            return None
        tipo = self._enumerado(obj, "tipo", ruta, TIPOS_HECHO, nulo=True)
        fechas = {
            clave: self._fecha(obj, clave, ruta, nulo=True)
            for clave in ("fecha_inicio", "fecha_terminacion", "fecha_ejecucion", "fecha_negativa")
        }
        objeto_negativa = self._enumerado(obj, "objeto_negativa", ruta, OBJETOS_NEGATIVA, nulo=True)

        if _validos(tipo) and all(c in obj for c in self.CAMPOS_HECHO):
            self._comprobar_hecho(tipo, fechas, objeto_negativa, ruta)

        inicio, terminacion = fechas["fecha_inicio"], fechas["fecha_terminacion"]
        if isinstance(inicio, date) and isinstance(terminacion, date) and inicio > terminacion:
            self.error(
                "ERR-04",
                f"«fecha_inicio» ({inicio}) es posterior a «fecha_terminacion» ({terminacion})",
                _ruta(ruta, "fecha_inicio"),
            )
        return HechoInicial(
            tipo,
            inicio,
            terminacion,
            fechas["fecha_ejecucion"],
            fechas["fecha_negativa"],
            objeto_negativa,
        )

    def _comprobar_hecho(self, tipo, fechas, objeto_negativa, ruta):
        """ERR-02 y ERR-03. Solo con `tipo` válido; un campo mal formado ya es ERR-01."""
        if tipo is None:
            # §4.5: «usa `hecho_inicial` con todos los campos a `null`».
            # AMBIGÜEDAD: el §8 no dice qué código lleva un campo rellenado con
            # `tipo = null`. Se usa ERR-02, que es el de las fechas que no
            # corresponden al tipo.
            rellenos = [c for c, v in {**fechas, "objeto_negativa": objeto_negativa}.items() if _presente(v)]
            for clave in rellenos:
                self.error("ERR-02", f"Con «tipo» null, «{clave}» debe ser null (§4.5)", _ruta(ruta, clave))
            return

        propia = self.FECHA_DEL_TIPO[tipo]
        # §3: `fecha_terminacion` es null «mientras la relación siga viva», así
        # que solo la operación ocasional y la negativa exigen su fecha.
        if tipo != RELACION_DE_NEGOCIOS and fechas[propia] is None:
            self.error("ERR-02", f"Con «tipo» «{tipo}», «{propia}» no puede ser null", _ruta(ruta, propia))
        for clave in self.FECHA_DEL_TIPO.values():
            if clave != propia and _presente(fechas[clave]):
                self.error("ERR-02", f"Con «tipo» «{tipo}», «{clave}» debe ser null", _ruta(ruta, clave))

        if tipo != RELACION_DE_NEGOCIOS and _presente(fechas["fecha_inicio"]):
            # AMBIGÜEDAD: el §3 define `fecha_inicio` como «Inicio de la
            # relación de negocios» pero no dice qué pasa con otro tipo. Se
            # rechaza como ERR-02: es una fecha de otro tipo de hecho.
            self.error(
                "ERR-02",
                f"Con «tipo» «{tipo}», «fecha_inicio» debe ser null: es el inicio de una relación de negocios",
                _ruta(ruta, "fecha_inicio"),
            )

        if tipo == NEGATIVA:
            if objeto_negativa is None:
                self.error("ERR-03", "Una negativa necesita «objeto_negativa»", _ruta(ruta, "objeto_negativa"))
        elif _presente(objeto_negativa):
            # AMBIGÜEDAD: el modelo no dice qué pasa con `objeto_negativa`
            # rellenado sin negativa. Se rechaza como ERR-02, un dato de otro
            # tipo de hecho.
            self.error(
                "ERR-02",
                f"Con «tipo» «{tipo}», «objeto_negativa» debe ser null",
                _ruta(ruta, "objeto_negativa"),
            )

    # --- Documentos (§4) -----------------------------------------------------

    COMUNES = ("id", "categoria", "fecha_documento")

    # Por categoría: (obligatorios, opcionales), además de los comunes.
    CAMPOS_CATEGORIA = {
        DILIGENCIA_DEBIDA: ((), ()),
        OPERACIONES: ((), ("fecha_ejecucion_operacion",)),
        EXAMEN_ESPECIAL: (
            ("fecha_apertura", "fecha_cierre", "fecha_decision_comunicacion", "fecha_comunicacion"),
            (),
        ),
        COMUNICACION_CONTROL_INTERNO: (("subtipo",), ("examen_especial_id", "fecha_fin_vigencia")),
        APLICACION_FONDOS: (("proyecto", "fecha_aplicacion", "fecha_fin_proyecto"), ()),
    }

    def _documentos(self, expediente, hecho):
        lista = self._campo(expediente, "documentos", "expediente", lambda v: isinstance(v, list), "una lista", False)
        if not isinstance(lista, list):
            return []
        # AMBIGÜEDAD: el modelo no dice si la lista puede estar vacía. Se
        # admite: un expediente sin documentos no tiene nada que calcular,
        # pero no es incoherente.
        documentos = [self._documento(dato, f"expediente.documentos[{i}]", hecho) for i, dato in enumerate(lista)]
        self._comprobar_ids(lista, documentos)
        return documentos

    def _documento(self, obj, ruta, hecho):
        if not isinstance(obj, dict):
            self.error("ERR-01", "Debe ser un objeto", ruta)
            return None
        categoria = self._enumerado(obj, "categoria", ruta, CATEGORIAS)
        if categoria is None or categoria is INVALIDO:
            # Sin categoría no se sabe qué campos lleva: solo se comprueban los comunes.
            self._objeto(obj, ruta, self.COMUNES, ignorar=tuple(obj))
            self._texto(obj, "id", ruta)
            self._fecha(obj, "fecha_documento", ruta)
            return None

        obligatorios, opcionales = self.CAMPOS_CATEGORIA[categoria]
        self._objeto(obj, ruta, self.COMUNES + obligatorios, ("descripcion",) + opcionales)
        comunes = {
            "id": self._texto(obj, "id", ruta),
            "fecha_documento": self._fecha(obj, "fecha_documento", ruta),
            # AMBIGÜEDAD: `descripcion` es «cadena, no obligatorio», sin
            # null. Se admite null como equivalente a omitirla: es texto
            # libre que el cálculo no usa.
            "descripcion": self._texto(obj, "descripcion", ruta, nulo=True),
        }

        if categoria == DILIGENCIA_DEBIDA:
            return DocumentoDiligenciaDebida(**comunes)
        if categoria == OPERACIONES:
            return self._operacion(obj, ruta, hecho, comunes)
        if categoria == EXAMEN_ESPECIAL:
            return DocumentoExamenEspecial(
                **comunes,
                fecha_apertura=self._fecha(obj, "fecha_apertura", ruta),
                fecha_cierre=self._fecha(obj, "fecha_cierre", ruta, nulo=True),
                fecha_decision_comunicacion=self._fecha(obj, "fecha_decision_comunicacion", ruta, nulo=True),
                fecha_comunicacion=self._fecha(obj, "fecha_comunicacion", ruta, nulo=True),
            )
        if categoria == COMUNICACION_CONTROL_INTERNO:
            return self._comunicacion(obj, ruta, comunes)
        return DocumentoAplicacionFondos(
            **comunes,
            proyecto=self._texto(obj, "proyecto", ruta),
            fecha_aplicacion=self._fecha(obj, "fecha_aplicacion", ruta),
            fecha_fin_proyecto=self._fecha(obj, "fecha_fin_proyecto", ruta, nulo=True),
        )

    def _operacion(self, obj, ruta, hecho, comunes):
        # AMBIGÜEDAD: el tipo de `fecha_ejecucion_operacion` es «fecha», sin
        # null, y solo es obligatoria dentro de una relación. Se admite null
        # como equivalente a omitirla, y dentro de una relación los dos casos
        # son ERR-08 («ausente»).
        fecha = self._fecha(obj, "fecha_ejecucion_operacion", ruta, nulo=True)
        if hecho is not None and hecho.tipo == RELACION_DE_NEGOCIOS and fecha is None:
            self.error(
                "ERR-08",
                "Una operación de una relación de negocios necesita «fecha_ejecucion_operacion»",
                _ruta(ruta, "fecha_ejecucion_operacion"),
            )
        # AMBIGÜEDAD: en una operación ocasional, el modelo no dice si
        # `fecha_ejecucion_operacion` debe coincidir con
        # `hecho_inicial.fecha_ejecucion`. No se comprueba.
        return DocumentoOperacion(**comunes, fecha_ejecucion_operacion=fecha)

    def _comunicacion(self, obj, ruta, comunes):
        subtipo = self._enumerado(obj, "subtipo", ruta, SUBTIPOS)
        if subtipo in SUBTIPOS_CON_VIGENCIA and "fecha_fin_vigencia" not in obj:
            self.error(
                "ERR-01",
                f"Falta el campo obligatorio «fecha_fin_vigencia» (obligatorio con «{subtipo}»)",
                _ruta(ruta, "fecha_fin_vigencia"),
            )
        # AMBIGÜEDAD: con otros subtipos `fecha_fin_vigencia` no es
        # obligatoria, pero el modelo no dice si puede tener valor. Se admite:
        # es un hecho que el cálculo simplemente no usa.
        fin_vigencia = self._fecha(obj, "fecha_fin_vigencia", ruta, nulo=True)
        referencia = self._texto(obj, "examen_especial_id", ruta, nulo=True)
        return DocumentoComunicacionControlInterno(
            **comunes,
            subtipo=subtipo,
            examen_especial_id=referencia,
            fecha_fin_vigencia=fin_vigencia,
        )

    def _comprobar_ids(self, lista, documentos):
        """ERR-07: ids repetidos y referencias `examen_especial_id`."""
        vistos = {}
        examenes = set()
        for i, (dato, doc) in enumerate(zip(lista, documentos)):
            if not isinstance(dato, dict) or not isinstance(dato.get("id"), str):
                continue
            id_ = dato["id"]
            if id_ in vistos:
                self.error(
                    "ERR-07",
                    f"El id de documento «{id_}» está repetido (también en documentos[{vistos[id_]}])",
                    f"expediente.documentos[{i}].id",
                )
            else:
                vistos[id_] = i
            if dato.get("categoria") == EXAMEN_ESPECIAL:
                examenes.add(id_)

        for i, (dato, doc) in enumerate(zip(lista, documentos)):
            if not isinstance(doc, DocumentoComunicacionControlInterno):
                continue
            referencia = doc.examen_especial_id
            if referencia is None or referencia is INVALIDO:
                continue
            ruta = f"expediente.documentos[{i}].examen_especial_id"
            if doc.subtipo in SUBTIPOS and doc.subtipo != COMUNICACION_POR_INDICIO:
                # AMBIGÜEDAD: §4.4 dice «Solo con `comunicacion_por_indicio`»,
                # pero el §8 no da código para usarlo con otro subtipo. Se usa
                # ERR-07, el error de `examen_especial_id`.
                self.error(
                    "ERR-07",
                    f"«examen_especial_id» solo se admite con «{COMUNICACION_POR_INDICIO}», no con «{doc.subtipo}»",
                    ruta,
                )
            elif referencia not in vistos:
                self.error("ERR-07", f"«examen_especial_id» apunta a «{referencia}», que no existe", ruta)
            elif referencia not in examenes:
                self.error(
                    "ERR-07",
                    f"«examen_especial_id» apunta a «{referencia}», que no es un «{EXAMEN_ESPECIAL}»",
                    ruta,
                )

    def _comprobar_tipo_nulo(self, hecho, documentos):
        """ERR-05."""
        if hecho is None or hecho.tipo is not None:
            return
        # AMBIGÜEDAD: con la lista vacía, «solo contenga documentos
        # `aplicacion_fondos`» se cumple. Se admite `tipo = null` sin
        # documentos.
        for doc in documentos:
            if doc.categoria != APLICACION_FONDOS:
                self.error(
                    "ERR-05",
                    f"«tipo» null solo se admite si todos los documentos son «{APLICACION_FONDOS}»; "
                    f"«{doc.id}» es «{doc.categoria}»",
                    "expediente.hecho_inicial.tipo",
                )

    def _comprobar_fondos(self, sujeto, documentos):
        """ERR-06."""
        if sujeto is None or sujeto.naturaleza != "sujeto_obligado":
            return
        for doc in documentos:
            if doc.categoria == APLICACION_FONDOS:
                self.error(
                    "ERR-06",
                    f"«{doc.id}» es «{APLICACION_FONDOS}», que solo admiten fundaciones y asociaciones",
                    "sujeto.naturaleza",
                )

    # --- Prórrogas (§6) ------------------------------------------------------

    def _prorrogas(self, expediente):
        lista = self._campo(
            expediente, "prorrogas_autoridad", "expediente", lambda v: isinstance(v, list), "una lista", False
        )
        if not isinstance(lista, list):
            return []
        prorrogas = []
        for i, obj in enumerate(lista):
            ruta = f"expediente.prorrogas_autoridad[{i}]"
            if not self._objeto(obj, ruta, ("autoridad", "fecha_requerimiento", "fecha_fin")):
                continue
            # AMBIGÜEDAD: el modelo no dice si `fecha_fin` puede ser anterior a
            # `fecha_requerimiento`. No se comprueba: el recorte y la validez de
            # la prórroga son del cálculo (especificación, D-11 y D-12).
            prorrogas.append(
                ProrrogaAutoridad(
                    self._texto(obj, "autoridad", ruta),
                    self._fecha(obj, "fecha_requerimiento", ruta),
                    # §5: `fecha_fin` es «el final previsto de la prórroga y no
                    # un hecho ocurrido», así que no cuenta para ERR-09.
                    self._fecha(obj, "fecha_fin", ruta, hecho=False),
                )
            )
        return prorrogas

    # --- Fecha de referencia (§5) --------------------------------------------

    def _comprobar_hechos_posteriores(self, fecha_referencia):
        """ERR-09: un error por cada fecha de un hecho posterior a la referencia."""
        for ruta, fecha in self.hechos:
            if fecha > fecha_referencia:
                self.error(
                    "ERR-09",
                    f"{fecha} es posterior a «fecha_referencia» ({fecha_referencia})",
                    ruta,
                )
