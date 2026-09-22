# plazos-conservacion-pbc

Sitio: https://mshodai.github.io/plazos-conservacion-pbc/, por qué la Ley 10/2010 y su Reglamento dan respuestas opuestas sobre cuándo empieza a contar el plazo de una operación.

Un sujeto obligado por la normativa de prevención del blanqueo de capitales tiene que conservar la documentación de cada cliente el tiempo que marca la ley, ni menos ni más: conservar de menos es una infracción, y conservar datos personales cuando la norma manda eliminarlos también incumple.

El escenario. Una entidad terminó la relación con un cliente el 31 de octubre de 2021. En junio de 2028 alguien pregunta si ya se puede borrar la documentación de diligencia debida de ese cliente. Con la Ley 10/2010, la respuesta es que no: se conserva diez años, hasta el 31 de octubre de 2031, pero desde el quinto año solo pueden consultarla los órganos de control interno y, en su caso, los encargados de la defensa legal. Con el Reglamento (UE) 2024/1624 (AMLR), aplicable desde el 10 de julio de 2027, el plazo es de cinco años, que vencieron el 31 de octubre de 2026, y los datos personales hay que suprimirlos. Y ningún texto dice cuál de los dos manda para un expediente cuyo plazo empezó con la Ley y seguía en curso cuando empezó a aplicarse el AMLR.

Esta herramienta no da un plazo. Calcula el estado de cada documento en seis regímenes (la Ley, el AMLR y cuatro lecturas de la transición entre ambos), dice de qué lectura de la norma depende cada estado y muestra dónde difieren. El porqué está en el [ADR 0001](docs/adr/0001-calcular-seis-regimenes.md).

## El caso, calculado

El repositorio incluye un corpus de ocho expedientes sintéticos en `corpus/`, cada uno con su resultado esperado. El del escenario es el caso 03:

```
$ plazos-conservacion corpus/03-plazo-en-curso-el-10-de-julio-de-2027.json
Expediente EXP-FICTICIO-03
Fecha de referencia: 2028-06-30 · AMLR aplicable desde el 2027-07-10

Resultado de un cálculo bajo las lecturas que declara la especificación (docs/especificacion-calculo.md), no una determinación jurídica. Donde la norma no fija un dato, el cálculo da todas las lecturas y no elige; las decisiones propias se citan como D-n.

== Documento DOC-FICTICIO-1 (diligencia_debida)

Estado el 2028-06-30:
  ley_10_2010  acceso_restringido
  amlr         supresion_exigida
  T-1          acceso_restringido
  T-2          supresion_exigida
  T-3          en_conservacion
  T-4          acceso_restringido

Dónde difieren:
  La Ley y el AMLR dan estados distintos el 2028-06-30.
  T-1 a T-4 no coinciden: el estado depende de cómo se resuelva la transición (S-1, D-21).
  ley_10_2010, T-1, T-4: acceso_restringido; amlr, T-2: supresion_exigida; T-3: en_conservacion
  Periodos con estados distintos:
    del 2026-11-01 al 2027-07-09 (AMLR aún no aplicable): ley_10_2010, T-1, T-2, T-3, T-4: acceso_restringido; amlr: supresion_exigida
    del 2027-07-10 al 2031-10-31: ley_10_2010, T-1, T-4: acceso_restringido; amlr, T-2: supresion_exigida; T-3: en_conservacion
    desde el 2031-11-01: ley_10_2010, T-1, T-3, T-4: eliminacion_exigida; amlr, T-2: supresion_exigida

Línea temporal (◀ fecha de referencia):
  ley_10_2010  plazo_no_iniciado → 2021-10-31 en_conservacion → 2026-11-01 acceso_restringido ◀ → 2031-11-01 eliminacion_exigida
  amlr         plazo_no_iniciado → 2021-10-31 en_conservacion → 2026-11-01 supresion_exigida ◀
  T-1          plazo_no_iniciado → 2021-10-31 en_conservacion → 2026-11-01 acceso_restringido ◀ → 2031-11-01 eliminacion_exigida
  T-2          plazo_no_iniciado → 2021-10-31 en_conservacion → 2026-11-01 acceso_restringido → 2027-07-10 supresion_exigida ◀
  T-3          plazo_no_iniciado → 2021-10-31 en_conservacion → 2026-11-01 acceso_restringido → 2027-07-10 en_conservacion ◀ → 2031-11-01 eliminacion_exigida
  T-4          plazo_no_iniciado → 2021-10-31 en_conservacion → 2026-11-01 acceso_restringido ◀ → 2031-11-01 eliminacion_exigida

Lecturas:
  ley_10_2010:
    DD: acceso_restringido (inicio 2021-10-31 · restringido desde 2026-11-01 · vence 2031-10-31) — Ley 25.1.a; RD 28.1
  amlr:
    77.3: supresion_exigida (inicio 2021-10-31 · vence 2026-10-31) — AMLR 77.1.a y 77.3
  T-1: las mismas que ley_10_2010
  T-2: las mismas que amlr
  T-3:
    DD: en_conservacion (inicio 2021-10-31 · vence 2031-10-31) — Ley 25.1.a; RD 28.1; T-3: el primero de F + 10 años y A + 5 años
  T-4: las mismas que ley_10_2010

Avisos:
  D-10 (amlr, T-2): La supresión del AMLR 77.3 se refiere a los datos personales; el AMLR no dice qué hacer con el resto de la información

La línea temporal es una proyección de los hechos que constan hoy en la entrada, no una predicción: aplica esos hechos a todas las fechas, sin tener en cuenta cuándo se conoció cada uno ni hechos futuros, como una prórroga nueva o la terminación de una relación que sigue viva. Si cambia un hecho, cambia la línea temporal.
```

Cómo leerlo:

- **Estado el 2028-06-30.** La Ley da `acceso_restringido`; el AMLR, `supresion_exigida`. Las cuatro lecturas de la transición no coinciden: si la Ley sigue rigiendo los plazos que empezaron con ella (T-1) o como plazo nacional más largo (T-4), el documento se conserva con acceso restringido; si el AMLR se aplica desde el 10 de julio de 2027 contando desde la terminación (T-2), hay que suprimir; si cuenta desde el 10 de julio de 2027 (T-3), se conserva hasta el 31 de octubre de 2031.
- **Línea temporal.** En qué fecha cambia el estado bajo cada régimen; `◀` marca el tramo de la fecha de referencia. Es una proyección de los hechos que constan hoy en la entrada, no una predicción.
- **Lecturas.** De qué regla sale cada estado, con su inicio, su vencimiento y la cita. `DD` es la lectura única de la diligencia debida con la Ley; `77.3`, la del AMLR.
- **Avisos.** Aquí, que la supresión del AMLR se refiere solo a los datos personales.

El código de salida es 1, porque alguna lectura exige actuar: con T-2 hay que suprimir, y con la Ley, T-1 y T-4, restringir el acceso.

## Instalación

Hace falta Python 3.11 o posterior (probado con 3.11, 3.12 y 3.14). No tiene dependencias externas: `pip install` solo descarga setuptools para construir el paquete. Desde la raíz del repositorio:

```sh
python3 -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\activate
pip install .
plazos-conservacion corpus/03-plazo-en-curso-el-10-de-julio-de-2027.json
```

**Uso:** `plazos-conservacion FICHERO [--json]`. Con `--json`, el mismo informe en JSON, con las fechas en formato `AAAA-MM-DD`.

**Códigos de salida:**
- **1:** en la fecha de referencia, en algún documento, alguna lectura de algún régimen exige actuar: da `eliminacion_exigida`, `supresion_exigida` o `acceso_restringido`.
- **0:** ninguna lectura lo exige, aunque los regímenes discrepen; la discrepancia está en el informe. En el corpus pasa en los casos 01 y 06. Solo mira la fecha de referencia: lo que haya que hacer más adelante está en la línea temporal.
- **2:** el fichero no se puede leer o la entrada no es válida. Los errores de validación salen con su código (`ERR-01` a `ERR-09`) y la ruta del dato.

**Con tu propio expediente.** La entrada es un JSON con el sujeto obligado, el hecho que inicia el cómputo (terminación de la relación, ejecución de la operación ocasional o negativa), los documentos con sus fechas, las prórrogas de la autoridad y si hay un procedimiento judicial pendiente. El formato, con un ejemplo, está en [docs/modelo-datos.md](docs/modelo-datos.md). La entrada recoge hechos, no el régimen: el régimen es un parámetro del cálculo.

**El corpus.** Los ocho casos, con su tabla de estados, están en [corpus/README.md](corpus/README.md). Se regeneran con `python corpus/generar.py`, que comprueba cada caso contra su resultado esperado, escrito a mano desde la especificación, antes de escribirlo.

**Tests:** `pip install pytest` y `pytest` desde la raíz.

## Qué calcula

Para cada documento del expediente, su estado en una fecha de referencia bajo seis regímenes:

- **`ley_10_2010`**: la Ley 10/2010 y el RD 304/2014. Diez años; acceso restringido a los órganos de control interno desde el quinto año; después, eliminación.
- **`amlr`**: el AMLR. Cinco años desde la extinción de la relación, la ejecución de la operación ocasional o la negativa; prórroga de la autoridad de hasta cinco años más; conservación facultativa para procedimientos judiciales pendientes el 10 de julio de 2027; después, supresión de los datos personales.
- **`T-1` a `T-4`**: lo que se aplica según cómo se resuelva la transición del 10 de julio de 2027. T-1, la Ley sigue rigiendo los plazos que empezaron con ella. T-2, el AMLR se aplica desde esa fecha, contando desde el hecho original. T-3, el AMLR cuenta desde esa fecha, sin pasar del vencimiento de la Ley. T-4, la Ley sigue como plazo nacional más largo.

Por categoría de documento: diligencia debida, operaciones, examen especial, comunicación y control interno, y aplicación de fondos en fundaciones y asociaciones.

Donde la norma no fija desde cuándo cuenta el plazo, el cálculo da una lectura por cada inicio posible:
- examen especial: apertura, cierre, decisión, comunicación o terminación de la relación (EE-1 a EE-5);
- control interno: fecha del documento, fin de vigencia o terminación de la relación (CI-1 a CI-3);
- aplicación de fondos: aplicación o fin del proyecto (AF-1, AF-2);
- operaciones dentro de una relación: ejecución de la operación, según la Ley, o terminación de la relación, según el RD (OP-1, OP-2);
- negativa con la Ley, que no cuenta desde ella: fecha de la negativa o del documento (NG-1, NG-2);
- período adicional del art. 77.4: sin él o con él (PA-1, PA-2).

Si las lecturas de un régimen dan estados distintos, el estado es `indeterminado`, con las lecturas a la vista. Los estados posibles son `plazo_no_iniciado`, `en_conservacion`, `acceso_restringido`, `eliminacion_exigida`, `conservacion_prorrogada`, `conservacion_facultativa_77_4`, `supresion_exigida`, `sin_regla` (categorías que el AMLR no regula) e `indeterminado`.

Además, la línea temporal de cada régimen y los periodos en que los regímenes difieren. Las reglas completas, con las decisiones propias numeradas (D-1 a D-28) y su motivo, están en la [especificación del cálculo](docs/especificacion-calculo.md).

## Qué no hace

- **No dice qué lectura es la correcta.** Si la Ley pervive tras el 10 de julio de 2027, si una operación cuenta desde su ejecución o desde la terminación, desde qué fecha cuenta un examen especial: lo calcula todo y no elige.
- **No clasifica documentos ni comprueba hechos.** La categoría de cada documento, que un procedimiento judicial está relacionado con el expediente o que una prórroga es válida los afirma la entrada.
- **No decide a quién se aplica la norma.** Por ejemplo, si una fundación sigue obligada tras el AMLR, o si un expediente de un club de fútbol está en el ámbito del AMLR.
- **No distingue qué parte de un documento es dato personal.** La supresión del AMLR se refiere a los datos personales; qué hacer con el resto no lo dice la norma ni la herramienta.
- **No gestiona permisos.** Informa de desde cuándo rige el acceso restringido, no de quién puede acceder.
- **No prevé hechos futuros.** Una relación que sigue viva no tiene plazo iniciado; una prórroga que aún no se ha requerido no aparece.
- **No calcula otras obligaciones de conservación** (mercantiles, fiscales, laborales) ni las del Reglamento general de protección de datos, que pueden dar plazos distintos para el mismo documento.
- **No trata el intercambio de información en asociaciones** del art. 77.1.d del AMLR.
- **No borra ni archiva nada.** Lee un JSON y devuelve un informe.

## Los quince casos que la norma no resuelve

Al analizar los textos aparecieron quince puntos en que el resultado no está determinado por un texto único. Trece vienen de la norma: la transición del 10 de julio de 2027, la negativa bajo la Ley, la contradicción entre la Ley y el RD en las operaciones, los plazos sin inicio declarado del examen especial, el control interno y la aplicación de fondos, las categorías que el AMLR no regula, los plazos nacionales más largos, el período adicional del art. 77.4, el cómputo de los años, entre otros. Dos vienen del modelo de datos: la norma sí responde, pero la entrada no recoge el dato necesario.

Están en [docs/ambiguedades.md](docs/ambiguedades.md), cada uno con qué dice la norma, por qué no determina un comportamiento único, qué hace esta implementación, cómo se señala en la salida y a qué régimen afecta.

## Fuentes

| Documento | Versión |
|---|---|
| Ley 10/2010, de 28 de abril, de prevención del blanqueo de capitales y de la financiación del terrorismo | Texto consolidado, última modificación de 21 de marzo de 2026 |
| Real Decreto 304/2014, de 5 de mayo, Reglamento de la Ley 10/2010 | Texto consolidado, última modificación de 24 de abril de 2024 |
| Reglamento (UE) 2024/1624 (AMLR), de 31 de mayo de 2024 | Texto publicado en el DO L de 19 de junio de 2024, sin consolidar |

Los documentos se descargaron el 15 de septiembre de 2026. Las URL y las huellas SHA-256 de cada versión están en [docs/fuentes/FUENTES.md](docs/fuentes/FUENTES.md). Los PDF no se redistribuyen.

**Calendario.**
- **Hasta el 9 de julio de 2027:** se aplica la Ley 10/2010. La herramienta calcula también el AMLR, para comparar, y avisa de que todavía no es aplicable.
- **10 de julio de 2027:** el AMLR «será aplicable» (art. 90). Ningún texto dice qué pasa con los plazos que empezaron con la Ley y siguen en curso; de ahí T-1 a T-4.
- **10 de julio de 2029:** aplicación del AMLR a los agentes de fútbol y a los clubes de fútbol profesional (art. 90).
- **10 de julio de 2032:** fin de la conservación facultativa para documentos relacionados con procedimientos judiciales pendientes el 10 de julio de 2027 (art. 77.4), o **10 de julio de 2037** si el Estado permite o exige el período adicional.

## Otros repositorios del proyecto

- [validador-cadena-verifactu](https://github.com/mshodai/validador-cadena-verifactu): comprueba la integridad de una cadena de registros de facturación de Verifactu.
- [calculo-titularidad-real](https://github.com/mshodai/calculo-titularidad-real): calcula la titularidad real bajo la Ley 10/2010 y el AMLR.
- [plazos-actualizacion-pbc](https://github.com/mshodai/plazos-actualizacion-pbc): calcula la fecha de la próxima revisión obligatoria de la información de un cliente bajo la Ley 10/2010 y el AMLR.
- [registro-examen-especial-pbc](https://github.com/mshodai/registro-examen-especial-pbc): comprueba si el registro de un examen especial en el que pudo intervenir un sistema de IA está completo bajo la Ley 10/2010 y bajo el AMLR.

## Licencia

MIT; el texto completo está en [LICENSE](LICENSE). Cubre el código y la documentación de este repositorio, no los textos legales de `docs/fuentes/`, que no se incluyen.

---

Es una implementación de referencia, probada sobre datos sintéticos. No es software de cumplimiento normativo y no constituye asesoramiento jurídico.
