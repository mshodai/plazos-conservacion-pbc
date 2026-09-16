---
title: "¿Se puede eliminar la documentación de una operación de hace más de diez años si la relación con el cliente sigue viva?"
description: "La Ley 10/2010 cuenta los diez años de conservación desde la ejecución de la operación; su Reglamento, el RD 304/2014, desde la terminación de la relación de negocios. Qué dice cada texto, por qué dan respuestas opuestas para el mismo documento y qué debería hacer una herramienta de cálculo."
---

# Dos textos, un documento: cuándo empieza a contar el plazo de una operación

Un sujeto obligado por la normativa de prevención del blanqueo de capitales tiene una relación de negocios con un cliente desde 2010. La relación sigue viva. Dentro de ella se ejecutó una operación el 20 de mayo de 2015. El 1 de enero de 2026, alguien revisa el archivo y se pregunta:

**La documentación de esa operación, ¿hay que conservarla o hay que eliminarla?**

La respuesta depende de qué texto se lea, y los dos textos pertenecen a la misma cadena normativa.

## Lo que dice la Ley

La Ley 10/2010, de prevención del blanqueo de capitales y de la financiación del terrorismo, regula la conservación en su art. 25.1. El primer párrafo fija la regla general y lo que pasa al final del plazo: «Los sujetos obligados conservarán durante un período de diez años la documentación en que se formalice el cumplimiento de las obligaciones establecidas en la presente ley, procediendo tras el mismo a su eliminación».

Para las operaciones, la letra b) concreta desde cuándo cuentan esos diez años: «Original o copia con fuerza probatoria de los documentos o registros que acrediten adecuadamente las operaciones, los intervinientes en las mismas y las relaciones de negocio, durante un periodo de diez años desde la ejecución de la operación o la terminación de la relación de negocios».

La frase tiene dos objetos (las operaciones y las relaciones de negocio) y dos fechas (la ejecución y la terminación). Leída sobre la operación, el documento que la acredita cuenta desde su ejecución. Para la operación del 20 de mayo de 2015, el plazo venció el 20 de mayo de 2025. El 1 de enero de 2026 ya no hay que conservarla: la Ley manda «su eliminación».

## Lo que dice su Reglamento

El Real Decreto 304/2014 aprueba el Reglamento de la Ley 10/2010, que se declara desarrollo de ella: «Este reglamento regula, en desarrollo de la Ley 10/2010, de 28 de abril, de prevención del blanqueo de capitales y de la financiación del terrorismo, las obligaciones de los sujetos obligados por dicha ley» (art. 1).

Su art. 29.1 regula la misma obligación sobre los mismos documentos: «Los sujetos obligados conservarán los documentos y mantendrán registros adecuados de todas las relaciones de negocio y operaciones, nacionales e internacionales, durante un periodo de diez años desde la terminación de la relación de negocio o la ejecución de la operación ocasional».

Una palabra cambia el resultado: «ocasional». Para el Reglamento, solo la operación ocasional, la que se hace fuera de una relación de negocios, cuenta desde su ejecución. Una operación dentro de una relación cuenta desde la terminación de la relación. La relación sigue viva, así que el plazo de diez años ni siquiera ha empezado. El 1 de enero de 2026 hay que conservar la documentación.

## Por qué importa

**No es una laguna.** Una laguna es un caso que la norma no trata. Aquí la Ley y el Reglamento que la desarrolla tratan el mismo caso, con la misma obligación, sobre el mismo documento, y dan respuestas opuestas: eliminar ya, o conservar hasta diez años después de un hecho que todavía no ha ocurrido.

Hay argumentos en los dos sentidos, y ninguno es un texto que zanje la cuestión:
- **A favor de contar desde la terminación:** el mismo art. 25.1 de la Ley, en su primer párrafo, cuenta la restricción de acceso desde la operación ocasional: «Transcurridos cinco años desde la terminación de la relación de negocios o la ejecución de la operación ocasional, la documentación conservada únicamente será accesible por los órganos de control interno». Y la letra a), sobre diligencia debida, también dice «la ejecución de la operación» sin «ocasional», aunque se refiere a documentación propia de la relación.
- **A favor de contar desde la ejecución:** es la letra de la Ley, y el Reglamento se declara su desarrollo (RD, art. 1).

**Las consecuencias van en los dos sentidos.**
- **Eliminar antes de tiempo** incumple la obligación de conservar. La Ley lo tipifica: «Constituirán infracciones graves las siguientes: [...] l) El incumplimiento de la obligación de conservación de documentos, en los términos del artículo 25» (art. 52.1).
- **Conservar más allá del plazo** incumple la obligación de eliminar del propio art. 25.1 («procediendo tras el mismo a su eliminación»). Si la documentación contiene datos personales, choca además con el principio de limitación del plazo de conservación del Reglamento (UE) 2016/679: los datos personales serán «mantenidos de forma que se permita la identificación de los interesados durante no más tiempo del necesario para los fines del tratamiento de los datos personales» (art. 5.1.e).

No hay una opción prudente. Conservar «por si acaso» es una de las dos lecturas, con su propio riesgo.

El Reglamento (UE) 2024/1624 (AMLR), que «será aplicable a partir del 10 de julio de 2027» (art. 90), no reproduce la divergencia: cuenta cinco años «a partir de la fecha de extinción de la relación de negocios o de la fecha en la que se ejecute la operación ocasional» (art. 77.3). Pero hasta esa fecha rige la Ley, y qué pasa con los plazos en curso ese día es otro caso que ningún texto resuelve.

## Qué hace la herramienta

[plazos-conservacion-pbc](https://github.com/mshodai/plazos-conservacion-pbc) calcula el estado de cada documento de un expediente en una fecha dada. Para una operación dentro de una relación de negocios, calcula las dos lecturas:

- **OP-1**, la letra de la Ley: diez años desde `fecha_ejecucion_operacion` (art. 25.1.b).
- **OP-2**, el Reglamento: diez años desde la terminación de la relación (RD, art. 29.1).

Si las dos dan el mismo estado, el régimen da ese estado. Si dan estados distintos, el régimen da `indeterminado` y muestra las dos lecturas con sus fechas. No elige una en silencio.

El escenario de este artículo es el [caso 04 del corpus](https://github.com/mshodai/plazos-conservacion-pbc/blob/main/corpus/04-operacion-en-relacion-viva.json) ([resultado esperado](https://github.com/mshodai/plazos-conservacion-pbc/blob/main/corpus/04-operacion-en-relacion-viva.esperado.json)), con datos sintéticos. Parte de la salida:

```
$ plazos-conservacion corpus/04-operacion-en-relacion-viva.json
Expediente EXP-FICTICIO-04
Fecha de referencia: 2026-01-01 · AMLR aplicable desde el 2027-07-10
[…]
== Documento DOC-FICTICIO-1 (operaciones)

Estado el 2026-01-01:
  ley_10_2010  indeterminado
  amlr         plazo_no_iniciado
  T-1          indeterminado
  T-2          indeterminado
  T-3          indeterminado
  T-4          indeterminado
[…]
Lecturas:
  ley_10_2010:
    OP-1: eliminacion_exigida (inicio 2015-05-20 · vence 2025-05-20) — Ley 25.1.b
    OP-2: plazo_no_iniciado — RD 29.1
[…]
```

Con la Ley, OP-1 exige eliminar desde el 21 de mayo de 2025 y OP-2 no ha empezado a contar: `indeterminado`. T-1 a T-4 son las cuatro lecturas de la transición al AMLR; antes del 10 de julio de 2027 las cuatro aplican la Ley, y por eso coinciden con ella. El régimen `amlr` se calcula para comparar, aunque todavía no sea aplicable: con él la divergencia desaparece y la documentación no ha empezado su plazo. El código de salida es 1.

Este es uno de los quince casos que el proyecto documenta en [docs/ambiguedades.md](https://github.com/mshodai/plazos-conservacion-pbc/blob/main/docs/ambiguedades.md) (S-3), cada uno con qué dice la norma, por qué no determina un comportamiento único, qué hace la implementación y cómo se señala en la salida.

## La consecuencia general

Una herramienta que devuelve «conservar hasta tal fecha» para este documento ha elegido entre la Ley y su Reglamento. Si devuelve el 20 de mayo de 2025, ha leído la Ley sobre la operación; si no devuelve fecha porque la relación sigue viva, ha seguido el Reglamento. Las dos respuestas son defendibles, y las dos tienen consecuencias legales si son las equivocadas.

**Cuando una norma y su desarrollo divergen, una herramienta que devuelve un solo plazo está tomando una decisión jurídica sin declararla.** Quien usa el resultado no sabe que ha habido una elección, ni cuál, ni que existía la otra.

La alternativa no es que la herramienta decida mejor, sino que no decida: que calcule las lecturas que los textos permiten, diga de qué artículo sale cada una y marque como indeterminado lo que los textos no determinan. La decisión sigue siendo necesaria, pero la toma quien responde de ella, sabiendo que la está tomando.

---

El código, la especificación, el corpus y las fuentes con su versión están en [github.com/mshodai/plazos-conservacion-pbc](https://github.com/mshodai/plazos-conservacion-pbc). El texto del Reglamento (UE) 2016/679 citado es el publicado en el «Diario Oficial de la Unión Europea» L 119 de 4.5.2016, tal como lo sirve el BOE (DOUE-L-2016-80807); su URL y su huella están en [docs/fuentes/FUENTES.md](https://github.com/mshodai/plazos-conservacion-pbc/blob/main/docs/fuentes/FUENTES.md).

Este artículo es un análisis de la arquitectura de una herramienta de cálculo, no asesoramiento jurídico.
