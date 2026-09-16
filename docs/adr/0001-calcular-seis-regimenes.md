# 0001. Calcular seis regímenes y compararlos en lugar de devolver un plazo

- Estado: aceptada
- Fecha: 17/09/2026

## Contexto

Los sujetos obligados por la normativa de prevención del blanqueo de capitales (PBC) tienen que conservar la documentación de diligencia debida, de las operaciones, de los exámenes especiales y de sus comunicaciones y controles internos. Conservarla es una obligación legal que falla en los dos sentidos.

- **Conservar de menos incumple la ley sectorial.** La Ley 10/2010 manda conservar «durante un período de diez años la documentación en que se formalice el cumplimiento de las obligaciones establecidas en la presente ley» (art. 25.1), y el incumplimiento de esa obligación es una infracción (art. 52.1.l).
- **Conservar de más también incumple.** La misma Ley manda proceder «tras el mismo a su eliminación» (art. 25.1). El AMLR dice que «las entidades obligadas suprimirán los datos personales al expirar el período de cinco años» y enmarca esa supresión en el Reglamento (UE) 2016/679, el RGPD (art. 77.3). Guardar datos personales más allá del plazo que justifica su tratamiento es un problema de protección de datos, no una prudencia. El texto del RGPD no está entre las fuentes del proyecto; la obligación de suprimir sí está en las dos normas sectoriales.

Así que la pregunta útil no es «cuánto hay que guardar como mínimo», sino en qué estado está cada documento en una fecha dada: todavía no ha empezado su plazo, se conserva, se conserva con acceso restringido, se puede o se debe eliminar.

Dos regímenes conviven, con plazos distintos:

- **El español, vigente.** Ley 10/2010 y su Reglamento, el RD 304/2014: diez años, en general desde la terminación de la relación de negocios o la ejecución de la operación ocasional (Ley 25.1; RD 28.1 y 29.1), con acceso restringido a los órganos de control interno «transcurridos cinco años» (Ley 25.1).
- **El AMLR, Reglamento (UE) 2024/1624.** «Será aplicable a partir del 10 de julio de 2027» (art. 90). Cinco años desde la extinción de la relación, la ejecución de la operación ocasional o la negativa a entablarlas, con prórroga posible a petición de la autoridad (art. 77.3) y un régimen propio para procedimientos judiciales pendientes (art. 77.4).

Ningún texto dice qué pasa el 10 de julio de 2027 con los expedientes cuyo plazo de diez años empezó con la Ley y sigue en curso ese día. El AMLR es directamente aplicable, pero su único régimen transitorio sobre conservación es el de los procedimientos judiciales (art. 77.4), y la Ley consolidada a 21 de marzo de 2026 no tiene ninguna adaptación. Un mismo documento puede estar, ese día, en acceso restringido con la Ley, en supresión exigida con el AMLR contado desde el hecho original, o en conservación ordinaria con el AMLR contado desde el 10 de julio de 2027.

## Decisión

La herramienta calcula el estado de cada documento en **seis regímenes** y los compara. No devuelve un plazo.

Los seis son la Ley aplicada sola (`ley_10_2010`), el AMLR aplicado solo (`amlr`) y cuatro lecturas de la transición (`T-1` a `T-4`: pervivencia de la Ley, AMLR desde el hecho original, AMLR desde el 10 de julio de 2027 con el límite de la Ley, y la Ley como plazo nacional superior). Se calculan siempre los seis y ninguno es el principal ([especificación](../especificacion-calculo.md), §1.1 y §4; D-14).

Hay tres razones.

**Quince casos que la norma no resuelve.** Trece vienen de los textos y dos del modelo de datos ([ambiguedades.md](../ambiguedades.md)). Algunos cambian el estado en expedientes corrientes:
- el RD no dice desde cuándo cuentan los diez años del examen especial, y un retraso de cinco días entre el cierre y la comunicación basta para que una lectura exija eliminar y otra siga conservando (S-4);
- la Ley cuenta las operaciones «desde la ejecución de la operación» y el RD desde la terminación de la relación, así que una operación puede tener que eliminarse con la relación todavía viva, o no (S-3);
- la transición (S-1).

Un plazo único resuelve cada uno de ellos en un sentido, sin decir cuál.

**Veintisiete decisiones propias.** La especificación numera D-1 a D-27 (una de ellas, D-15, retirada), cada una con su motivo: cómo se cuentan los años, qué pasa con una prórroga requerida tarde, cómo se combina el plazo de la Ley con el del AMLR en T-4. A esas se suman las diecisiete de validación del modelo (V-1 a V-17). Ninguna es la ley. Un plazo sin más las incorpora todas sin nombrar ninguna.

**El campo que más decide no puede quedar en manos de quien rellena la entrada.** En una primera versión, la entrada llevaba un campo `regimen`. Quien lo rellenaba con `ley_10_2010` elegía, sin saberlo, que la Ley pervive para los expedientes en curso; con `amlr`, que el AMLR se aplica desde el hecho original; y la lectura que cuenta desde el 10 de julio de 2027 no podía salir nunca. Esa elección es la que más cambia el resultado y es jurídica, no un dato del expediente. Por eso la entrada solo recoge hechos, y el régimen es un parámetro del cálculo que se recorre entero ([modelo-datos.md](../modelo-datos.md), §0; D-15, retirada).

## Consecuencias

**Cada estado va con la lectura que lo sostiene.** Donde la norma no fija el inicio del plazo, el cálculo da una lectura por cada inicio posible (`EE-1` a `EE-5`, `CI-1` a `CI-3`, `AF-1` y `AF-2`, `OP-1` y `OP-2`, `NG-1` y `NG-2`, `PA-1` y `PA-2`), con su fecha de inicio, su vencimiento y la cita en que se basa. Quien discuta un estado puede ver de qué lectura depende y discutir esa lectura.

**`indeterminado` cuando las lecturas discrepan.** Si las lecturas de un régimen dan estados distintos en la fecha de referencia, el régimen da `indeterminado` (D-6), no el estado más prudente ni el más probable. Las lecturas se devuelven siempre, así que se ve en qué discrepan. Las categorías que el AMLR no regula dan `sin_regla` (D-17), que no significa ni conservar ni suprimir.

**La línea temporal es una proyección, no una predicción.** Para cada régimen, el informe da las fechas en que cambia el estado. Se calculan aplicando los hechos que constan hoy en la entrada a todas las fechas: no saben cuándo se conoció cada hecho ni prevén hechos futuros, como la terminación de una relación viva o un requerimiento nuevo de la autoridad. Dicen cuándo cambiaría el estado si los hechos no cambian, no cuándo va a cambiar (D-25).

**El código de salida solo mira la fecha de referencia.** Devuelve 0 si en esa fecha los seis regímenes dan el mismo estado para todos los documentos y ninguno es `indeterminado`; 1 si no; 2 si la entrada no es válida (especificación, §9.3; D-27). Un documento en el que los regímenes coinciden hoy y divergen dentro de cinco años da 0: la divergencia futura está en la línea temporal, no en el código.

**La frontera entre lo que la herramienta calcula y lo que exige decidir a quién aplica la norma.** La herramienta calcula fechas y estados bajo lecturas declaradas, de forma exacta y reproducible. No decide:

- **qué lectura es la correcta**: si la Ley pervive tras el 10 de julio de 2027, si una operación cuenta desde su ejecución o desde la terminación, desde qué fecha cuenta un examen especial;
- **si la norma se aplica al expediente**: si una fundación o una asociación siguen obligadas tras el AMLR (S-8), o si un expediente de un club de fútbol está en el ámbito del art. 3.3.o (S-15);
- **hechos que la entrada afirma y no comprueba**: la categoría de cada documento, que un procedimiento judicial está relacionado con el expediente, que una prórroga de la autoridad es válida;
- **lo que la norma deja a quien la aplica**: quién conserva el acceso durante la restricción (especificación, §6.3; D-16), qué información del documento es dato personal y qué hacer con la que no lo es (D-10).

Donde uno de estos puntos cambia el estado, la salida lo muestra como lecturas, `indeterminado`, regímenes que no coinciden o `sin_regla`. No lo resuelve.

**Costes.**
- El informe es largo: seis regímenes, sus lecturas y sus líneas temporales por documento. Quien solo quiere saber «cuándo borro» tiene que leer de qué depende la respuesta.
- `indeterminado` y la falta de coincidencia son frecuentes: en el corpus, siete de ocho casos dan código 1. No es un defecto del cálculo; es la cantidad de cosas que la norma no resuelve.
- Cada decisión nueva hay que declararla en la especificación y reflejarla en el corpus, cuyos resultados esperados se escriben a mano.

## Referencias

- Ley 10/2010, de 28 de abril, arts. 7.3, 25 y 52.1.l (texto consolidado, última modificación de 21 de marzo de 2026): <https://www.boe.es/buscar/act.php?id=BOE-A-2010-6737>
- Real Decreto 304/2014, de 5 de mayo, arts. 25, 28, 29 y 42 (texto consolidado, última modificación de 24 de abril de 2024): <https://www.boe.es/buscar/act.php?id=BOE-A-2014-4742>
- Reglamento (UE) 2024/1624 (AMLR), arts. 77 y 90 (DO L de 19.6.2024): <http://data.europa.eu/eli/reg/2024/1624/oj>
- Versiones y huellas de los documentos usados: [fuentes/FUENTES.md](../fuentes/FUENTES.md)
