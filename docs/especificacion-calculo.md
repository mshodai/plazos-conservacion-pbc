# Especificación del cálculo

Este documento explica cómo se calcula el estado de conservación de un documento en una fecha de referencia, con la Ley 10/2010 y su Reglamento, con el AMLR y con cada lectura de la transición entre ambos. La entrada es el JSON de [`modelo-datos.md`](modelo-datos.md), que solo recoge hechos y no lleva régimen. No contiene código.

Siglas y fuentes: las de [`modelo-datos.md`](modelo-datos.md) (detalle y huellas en [`fuentes/FUENTES.md`](fuentes/FUENTES.md)). Las referencias «S-n» remiten a los casos sin resolver de ese documento.

Convenciones:

- Las citas van entre comillas «» y son literales.
- **[D-n]** marca una decisión de este proyecto que no sale de los textos. Todas están numeradas y reunidas en el [§9](#9-índice-de-decisiones). Los números son estables: una decisión retirada conserva su número y no se reutiliza.
- **Lectura** es una interpretación posible de un texto que no se resuelve. Cuando hay varias, el cálculo las devuelve todas con su resultado (§1.4) y no elige.

---

## 1. Marco común

### 1.1. El régimen es un parámetro del cálculo

El cálculo recibe la entrada y un **régimen**, que puede ser uno de estos seis:

| Régimen | Qué calcula | Sección |
|---|---|---|
| `ley_10_2010` | La Ley y el RD, aplicados solos, en cualquier fecha. | §2 |
| `amlr` | El AMLR, aplicado solo, en cualquier fecha. | §3 |
| `T-1` a `T-4` | Lo que se aplica en `fecha_referencia` según cada lectura de la transición del 10 de julio de 2027. | §4 |

Los dos primeros sirven para comparar las normas tal como están escritas; los cuatro últimos, para saber qué se aplica en una fecha concreta según cómo se resuelva la transición, que ningún texto resuelve (S-1).

**[D-14]** Una ejecución completa calcula **los seis regímenes** sobre la misma entrada y los devuelve juntos (§1.4). Ninguno es el principal ni el resultado por defecto. **[D-15, retirada]**: en la versión anterior la entrada llevaba un campo `regimen` que fijaba un estado principal y, sin que quien rellenaba la entrada lo supiera, elegía T-1/T-4 o T-2; T-3 no podía salir nunca como estado principal.

### 1.2. Pasos del cálculo

Para cada régimen y cada documento del expediente:

1. **Validar** la entrada según [`modelo-datos.md`](modelo-datos.md). La validación no depende del régimen.
2. **Determinar la fecha de inicio del cómputo** según la categoría y el régimen (§2.1, §3.1 y §4.2). Si el texto no la fija, se obtiene una fecha por cada lectura.
3. **Calcular las fechas de transición** de cada lectura: vencimiento del plazo y, en su caso, inicio del acceso restringido, fin de la prórroga o fin de la conservación facultativa.
4. **Comparar con `fecha_referencia`** y asignar el estado de cada lectura.

### 1.3. Cómputo de fechas

Ninguna de las tres fuentes dice cómo se cuentan los años (S-13). Se usan estas reglas:

- **[D-1]** «N años desde F» vence en la fecha V que tiene el mismo día y mes que F, N años después. Si ese día no existe (F es un 29 de febrero y el año de V no es bisiesto), V es el 28 de febrero.
- **[D-2]** El día V todavía está dentro del plazo. El estado posterior al plazo empieza en V + 1 día.
- **[D-3]** El día F ya está dentro del plazo. Antes de F, el plazo no ha empezado.
- **[D-4]** «Transcurridos cinco años desde F» (Ley, art. 25.1) se cumple en V₅ + 1 día, donde V₅ es F + 5 años según [D-1]. Es coherente con [D-2].

### 1.4. Forma del resultado

**[D-5]** Para cada documento, el resultado tiene una entrada por régimen (`ley_10_2010`, `amlr`, `T-1`, `T-2`, `T-3`, `T-4`). Cada una incluye:

- `estado`: uno de los estados del régimen (§2.2, §3.2 y §4.2), o `indeterminado` (ver [D-6]).
- `lecturas`: lista con una entrada por lectura de la categoría. Cada entrada tiene su identificador (por ejemplo `OP-1`), su fecha de inicio del cómputo, sus fechas de transición, su estado en `fecha_referencia` y la cita en que se basa.
- `avisos`: incidencias que no impiden el cálculo, como una prórroga recortada ([D-12]) o el AMLR calculado antes de ser aplicable ([D-20]).

Además, el documento lleva una **comparación de la transición**: los estados de T-1 a T-4 uno junto a otro y si coinciden. **[D-21]**: si no coinciden, el resultado lo señala expresamente, porque significa que el estado del documento en `fecha_referencia` depende de cómo se resuelva S-1.

**[D-6]** Dentro de un régimen, si todas las lecturas de la categoría dan el mismo estado en `fecha_referencia`, `estado` toma ese valor, aunque las fechas de transición sean distintas. Si difieren, `estado` es `indeterminado`. Las lecturas se devuelven siempre. Las lecturas de categoría y las de transición no se mezclan en un solo `indeterminado`: cada régimen `T-n` tiene su propio `estado`.

---

## 2. Régimen de la Ley 10/2010 y el RD 304/2014

### 2.1. Inicio del cómputo y plazo por categoría

Regla general: Ley, art. 25.1, primer párrafo: «Los sujetos obligados conservarán durante un período de diez años la documentación en que se formalice el cumplimiento de las obligaciones establecidas en la presente ley, procediendo tras el mismo a su eliminación».

Llamaremos **H** a la fecha del hecho inicial: `fecha_terminacion` si es una relación de negocios y `fecha_ejecucion` si es una operación ocasional. Si el hecho inicial es una negativa, la Ley no da fecha de inicio: ver «Expedientes con negativa» al final de este apartado.

Este régimen no usa `prorrogas_autoridad` ni `procedimiento_judicial_pendiente_2027_07_10`: la Ley y el RD no tienen nada equivalente (modelo §6).

#### `diligencia_debida`: 10 años desde H

- Ley, art. 25.1.a: «durante un periodo de diez años desde la terminación de la relación de negocios o la ejecución de la operación».
- RD, art. 28.1: «durante un periodo de diez años desde la terminación de la relación de negocio o la ejecución de la operación ocasional».

Una sola lectura. Si la relación sigue viva (`fecha_terminacion = null`), el plazo no ha empezado.

#### `operaciones`: 10 años, con dos lecturas (§5)

- **OP-1.** Desde `fecha_ejecucion_operacion`. Ley, art. 25.1.b: «durante un periodo de diez años desde la ejecución de la operación o la terminación de la relación de negocios».
- **OP-2.** Desde H. RD, art. 29.1: «durante un periodo de diez años desde la terminación de la relación de negocio o la ejecución de la operación ocasional».

Si el hecho inicial es una operación ocasional, las dos lecturas coinciden: `fecha_ejecucion_operacion` y H son la misma operación.

#### `examen_especial`: 10 años sin inicio declarado (S-4)

RD, art. 25.4: «Los sujetos obligados conservarán los expedientes de examen especial durante el plazo de diez años».

Lecturas, cada una con su fecha candidata del RD 25.3 («sus fechas de apertura y cierre [...] la decisión sobre su comunicación [...] y su fecha, así como la fecha en que, en su caso, se realizó la comunicación»):

| Lectura | Inicio | Si la fecha es `null` |
|---|---|---|
| EE-1 | `fecha_apertura` | — (obligatoria) |
| EE-2 | `fecha_cierre` | plazo no iniciado |
| EE-3 | `fecha_decision_comunicacion` | plazo no iniciado |
| EE-4 | `fecha_comunicacion` si existe; si no, `fecha_decision_comunicacion` | plazo no iniciado |
| EE-5 | H, por analogía con Ley 25.1.a y b | plazo no iniciado |

**[D-7]** EE-4 usa la fecha de decisión cuando no hubo comunicación. Sin esa sustitución, un examen que concluye sin comunicar no tendría nunca inicio del cómputo en esa lectura.

#### `comunicacion_control_interno`: 10 años sin inicio declarado (S-5)

RD, art. 29.2: «Los sujetos obligados conservarán durante un periodo de diez años los documentos en que se formalice el cumplimiento de sus obligaciones de comunicación y de control interno».

| Lectura | Inicio | Cuándo aplica |
|---|---|---|
| CI-1 | `fecha_documento` | Siempre. |
| CI-2 | `fecha_fin_vigencia` (`null` = plazo no iniciado) | Solo con `politicas_procedimientos` y `analisis_riesgo`. |
| CI-3 | H | Solo si el expediente tiene hecho inicial. |

#### `aplicacion_fondos`: 10 años sin inicio declarado (S-7)

RD, art. 42.3.d: «Conservar durante un plazo de diez años los documentos o registros que acrediten la aplicación de los fondos en los diferentes proyectos».

| Lectura | Inicio |
|---|---|
| AF-1 | `fecha_aplicacion` |
| AF-2 | `fecha_fin_proyecto` (`null` = plazo no iniciado) |

#### Expedientes con negativa (S-2)

La negativa es un hecho válido de la entrada (modelo §3.1), pero ni la Ley 25.1 ni los RD 28.1 y 29.1 cuentan desde ella. La documentación reunida está cubierta por la regla general de la Ley 25.1 («la documentación en que se formalice el cumplimiento de las obligaciones establecidas en la presente ley»), que fija diez años sin inicio.

**[D-18]** Para todas las categorías cuya regla usa H, un expediente con negativa da dos lecturas:

| Lectura | Inicio |
|---|---|
| NG-1 | `fecha_negativa`, por analogía con la terminación de la relación |
| NG-2 | `fecha_documento` |

Las categorías con lecturas propias (EE-n, CI-n, AF-n) sustituyen la lectura EE-5 o CI-3, que usan H, por NG-1 y NG-2. No hay acceso restringido: el art. 25.1 lo cuenta desde la terminación o la ejecución de la operación ocasional ([D-8]).

### 2.2. Estados y transiciones

| Estado | Desde | Hasta | Base |
|---|---|---|---|
| `plazo_no_iniciado` | — | día anterior a la fecha de inicio | [D-3]. Mientras tanto hay que conservar el documento: el deber nace con la obligación que documenta (Ley 25.1). |
| `en_conservacion` | fecha de inicio | V (inicio + 10 años) o día anterior a R | Ley 25.1; RD 28.1, 29.1, 29.2, 25.4 y 42.3.d |
| `acceso_restringido` | R = H + 5 años + 1 día | V | Ley 25.1, primer párrafo. Ver §6. |
| `eliminacion_exigida` | V + 1 día | — | Ley 25.1: «procediendo tras el mismo a su eliminación» |

El acceso restringido y el plazo de diez años pueden contarse desde fechas distintas:

- **R siempre se cuenta desde H.** El art. 25.1 lo cuenta «desde la terminación de la relación de negocios o la ejecución de la operación ocasional», no desde el documento.
- **R solo existe si el expediente tiene hecho inicial.** **[D-8]**: sin hecho inicial (por ejemplo, una fundación con solo `aplicacion_fondos`), el documento nunca pasa a `acceso_restringido`. Ver §6.3.
- **Si R > V** (el documento vence antes de que empiece la restricción, como en OP-1), el documento pasa de `en_conservacion` a `eliminacion_exigida` sin estar nunca restringido.
- **Si la fecha de inicio es posterior a R** (por ejemplo, EE-2 con un examen cerrado más de cinco años después de H), el documento está en `acceso_restringido` desde su fecha de inicio. **[D-9]**: la restricción se aplica a «la documentación conservada» sin excepciones por fecha, así que también cubre la documentación posterior a R.

No hay prórroga del plazo ni conservación facultativa: no se encontró ninguna en la Ley ni en el RD (modelo §6.1).

---

## 3. Régimen del AMLR

### 3.1. Inicio del cómputo y plazo por categoría

AMLR, art. 77.3: «La información indicada en los apartados 1 y 2 se conservará durante un período de cinco años, a partir de la fecha de extinción de la relación de negocios o de la fecha en la que se ejecute la operación ocasional, o de la fecha de la negativa a entablar una relación de negocios o llevar a cabo una operación ocasional».

Aquí **H** es `fecha_terminacion`, `fecha_ejecucion` o `fecha_negativa`, según el tipo de hecho inicial. Todas las categorías con regla usan H. Ningún campo propio de un documento inicia el cómputo.

| Categoría | Regla | Plazo | Inicio |
|---|---|---|---|
| `diligencia_debida` | Art. 77.1.a: «una copia de los documentos y la información obtenidos durante la realización del procedimiento de diligencia debida con respecto al cliente» | 5 años | H |
| `operaciones` | Art. 77.1.c: «los justificantes y registros de operaciones» | 5 años | H. Dentro de una relación de negocios, la extinción de la relación: el art. 77.3 solo cuenta desde la ejecución de la operación «ocasional». |
| `examen_especial` | Art. 77.1.b: «un registro de la evaluación realizada de conformidad con el artículo 69, apartado 2 [...] y una copia de las comunicaciones, si las hay, de sospechas de operaciones» | 5 años | H. Si el expediente no tiene hecho inicial: `indeterminado`, sin lecturas (S-4). |
| `comunicacion_control_interno` con `subtipo = "comunicacion_por_indicio"` | Art. 77.1.b: «una copia de las comunicaciones, si las hay, de sospechas de operaciones» | 5 años | H ([D-19]) |
| `comunicacion_control_interno`, resto de subtipos | **Ninguna** en el art. 77.1 | — | — (§7) |
| `aplicacion_fondos` | **Ninguna** | — | — (§7) |

### 3.2. Estados y transiciones

| Estado | Desde | Hasta | Base |
|---|---|---|---|
| `plazo_no_iniciado` | — | H − 1 día | [D-3] |
| `en_conservacion` | H | V = H + 5 años | Art. 77.3. Art. 77.1: «Las entidades obligadas velarán por que los documentos, la información y los registros mantenidos en virtud del presente artículo no se expurguen». |
| `conservacion_prorrogada` | V + 1 día | P = fin de la prórroga ([D-11], [D-12]) | Art. 77.3, segundo párrafo |
| `conservacion_facultativa_77_4` | 2027-07-10 | 2032-07-10 (lectura PA-1) o 2037-07-10 (lectura PA-2) | Art. 77.4 ([D-13]) |
| `supresion_exigida` | V + 1 día, o P + 1 día, o fin de la conservación facultativa + 1 día | — | Art. 77.3: «las entidades obligadas suprimirán los datos personales al expirar el período de cinco años» |
| `sin_regla` | — | — | §7 |

**[D-10]** `supresion_exigida` se refiere solo a los datos personales, como dice el art. 77.3. El AMLR no dice qué hacer después con la información que no es personal. El resultado lo indica en `avisos` y no lo convierte en otro estado.

**Prórroga de la autoridad.** Art. 77.3, segundo párrafo: «Las autoridades competentes podrán exigir, según cada caso concreto, que se siga conservando la información [...]. La prórroga máxima del período de conservación no excederá de un período de cinco años».

- **[D-11]** Solo cuenta una prórroga con `fecha_requerimiento` ≤ V. «Que se siga conservando» presupone que el plazo no ha vencido. Si el requerimiento llega después, no se aplica y se emite un aviso.
- **[D-12]** Si hay varias prórrogas, P es la `fecha_fin` más tardía, con un límite de V + 5 años. Si alguna `fecha_fin` supera ese límite, se recorta y se emite un aviso. El límite es acumulado: «la prórroga máxima [...] no excederá de un período de cinco años».

**Procedimientos judiciales pendientes.** Art. 77.4: «la entidad obligada podrá conservar esa información o esos documentos durante un período de cinco años a partir del 10 de julio de 2027». El segundo párrafo permite a los Estados miembros «permitir o requerir la conservación de los datos o información durante un período adicional de cinco años».

- **[D-13]** Si `procedimiento_judicial_pendiente_2027_07_10 = true` y el documento estaría en `supresion_exigida` en `fecha_referencia`, pasa a `conservacion_facultativa_77_4` mientras `fecha_referencia` no supere el fin de la conservación facultativa. Es facultativa porque el texto dice «podrá». Si el documento estaría en `en_conservacion` o `conservacion_prorrogada`, prevalece ese estado.
- Si España permite o exige el período adicional no está en las fuentes (S-11), así que hay dos lecturas: **PA-1**, sin período adicional (fin el 2032-07-10), y **PA-2**, con él (fin el 2037-07-10). Con PA-2 también se usa «facultativa», porque tampoco se sabe si sería permitir o requerir. Con `procedimiento_judicial_pendiente_2027_07_10 = false`, estas lecturas no existen.

---

## 4. Transición de régimen: 10 de julio de 2027

### 4.1. Lo que dicen los textos

- AMLR, art. 90: «Será aplicable a partir del 10 de julio de 2027, excepto para las entidades obligadas a que se refiere el artículo 3, punto 3, letras n) a o), para quienes será aplicable desde el 10 de julio de 2029». Y: «El presente Reglamento será obligatorio en todos sus elementos y directamente aplicable en cada Estado miembro».
- AMLR, art. 77.4: el único régimen transitorio sobre conservación, limitado a procedimientos judiciales pendientes (§3.2).
- AMLR, art. 77.3: «Sin perjuicio de los períodos de conservación de los datos recogidos a efectos de otros actos jurídicos de la Unión o del Derecho nacional que cumplan el Reglamento (UE) 2016/679».
- Considerando 156: solo trata los procedimientos judiciales en curso.
- La Ley consolidada a 21 de marzo de 2026 no contiene ninguna adaptación al AMLR ni ninguna regla transitoria sobre conservación.

**Lo que ningún texto dice:** qué plazo se aplica a un documento cuyo plazo de diez años empezó con la Ley antes del 10 de julio de 2027 y sigue en curso ese día. Tampoco dice si el art. 25 de la Ley sigue vigente como «Derecho nacional» en el sentido del art. 77.3 (S-1, S-9).

En lo que sigue, **A** es la fecha de aplicación: 2027-07-10, o 2029-07-10 si `sujeto.actividad` es `agente_de_futbol` o `club_de_futbol_profesional` (para los clubes, ver S-15).

### 4.2. Lecturas

| Lectura | Idea | Documento con H < A | Documento con H ≥ A |
|---|---|---|---|
| **T-1. Pervivencia de la Ley** | El plazo iniciado sigue la norma vigente cuando empezó. | Régimen de la Ley entero (§2): 10 años y acceso restringido. | AMLR (§3). |
| **T-2. Aplicación inmediata con cómputo desde H** | El AMLR se aplica desde A a todo lo conservado y cuenta los 5 años desde el hecho original. | Hasta A − 1: Ley. Desde A: AMLR con V = H + 5 años. Si V < A, `supresion_exigida` desde A (salvo art. 77.4). | AMLR (§3). |
| **T-3. Aplicación inmediata con cómputo desde A** | Por analogía con el art. 77.4, que cuenta «a partir del 10 de julio de 2027», los 5 años corren desde A. | Hasta A − 1: Ley. Desde A: vence el primero de estos dos días: el vencimiento de la Ley (H + 10 años) o A + 5 años. Sin acceso restringido. | AMLR (§3). |
| **T-4. Plazo nacional superior** | Los 10 años de la Ley son un «período de conservación [...] del Derecho nacional» (art. 77.3) y siguen rigiendo mientras la Ley no cambie. | Régimen de la Ley (§2). | Desde A, el mayor de los dos plazos: el de la Ley (§2, con sus lecturas NG-n para las negativas) y el del AMLR (§3). Se mantiene la restricción de la Ley. |

Notas:

- **T-3** limita el plazo al vencimiento de la Ley para no resucitar documentos que la Ley ya mandaba eliminar. Sin ese límite, un documento con H = 2018-01-01 (eliminación exigida por la Ley desde 2028-01-02) volvería a tener que conservarse hasta 2032-07-10. Es parte de cómo se construye la lectura, no una decisión sobre cuál aplicar.
- **T-4** no es solo transitoria: afecta también a los hechos posteriores a A. Se incluye aquí porque es la que más cambia el resultado desde A.
- **Relación viva el día A** (`fecha_terminacion` nula o posterior a A): el plazo no había empezado con la Ley. T-1, T-2 y T-3 coinciden en aplicar el AMLR; T-4 aplica 10 años.
- **Categorías sin inicio declarado** (`examen_especial`, `comunicacion_control_interno` y `aplicacion_fondos` con la Ley): la comparación con A se hace con la fecha de inicio de cada lectura de la categoría. El resultado es la combinación de ambas, por ejemplo `T-1 × EE-2`.
- **Categorías sin regla en el AMLR:** con T-2 y T-3 quedan en `sin_regla` desde A. Con T-1, siguen la Ley si la fecha de inicio de la lectura es anterior a A, y quedan en `sin_regla` si no. Con T-4 siguen la Ley. Ver §7.

### 4.3. Antes de A y cuándo coinciden las lecturas

- **Antes de A**, los cuatro regímenes `T-n` dan el resultado de `ley_10_2010`: el AMLR todavía no es aplicable. Se calculan igual ([D-14]), y la comparación dice que coinciden.
- **Desde A**, `T-1`, `T-2` y `T-3` coinciden con `amlr` para los documentos con H ≥ A, y difieren entre sí solo en los documentos con H < A.
- `T-4` puede diferir de los demás en cualquier documento desde A.

**[D-20]** El régimen `amlr` se calcula también cuando `fecha_referencia` es anterior a A, porque comparar las normas es uno de los objetivos del proyecto. El resultado lleva el aviso de que el AMLR no es aplicable en esa fecha. Base: art. 90, «Será aplicable a partir del 10 de julio de 2027».

---

## 5. Contradicción entre la Ley y el RD: operaciones dentro de una relación de negocios

### 5.1. Los textos

- Ley, art. 25.1.b: «Original o copia con fuerza probatoria de los documentos o registros que acrediten adecuadamente las operaciones, los intervinientes en las mismas y las relaciones de negocio, durante un periodo de diez años desde la ejecución de la operación o la terminación de la relación de negocios».
- RD, art. 29.1: «conservarán los documentos y mantendrán registros adecuados de todas las relaciones de negocio y operaciones, nacionales e internacionales, durante un periodo de diez años desde la terminación de la relación de negocio o la ejecución de la operación ocasional».

La Ley dice «la operación» y el RD, «la operación ocasional». Para una operación ocasional dan lo mismo. Para una operación ejecutada dentro de una relación de negocios, dan fechas distintas.

### 5.2. Lecturas

- **OP-1 (letra de la Ley).** El «o» reparte las dos fechas entre los dos objetos de la frase: los documentos que acreditan operaciones cuentan desde su ejecución, y los que acreditan relaciones de negocio, desde su terminación. Una operación dentro de una relación viva puede vencer antes de que la relación termine.
- **OP-2 (RD).** Dentro de una relación, el plazo cuenta desde su terminación. Solo la operación ocasional cuenta desde su ejecución.

**Argumentos que recogen los textos y que el cálculo no pondera:**

- *A favor de OP-2:* el mismo art. 25.1, en su primer párrafo, cuenta la restricción de acceso «desde la terminación de la relación de negocios o la ejecución de la operación ocasional». Además, el art. 25.1.a también dice «la operación» sin «ocasional» y se aplica a la diligencia debida, que es propia de la relación.
- *A favor de OP-1:* es la letra de la norma de rango superior, y el RD es su desarrollo reglamentario.

Una tercera lectura, «la más tardía de las dos fechas», da siempre el resultado de OP-2, porque la terminación no puede ser anterior a una operación de la relación. No se calcula por separado.

### 5.3. Resultado

Las dos lecturas se devuelven siempre ([D-5]). Divergen mientras `fecha_referencia` esté entre `fecha_ejecucion_operacion` + 10 años + 1 día y la fecha en que OP-2 exige eliminar el documento. Con el AMLR la contradicción desaparece: el art. 77.3 dice «operación ocasional» (§3.1).

---

## 6. Acceso restringido a partir del quinto año (solo la Ley)

### 6.1. El texto

Ley, art. 25.1, primer párrafo: «Transcurridos cinco años desde la terminación de la relación de negocios o la ejecución de la operación ocasional, la documentación conservada únicamente será accesible por los órganos de control interno del sujeto obligado, con inclusión de las unidades técnicas de prevención, y, en su caso, aquellos encargados de su defensa legal».

El AMLR no tiene ningún estado equivalente.

### 6.2. Qué significa operativamente

Lo que se sigue directamente del texto:

- **El documento se conserva íntegro.** No hay eliminación, anonimización ni reducción: la restricción se aplica a «la documentación conservada».
- **Solo tres grupos pueden acceder:**
  - los órganos de control interno (Ley, art. 26 ter; RD, art. 35.2: «un órgano de control interno responsable de la aplicación de los procedimientos de prevención»);
  - las unidades técnicas (RD, art. 35.3: «una unidad técnica para el tratamiento y análisis de la información»);
  - «en su caso», los encargados de la defensa legal.
- **Todos los demás pierden el acceso,** incluidos quienes gestionan la relación con el cliente.
- **Las autoridades siguen pudiendo pedir la documentación:**
  - Ley, art. 25.1, segundo párrafo: se conserva «para su uso en toda investigación o análisis [...] por parte del Servicio Ejecutivo de la Comisión o de cualquier otra autoridad legalmente competente»;
  - Ley, art. 25.2: el archivo «deberá asegurar la adecuada gestión y disponibilidad de la documentación, tanto a efectos de control interno, como de atención en tiempo y forma a los requerimientos de las autoridades»;
  - RD, art. 30: la documentación «podrá ser requerida por la Comisión, por sus órganos de apoyo o por cualquier otra autoridad».

  El texto no dice quién atiende esos requerimientos. Si solo los órganos de control interno tienen acceso, solo ellos podrían atenderlos, pero eso es una inferencia.

En el cálculo, `acceso_restringido` es un estado de conservación: el documento sigue debiendo conservarse. **[D-16]**: el cálculo no modela permisos. Solo informa de desde cuándo rige la restricción.

### 6.3. Lo que no dice ningún texto

1. **El representante ante el Servicio Ejecutivo.** La Ley, art. 26 ter.2, le da «acceso sin limitación alguna a cualquier información obrante en el sujeto obligado». El art. 25.1 no lo nombra entre quienes conservan el acceso. Tampoco se sabe si cuenta como «órgano de control interno». En las entidades sin órgano de control interno, sus funciones las desempeña el representante (RD, art. 35.2, segundo párrafo), así que allí parece incluido; en las demás, no consta.
2. **Las personas autorizadas** que designa el representante (RD, art. 35.1). No se mencionan.
3. **El experto externo** (Ley, art. 28: examen anual de las medidas de control interno). No se menciona. Su examen puede requerir documentación de más de cinco años.
4. **Los órganos de control interno del grupo.** RD, art. 36.2: «deberán tener acceso, sin restricción alguna, a cualquier información obrante en las filiales o sucursales». No se sabe si son «órganos de control interno del sujeto obligado» cuando el documento es de una filial.
5. **Los documentos que no dependen de una relación ni de una operación** (políticas, análisis de riesgo, actas, aplicación de fondos): la restricción cuenta desde un hecho que estos documentos no tienen. [D-8] no les aplica la restricción.
6. **Qué ocurre si el plazo de diez años empieza después de R** (lecturas EE-n, CI-n): [D-9].
7. **Qué medidas técnicas se exigen.** El art. 25.2 pide soportes que garanticen integridad y localización, pero no nada específico para la restricción.
8. **Si la restricción sobrevive al AMLR.** Solo T-1 y T-4 la mantienen (§4.2).
9. **Si una relación nueva con el mismo cliente reabre el acceso** a la documentación de la anterior (S-10).

---

## 7. Categorías sin plazo declarado en el AMLR

### 7.1. `comunicacion_control_interno`

El art. 77.1 enumera lo que se conserva: diligencia debida (a), evaluación y comunicaciones de sospecha (b), operaciones (c) e intercambio de información en asociaciones (d). No incluye las políticas, los análisis de riesgo, las actas del órgano de control ni las comunicaciones sistemáticas. El art. 9.2.a.vi pide políticas internas sobre «la conservación de registros y políticas en relación con el tratamiento de datos personales con arreglo al artículo 76 y 77», pero no fija ningún plazo. La búsqueda de «conserv» en la parte dispositiva del AMLR no encontró otro.

Las comunicaciones de sospecha no están en este caso. Se registran en esta categoría con `subtipo = "comunicacion_por_indicio"` (modelo §4.4) y siguen el art. 77.1.b. **[D-19]**: se les aplica el art. 77.1.b aunque la categoría sea la misma que la de los documentos sin regla, porque la letra b) las nombra expresamente.

### 7.2. `aplicacion_fondos`

Las fundaciones y asociaciones no figuran como tales entre las entidades obligadas del art. 3 del AMLR, y ningún artículo equivale a la Ley 39 ni al RD 42.3.d (S-8).

### 7.3. Resultado

**[D-17]** Con el régimen `amlr`, estas dos categorías dan `estado = sin_regla`, sin fechas. No es lo mismo que `supresion_exigida`: el AMLR no manda suprimir lo que no regula, porque el art. 77.3 solo habla de «la información indicada en los apartados 1 y 2». Tampoco es `en_conservacion`, porque el AMLR no obliga a conservarlo.

Las lecturas posibles se devuelven en `lecturas`:

| Lectura | Contenido | Resultado |
|---|---|---|
| SR-1 | No hay obligación del AMLR y lo decide la entidad. | `sin_regla` |
| SR-2 | Siguen vigentes el RD 29.2 o el RD 42.3.d como Derecho nacional (análoga a T-4). | Cálculo del §2 con sus lecturas CI-n o AF-n. |
| SR-3 | Se aplica por extensión el art. 77.3. | No calculable: el art. 77.3 cuenta desde un hecho inicial que estos documentos no suelen tener. Solo se calcula si el expediente tiene hecho inicial (H + 5 años). |

---

## 8. Ejemplos

Salvo que se indique otra cosa: `sujeto.naturaleza = "sujeto_obligado"`, sin prórrogas y sin procedimiento judicial pendiente. «Ley» y «AMLR» se refieren al cálculo puro de §2 y §3.

### Ejemplo 1. Diligencia debida: diez años frente a cinco

Relación de negocios terminada el **2020-03-15**. Documento: copia del DNI.

| | Ley | AMLR |
|---|---|---|
| Inicio | 2020-03-15 | 2020-03-15 |
| Acceso restringido desde | 2025-03-16 | — |
| Vencimiento V | 2030-03-15 | 2025-03-15 |
| Eliminación / supresión desde | 2030-03-16 | 2025-03-16 |

Con `fecha_referencia = 2028-01-01` (posterior a A = 2027-07-10), los regímenes de transición:

| Régimen | Estado | Por qué |
|---|---|---|
| T-1 | `acceso_restringido` | Ley: restringido desde 2025-03-16 hasta 2030-03-15. |
| T-2 | `supresion_exigida` | V = 2025-03-15 < A: suprimir desde 2027-07-10. |
| T-3 | `en_conservacion` | Vence el primero de 2030-03-15 y 2032-07-10, es decir, 2030-03-15. Sin restricción. |
| T-4 | `acceso_restringido` | Igual que T-1. |

Régimen `ley_10_2010`: `acceso_restringido`. Régimen `amlr`: `supresion_exigida`. La comparación de la transición señala que T-1 a T-4 no coinciden ([D-21]): el estado de este documento el 2028-01-01 depende de cómo se resuelva S-1.

### Ejemplo 2. Operación ocasional en año bisiesto, después de la transición

Operación ocasional ejecutada el **2028-02-29**. `fecha_referencia = 2033-03-01`.

| | Ley (y T-4) | AMLR (y T-1, T-2, T-3) |
|---|---|---|
| Vencimiento V | 2038-02-28 ([D-1]) | 2033-02-28 ([D-1]) |
| Acceso restringido desde | 2033-03-01 ([D-4]) | — |
| Estado el 2033-03-01 | `acceso_restringido` | `supresion_exigida` |

El mismo día en que la Ley empieza a restringir el acceso, el AMLR ya obliga a suprimir. Como H ≥ A, T-1, T-2 y T-3 coinciden; solo T-4 conserva el documento.

### Ejemplo 3. Negativa: solo existe en el AMLR

Negativa a entablar una relación el **2028-05-10**. Documento: registro de la decisión (art. 21.3). `fecha_referencia = 2030-01-01`.

- **AMLR:** inicio 2028-05-10; V = 2033-05-10. Estado: `en_conservacion`.
- **Ley:** la negativa no inicia el cómputo (S-2). Lecturas [D-18]: NG-1 desde 2028-05-10, V = 2038-05-10; NG-2 desde la fecha del registro, que aquí es la misma. Estado: `en_conservacion`.
- **Transición:** H ≥ A, así que T-1, T-2 y T-3 dan lo mismo que `amlr`: `en_conservacion`. T-4 toma el mayor plazo, el de la Ley: `en_conservacion` hasta 2038-05-10.
- Los seis regímenes coinciden el 2030-01-01. Divergen desde el 2033-05-11: `amlr`, T-1, T-2 y T-3 dan `supresion_exigida`; `ley_10_2010` y T-4, `en_conservacion`.

### Ejemplo 4. Operación dentro de una relación: contradicción entre la Ley y el RD

Relación de negocios del 2012-01-01 al **2026-12-31**. Operación ejecutada el **2014-04-01**.

| | OP-1 (Ley) | OP-2 (RD) | AMLR |
|---|---|---|---|
| Inicio | 2014-04-01 | 2026-12-31 | 2026-12-31 |
| Vencimiento V | 2024-04-01 | 2036-12-31 | 2031-12-31 |
| Acceso restringido desde | — (R = 2032-01-01 > V) | 2032-01-01 | — |
| Eliminación / supresión desde | 2024-04-02 | 2037-01-01 | 2032-01-01 |

- **`fecha_referencia = 2025-01-01`, régimen `ley_10_2010`** (antes de A, así que T-1 a T-4 dan lo mismo):
  - OP-1: `eliminacion_exigida`, con la relación todavía viva.
  - OP-2: `en_conservacion`.
  - `estado = indeterminado`.
- **`fecha_referencia = 2032-06-01`, régimen `ley_10_2010`:**
  - OP-1: `eliminacion_exigida`.
  - OP-2: `acceso_restringido`.
  - `estado = indeterminado`.
  - Régimen `amlr`: `supresion_exigida`.
  - Regímenes de transición (H = 2026-12-31 < A), cada uno con sus lecturas OP-1 y OP-2:
    - T-1 y T-4: OP-1 `eliminacion_exigida`, OP-2 `acceso_restringido`; `estado = indeterminado`.
    - T-2: `supresion_exigida` (el AMLR no distingue OP-1 y OP-2).
    - T-3: OP-1 `eliminacion_exigida` (vencida con la Ley antes de A); OP-2 `en_conservacion`, hasta el primero de 2036-12-31 y 2032-07-10, es decir, 2032-07-10; `estado = indeterminado`.

### Ejemplo 5. Examen especial: cinco lecturas con la Ley, una con el AMLR

Relación terminada el **2023-09-30**. Examen especial: apertura 2019-02-01, cierre 2019-04-15, decisión 2019-04-15, comunicación 2019-04-20. `fecha_referencia = 2029-04-18`. R = 2028-10-01.

| Lectura | Inicio | V | Estado el 2029-04-18 |
|---|---|---|---|
| EE-1 (apertura) | 2019-02-01 | 2029-02-01 | `eliminacion_exigida` |
| EE-2 (cierre) | 2019-04-15 | 2029-04-15 | `eliminacion_exigida` |
| EE-3 (decisión) | 2019-04-15 | 2029-04-15 | `eliminacion_exigida` |
| EE-4 (comunicación) | 2019-04-20 | 2029-04-20 | `acceso_restringido` |
| EE-5 (H) | 2023-09-30 | 2033-09-30 | `acceso_restringido` |
| **AMLR** | 2023-09-30 | 2028-09-30 | `supresion_exigida` |

- **Ley:** `estado = indeterminado`. Un retraso de cinco días entre el cierre y la comunicación basta para que las lecturas den estados distintos.
- **AMLR:** hay una sola regla y el estado es `supresion_exigida`.

### Ejemplo 6. Política interna: diez años frente a ninguna regla

Política aprobada el **2020-01-01** y sustituida el **2026-01-01**. `fecha_referencia = 2028-01-01`.

- **Ley:**
  - CI-1: V = 2030-01-01, `en_conservacion`.
  - CI-2: V = 2036-01-01, `en_conservacion`.
  - CI-3 no aplica.
  - `estado = en_conservacion` ([D-6]). Nunca pasa a `acceso_restringido` ([D-8]).
- **AMLR:** `estado = sin_regla`. Lecturas: SR-1 `sin_regla`; SR-2 `en_conservacion`; SR-3 no calculable.

### Ejemplo 7. Prórroga de la autoridad

Relación terminada el **2028-03-01**. La autoridad requiere el 2032-11-01 que se conserve hasta el 2040-01-01.

- **AMLR:**
  - V = 2033-03-01. El requerimiento es anterior a V, así que se aplica ([D-11]).
  - P = 2038-03-01: el 2040-01-01 se recorta al límite V + 5 años, con aviso ([D-12]).
- **Ley:**
  - V = 2038-03-01.
  - Restringido desde 2033-03-02.

| `fecha_referencia` | AMLR | Ley |
|---|---|---|
| 2033-03-01 | `en_conservacion` | `en_conservacion` |
| 2036-01-01 | `conservacion_prorrogada` | `acceso_restringido` |
| 2038-03-02 | `supresion_exigida` | `eliminacion_exigida` |

Ambos regímenes coinciden en la fecha final, pero con estados intermedios distintos. La prórroga es un requerimiento de la autoridad para este expediente; la restricción es general y automática.

### Ejemplo 8. Procedimiento judicial pendiente el 10 de julio de 2027

Relación terminada el **2021-01-15**. `procedimiento_judicial_pendiente_2027_07_10 = true`. `fecha_referencia = 2031-06-01`.

- **AMLR:**
  - V = 2026-01-15, anterior a A.
  - Sin el art. 77.4, el estado sería `supresion_exigida`.
  - Con el art. 77.4: `conservacion_facultativa_77_4` hasta 2032-07-10 con PA-1 y hasta 2037-07-10 con PA-2 ([D-13]). Las dos dan el mismo estado el 2031-06-01.
- **Ley:**
  - V = 2031-01-15; restringido desde 2026-01-16.
  - Estado: `eliminacion_exigida` desde 2031-01-16. La Ley y el RD no tienen excepción por procedimiento judicial: la búsqueda de «procedimiento judicial» solo encontró el RD, art. 45, sobre medios de pago intervenidos.

Aquí la Ley obliga a eliminar y el AMLR permite conservar.

---

## 9. Índice de decisiones

| Id | Decisión | Sección |
|---|---|---|
| D-1 | «N años desde F» vence el mismo día y mes N años después; 29 de febrero → 28 de febrero. | §1.3 |
| D-2 | El día de vencimiento está dentro del plazo. | §1.3 |
| D-3 | El día de inicio está dentro del plazo. | §1.3 |
| D-4 | «Transcurridos cinco años» se cumple el día siguiente al quinto aniversario. | §1.3 |
| D-5 | El resultado tiene una entrada por régimen, cada una con estado, lecturas y avisos. | §1.4 |
| D-6 | Dentro de un régimen, si todas las lecturas coinciden en el estado, no es `indeterminado`. | §1.4 |
| D-7 | EE-4 usa la fecha de decisión si no hubo comunicación. | §2.1 |
| D-8 | Sin hecho inicial no hay acceso restringido. | §2.2, §6.3 |
| D-9 | La restricción también cubre documentación cuyo plazo empieza después de R. | §2.2 |
| D-10 | `supresion_exigida` se refiere solo a datos personales; lo demás va a avisos. | §3.2 |
| D-11 | Una prórroga requerida después del vencimiento no se aplica. | §3.2 |
| D-12 | Las prórrogas se acumulan con un límite total de cinco años. | §3.2 |
| D-13 | El art. 77.4 da conservación facultativa; el período adicional se trata con las lecturas PA-1 y PA-2. | §3.2 |
| D-14 | El régimen es un parámetro del cálculo; se calculan siempre los seis y ninguno es principal. | §1.1 |
| D-15 | *Retirada.* Era: el campo `regimen` de la entrada fijaba el estado principal. Sustituida por D-14. | §1.1 |
| D-16 | El cálculo no modela permisos de acceso. | §6.2 |
| D-17 | Las categorías sin regla en el AMLR dan `sin_regla`, con lecturas SR-1 a SR-3. | §7.3 |
| D-18 | Con la Ley, un expediente con negativa da las lecturas NG-1 (fecha de la negativa) y NG-2 (fecha del documento), sin acceso restringido. | §2.1 |
| D-19 | Una comunicación por indicio sigue el AMLR 77.1.b, aunque esté en `comunicacion_control_interno`. | §3.1, §7.1 |
| D-20 | El AMLR se calcula también antes de A, con aviso. | §4.3 |
| D-21 | Si T-1 a T-4 no coinciden, el resultado lo señala expresamente. | §1.4 |
