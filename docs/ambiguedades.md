# Ambigüedades

Casos en que el resultado no está determinado por un texto único. Para cada uno: qué dice la norma, por qué no determina un comportamiento único, qué hace esta implementación, cómo se señala en la salida y a qué régimen afecta.

Siglas y fuentes: las de [`modelo-datos.md`](modelo-datos.md) (detalle y huellas en [`fuentes/FUENTES.md`](fuentes/FUENTES.md)). Las decisiones se citan como en su documento: **D-n** en [`especificacion-calculo.md`](especificacion-calculo.md) y **V-n** en el §8.2 de [`modelo-datos.md`](modelo-datos.md). Los identificadores S-n son estables: no se renumeran ni se reutilizan.

Hay dos secciones:

- [**Casos que la norma no resuelve**](#1-casos-que-la-norma-no-resuelve) (S-1 a S-13): el texto calla, se contradice o remite a algo que no está en las fuentes.
- [**Casos que vienen del modelo de datos o de la validación**](#2-casos-que-vienen-del-modelo-de-datos-o-de-la-validación) (S-14 y S-15): la norma sí da una respuesta, pero el modelo no recoge el dato que haría falta para aplicarla.

**Cómo se señala en la salida.** La salida (especificación, §9) tiene cuatro mecanismos, y cada caso dice cuáles usa:

- **lecturas**: el cálculo da una lectura por cada interpretación, con su identificador (por ejemplo `OP-1`, `OP-2`) y sus fechas;
- **`indeterminado`**: el estado de un régimen cuando sus lecturas dan estados distintos en la fecha de referencia (D-6);
- **regímenes de transición**: T-1 a T-4 junto a `ley_10_2010` y `amlr`, con la comparación que señala si no coinciden (D-14, D-21);
- **`sin_regla`**: el estado de una categoría que el AMLR no regula (D-17).

Algunos casos **no se señalan**: la implementación aplica una decisión y la salida no dice que otra lectura cambiaría el resultado. Cada caso lo indica.

---

## 1. Casos que la norma no resuelve

<a id="s-1"></a>
### S-1. Paso de la Ley al AMLR

**Régimen.** Transición: afecta al estado en cualquier fecha desde el 10 de julio de 2027 (A) de los documentos cuyo plazo empezó con la Ley.

**Qué dice la norma.**
- AMLR, art. 90: «Será aplicable a partir del 10 de julio de 2027, excepto para las entidades obligadas a que se refiere el artículo 3, punto 3, letras n) a o), para quienes será aplicable desde el 10 de julio de 2029». Y: «El presente Reglamento será obligatorio en todos sus elementos y directamente aplicable en cada Estado miembro».
- AMLR, art. 77.4: régimen transitorio solo para procedimientos judiciales pendientes (S-11).
- La Ley consolidada a 21 de marzo de 2026 no contiene ninguna adaptación al AMLR ni regla transitoria sobre conservación.

**Por qué no determina un comportamiento único.** Ningún texto dice qué plazo se aplica a un documento cuyo plazo de diez años empezó con la Ley y sigue en curso el día A: si sigue la Ley, si pasa a los cinco años del AMLR contados desde el hecho original (y entonces puede estar ya vencido) o desde A, o si los diez años de la Ley siguen como plazo nacional (S-9).

**Qué hace la implementación.** No elige. Calcula cuatro lecturas como regímenes propios (especificación, §4.2): T-1 (pervivencia de la Ley), T-2 (AMLR desde H), T-3 (AMLR desde A, con el límite de la Ley) y T-4 (plazo nacional superior). El régimen es un parámetro del cálculo, no un dato de la entrada (modelo, §0; D-14), precisamente para que quien rellena la entrada no elija sin saberlo. Cómo se construye cada lectura en los casos límite lo fijan D-23 (T-3 tras su vencimiento) y D-24 (T-4 con F ≥ A).

**Cómo se señala en la salida.** Regímenes de transición: el informe da el estado en T-1 a T-4 y, si no coinciden, lo dice expresamente («T-1 a T-4 no coinciden: el estado depende de cómo se resuelva la transición (S-1, D-21)»). Los periodos de la línea temporal en que difieren se listan aparte. Código de salida 1 (§9.3). Corpus: caso 03.

<a id="s-2"></a>
### S-2. Negativa bajo la Ley

**Régimen.** Ley (y T-4, que la aplica también a hechos posteriores a A).

**Qué dice la norma.**
- Ley, art. 7.3: «La negativa a establecer relaciones de negocio o a ejecutar operaciones o la terminación de la relación de negocios por imposibilidad de aplicar las medidas de diligencia debida [...] no conllevará [...] ningún tipo de responsabilidad».
- Ley, art. 25.1, y RD, arts. 28.1 y 29.1: los plazos cuentan «desde la terminación de la relación de negocios o la ejecución de la operación ocasional».
- En cambio, AMLR, art. 77.3, cuenta también desde «la fecha de la negativa».

**Por qué no determina un comportamiento único.** La Ley reconoce la negativa, pero ningún plazo empieza en ella. La documentación reunida antes de negarse está cubierta por la regla general del art. 25.1 («diez años»), que no dice desde cuándo.

**Qué hace la implementación.** La negativa es un hecho válido de la entrada (modelo, §3.1). Con la Ley, las lecturas que usan H se sustituyen por dos: NG-1, desde la fecha de la negativa, y NG-2, desde la fecha del documento (D-18). No hay acceso restringido, porque el art. 25.1 lo cuenta desde la terminación o la ejecución (D-8).

**Cómo se señala en la salida.** Lecturas `NG-1` y `NG-2`; `indeterminado` si dan estados distintos. Tests: especificación, ejemplo 3.

<a id="s-3"></a>
### S-3. Operaciones dentro de una relación de negocios: la Ley frente al RD

**Régimen.** Ley (y T-1, T-3 y T-4 para plazos que empezaron antes de A). En el AMLR no existe: el art. 77.3 dice «operación ocasional».

**Qué dice la norma.**
- Ley, art. 25.1.b: «durante un periodo de diez años desde la ejecución de la operación o la terminación de la relación de negocios».
- RD, art. 29.1: «durante un periodo de diez años desde la terminación de la relación de negocio o la ejecución de la operación ocasional».

**Por qué no determina un comportamiento único.** La Ley dice «la operación» y el RD, «la operación ocasional». Para una operación dentro de una relación, la Ley permite contar desde su ejecución, y el RD, solo desde la terminación. Hay argumentos en los dos sentidos (especificación, §5.2): el RD es desarrollo de una norma de rango superior, pero el propio art. 25.1 cuenta la restricción de acceso desde la «operación ocasional».

**Qué hace la implementación.** Dos lecturas: OP-1 (desde `fecha_ejecucion_operacion`, letra de la Ley) y OP-2 (desde la terminación, RD). No pondera los argumentos. En una operación ocasional las dos coinciden (V-14).

**Cómo se señala en la salida.** Lecturas `OP-1` y `OP-2`; `indeterminado` si dan estados distintos. Con OP-1, una operación puede exigir eliminación con la relación todavía viva. Corpus: caso 04.

<a id="s-4"></a>
### S-4. Inicio del plazo del examen especial

**Régimen.** Ley. En el AMLR el plazo cuenta desde H (art. 77.3), así que no hay ambigüedad sobre el inicio.

**Qué dice la norma.**
- RD, art. 25.4: «Los sujetos obligados conservarán los expedientes de examen especial durante el plazo de diez años».
- RD, art. 25.3: el registro recoge «sus fechas de apertura y cierre [...] la decisión sobre su comunicación [...] y su fecha, así como la fecha en que, en su caso, se realizó la comunicación».
- Ley, art. 17, y RD, art. 24: el examen puede tratar un «hecho u operación» o las operaciones que «se hubieran intentado y no ejecutado».

**Por qué no determina un comportamiento único.** El RD fija diez años sin decir desde cuándo. Cualquiera de las cuatro fechas del registro, o la terminación de la relación por analogía con la Ley 25.1.a y b, es un inicio posible, y dan vencimientos distintos. Además, un examen puede no tener relación ni operación ejecutada.

**Qué hace la implementación.** Cinco lecturas: EE-1 (apertura), EE-2 (cierre), EE-3 (decisión), EE-4 (comunicación, o la decisión si no la hubo: D-7) y EE-5 (H). Una fecha `null` da `plazo_no_iniciado` en su lectura; con la relación viva, también EE-5 (D-22). El modelo exige un hecho inicial para cualquier documento que no sea de aplicación de fondos (`ERR-05`), así que un examen sin relación ni operación no se puede representar con su propio hecho: se registra en el expediente del cliente.

**Cómo se señala en la salida.** Lecturas `EE-1` a `EE-5`; `indeterminado` si dan estados distintos. Corpus: caso 05; especificación, ejemplo 5.

<a id="s-5"></a>
### S-5. Inicio del plazo de los documentos de comunicación y control interno

**Régimen.** Ley.

**Qué dice la norma.**
- RD, art. 29.2: «Los sujetos obligados conservarán durante un periodo de diez años los documentos en que se formalice el cumplimiento de sus obligaciones de comunicación y de control interno».
- Ley, art. 25.1, primer párrafo: la regla general de diez años, sin inicio.

**Por qué no determina un comportamiento único.** No se dice desde cuándo cuentan los diez años. Muchos de estos documentos (políticas, análisis de riesgo, actas) son de toda la entidad y no dependen de un cliente, y una política vigente durante años puede contarse desde que se aprobó o desde que se sustituyó.

**Qué hace la implementación.** Tres lecturas: CI-1 (fecha del documento), CI-2 (fin de vigencia, solo en políticas y análisis de riesgo) y CI-3 (H del expediente; con negativa, NG-1 y NG-2). CI-3 existe siempre que el expediente tenga hecho inicial (D-22); con la relación viva da `plazo_no_iniciado`. Estos documentos se admiten dentro de un expediente aunque no sean de un cliente (modelo, §4.4).

**Cómo se señala en la salida.** Lecturas `CI-1` a `CI-3`; `indeterminado` si dan estados distintos. Corpus: caso 06; especificación, ejemplo 6.

<a id="s-6"></a>
### S-6. Documentos de control interno bajo el AMLR

**Régimen.** AMLR (y T-2 y T-3; T-1 desde A para plazos que no empezaron con la Ley).

**Qué dice la norma.**
- AMLR, art. 77.1: enumera diligencia debida (a), evaluación y comunicaciones de sospecha (b), operaciones (c) e intercambio de información en asociaciones (d).
- AMLR, art. 9.2.a.vi: las políticas internas deben cubrir «la conservación de registros y políticas en relación con el tratamiento de datos personales con arreglo al artículo 76 y 77», sin plazo.
- La búsqueda de «conserv» en la parte dispositiva del AMLR no encontró otro plazo.

**Por qué no determina un comportamiento único.** El AMLR no incluye estos documentos en el art. 77.1 ni les da otro plazo. No se sabe si no hay que conservarlos, si se aplica por extensión el art. 77.3 o si decide el Derecho nacional (S-9).

**Qué hace la implementación.** Estado `sin_regla`, que no es ni conservar ni suprimir (D-17). Las comunicaciones de sospecha sí tienen regla: van al art. 77.1.b aunque estén en esta categoría (D-19). Tres lecturas informativas: SR-1 (sin obligación), SR-2 (el RD 29.2 como Derecho nacional, con sus lecturas CI-n) y SR-3 (art. 77.3 por extensión, desde H).

**Cómo se señala en la salida.** Estado `sin_regla`, que por D-17 no pasa a `indeterminado` aunque las lecturas `SR-1`, `SR-2/CI-n` y `SR-3` difieran. Corpus: caso 06; especificación, ejemplo 6.

<a id="s-7"></a>
### S-7. Inicio del plazo en fundaciones y asociaciones

**Régimen.** Ley.

**Qué dice la norma.**
- RD, art. 42.3.d: «Conservar durante un plazo de diez años los documentos o registros que acrediten la aplicación de los fondos en los diferentes proyectos».
- Ley, art. 39: los registros de identificación de quienes aportan o reciben fondos se conservan «durante el plazo establecido en el artículo 25».

**Por qué no determina un comportamiento único.** El RD 42.3.d no dice desde cuándo, y tanto la aplicación de los fondos como el fin del proyecto son inicios posibles. El art. 39 remite al art. 25, que cuenta desde la terminación de una relación o la ejecución de una operación ocasional, y ninguna de las dos encaja claramente con una donación o una ayuda.

**Qué hace la implementación.** Para `aplicacion_fondos`, dos lecturas: AF-1 (aplicación) y AF-2 (fin del proyecto). Un expediente de fundación con solo este tipo de documentos puede no tener hecho inicial, y entonces no hay acceso restringido (D-8). Los registros de identificación del art. 39 van en `diligencia_debida` (modelo, §4.5) y siguen el art. 25 con el hecho inicial del expediente, que el modelo exige para esa categoría (`ERR-05`).

**Cómo se señala en la salida.** Lecturas `AF-1` y `AF-2`; `indeterminado` si dan estados distintos. Para los registros de identificación, **no se señala**: se aplica la regla de diligencia debida sin lectura alternativa.

<a id="s-8"></a>
### S-8. Fundaciones y asociaciones bajo el AMLR

**Régimen.** AMLR (y T-2 y T-3; T-1 desde A para plazos que no empezaron con la Ley).

**Qué dice la norma.** AMLR, art. 3: la lista de entidades obligadas no incluye a las fundaciones ni a las asociaciones como tales. Ningún artículo equivale a la Ley 39 ni al RD 42.3.d.

**Por qué no determina un comportamiento único.** No se sabe si las obligaciones nacionales de los arts. 39 de la Ley y 42 del RD seguirán vigentes desde A, ni, si lo hacen, cómo se combinan con el AMLR.

**Qué hace la implementación.** Igual que S-6: `sin_regla` (D-17), con las lecturas SR-1, SR-2 (AF-n) y, si hay hecho inicial, SR-3.

**Cómo se señala en la salida.** Estado `sin_regla`, con lecturas `SR-1`, `SR-2/AF-n` y, en su caso, `SR-3`.

<a id="s-9"></a>
### S-9. Plazos nacionales más largos después del AMLR

**Régimen.** Los dos: afecta a la transición y a las categorías sin regla del AMLR.

**Qué dice la norma.** AMLR, art. 77.3: «Sin perjuicio de los períodos de conservación de los datos recogidos a efectos de otros actos jurídicos de la Unión o del Derecho nacional que cumplan el Reglamento (UE) 2016/679, las entidades obligadas suprimirán los datos personales al expirar el período de cinco años».

**Por qué no determina un comportamiento único.** No se sabe si los diez años de la Ley 10/2010 son uno de esos períodos nacionales. Si lo son, el plazo más largo prevalecería también para documentos posteriores a A.

**Qué hace la implementación.** No lo decide en `amlr`, que aplica solo el AMLR. La lectura T-4 (especificación, §4.2) es exactamente esta hipótesis: la Ley sigue como plazo nacional, con el mayor de los dos plazos para hechos posteriores a A (D-24). Para las categorías sin regla, la lectura SR-2 es la misma hipótesis.

**Cómo se señala en la salida.** Régimen `T-4` y lecturas `SR-2/…`. No hay aviso propio.

<a id="s-10"></a>
### S-10. Hecho inicial desconocido o relación reanudada

**Régimen.** Los dos.

**Qué dice la norma.** Ley, art. 25.1, RD, arts. 28.1 y 29.1, y AMLR, art. 77.3: los plazos cuentan desde la terminación de «la relación de negocios». Ningún texto trata la relación que termina y se reanuda con el mismo cliente.

**Por qué no determina un comportamiento único.** Si una relación termina y después se inicia otra con el mismo cliente, no se sabe si la documentación de diligencia debida de la primera sigue su propio plazo o el de la segunda, ni si la nueva relación reabre el acceso restringido (especificación, §6.3.9).

**Qué hace la implementación.** Mientras la relación sigue viva, `fecha_terminacion` es `null` y ningún plazo que cuente desde ella ha empezado (`plazo_no_iniciado`). Cada relación es un expediente distinto (modelo, §3); reutilizar documentos entre expedientes queda fuera del modelo.

**Cómo se señala en la salida.** **No se señala** la reanudación: el cálculo solo ve el expediente que recibe. La relación viva se ve en `plazo_no_iniciado` y en la nota de la línea temporal, que advierte que no prevé hechos futuros como la terminación de una relación (D-25).

<a id="s-11"></a>
### S-11. Período adicional del art. 77.4 del AMLR

**Régimen.** AMLR (y T-2; T-3 cuando vence por A + 5 años; T-1 y T-4 cuando usan el AMLR).

**Qué dice la norma.** AMLR, art. 77.4: con procedimientos judiciales pendientes el 10 de julio de 2027, la entidad «podrá conservar esa información o esos documentos durante un período de cinco años a partir del 10 de julio de 2027». Segundo párrafo: los Estados miembros podrán «permitir o requerir la conservación de los datos o información durante un período adicional de cinco años».

**Por qué no determina un comportamiento único.** Depende de una decisión nacional que no está en las fuentes: si España permite, exige o no prevé el período adicional. Tampoco se dice si la fecha de 2027 vale para las entidades a las que el AMLR se aplica desde 2029.

**Qué hace la implementación.** Dos lecturas: PA-1, sin período adicional (conservación facultativa hasta el 2032-07-10), y PA-2, con él (hasta el 2037-07-10). En las dos, «facultativa» (D-13). La conservación facultativa empieza el 2027-07-10 también para el fútbol, porque el art. 77.4 fija esa fecha; antes de ese día no se aplica (comentario `AMBIGÜEDAD` en `calculo.py`). La versión 1 del modelo tenía un campo `prorroga_nacional_77_4`; se quitó porque no es un hecho del expediente (modelo, §6).

**Cómo se señala en la salida.** Lecturas `PA-1` y `PA-2` (o `DD/PA-1`, etc., en los regímenes de transición); `indeterminado` desde el 2032-07-11, cuando PA-1 exige suprimir y PA-2 permite conservar. Corpus: caso 08.

<a id="s-12"></a>
### S-12. Negativa a una operación dentro de una relación viva

**Régimen.** AMLR.

**Qué dice la norma.** AMLR, art. 77.3: la negativa «a entablar una relación de negocios o llevar a cabo una operación ocasional».

**Por qué no determina un comportamiento único.** Negarse a una operación concreta de un cliente con relación viva no es ninguna de las dos cosas: no se sabe si inicia un plazo propio para la documentación de esa operación.

**Qué hace la implementación.** No hay campo para ella. La documentación sigue el hecho inicial de la relación.

**Cómo se señala en la salida.** **No se señala.**

<a id="s-13"></a>
### S-13. Cómputo de «años»

**Régimen.** Los dos.

**Qué dice la norma.** Ley 25.1, RD 28.1, 29.1, 29.2, 25.4 y 42.3.d: «diez años»; AMLR 77.3: «cinco años»; Ley 25.1: «Transcurridos cinco años». Ninguna de las tres fuentes dice cómo se cuentan.

**Por qué no determina un comportamiento único.** Contar de fecha a fecha, contar el día inicial o no, y qué hacer con un 29 de febrero dan vencimientos que difieren en un día, y en ese día el estado puede ser distinto.

**Qué hace la implementación.** D-1 (mismo día y mes; 29 de febrero → 28), D-2 (el día del vencimiento está dentro del plazo), D-3 (el día de inicio también) y D-4 («transcurridos cinco años» se cumple el día siguiente al quinto aniversario). Solo fechas de día, sin hora (modelo, §2).

**Cómo se señala en la salida.** **No se señala** como alternativa: la salida da las fechas calculadas con D-1 a D-4 en cada lectura y en la línea temporal. Especificación, ejemplo 2.

---

## 2. Casos que vienen del modelo de datos o de la validación

> **Origen: modelo de datos.** En estos casos la norma sí da una respuesta. La falta de determinación viene de que el modelo no recoge el dato necesario o deja la categoría fuera de su alcance. Se podrían resolver ampliando el modelo, sin necesidad de interpretar la norma.

<a id="s-14"></a>
### S-14. Intercambio de información en asociaciones (AMLR, art. 77.1.d)

**Origen.** Modelo de datos: categoría fuera de alcance.

**Régimen.** AMLR.

**Qué dice la norma.** AMLR, art. 77.1.d: cuando participen en asociaciones para el intercambio de información, las entidades conservarán «copias de los documentos e información obtenidos en el marco de dichas asociaciones, y registros de todos los casos de intercambio de información», con el plazo del art. 77.3. La Ley no tiene equivalente.

**Por qué no determina un comportamiento único.** La norma sí da la regla. El modelo no tiene categoría para estos documentos: no son ninguna de las cinco del §4, y la decisión de dejarlos fuera fue del proyecto (modelo, §4).

**Qué hace la implementación.** No los admite. Un documento con otra `categoria` es un error de validación (`ERR-01`). Registrarlo en otra categoría aplicaría una regla que no le corresponde.

**Cómo se señala en la salida.** Con una categoría no prevista, error `ERR-01` y código de salida 2. Si se registra en otra categoría, **no se señala**.

<a id="s-15"></a>
### S-15. Clubes de fútbol profesional: tipo de operación

**Origen.** Modelo de datos: dato no recogido.

**Régimen.** AMLR (y T-1 a T-4, a través de la fecha A).

**Qué dice la norma.** AMLR, art. 3, punto 3, letra o): los clubes de fútbol profesional son entidades obligadas «en relación con» operaciones con un inversor, con un patrocinador y otras que enumera. Art. 90: para ellos el AMLR se aplica desde el 10 de julio de 2029.

**Por qué no determina un comportamiento único.** La norma sí distingue: el AMLR solo se aplica a las operaciones enumeradas. El modelo solo recoge que el sujeto es un club (`sujeto.actividad`), no el tipo de operación del expediente, así que no puede saber si ese expediente está dentro del ámbito del AMLR.

**Qué hace la implementación.** Para cualquier expediente de un club, A es el 2029-07-10 y el AMLR se calcula como si el expediente estuviera en su ámbito.

**Cómo se señala en la salida.** **No se señala**: la salida da `fecha_aplicacion_amlr` = 2029-07-10, pero no advierte de que el expediente podría quedar fuera del AMLR.
