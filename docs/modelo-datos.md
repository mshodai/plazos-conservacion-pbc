# Modelo de datos de entrada

Este documento define el JSON que recibe el cálculo del estado de conservación de un expediente de prevención del blanqueo de capitales en una fecha dada. Solo describe la entrada. Cómo se calcula y qué devuelve el cálculo está en [`especificacion-calculo.md`](especificacion-calculo.md).

Siglas y fuentes (detalle y huellas en [`fuentes/FUENTES.md`](fuentes/FUENTES.md)):

- **Ley**: Ley 10/2010, texto consolidado con última modificación de 21 de marzo de 2026.
- **RD**: Reglamento aprobado por el Real Decreto 304/2014, texto consolidado con última modificación de 24 de abril de 2024.
- **AMLR**: Reglamento (UE) 2024/1624, texto publicado en el DO L de 19.6.2024.

Convenciones:

- Las citas van entre comillas «» y son literales.
- **[Decisión propia]** marca lo que no sale de los textos, sino del diseño de este proyecto. Las decisiones de validación están numeradas (V-1 a V-17) en el §8.2.
- Los casos que la norma no resuelve se recogen en la sección [Casos que la norma no resuelve](#casos-que-la-norma-no-resuelve) (S-1 a S-15). El modelo no los decide.

---

## 0. Principios

1. **La entrada recoge hechos, no conclusiones.** **[Decisión propia]** El JSON dice qué documentos hay, cuándo terminó la relación, cuándo se abrió un examen especial o si la autoridad ha requerido una prórroga. No dice qué plazo aplica, desde cuándo cuenta ni en qué estado está un documento: eso lo deduce el cálculo, y depende del régimen y de la lectura.
2. **El régimen no forma parte de la entrada.** **[Decisión propia]** El régimen es un parámetro del cálculo. El mismo JSON se calcula con la Ley, con el AMLR y con cada lectura de la transición entre ambos (especificación, §4). Si la entrada incluyera un campo `regimen`, quien la rellena estaría eligiendo sin saberlo cómo se resuelve la transición del 10 de julio de 2027 (S-1), que ningún texto resuelve.
3. **La validación no depende del régimen.** **[Decisión propia]** Un hecho que un régimen no usa, como una negativa bajo la Ley o una prórroga de la autoridad bajo la Ley, no es un error de entrada. Qué hace cada régimen con ese hecho lo dice la especificación.

---

## 1. Ejemplo completo

```json
{
  "version_modelo": 2,
  "fecha_referencia": "2031-03-01",
  "sujeto": {
    "naturaleza": "sujeto_obligado",
    "actividad": "otra"
  },
  "expediente": {
    "id": "EXP-2019-0042",
    "hecho_inicial": {
      "tipo": "relacion_de_negocios",
      "fecha_inicio": "2019-05-10",
      "fecha_terminacion": "2024-11-30",
      "fecha_ejecucion": null,
      "fecha_negativa": null,
      "objeto_negativa": null
    },
    "documentos": [
      {
        "id": "DOC-1",
        "categoria": "diligencia_debida",
        "descripcion": "Copia del DNI del cliente",
        "fecha_documento": "2019-05-10"
      },
      {
        "id": "DOC-2",
        "categoria": "operaciones",
        "descripcion": "Orden de transferencia",
        "fecha_documento": "2021-02-03",
        "fecha_ejecucion_operacion": "2021-02-03"
      },
      {
        "id": "DOC-3",
        "categoria": "examen_especial",
        "descripcion": "Expediente de examen especial 2023/17",
        "fecha_documento": "2023-06-01",
        "fecha_apertura": "2023-06-01",
        "fecha_cierre": "2023-07-15",
        "fecha_decision_comunicacion": "2023-07-15",
        "fecha_comunicacion": "2023-07-17"
      },
      {
        "id": "DOC-4",
        "categoria": "comunicacion_control_interno",
        "descripcion": "Comunicación por indicio al Servicio Ejecutivo",
        "subtipo": "comunicacion_por_indicio",
        "examen_especial_id": "DOC-3",
        "fecha_documento": "2023-07-17",
        "fecha_fin_vigencia": null
      }
    ],
    "prorrogas_autoridad": [],
    "procedimiento_judicial_pendiente_2027_07_10": false
  }
}
```

Las fundaciones y asociaciones usan además la categoría `aplicacion_fondos` (ver §4.5).

---

## 2. Campos de primer nivel

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `version_modelo` | entero | sí | Versión de este esquema. Es `2`: la versión 1 tenía el campo `regimen` (ver §6). **[Decisión propia]** |
| `fecha_referencia` | fecha ISO 8601 (`AAAA-MM-DD`) | sí | Fecha para la que se calcula el estado. Ver §5. |
| `sujeto` | objeto | sí | Quién conserva. Ver §2.1. |
| `expediente` | objeto | sí | Hecho que inicia el cómputo, documentos y circunstancias que pueden alterar el plazo. Ver §3 y §4. |

No hay campo de régimen (§0, principio 2). Un JSON con `regimen` es un error de validación (`ERR-01`), para que una entrada de la versión 1 no se calcule como si ese campo sirviera de algo. **[Decisión propia]** Lo mismo vale para cualquier otro campo que el modelo no defina ([V-2](#82-decisiones-de-validación)).

Todas las fechas son de día, sin hora ni zona horaria. **[Decisión propia]**: ninguna de las fuentes fija los plazos por horas.

### 2.1. `sujeto`

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `naturaleza` | `"sujeto_obligado"` \| `"fundacion"` \| `"asociacion"` | sí | Determina si se admite la categoría `aplicacion_fondos` (§4.5). |
| `actividad` | `"agente_de_futbol"` \| `"club_de_futbol_profesional"` \| `"otra"` | sí | Hecho del que depende la fecha de aplicación del AMLR (§6). Sustituye al booleano `amlr_art3_3_n_o` de la versión 1, que era una conclusión: qué letra del art. 3 se aplica. **[Decisión propia]** |

---

## 3. Fechas que pueden iniciar el cómputo: `expediente.hecho_inicial`

Cada expediente tiene **un único** hecho inicial. **[Decisión propia]**: si el mismo cliente tiene varias relaciones de negocio o varias operaciones ocasionales, cada una es un expediente distinto.

| Campo | Tipo | Descripción |
|---|---|---|
| `tipo` | `"relacion_de_negocios"` \| `"operacion_ocasional"` \| `"negativa"` \| `null` | Qué hecho es. `null` solo en el caso de §4.5. |
| `fecha_inicio` | fecha \| `null` | Inicio de la relación de negocios. **No inicia ningún cómputo** en ninguno de los dos regímenes. Se guarda como dato de control (no puede ser posterior a `fecha_terminacion`). **[Decisión propia]** |
| `fecha_terminacion` | fecha \| `null` | Terminación de la relación de negocios. `null` mientras la relación siga viva. |
| `fecha_ejecucion` | fecha \| `null` | Ejecución de la operación ocasional. |
| `fecha_negativa` | fecha \| `null` | Fecha de la negativa a entablar la relación o a realizar la operación ocasional. |
| `objeto_negativa` | `"relacion_de_negocios"` \| `"operacion_ocasional"` \| `null` | A qué se negó la entidad. |

Solo se rellena la fecha que corresponde al `tipo`; las otras dos van a `null`.

### 3.1. Qué fechas usa cada régimen

| Hecho | Ley 10/2010 y RD 304/2014 | AMLR |
|---|---|---|
| Terminación de la relación de negocios | Sí | Sí |
| Ejecución de la operación ocasional | Sí | Sí |
| Negativa a entablar la relación o a ejecutar la operación | **No** | **Sí** |

**Ley 10/2010.** Art. 25.1: «Transcurridos cinco años desde la terminación de la relación de negocios o la ejecución de la operación ocasional». Letra a): «durante un periodo de diez años desde la terminación de la relación de negocios o la ejecución de la operación». Letra b): «durante un periodo de diez años desde la ejecución de la operación o la terminación de la relación de negocios».

**RD 304/2014.** Arts. 28.1 y 29.1: «durante un periodo de diez años desde la terminación de la relación de negocio o la ejecución de la operación ocasional».

**AMLR.** Art. 77.3: «se conservará durante un período de cinco años, a partir de la fecha de extinción de la relación de negocios o de la fecha en la que se ejecute la operación ocasional, o de la fecha de la negativa a entablar una relación de negocios o llevar a cabo una operación ocasional».

**Dato que solo usa el AMLR: la fecha de la negativa.** La Ley reconoce que la negativa existe. Art. 7.3: «La negativa a establecer relaciones de negocio o a ejecutar operaciones o la terminación de la relación de negocios por imposibilidad de aplicar las medidas de diligencia debida [...] no conllevará [...] ningún tipo de responsabilidad». Pero ni el art. 25 de la Ley ni los arts. 28 y 29 del RD la usan como inicio del plazo. El AMLR, además, obliga a documentarla. Art. 21.3, párrafo segundo: la obligación de mantener un registro «se aplicará también a las situaciones en que las entidades obligadas rechacen establecer una relación de negocios».

Una negativa es un hecho y se admite siempre (§0, principio 3). Qué plazo tiene la documentación de una negativa bajo la Ley es el caso [S-2](#s-2).

---

## 4. Documentos: `expediente.documentos[]`

Campos comunes a todas las categorías:

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `id` | cadena | sí | Identificador único dentro del expediente. |
| `categoria` | ver §4.1–§4.5 | sí | Qué documenta el documento. |
| `descripcion` | cadena | no | Texto libre. |
| `fecha_documento` | fecha | sí | Fecha en que se obtuvo o se generó el documento. **[Decisión propia]**: se pide siempre. Para qué sirve en cada régimen lo dice la especificación. |

**La categoría describe la naturaleza del documento, no la regla que se le aplica.** **[Decisión propia]** Una misma categoría puede caer bajo artículos distintos según el régimen. Por ejemplo, una comunicación por indicio va al RD 29.2 con la Ley y al AMLR 77.1.b con el AMLR. Esa correspondencia la hace el cálculo. Las citas de cada categoría explican por qué existe y qué datos pide, no cómo se calcula.

Cada categoría añade sus propios campos. Todos son obligatorios con independencia del régimen que los use (§0, principio 3).

### Qué regla cubre cada categoría

| Categoría | Ley 10/2010 / RD 304/2014 | AMLR |
|---|---|---|
| `diligencia_debida` | Ley 25.1.a; RD 28.1 | 77.1.a |
| `operaciones` | Ley 25.1.b; RD 29.1 (S-3) | 77.1.c |
| `examen_especial` | RD 25.4, sin inicio del cómputo declarado (S-4) | 77.1.b |
| `comunicacion_control_interno` | RD 29.2, sin inicio del cómputo declarado (S-5) | Solo las comunicaciones de sospecha (77.1.b); el resto **sin regla** (S-6) |
| `aplicacion_fondos` | RD 42.3.d, sin inicio del cómputo declarado (S-7) | **Sin regla** (S-8) |

Reglas que afectan a todas las categorías:

- **Ley, restricción de acceso.** Art. 25.1: «Transcurridos cinco años desde la terminación de la relación de negocios o la ejecución de la operación ocasional, la documentación conservada únicamente será accesible por los órganos de control interno del sujeto obligado, con inclusión de las unidades técnicas de prevención, y, en su caso, aquellos encargados de su defensa legal». El AMLR no tiene nada equivalente.
- **Ley, eliminación.** Art. 25.1: «conservarán durante un período de diez años la documentación en que se formalice el cumplimiento de las obligaciones establecidas en la presente ley, procediendo tras el mismo a su eliminación».
- **AMLR, supresión.** Art. 77.3: «Sin perjuicio de los períodos de conservación de los datos recogidos a efectos de otros actos jurídicos de la Unión o del Derecho nacional que cumplan el Reglamento (UE) 2016/679, las entidades obligadas suprimirán los datos personales al expirar el período de cinco años». Ver [S-9](#s-9).

### 4.1. `diligencia_debida`

Documentos obtenidos o generados al aplicar las medidas de diligencia debida.

**Ley 10/2010 / RD.**
- Ley, art. 25.1.a: «Copia de los documentos exigibles en aplicación de las medidas de diligencia debida, durante un periodo de diez años desde la terminación de la relación de negocios o la ejecución de la operación».
- RD, art. 28.1: «toda la documentación obtenida o generada en aplicación de las medidas de diligencia debida, con inclusión, en particular, de las copias de los documentos fehacientes de identificación, las declaraciones del cliente, la documentación e información aportada por el cliente u obtenida de fuentes fiables independientes, la documentación contractual y los resultados de cualquier análisis efectuado, durante un periodo de diez años desde la terminación de la relación de negocio o la ejecución de la operación ocasional».

**AMLR.**
- Art. 77.1.a: «una copia de los documentos y la información obtenidos durante la realización del procedimiento de diligencia debida con respecto al cliente conforme al capítulo III, incluida la información obtenida a través de medios de identificación electrónica».
- Art. 21.3: «un registro de las medidas adoptadas para cumplir el requisito de aplicar las medidas de diligencia debida con respecto al cliente, incluidos registros de las decisiones adoptadas y de los documentos justificativos y las justificaciones pertinentes». Este registro se aplica también cuando la entidad rechaza la relación. **[Decisión propia]**: estos registros van en esta categoría.

**Campos propios:** ninguno.

### 4.2. `operaciones`

Documentos o registros que acreditan las operaciones, sus intervinientes y las relaciones de negocio.

**Ley 10/2010 / RD.**
- Ley, art. 25.1.b: «Original o copia con fuerza probatoria de los documentos o registros que acrediten adecuadamente las operaciones, los intervinientes en las mismas y las relaciones de negocio, durante un periodo de diez años desde la ejecución de la operación o la terminación de la relación de negocios».
- RD, art. 29.1: «conservarán los documentos y mantendrán registros adecuados de todas las relaciones de negocio y operaciones, nacionales e internacionales, durante un periodo de diez años desde la terminación de la relación de negocio o la ejecución de la operación ocasional».

**AMLR.** Art. 77.1.c: «los justificantes y registros de operaciones, consistentes en documentos originales o en copias que tengan fuerza probatoria similar en procedimientos judiciales en virtud del Derecho nacional aplicable, que sean necesarios para identificar las operaciones».

**Campos propios:**

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `fecha_ejecucion_operacion` | fecha | sí, si `hecho_inicial.tipo = "relacion_de_negocios"` | Fecha de ejecución de la operación concreta dentro de la relación. Hace falta para la lectura literal del art. 25.1.b de la Ley ([S-3](#s-3)). En una operación ocasional es opcional y, si se indica, coincide con `hecho_inicial.fecha_ejecucion` (V-14). `null` equivale a omitirla (V-8). |

### 4.3. `examen_especial`

Expedientes de examen especial (Ley, art. 17; RD, art. 25) y, en el AMLR, registros de la evaluación de operaciones del art. 69.2.

**Ley 10/2010 / RD.**
- RD, art. 25.4: «Los sujetos obligados conservarán los expedientes de examen especial durante el plazo de diez años». No dice desde cuándo.
- RD, art. 25.3: el registro de expedientes recoge «sus fechas de apertura y cierre [...] la decisión sobre su comunicación o no al Servicio Ejecutivo de la Comisión y su fecha, así como la fecha en que, en su caso, se realizó la comunicación».

**AMLR.** Art. 77.1.b: «un registro de la evaluación realizada de conformidad con el artículo 69, apartado 2, incluida la información y las circunstancias consideradas y los resultados de dicha evaluación, con independencia de que dicha evaluación dé lugar o no a una comunicación de operaciones sospechosas a la UIF, y una copia de las comunicaciones, si las hay, de sospechas de operaciones».

**Datos que usa la Ley/RD y no el AMLR:** las cuatro fechas del registro del art. 25.3 RD. El AMLR no exige un registro con esas fechas ni las usa para el plazo.

**Campos propios:**

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `fecha_apertura` | fecha | sí | RD 25.3. |
| `fecha_cierre` | fecha \| `null` | sí | RD 25.3. `null` si el examen sigue abierto. |
| `fecha_decision_comunicacion` | fecha \| `null` | sí | RD 25.3. `null` si aún no se ha decidido. |
| `fecha_comunicacion` | fecha \| `null` | sí | RD 25.3: «en su caso». `null` si no se ha comunicado. |

Estas fechas se piden aunque el AMLR no las use (§0, principio 3). En la versión 1 solo eran obligatorias con la Ley. Cuál de ellas inicia el plazo con la Ley es el caso [S-4](#s-4).

### 4.4. `comunicacion_control_interno`

Documentos que formalizan el cumplimiento de las obligaciones de comunicación y de control interno.

**Ley 10/2010 / RD.**
- RD, art. 29.2: «Los sujetos obligados conservarán durante un periodo de diez años los documentos en que se formalice el cumplimiento de sus obligaciones de comunicación y de control interno». No dice desde cuándo.
- Ley, art. 25.1, primer párrafo: la regla general de diez años para «la documentación en que se formalice el cumplimiento de las obligaciones establecidas en la presente ley». Tampoco dice desde cuándo.

**AMLR.** El art. 77.1 enumera cuatro tipos de documentos: diligencia debida, evaluación y comunicaciones de sospecha, operaciones e intercambio de información en asociaciones. Las comunicaciones de sospecha están en la letra b): «una copia de las comunicaciones, si las hay, de sospechas de operaciones». Los documentos de control interno no están. Ver [S-6](#s-6).

**Campos propios:**

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `subtipo` | `"comunicacion_por_indicio"` \| `"comunicacion_sistematica"` \| `"politicas_procedimientos"` \| `"analisis_riesgo"` \| `"organo_control_interno"` \| `"otro"` | sí | **[Decisión propia]**. Los valores se basan en Ley arts. 18 y 26 y en RD arts. 26, 27, 31, 32 y 35. Sirven para distinguir las comunicaciones de sospecha (que el AMLR sí regula) del resto, y las políticas que se sustituyen ([S-5](#s-5)). |
| `examen_especial_id` | cadena \| `null` | no | Solo con `comunicacion_por_indicio`: `id` del documento `examen_especial` del que resulta la comunicación. Si se indica, debe existir en el expediente. **[Decisión propia]** |
| `fecha_fin_vigencia` | fecha \| `null` | sí si `subtipo` es `politicas_procedimientos` o `analisis_riesgo` | Fecha en que el documento se sustituyó o dejó de aplicarse. `null` si sigue vigente. |

En la versión 1, con el AMLR, una comunicación de sospecha tenía que registrarse en `examen_especial`, y registrarla aquí era un error. Esa regla hacía depender la entrada del régimen. **[Decisión propia]**: la comunicación va siempre aquí, con `subtipo = "comunicacion_por_indicio"`, y el cálculo le aplica el art. 77.1.b cuando calcula el AMLR.

### 4.5. `aplicacion_fondos`

Documentos o registros que acreditan cómo han aplicado los fondos las fundaciones y asociaciones. Solo es válida si `sujeto.naturaleza` es `"fundacion"` o `"asociacion"`. **[Decisión propia]**

**Ley 10/2010 / RD.**
- RD, art. 42.3.d: «Conservar durante un plazo de diez años los documentos o registros que acrediten la aplicación de los fondos en los diferentes proyectos». No dice desde cuándo.
- Una obligación distinta pero cercana está en el art. 39 de la Ley: «todas las fundaciones conservarán durante el plazo establecido en el artículo 25 registros con la identificación de todas las personas que aporten o reciban a título gratuito fondos o recursos de la fundación, en los términos de los artículos 3 y 4 de esta Ley». El párrafo tercero lo extiende a las asociaciones. Estos registros de identificación **no** van en `aplicacion_fondos`, sino en `diligencia_debida`. **[Decisión propia]**: se hace así porque el art. 39 remite a los arts. 3 y 4, que regulan la identificación. Qué hecho inicia su plazo es el caso [S-7](#s-7).

**AMLR.** No hay regla. Ver [S-8](#s-8).

**Campos propios:**

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `proyecto` | cadena | sí | Identificador del proyecto al que se aplican los fondos. |
| `fecha_aplicacion` | fecha | sí | Fecha en que se aplicaron los fondos. |
| `fecha_fin_proyecto` | fecha \| `null` | sí | Cierre del proyecto. `null` si sigue en curso. |

**[Decisión propia]**: se piden las dos fechas porque cualquiera de ellas podría iniciar el cómputo ([S-7](#s-7)).

**[Decisión propia]**: el expediente de una fundación o asociación que solo contenga documentos `aplicacion_fondos` usa `hecho_inicial` con todos los campos a `null` y `tipo = null`. Ninguna otra categoría admite `tipo = null`.

---

## 5. Fecha de referencia

`fecha_referencia` es la fecha para la que se calcula el estado de cada documento. La lista de estados está en la especificación.

- Es obligatoria. **[Decisión propia]**: no se toma la fecha del sistema por defecto, para que el mismo JSON dé siempre el mismo resultado.
- Puede ser pasada o futura, y anterior o posterior al 10 de julio de 2027. **[Decisión propia]**: la fecha no restringe con qué régimen se puede calcular. Qué hace el cálculo con el AMLR antes de que sea aplicable lo dice la especificación.
- Los hechos del expediente no pueden ser posteriores a ella. Si lo son, es un error de validación. **[Decisión propia]**: los hechos posteriores a la fecha de referencia no se conocían en esa fecha. Se exceptúa `prorrogas_autoridad[].fecha_fin`, que es el final previsto de la prórroga y no un hecho ocurrido. Ver también [S-10](#s-10).

---

## 6. Hechos relevantes para el régimen y la transición

La versión 1 tenía un campo `regimen` obligatorio. Se ha quitado porque decidía, sin que quien rellena la entrada lo supiera, cómo se resuelve la transición del 10 de julio de 2027. Con `ley_10_2010` se aplicaba la Ley entera aunque la fecha fuera posterior; con `amlr`, el AMLR contando desde el hecho original. Otras lecturas posibles no podían salir nunca como resultado ([S-1](#s-1)). Ahora el régimen es un parámetro del cálculo (§0).

Lo que dicen los textos sobre la aplicación en el tiempo:

- AMLR, art. 90: «Será aplicable a partir del 10 de julio de 2027, excepto para las entidades obligadas a que se refiere el artículo 3, punto 3, letras n) a o), para quienes será aplicable desde el 10 de julio de 2029». Letra n): «los agentes de fútbol». Letra o): «los clubes de fútbol profesional» en relación con determinadas operaciones.
- AMLR, art. 77.4: «Cuando, a 10 de julio de 2027, haya procedimientos judiciales relacionados con la prevención, la detección, la investigación o el enjuiciamiento de presuntas actividades de blanqueo de capitales o financiación del terrorismo pendientes en un Estado miembro, y obren en poder de una entidad obligada información o documentos relacionados con esos procedimientos pendientes, la entidad obligada podrá conservar esa información o esos documentos durante un período de cinco años a partir del 10 de julio de 2027». El segundo párrafo permite a los Estados miembros un período adicional de cinco años.

Los hechos que la entrada recoge para ello:

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `sujeto.actividad` | ver §2.1 | sí | De qué fecha de aplicación del AMLR se trata (art. 90). |
| `expediente.prorrogas_autoridad[]` | lista de `{ "autoridad": cadena, "fecha_requerimiento": fecha, "fecha_fin": fecha }` | sí (puede estar vacía) | AMLR, art. 77.3, párrafo segundo: «Las autoridades competentes podrán exigir, según cada caso concreto, que se siga conservando la información [...]. La prórroga máxima del período de conservación no excederá de un período de cinco años». Es un hecho: se admite aunque la Ley no tenga una prórroga equivalente. |
| `expediente.procedimiento_judicial_pendiente_2027_07_10` | booleano | sí | AMLR, art. 77.4, primer párrafo: si había un procedimiento judicial pendiente relacionado con el expediente en esa fecha. |

**[Decisión propia]**: la prórroga y el procedimiento judicial se aplican al expediente entero y no a cada documento. El art. 77.3 habla de «la información a que se refiere el párrafo primero» sin distinguir.

**Quitado respecto a la versión 1:** `prorroga_nacional_77_4`. Decía si España permite o exige el período adicional del art. 77.4, segundo párrafo. No es un hecho del expediente sino el contenido de una norma nacional que no está en las fuentes ([S-11](#s-11)). El cálculo trata las dos posibilidades como lecturas.

---

## 7. Qué régimen usa cada dato

Todos los datos se validan igual con independencia del régimen (§0). Esta tabla solo dice quién los usa.

| Dato | Ley 10/2010 / RD | AMLR | Base |
|---|---|---|---|
| `hecho_inicial.fecha_terminacion` | sí | sí | Ley 25.1; RD 28.1 y 29.1; AMLR 77.3 |
| `hecho_inicial.fecha_ejecucion` | sí | sí | Ídem |
| `hecho_inicial.fecha_negativa` | **no** como inicio del plazo (S-2) | **sí** | AMLR 77.3 y 21.3 |
| `operaciones.fecha_ejecucion_operacion` | sí (lectura literal de 25.1.b) | no | Ley 25.1.b; [S-3](#s-3) |
| Fechas del registro de examen especial | **sí** | no | RD 25.3 y 25.4 |
| `comunicacion_control_interno`, salvo `comunicacion_por_indicio` | **sí** | sin regla | RD 29.2; [S-6](#s-6) |
| `comunicacion_control_interno` con `comunicacion_por_indicio` | sí | sí | RD 29.2; AMLR 77.1.b |
| `aplicacion_fondos.*` | **sí** | sin regla | RD 42.3.d |
| `prorrogas_autoridad` | no | **sí** | AMLR 77.3 |
| `procedimiento_judicial_pendiente_2027_07_10` | no | **sí** | AMLR 77.4 |
| `sujeto.actividad` | no | **sí** | AMLR 90 |

---

## 8. Validación

La validación no depende del régimen (§0, principio 3). Se recogen todos los errores de la entrada, no solo el primero, y si hay alguno la entrada se rechaza entera.

### 8.1. Errores

| Código | Error | Sección |
|---|---|---|
| `ERR-01` | Estructura o tipo: el JSON está mal formado o repite una clave en un mismo objeto; falta un campo obligatorio; un valor no es del tipo indicado; `version_modelo` no es `2`; hay un campo `regimen` o cualquier otro campo que el modelo no define. | §2, [V-2](#82-decisiones-de-validación), [V-3](#82-decisiones-de-validación) |
| `ERR-02` | `hecho_inicial` no tiene la fecha que corresponde a su `tipo`, o tiene rellenos campos de otro tipo de hecho. | §3, V-5 a V-7 |
| `ERR-03` | `tipo = "negativa"` sin `objeto_negativa`. | §3 |
| `ERR-04` | `fecha_inicio` posterior a `fecha_terminacion`. | §3 |
| `ERR-05` | `tipo = null` en un expediente con documentos que no son `aplicacion_fondos`. | §4.5 |
| `ERR-06` | `aplicacion_fondos` con `sujeto.naturaleza = "sujeto_obligado"`. | §4.5 |
| `ERR-07` | `id` de documento repetido, o `examen_especial_id` que no existe, no es un `examen_especial` o está en un subtipo que no es `comunicacion_por_indicio`. | §4, §4.4, V-10 |
| `ERR-08` | `fecha_ejecucion_operacion` ausente o `null` en una operación de una relación de negocios, o distinta de `hecho_inicial.fecha_ejecucion` en una operación ocasional. | §4.2, V-8, V-14 |
| `ERR-09` | Un hecho posterior a `fecha_referencia`. Un error por cada fecha. | §5 |

### 8.2. Decisiones de validación

Todas son **[Decisión propia]**. Cada una cambia el resultado de la validación: si una entrada se acepta o se rechaza, o con qué código.

| Id | Decisión | Alternativa descartada | Motivo |
|---|---|---|---|
| V-1 | Códigos `ERR-01` a `ERR-09` (§8.1): n es el número que tenía cada error en la lista de la versión anterior de este documento. Son estables y no se reutilizan. | Códigos descriptivos (`ERR-TIPO-NULO`…). | Números cortos y estables, como en el proyecto `calculo-titularidad-real`. |
| V-2 | Un campo desconocido es `ERR-01`, en cualquier objeto. También cuenta como desconocido el campo propio de otra categoría (por ejemplo, `fecha_apertura` en un documento de `diligencia_debida`). | Ignorarlo. | Un campo que el cálculo no lee pasaría como si sirviera de algo: una errata en un campo opcional o un campo de la versión 1 (`regimen`, `amlr_art3_3_n_o`, `prorroga_nacional_77_4`). |
| V-3 | Son `ERR-01`: un JSON mal formado, una clave repetida en un mismo objeto y un `version_modelo` distinto de `2`. | Códigos propios; con la clave repetida, quedarse con el último valor, como hace un lector JSON habitual. | Son errores de estructura. Una clave repetida suele ser un error de edición, y quedarse con un valor lo taparía. |
| V-4 | Los seis campos de `hecho_inicial` son obligatorios, con `null` cuando no aplican. | Poder omitir los que no aplican. | Un campo olvidado no se distingue de un `null` intencionado. |
| V-5 | Con `tipo = null`, cualquier campo de `hecho_inicial` con valor es `ERR-02`. | `ERR-01`, o ignorarlo. | El §4.5 exige «todos los campos a `null`», y `ERR-02` es el error de los datos que no corresponden al tipo. |
| V-6 | `fecha_inicio` con valor en un hecho que no es `relacion_de_negocios` es `ERR-02`. | Admitirla e ignorarla. | El §3 la define como «Inicio de la relación de negocios»: en otro tipo es una fecha de otro hecho. |
| V-7 | `objeto_negativa` con valor en un hecho que no es `negativa` es `ERR-02`. | Admitirlo e ignorarlo. | Igual que V-6. |
| V-8 | `fecha_ejecucion_operacion` a `null` equivale a omitirla: dentro de una relación de negocios los dos casos son `ERR-08`; en otro caso se admiten. | Tratar `null` como `ERR-01`, porque el tipo es «fecha». | Los dos significan que no hay dato. |
| V-9 | `descripcion` a `null` equivale a omitirla. | `ERR-01`. | Es texto libre que el cálculo no usa. |
| V-10 | `examen_especial_id` con valor en un subtipo distinto de `comunicacion_por_indicio` es `ERR-07`. | `ERR-01`, o ignorarlo. | El §4.4 lo admite «Solo con `comunicacion_por_indicio`», y `ERR-07` es el error de ese campo. |
| V-11 | Se admiten textos vacíos, también en los `id`. | Rechazarlos. | Ningún texto interviene en el cálculo salvo como identificador, y un `id` vacío sigue pudiendo ser único. |
| V-12 | Se admite una lista de documentos vacía, también con `tipo = null`. | Rechazarla. | No hay nada que calcular, pero la entrada no es incoherente; con `tipo = null`, la condición del §4.5 se cumple. |
| V-13 | Se admite `fecha_fin_vigencia` con valor en subtipos que no la exigen. | Rechazarla. | Es un hecho que el cálculo no usa en esos subtipos. |
| V-14 | En una operación ocasional, `fecha_ejecucion_operacion` puede omitirse, pero si tiene valor debe coincidir con `hecho_inicial.fecha_ejecucion`; si no, es `ERR-08`. | Admitir la diferencia sin comprobarla. | Es la misma operación. La especificación (§2.1) da por hecho que las dos fechas coinciden y por eso OP-1 y OP-2 dan lo mismo; con fechas distintas, OP-1 daría un resultado que depende de un dato contradictorio. |
| V-15 | No se comprueba que `fecha_fin` de una prórroga sea posterior a `fecha_requerimiento`. | Rechazar la prórroga. | Qué prórroga vale y hasta cuándo lo decide el cálculo (especificación, D-11 y D-12). |
| V-16 | En las fechas del examen especial solo se valida el formato, no el orden entre ellas (apertura ≤ cierre ≤ decisión ≤ comunicación). | Exigir ese orden. | Un orden anómalo se puede deber a cómo registra la entidad sus expedientes, y el cálculo no depende de él. |
| V-17 | Un dato presente pero mal formado solo da `ERR-01`: las comprobaciones que dependen de él no se hacen. Si un documento no tiene una `categoria` válida, solo se comprueban sus campos comunes. | Hacer todas las comprobaciones y dar también los errores derivados. | Un error derivado desaparece al corregir el primero y oculta cuál es el dato que falla. |

---

## Casos que la norma no resuelve

Cada caso indica qué deja abierto el texto y qué datos recoge el modelo para no cerrar la cuestión. Ninguno se resuelve aquí; la especificación dice cómo se señala cada uno en la salida.

<a id="s-1"></a>
**S-1. Paso de la Ley al AMLR.** El AMLR se aplica desde el 10 de julio de 2027 (art. 90) y su único régimen transitorio sobre conservación es el de los procedimientos judiciales pendientes (art. 77.4). No hay regla para los expedientes cuyo plazo de diez años empezó bajo la Ley y sigue en curso en esa fecha, ni para los que ya habrían superado los cinco años del AMLR. La Ley consolidada a 21 de marzo de 2026 tampoco lo prevé. *Modelo:* la entrada no lleva régimen (§0, §6); el cálculo compara las lecturas.

<a id="s-2"></a>
**S-2. Negativa bajo la Ley.** La Ley menciona la negativa (art. 7.3), pero ni ella ni el RD dan un plazo que empiece en esa fecha. La documentación de diligencia debida reunida antes de negarse no tiene, según la letra de la Ley, un hecho que inicie su cómputo. *Modelo:* la negativa se registra como hecho con su fecha.

<a id="s-3"></a>
**S-3. Operaciones dentro de una relación de negocios, bajo la Ley.** La Ley (25.1.b) cuenta «desde la ejecución de la operación o la terminación de la relación de negocios», sin decir «ocasional». El RD (29.1) cuenta «desde la terminación de la relación de negocio o la ejecución de la operación ocasional». Con la letra de la Ley, una operación dentro de una relación viva podría contar desde su ejecución. Con el RD, cuenta desde la terminación. *Modelo:* se pide `fecha_ejecucion_operacion` para poder calcular las dos lecturas.

<a id="s-4"></a>
**S-4. Inicio del plazo del examen especial, bajo la Ley.** El RD 25.4 fija diez años sin decir desde cuándo. Hay varias candidatas: apertura, cierre, decisión, comunicación, o el hecho inicial del expediente por analogía con Ley 25.1.a y b. Además, el examen puede tratar un «hecho u operación» (Ley 17) o una tentativa (RD 24, último párrafo) sin relación de negocios ni operación ocasional. *Modelo:* se piden las cuatro fechas del registro del RD 25.3.

<a id="s-5"></a>
**S-5. Inicio del plazo de los documentos de comunicación y control interno, bajo la Ley.** El RD 29.2 fija diez años sin decir desde cuándo. Hay varias candidatas: la fecha del documento o, en las políticas y análisis de riesgo que se sustituyen, el fin de su vigencia. Tampoco está claro si estos documentos están ligados a un expediente de cliente: muchos, como las políticas o las actas, son de toda la entidad. *Modelo:* `fecha_documento` y `fecha_fin_vigencia`. **[Decisión propia]**: se admiten dentro de un expediente, aunque no pertenezcan a un cliente.

<a id="s-6"></a>
**S-6. Documentos de control interno bajo el AMLR.** El art. 77.1 no los incluye y no se encontró otro plazo de conservación para ellos. La búsqueda fue de «conserv» en la parte dispositiva del AMLR. El art. 9.2, letra a), inciso vi), pide políticas internas sobre «la conservación de registros», pero no da un plazo. No se sabe si deben conservarse, durante cuánto tiempo, o si decide el Derecho nacional. *Modelo:* el `subtipo` separa las comunicaciones de sospecha, que sí tienen regla, del resto.

<a id="s-7"></a>
**S-7. Inicio del plazo en fundaciones y asociaciones, bajo la Ley.** El RD 42.3.d fija diez años para los documentos de aplicación de fondos sin decir desde cuándo: puede ser la aplicación o el fin del proyecto. El art. 39 de la Ley remite al «plazo establecido en el artículo 25» para los registros de identificación de aportantes y receptores. Pero el art. 25 cuenta desde la terminación de la relación o la ejecución de la operación, y ninguna de las dos encaja claramente con una donación o una ayuda. *Modelo:* `fecha_aplicacion` y `fecha_fin_proyecto`; los registros de identificación van en `diligencia_debida`.

<a id="s-8"></a>
**S-8. Fundaciones y asociaciones bajo el AMLR.** El art. 3 del AMLR, que enumera las entidades obligadas, no incluye a las fundaciones ni a las asociaciones como tales, y ninguna regla del AMLR equivale al art. 39 de la Ley ni al 42 del RD. No se sabe si esas obligaciones nacionales seguirán vigentes después del 10 de julio de 2027. *Modelo:* la categoría existe con independencia del régimen.

<a id="s-9"></a>
**S-9. Plazos nacionales más largos después del AMLR.** El art. 77.3 manda suprimir los datos personales a los cinco años, «sin perjuicio de los períodos de conservación [...] del Derecho nacional que cumplan el Reglamento (UE) 2016/679». No se sabe si los diez años de la Ley 10/2010 son uno de esos períodos. Si lo son, prevalecería el plazo más largo. *Modelo:* no hace falta ningún dato; es una de las lecturas que compara el cálculo.

<a id="s-10"></a>
**S-10. Hecho inicial desconocido o posterior.** Si la relación sigue viva (`fecha_terminacion = null`), ningún plazo ha empezado. Si la relación termina y luego se reanuda con el mismo cliente, los textos no dicen si los documentos de diligencia debida de la primera relación siguen su propio plazo o el de la segunda. *Modelo:* un expediente por relación (§3). Reutilizar documentos entre expedientes queda fuera del modelo.

<a id="s-11"></a>
**S-11. Período adicional del art. 77.4 AMLR.** Depende de que un Estado miembro lo permita o lo exija. Las fuentes de este proyecto no dicen si España lo ha hecho. *Modelo:* no se recoge como dato (§6).

<a id="s-12"></a>
**S-12. Negativa a una operación dentro de una relación viva.** El AMLR 77.3 habla de la negativa «a entablar una relación de negocios o llevar a cabo una operación ocasional». Negarse a una operación concreta de un cliente con relación viva no es ninguna de las dos cosas. *Modelo:* no hay campo; la documentación sigue el hecho inicial de la relación.

<a id="s-13"></a>
**S-13. Cómputo de «años».** Ninguna de las tres fuentes dice cómo se cuentan los años: de fecha a fecha, qué pasa con un hecho inicial un 29 de febrero, o si el día inicial cuenta. *Modelo:* solo fechas de día (§2).

<a id="s-14"></a>
**S-14. Intercambio de información en asociaciones (AMLR 77.1.d).** El AMLR obliga a conservar «copias de los documentos e información obtenidos en el marco de dichas asociaciones, y registros de todos los casos de intercambio de información». No es ninguna de las cinco categorías pedidas y la Ley no tiene equivalente. *Modelo:* **[Decisión propia]** queda fuera por ahora; no hay categoría para estos documentos.

<a id="s-15"></a>
**S-15. Clubes de fútbol profesional.** El art. 3, punto 3, letra o), del AMLR solo los incluye «en relación con» determinadas operaciones, y el art. 90 les aplica el Reglamento desde el 10 de julio de 2029. Para un club, que el AMLR se aplique a un expediente depende del tipo de operación, y el modelo no lo recoge. *Modelo:* `actividad` registra el hecho; no hay campo para el tipo de operación del art. 3.3.o. **[Decisión propia]**: queda fuera por ahora, como S-14.
