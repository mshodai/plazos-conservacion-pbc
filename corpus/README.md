# Corpus

Expedientes sintéticos con su resultado esperado. Lo genera `corpus/generar.py`, que comprueba cada caso con el código de `src/` antes de escribirlo. No se edita a mano.

```
python corpus/generar.py
```

Cada caso tiene la entrada (`NN-nombre.json`, según `docs/modelo-datos.md`) y el resultado esperado (`NN-nombre.esperado.json`): el estado del documento en los seis regímenes en la fecha de referencia, sus lecturas con sus fechas, los avisos y la línea temporal de cada régimen. Los resultados esperados están escritos a mano en `generar.py` a partir de `docs/especificacion-calculo.md`. El código de salida es el de `plazos-conservacion` (§9.3): 0 si los seis regímenes dan el mismo estado y ninguno es `indeterminado`; 1 si no.

| Caso | Referencia | ley_10_2010 | amlr | T-1 | T-2 | T-3 | T-4 | Código |
|---|---|---|---|---|---|---|---|---|
| 01-mismo-estado-en-los-seis | 2030-01-01 | en_conservacion | en_conservacion | en_conservacion | en_conservacion | en_conservacion | en_conservacion | 0 |
| 02-restringido-en-la-ley-suprimido-en-el-amlr | 2035-01-01 | acceso_restringido | supresion_exigida | supresion_exigida | supresion_exigida | supresion_exigida | acceso_restringido | 1 |
| 03-plazo-en-curso-el-10-de-julio-de-2027 | 2028-06-30 | acceso_restringido | supresion_exigida | acceso_restringido | supresion_exigida | en_conservacion | acceso_restringido | 1 |
| 04-operacion-en-relacion-viva | 2026-01-01 | indeterminado | plazo_no_iniciado | indeterminado | indeterminado | indeterminado | indeterminado | 1 |
| 05-examen-especial-cinco-lecturas | 2031-02-18 | indeterminado | supresion_exigida | indeterminado | supresion_exigida | indeterminado | indeterminado | 1 |
| 06-control-interno-sin-regla-en-el-amlr | 2030-06-01 | en_conservacion | sin_regla | sin_regla | sin_regla | sin_regla | en_conservacion | 1 |
| 07-prorroga-de-la-autoridad | 2035-06-01 | acceso_restringido | conservacion_prorrogada | conservacion_prorrogada | conservacion_prorrogada | conservacion_prorrogada | acceso_restringido | 1 |
| 08-procedimiento-judicial-pendiente | 2033-03-01 | eliminacion_exigida | indeterminado | eliminacion_exigida | indeterminado | eliminacion_exigida | eliminacion_exigida | 1 |

## Qué demuestra cada caso

**01-mismo-estado-en-los-seis.** Diligencia debida de una relación terminada el 2028-01-01, a fecha 2030-01-01. Los seis regímenes dan en_conservacion: la Ley vence el 2038-01-01 y el AMLR el 2033-01-01, y los dos plazos están en curso. Código 0, aunque la línea temporal muestra que divergen desde el 2033-01-02: el código solo mira la fecha de referencia (§9.3).

**02-restringido-en-la-ley-suprimido-en-el-amlr.** Diligencia debida de una relación terminada el 2029-06-30, a fecha 2035-01-01. El mismo día (2034-07-01) en que la Ley pasa a acceso restringido (quinto año, D-4), el AMLR exige suprimir (V + 1, D-2). T-1 a T-3 siguen el AMLR porque el plazo empieza después de A; T-4 mantiene la Ley.

**03-plazo-en-curso-el-10-de-julio-de-2027.** Diligencia debida de una relación terminada el 2021-10-31, cuyo plazo de la Ley sigue en curso el 2027-07-10. A fecha 2028-06-30 las lecturas de la transición no coinciden: T-1 y T-4 mantienen la Ley (acceso restringido), T-2 aplica el AMLR desde H y exige suprimir desde A, y T-3 cuenta desde A con el límite de la Ley y vuelve a en_conservacion sin restricción. T-1 y T-4 no pueden diferir aquí: para un plazo que empezó antes de A, las dos son la Ley (§4.2).

**04-operacion-en-relacion-viva.** Operación ejecutada el 2015-05-20 dentro de una relación que sigue viva, a fecha 2026-01-01. Con la letra de la Ley (OP-1, art. 25.1.b) la operación ya debía eliminarse el 2025-05-21; con el RD (OP-2, art. 29.1) su plazo no ha empezado, porque cuenta desde la terminación. La Ley queda indeterminado (D-6), y T-1 a T-4 con ella, porque es antes de A. La línea temporal no cambia al pasar de en_conservacion a eliminacion_exigida en OP-1: el estado del régimen sigue siendo indeterminado (D-26).

**05-examen-especial-cinco-lecturas.** Examen especial (apertura 2021-01-10, cierre 2021-02-15, decisión 2021-02-20, comunicación 2021-02-25) de una relación terminada el 2022-03-31, a fecha 2031-02-18. El RD 25.4 no dice desde cuándo cuentan los diez años: EE-1 y EE-2 ya exigen eliminar, EE-3 a EE-5 siguen en acceso restringido, y la Ley da indeterminado. El AMLR cuenta desde la terminación y exige suprimir desde el 2027-04-01.

**06-control-interno-sin-regla-en-el-amlr.** Análisis de riesgo del 2028-01-15, sustituido el 2029-01-15, en el expediente de una operación ocasional del 2028-02-01, a fecha 2030-06-01. La Ley (RD 29.2) lo conserva diez años con las lecturas CI-1 a CI-3, que hoy coinciden. El art. 77.1 del AMLR no lo incluye: sin_regla (D-17), con las lecturas SR-1 a SR-3. T-1 a T-3 quedan en sin_regla desde A; T-4 sigue la Ley.

**07-prorroga-de-la-autoridad.** Diligencia debida de una relación terminada el 2028-09-30, con un requerimiento de la autoridad del 2033-05-01 para conservarla hasta el 2036-12-31, a fecha 2035-06-01. En el AMLR, conservación prorrogada del 2033-10-01 al 2036-12-31 (art. 77.3, D-11, D-12); en la Ley, que no tiene prórroga, acceso restringido hasta el 2038-09-30. T-4 elimina por la Ley el 2038-10-01, porque la Ley acaba después que la prórroga (D-24). Como la línea temporal proyecta los hechos de hoy (D-25), la prórroga aparece aunque se requirió después de empezar el plazo.

**08-procedimiento-judicial-pendiente.** Diligencia debida de una relación terminada el 2019-11-30, relacionada con un procedimiento judicial pendiente el 2027-07-10, a fecha 2033-03-01. El AMLR ya exigía suprimir desde el 2024-12-01, pero el art. 77.4 permite conservar desde el 2027-07-10: hasta el 2032-07-10 sin período adicional (PA-1) o hasta el 2037-07-10 con él (PA-2). Hoy PA-1 exige suprimir y PA-2 permite conservar: indeterminado (D-13). La Ley, sin excepción judicial, exige eliminar desde el 2029-12-01, y T-3 también (D-23).
