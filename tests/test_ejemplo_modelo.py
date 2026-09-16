"""El ejemplo completo de docs/modelo-datos.md, §1, leído del propio documento.

Si el ejemplo cambia y deja de ser válido, o el modelo cambia y el ejemplo no,
estos tests fallan.
"""

import dataclasses
import re
from datetime import date
from pathlib import Path

from plazos.carga import cargar
from plazos.modelo import (
    DocumentoComunicacionControlInterno,
    DocumentoDiligenciaDebida,
    DocumentoExamenEspecial,
    DocumentoOperacion,
)

MODELO = Path(__file__).resolve().parent.parent / "docs" / "modelo-datos.md"


def _seccion(texto, titulo):
    """Texto desde el encabezado `titulo` hasta el siguiente de igual o mayor nivel."""
    nivel = titulo.split(" ")[0]
    inicio = texto.index(titulo)
    fin = re.search(rf"^#{{1,{len(nivel)}}} ", texto[inicio + len(titulo):], re.MULTILINE)
    return texto[inicio : inicio + len(titulo) + fin.start()] if fin else texto[inicio:]


TEXTO = MODELO.read_text(encoding="utf-8")
EJEMPLO = re.search(r"```json\n(.*?)\n```", _seccion(TEXTO, "## 1. Ejemplo completo"), re.DOTALL).group(1)
RESULTADO = cargar(EJEMPLO)


def test_el_ejemplo_es_valido():
    assert RESULTADO.errores == ()
    assert RESULTADO.valida


def test_estructura_leida():
    entrada = RESULTADO.entrada
    assert entrada.version_modelo == 2
    assert entrada.fecha_referencia == date(2031, 3, 1)
    assert (entrada.sujeto.naturaleza, entrada.sujeto.actividad) == ("sujeto_obligado", "otra")

    expediente = entrada.expediente
    assert expediente.id == "EXP-2019-0042"
    assert expediente.hecho_inicial.tipo == "relacion_de_negocios"
    assert expediente.hecho_inicial.fecha_terminacion == date(2024, 11, 30)
    assert expediente.prorrogas_autoridad == ()
    assert expediente.procedimiento_judicial_pendiente_2027_07_10 is False

    doc1, doc2, doc3, doc4 = expediente.documentos
    assert isinstance(doc1, DocumentoDiligenciaDebida)
    assert isinstance(doc2, DocumentoOperacion)
    assert doc2.fecha_ejecucion_operacion == date(2021, 2, 3)
    assert isinstance(doc3, DocumentoExamenEspecial)
    assert (doc3.fecha_cierre, doc3.fecha_comunicacion) == (date(2023, 7, 15), date(2023, 7, 17))
    assert isinstance(doc4, DocumentoComunicacionControlInterno)
    assert (doc4.subtipo, doc4.examen_especial_id) == ("comunicacion_por_indicio", "DOC-3")


def _campos_fecha(objeto, ruta="entrada"):
    """(ruta, valor) de todos los campos cuyo nombre empieza por «fecha»."""
    if dataclasses.is_dataclass(objeto):
        for campo in dataclasses.fields(objeto):
            valor = getattr(objeto, campo.name)
            if campo.name.startswith("fecha"):
                yield f"{ruta}.{campo.name}", valor
            yield from _campos_fecha(valor, f"{ruta}.{campo.name}")
    elif isinstance(objeto, tuple):
        for i, elemento in enumerate(objeto):
            yield from _campos_fecha(elemento, f"{ruta}[{i}]")


def test_todas_las_fechas_son_date():
    fechas = list(_campos_fecha(RESULTADO.entrada))
    assert len(fechas) > 10
    for ruta, valor in fechas:
        assert valor is None or type(valor) is date, ruta


CARGA = Path(__file__).resolve().parent.parent / "src" / "plazos" / "carga.py"


def test_los_codigos_son_los_del_documento():
    """§8.1: los códigos de la tabla son los de ERRORES, en el mismo orden."""
    from plazos.modelo import ERRORES

    tabla = _seccion(TEXTO, "### 8.1. Errores")
    assert re.findall(r"^\| `(ERR-\d\d)` \|", tabla, re.MULTILINE) == list(ERRORES)


def test_las_decisiones_citadas_en_el_codigo_existen():
    """Cada «Modelo, V-n» del código es una fila del §8.2."""
    decisiones = set(re.findall(r"^\| (V-\d+) \|", _seccion(TEXTO, "### 8.2. Decisiones de validación"), re.MULTILINE))
    assert decisiones == {f"V-{n}" for n in range(1, 18)}
    citadas = set(re.findall(r"Modelo, (V-\d+)", CARGA.read_text(encoding="utf-8")))
    assert citadas and citadas <= decisiones
