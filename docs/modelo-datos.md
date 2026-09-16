# Modelo de datos de entrada

Este documento define el JSON que recibe el cálculo del estado de conservación de un expediente de prevención del blanqueo de capitales en una fecha dada. Aquí solo se describe la entrada: la salida y el algoritmo se definirán más adelante.

Siglas y fuentes (detalle y huellas en [`fuentes/FUENTES.md`](fuentes/FUENTES.md)):

- **Ley**: Ley 10/2010, texto consolidado con última modificación de 21 de marzo de 2026.
- **RD**: Reglamento aprobado por el Real Decreto 304/2014, texto consolidado con última modificación de 24 de abril de 2024.
- **AMLR**: Reglamento (UE) 2024/1624, texto publicado en el DO L de 19.6.2024.

Convenciones:

- Las citas van entre comillas «» y son literales.
- **[Decisión propia]** marca lo que no sale de los textos, sino del diseño de este proyecto.
- **[Sin resolver]** marca un caso que la norma no resuelve. Se recoge en la sección [Casos que la norma no resuelve](#casos-que-la-norma-no-resuelve) y el modelo no lo decide.

---

## 1. Ejemplo completo

```json
{
  "version_modelo": 1,
  "fecha_referencia": "2031-03-01",
  "regimen": "ley_10_2010",
  "sujeto": {
    "naturaleza": "sujeto_obligado",
    "amlr_art3_3_n_o": false
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
        "descripcion": "Declaración mensual al Servicio Ejecutivo",
        "subtipo": "comunicacion_sistematica",
        "fecha_documento": "2022-01-15",
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
| `version_modelo` | entero | sí | Versión de este esquema. Empieza en `1`. **[Decisión propia]** |
| `fecha_referencia` | fecha ISO 8601 (`AAAA-MM-DD`) | sí | Fecha para la que se calcula el estado. Ver §5. |
| `regimen` | `"ley_10_2010"` \| `"amlr"` | sí | Régimen con el que se calcula. Ver §6. |
| `sujeto` | objeto | sí | Naturaleza de quien conserva. Ver §2.1. |
| `expediente` | objeto | sí | Hecho que inicia el cómputo, documentos y circunstancias que alteran el plazo. Ver §3 y §4. |

Todas las fechas son de día, sin hora ni zona horaria. **[Decisión propia]**: ninguna de las fuentes fija los plazos por horas.

### 2.1. `sujeto`

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `naturaleza` | `"sujeto_obligado"` \| `"fundacion"` \| `"asociacion"` | sí | Determina si se admite la categoría `aplicacion_fondos` (§4.5). |
| `amlr_art3_3_n_o` | booleano | solo con `regimen = "amlr"` | `true` si se trata de un agente de fútbol o de un club de fútbol profesional. El AMLR no se les aplica hasta 2029 (§6). |

---

## 3. Fechas que pueden iniciar el cómputo: `expediente.hecho_inicial`

Cada expediente tiene **un único** hecho inicial. **[Decisión propia]**: si el mismo cliente tiene varias relaciones de negocio o varias operaciones ocasionales, cada una es un expediente distinto.

| Campo | Tipo | Descripción |
|---|---|---|
| `tipo` | `"relacion_de_negocios"` \| `"operacion_ocasional"` \| `"negativa"` \| `null` | Qué hecho es. `"negativa"` solo es válido con `regimen = "amlr"` (ver más abajo). `null` solo en el caso de §4.5. |
| `fecha_inicio` | fecha \| `null` | Inicio de la relación de negocios. **No inicia ningún cómputo** en ninguno de los dos regímenes. Se guarda como dato de control (no puede ser posterior a `fecha_terminacion`). **[Decisión propia]** |
| `fecha_terminacion` | fecha \| `null` | Terminación de la relación de negocios. `null` mientras la relación siga viva. |
| `fecha_ejecucion` | fecha \| `null` | Ejecución de la operación ocasional. |
| `fecha_negativa` | fecha \| `null` | Fecha de la negativa a entablar la relación o a realizar la operación ocasional. |
| `objeto_negativa` | `"relacion_de_negocios"` \| `"operacion_ocasional"` \| `null` | A qué se negó la entidad. |

Solo se rellena la fecha que corresponde al `tipo`; las otras dos van a `null`.

### 3.1. Qué fechas admite cada régimen

| Hecho | Ley 10/2010 y RD 304/2014 | AMLR |
|---|---|---|
| Terminación de la relación de negocios | Sí | Sí |
| Ejecución de la operación ocasional | Sí | Sí |
| Negativa a entablar la relación o a ejecutar la operación | **No** | **Sí** |

**Ley 10/2010.** Art. 25.1: «Transcurridos cinco años desde la terminación de la relación de negocios o la ejecución de la operación ocasional». Letra a): «durante un periodo de diez años desde la terminación de la relación de negocios o la ejecución de la operación». Letra b): «durante un periodo de diez años desde la ejecución de la operación o la terminación de la relación de negocios».

**RD 304/2014.** Arts. 28.1 y 29.1: «durante un periodo de diez años desde la terminación de la relación de negocio o la ejecución de la operación ocasional».

**AMLR.** Art. 77.3: «se conservará durante un período de cinco años, a partir de la fecha de extinción de la relación de negocios o de la fecha en la que se ejecute la operación ocasional, o de la fecha de la negativa a entablar una relación de negocios o llevar a cabo una operación ocasional».

**Dato que solo exige el AMLR: la fecha de la negativa.** La Ley reconoce que la negativa existe. Art. 7.3: «La negativa a establecer relaciones de negocio o a ejecutar operaciones o la terminación de la relación de negocios por imposibilidad de aplicar las medidas de diligencia debida [...] no conllevará [...] ningún tipo de responsabilidad». Pero ni el art. 25 de la Ley ni los arts. 28 y 29 del RD la usan como inicio del plazo. El AMLR, además, obliga a documentarla. Art. 21.3, párrafo segundo: la obligación de mantener un registro «se aplicará también a las situaciones en que las entidades obligadas rechacen establecer una relación de negocios».

Por eso, con `regimen = "ley_10_2010"`, `tipo = "negativa"` es un error de validación. **[Decisión propia]**: se rechaza en vez de sustituirse por otra fecha. Qué pasa con la documentación de una negativa bajo la Ley es el caso [S-2](#s-2).

---

## 4. Documentos: `expediente.documentos[]`

Campos comunes a todas las categorías:

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `id` | cadena | sí | Identificador único dentro del expediente. |
| `categoria` | ver §4.1–§4.5 | sí | Determina la regla de conservación. |
| `descripcion` | cadena | no | Texto libre. |
| `fecha_documento` | fecha | sí | Fecha en que se obtuvo o se generó el documento. En la Ley y en el AMLR solo inicia el cómputo donde se indica en §4.3–§4.5 como candidata. **[Decisión propia]**: se pide siempre como dato de control. |

Cada categoría añade sus propios campos.

### Resumen de reglas

| Categoría | Ley 10/2010 / RD 304/2014 | AMLR |
|---|---|---|
| `diligencia_debida` | 10 años desde la terminación o la ejecución (Ley 25.1.a; RD 28.1) | 5 años desde la extinción, la ejecución o la negativa (77.1.a y 77.3) |
| `operaciones` | 10 años desde la ejecución de la operación o desde la terminación (Ley 25.1.b; RD 29.1). Ver [S-3](#s-3) | 5 años desde la extinción, la ejecución o la negativa (77.1.c y 77.3) |
| `examen_especial` | 10 años, **sin inicio del cómputo declarado** (RD 25.4). Ver [S-4](#s-4) | 5 años desde la extinción, la ejecución o la negativa (77.1.b y 77.3) |
| `comunicacion_control_interno` | 10 años, **sin inicio del cómputo declarado** (RD 29.2). Ver [S-5](#s-5) | **No hay regla equivalente** en el art. 77.1. Ver [S-6](#s-6) |
| `aplicacion_fondos` | 10 años, **sin inicio del cómputo declarado** (RD 42.3.d). Ver [S-7](#s-7) | **No hay regla.** Ver [S-8](#s-8) |

Reglas que afectan a todas las categorías:

- **Ley, restricción de acceso.** Art. 25.1: «Transcurridos cinco años desde la terminación de la relación de negocios o la ejecución de la operación ocasional, la documentación conservada únicamente será accesible por los órganos de control interno del sujeto obligado, con inclusión de las unidades técnicas de prevención, y, en su caso, aquellos encargados de su defensa legal». El AMLR no tiene nada equivalente. Este es el único dato intermedio que exige la Ley y no el AMLR.
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

**Campos propios:** ninguno. El plazo se calcula desde `hecho_inicial`.

### 4.2. `operaciones`

Documentos o registros que acreditan las operaciones, sus intervinientes y las relaciones de negocio.

**Ley 10/2010 / RD.**
- Ley, art. 25.1.b: «Original o copia con fuerza probatoria de los documentos o registros que acrediten adecuadamente las operaciones, los intervinientes en las mismas y las relaciones de negocio, durante un periodo de diez años desde la ejecución de la operación o la terminación de la relación de negocios».
- RD, art. 29.1: «conservarán los documentos y mantendrán registros adecuados de todas las relaciones de negocio y operaciones, nacionales e internacionales, durante un periodo de diez años desde la terminación de la relación de negocio o la ejecución de la operación ocasional».

**AMLR.** Art. 77.1.c: «los justificantes y registros de operaciones, consistentes en documentos originales o en copias que tengan fuerza probatoria similar en procedimientos judiciales en virtud del Derecho nacional aplicable, que sean necesarios para identificar las operaciones».

**Campos propios:**

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `fecha_ejecucion_operacion` | fecha | sí, si `hecho_inicial.tipo = "relacion_de_negocios"` | Fecha de ejecución de la operación concreta dentro de la relación. Solo lo usa la lectura literal del art. 25.1.b de la Ley. Se pide para poder calcular las dos lecturas de [S-3](#s-3) sin elegir entre ellas. En el AMLR no inicia ningún cómputo. |

### 4.3. `examen_especial`

Expedientes de examen especial (Ley, art. 17; RD, art. 25) y, en el AMLR, registros de la evaluación de operaciones del art. 69.2.

**Ley 10/2010 / RD.**
- RD, art. 25.4: «Los sujetos obligados conservarán los expedientes de examen especial durante el plazo de diez años». No dice desde cuándo.
- RD, art. 25.3: el registro de expedientes recoge «sus fechas de apertura y cierre [...] la decisión sobre su comunicación o no al Servicio Ejecutivo de la Comisión y su fecha, así como la fecha en que, en su caso, se realizó la comunicación».

**AMLR.** Art. 77.1.b: «un registro de la evaluación realizada de conformidad con el artículo 69, apartado 2, incluida la información y las circunstancias consideradas y los resultados de dicha evaluación, con independencia de que dicha evaluación dé lugar o no a una comunicación de operaciones sospechosas a la UIF, y una copia de las comunicaciones, si las hay, de sospechas de operaciones». El plazo es el general del art. 77.3, que cuenta desde el hecho inicial.

**Datos que exige la Ley/RD y no el AMLR:** las cuatro fechas del registro del art. 25.3 RD. El AMLR no exige un registro con esas fechas ni las usa para el plazo.

**Campos propios:**

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `fecha_apertura` | fecha | sí con `ley_10_2010` | RD 25.3. |
| `fecha_cierre` | fecha \| `null` | sí con `ley_10_2010` | RD 25.3. `null` si el examen sigue abierto. |
| `fecha_decision_comunicacion` | fecha \| `null` | sí con `ley_10_2010` | RD 25.3. |
| `fecha_comunicacion` | fecha \| `null` | no | RD 25.3: «en su caso». `null` si se decidió no comunicar. |

Con la Ley, cualquiera de estas fechas podría iniciar el plazo de diez años: es el caso [S-4](#s-4). **[Decisión propia]**: se piden todas para no tener que elegir en el modelo.

### 4.4. `comunicacion_control_interno`

Documentos que formalizan el cumplimiento de las obligaciones de comunicación y de control interno.

**Ley 10/2010 / RD.**
- RD, art. 29.2: «Los sujetos obligados conservarán durante un periodo de diez años los documentos en que se formalice el cumplimiento de sus obligaciones de comunicación y de control interno». No dice desde cuándo.
- Ley, art. 25.1, primer párrafo: la regla general de diez años para «la documentación en que se formalice el cumplimiento de las obligaciones establecidas en la presente ley». Tampoco dice desde cuándo.

**AMLR.** El art. 77.1 enumera cuatro tipos de documentos: diligencia debida, evaluación y comunicaciones de sospecha, operaciones e intercambio de información en asociaciones. No incluye los de control interno. Ver [S-6](#s-6).

**Campos propios:**

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `subtipo` | `"comunicacion_por_indicio"` \| `"comunicacion_sistematica"` \| `"politicas_procedimientos"` \| `"analisis_riesgo"` \| `"organo_control_interno"` \| `"otro"` | sí | **[Decisión propia]**. Los valores se basan en Ley arts. 18 y 26 y en RD arts. 26, 27, 31, 32 y 35. Hacen falta por [S-5](#s-5) y [S-6](#s-6). |
| `fecha_fin_vigencia` | fecha \| `null` | sí si `subtipo` es `politicas_procedimientos` o `analisis_riesgo` | Fecha en que el documento se sustituyó o dejó de aplicarse. `null` si sigue vigente. **[Decisión propia]**: candidata a inicio del cómputo, ver [S-5](#s-5). |

Con `regimen = "amlr"`, una comunicación de sospecha a la UIF se registra en `examen_especial`, porque el art. 77.1.b la une a la evaluación. Si se registra con `subtipo = "comunicacion_por_indicio"` en esta categoría, es un error de validación. **[Decisión propia]**

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

Con una fundación o asociación, `hecho_inicial` puede no tener sentido para esta categoría. **[Decisión propia]**: el expediente de una fundación o asociación que solo contenga documentos `aplicacion_fondos` usa `hecho_inicial` con todos los campos a `null` y `tipo = null`. Ninguna otra categoría admite `tipo = null`.

---

## 5. Fecha de referencia

`fecha_referencia` es la fecha para la que se calcula el estado de cada documento: si el plazo no ha empezado, si está en curso, si el acceso está restringido (solo con la Ley), si hay que eliminar el documento, etc. La lista de estados se definirá con la salida.

- Es obligatoria. **[Decisión propia]**: no se toma la fecha del sistema por defecto, para que el mismo JSON dé siempre el mismo resultado.
- Puede ser pasada o futura. **[Decisión propia]**
- No puede ser anterior a ninguna fecha del expediente. Si lo es, es un error de validación. **[Decisión propia]**: los hechos posteriores a la fecha de referencia no se conocían en esa fecha. Ver también [S-10](#s-10).
- No elige el régimen (§6).

---

## 6. Régimen

`regimen` se indica explícitamente. **[Decisión propia]**

Lo que dicen los textos:

- AMLR, art. 90: «Será aplicable a partir del 10 de julio de 2027, excepto para las entidades obligadas a que se refiere el artículo 3, punto 3, letras n) a o), para quienes será aplicable desde el 10 de julio de 2029». Letra n): «los agentes de fútbol». Letra o): «los clubes de fútbol profesional» en relación con determinadas operaciones.
- AMLR, art. 77.4: «Cuando, a 10 de julio de 2027, haya procedimientos judiciales relacionados con la prevención, la detección, la investigación o el enjuiciamiento de presuntas actividades de blanqueo de capitales o financiación del terrorismo pendientes en un Estado miembro, y obren en poder de una entidad obligada información o documentos relacionados con esos procedimientos pendientes, la entidad obligada podrá conservar esa información o esos documentos durante un período de cinco años a partir del 10 de julio de 2027». El segundo párrafo permite a los Estados miembros un período adicional de cinco años.

Ninguna fuente dice qué régimen se aplica a un expediente cuyo hecho inicial es anterior al 10 de julio de 2027 si se calcula para una fecha posterior. Es el caso [S-1](#s-1). Por eso el régimen no se deduce de las fechas.

Validaciones:

- `regimen = "amlr"` con `fecha_referencia` anterior al 2027-07-10, o al 2029-07-10 si `sujeto.amlr_art3_3_n_o = true`: es un error de validación. **[Decisión propia]**

### 6.1. Campos que solo existen en el AMLR

| Campo | Tipo | Descripción |
|---|---|---|
| `expediente.prorrogas_autoridad[]` | lista de `{ "autoridad": cadena, "fecha_requerimiento": fecha, "fecha_fin": fecha }` | AMLR, art. 77.3, párrafo segundo: «Las autoridades competentes podrán exigir, según cada caso concreto, que se siga conservando la información [...]. La prórroga máxima del período de conservación no excederá de un período de cinco años». No se encontró en la Ley ni en el RD una prórroga equivalente del plazo de conservación. Con `ley_10_2010`, una lista no vacía es un error de validación. **[Decisión propia]** |
| `expediente.procedimiento_judicial_pendiente_2027_07_10` | booleano | AMLR, art. 77.4, primer párrafo. |
| `expediente.prorroga_nacional_77_4` | booleano, opcional | AMLR, art. 77.4, segundo párrafo: depende de que España lo permita o lo exija, y eso no está en las fuentes. Ver [S-11](#s-11). |

La prórroga se aplica al expediente entero y no a cada documento. **[Decisión propia]**: el art. 77.3 habla de «la información a que se refiere el párrafo primero» sin distinguir.

---

## 7. Datos exigidos por cada régimen

| Dato | Ley 10/2010 / RD | AMLR | Base |
|---|---|---|---|
| `hecho_inicial.fecha_terminacion` | sí | sí | Ley 25.1; RD 28.1 y 29.1; AMLR 77.3 |
| `hecho_inicial.fecha_ejecucion` | sí | sí | Ídem |
| `hecho_inicial.fecha_negativa` | **no** (no inicia el cómputo) | **sí** | AMLR 77.3 y 21.3 |
| `operaciones.fecha_ejecucion_operacion` | sí (para la lectura literal de 25.1.b) | no | Ley 25.1.b; [S-3](#s-3) |
| Fechas del registro de examen especial | **sí** | no | RD 25.3 y 25.4 |
| `comunicacion_control_interno.*` | **sí** | no hay categoría | RD 29.2 |
| `aplicacion_fondos.*` | **sí** | no hay regla | RD 42.3.d |
| `prorrogas_autoridad` | no | **sí** | AMLR 77.3 |
| `procedimiento_judicial_pendiente_2027_07_10` | no | **sí** | AMLR 77.4 |
| `sujeto.amlr_art3_3_n_o` | no | **sí** | AMLR 90 |

---

## Casos que la norma no resuelve

Cada caso indica qué deja abierto el texto y qué datos recoge el modelo para no cerrar la cuestión. Ninguno se resuelve aquí.

<a id="s-1"></a>
**S-1. Paso de la Ley al AMLR.** El AMLR se aplica desde el 10 de julio de 2027 (art. 90) y su único régimen transitorio sobre conservación es el de los procedimientos judiciales pendientes (art. 77.4). No hay regla para los expedientes cuyo plazo de diez años empezó bajo la Ley y sigue en curso en esa fecha, ni para los que ya habrían superado los cinco años del AMLR. La Ley consolidada a 21 de marzo de 2026 tampoco lo prevé. *Modelo:* `regimen` explícito (§6).

<a id="s-2"></a>
**S-2. Negativa bajo la Ley.** La Ley menciona la negativa (art. 7.3), pero ni ella ni el RD dan un plazo que empiece en esa fecha. La documentación de diligencia debida reunida antes de negarse no tiene, según la letra de la Ley, un hecho que inicie su cómputo. *Modelo:* `tipo = "negativa"` se rechaza con `ley_10_2010`.

<a id="s-3"></a>
**S-3. Operaciones dentro de una relación de negocios, bajo la Ley.** La Ley (25.1.b) cuenta «desde la ejecución de la operación o la terminación de la relación de negocios», sin decir «ocasional». El RD (29.1) cuenta «desde la terminación de la relación de negocio o la ejecución de la operación ocasional». Con la letra de la Ley, una operación dentro de una relación viva podría contar desde su ejecución. Con el RD, cuenta desde la terminación. *Modelo:* se pide `fecha_ejecucion_operacion` para poder calcular las dos lecturas.

<a id="s-4"></a>
**S-4. Inicio del plazo del examen especial, bajo la Ley.** El RD 25.4 fija diez años sin decir desde cuándo. Hay varias candidatas: apertura, cierre, decisión, comunicación, o el hecho inicial del expediente por analogía con Ley 25.1.a y b. Además, el examen puede tratar un «hecho u operación» (Ley 17) o una tentativa (RD 24, último párrafo) sin relación de negocios ni operación ocasional. *Modelo:* se piden las cuatro fechas del registro del RD 25.3.

<a id="s-5"></a>
**S-5. Inicio del plazo de los documentos de comunicación y control interno, bajo la Ley.** El RD 29.2 fija diez años sin decir desde cuándo. Hay varias candidatas: la fecha del documento o, en las políticas y análisis de riesgo que se sustituyen, el fin de su vigencia. Tampoco está claro si estos documentos están ligados a un expediente de cliente: muchos, como las políticas o las actas, son de toda la entidad. *Modelo:* `fecha_documento` y `fecha_fin_vigencia`. **[Decisión propia]**: se admiten dentro de un expediente, aunque no pertenezcan a un cliente.

<a id="s-6"></a>
**S-6. Documentos de control interno bajo el AMLR.** El art. 77.1 no los incluye y no se encontró otro plazo de conservación para ellos. La búsqueda fue de «conserv» en la parte dispositiva del AMLR. El art. 9.2, letra a), inciso vi), pide políticas internas sobre «la conservación de registros», pero no da un plazo. No se sabe si deben conservarse, durante cuánto tiempo, o si decide el Derecho nacional. *Modelo:* la categoría existe con `amlr`. El cálculo deberá devolver que no hay regla, no un plazo.

<a id="s-7"></a>
**S-7. Inicio del plazo en fundaciones y asociaciones, bajo la Ley.** El RD 42.3.d fija diez años para los documentos de aplicación de fondos sin decir desde cuándo: puede ser la aplicación o el fin del proyecto. El art. 39 de la Ley remite al «plazo establecido en el artículo 25» para los registros de identificación de aportantes y receptores. Pero el art. 25 cuenta desde la terminación de la relación o la ejecución de la operación, y ninguna de las dos encaja claramente con una donación o una ayuda. *Modelo:* `fecha_aplicacion` y `fecha_fin_proyecto`; los registros de identificación van en `diligencia_debida`.

<a id="s-8"></a>
**S-8. Fundaciones y asociaciones bajo el AMLR.** El art. 3 del AMLR, que enumera las entidades obligadas, no incluye a las fundaciones ni a las asociaciones como tales, y ninguna regla del AMLR equivale al art. 39 de la Ley ni al 42 del RD. No se sabe si esas obligaciones nacionales seguirán vigentes después del 10 de julio de 2027. *Modelo:* con `amlr`, `aplicacion_fondos` se admite y el cálculo deberá devolver que no hay regla.

<a id="s-9"></a>
**S-9. Plazos nacionales más largos después del AMLR.** El art. 77.3 manda suprimir los datos personales a los cinco años, «sin perjuicio de los períodos de conservación [...] del Derecho nacional que cumplan el Reglamento (UE) 2016/679». No se sabe si los diez años de la Ley 10/2010 son uno de esos períodos. Si lo son, prevalecería el plazo más largo. *Modelo:* no se recoge. Con `regimen` explícito, el cálculo aplica solo el régimen indicado.

<a id="s-10"></a>
**S-10. Hecho inicial desconocido o posterior.** Si la relación sigue viva (`fecha_terminacion = null`), ningún plazo ha empezado. Si la relación termina y luego se reanuda con el mismo cliente, los textos no dicen si los documentos de diligencia debida de la primera relación siguen su propio plazo o el de la segunda. *Modelo:* un expediente por relación (§3). Reutilizar documentos entre expedientes queda fuera del modelo.

<a id="s-11"></a>
**S-11. Período adicional del art. 77.4 AMLR.** Depende de que un Estado miembro lo permita o lo exija. Las fuentes de este proyecto no dicen si España lo ha hecho. *Modelo:* `prorroga_nacional_77_4` es un dato de entrada, no una regla.

<a id="s-12"></a>
**S-12. Negativa a una operación dentro de una relación viva.** El AMLR 77.3 habla de la negativa «a entablar una relación de negocios o llevar a cabo una operación ocasional». Negarse a una operación concreta de un cliente con relación viva no es ninguna de las dos cosas. *Modelo:* no hay campo; la documentación sigue el hecho inicial de la relación.

<a id="s-13"></a>
**S-13. Cómputo de «años».** Ninguna de las tres fuentes dice cómo se cuentan los años: de fecha a fecha, qué pasa con un hecho inicial un 29 de febrero, o si el día inicial cuenta. *Modelo:* solo fechas de día (§2). La regla se fijará con el algoritmo.

<a id="s-14"></a>
**S-14. Intercambio de información en asociaciones (AMLR 77.1.d).** El AMLR obliga a conservar «copias de los documentos e información obtenidos en el marco de dichas asociaciones, y registros de todos los casos de intercambio de información». No es ninguna de las cinco categorías pedidas y la Ley no tiene equivalente. *Modelo:* **[Decisión propia]** queda fuera por ahora; no hay categoría para estos documentos.
