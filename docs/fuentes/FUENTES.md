# Fuentes

Documentos oficiales que usa el proyecto. Los PDF no se redistribuyen (están en `.gitignore`), así que cada uno debe descargarse de su URL y guardarse en `docs/fuentes/` con el nombre indicado.

Hay dos grupos:

- **Normativa de conservación** (Ley 10/2010, RD 304/2014 y AMLR): la que aplica el cálculo. Estas copias proceden del proyecto `calculo-titularidad-real` (`docs/fuentes/`). Su SHA-256 coincide con el que figura allí para los mismos ficheros, así que son la misma versión.
- **Reglamento (UE) 2016/679** (RGPD): no interviene en el cálculo. Lo cita el artículo de la portada del sitio ([`docs/index.md`](../index.md)), por el principio de limitación del plazo de conservación (art. 5.1.e). Se descargó directamente para este repositorio.

**Qué significa cada columna:**

- **Autor.** Órgano emisor, tal como figura en la cabecera del documento. Entre paréntesis, el editor del PDF según sus metadatos (`pdfinfo`).
- **Versión o fecha declarada.** Copiada literalmente del documento.
- **Fecha de descarga.** En la normativa de conservación, es la de la descarga original: la fecha de creación de los ficheros en `calculo-titularidad-real`. Las copias de este repositorio se crearon el 2026-09-16 al copiarlas. Los metadatos de origen de macOS (`kMDItemWhereFroms`) confirman que se descargaron de `https://www.boe.es/` o de `https://eur-lex.europa.eu/`, pero no guardan la URL completa.
- **URL.** Es la dirección canónica deducida del identificador de cada documento, tomada de `calculo-titularidad-real`. Allí se comprobó el 2026-09-15:
  - las del BOE devuelven un fichero idéntico al local (mismo SHA-256);
  - EUR-Lex respondió a la descarga automática con `202` y un cuerpo vacío, así que su URL **no se ha podido comprobar**.

  En este repositorio no se han vuelto a comprobar.

  El RGPD se descargó del BOE el 2026-09-17 con `curl` desde la URL indicada. Una segunda descarga ese mismo día dio el mismo SHA-256.

## Documentos

| Fichero | Título | Autor | Versión o fecha declarada | Descarga | URL |
|---|---|---|---|---|---|
| `BOE-A-2010-6737-consolidado.pdf` | Ley 10/2010, de 28 de abril, de prevención del blanqueo de capitales y de la financiación del terrorismo | Jefatura del Estado (Agencia Estatal Boletín Oficial del Estado) | Texto consolidado. «Última modificación: 21 de marzo de 2026». Original: «BOE» núm. 103, de 29 de abril de 2010 | 2026-09-15 | https://www.boe.es/buscar/pdf/2010/BOE-A-2010-6737-consolidado.pdf · ficha: https://www.boe.es/buscar/act.php?id=BOE-A-2010-6737 |
| `BOE-A-2014-4742-consolidado.pdf` | Real Decreto 304/2014, de 5 de mayo, por el que se aprueba el Reglamento de la Ley 10/2010, de 28 de abril, de prevención del blanqueo de capitales y de la financiación del terrorismo | Ministerio de Economía y Competitividad (Agencia Estatal Boletín Oficial del Estado) | Texto consolidado. «Última modificación: 24 de abril de 2024». Original: «BOE» núm. 110, de 06 de mayo de 2014 | 2026-09-15 | https://www.boe.es/buscar/pdf/2014/BOE-A-2014-4742-consolidado.pdf · ficha: https://www.boe.es/buscar/act.php?id=BOE-A-2014-4742 |
| `OJ_L_202401624_ES_TXT.pdf` | Reglamento (UE) 2024/1624 del Parlamento Europeo y del Consejo, de 31 de mayo de 2024, relativo a la prevención de la utilización del sistema financiero para el blanqueo de capitales o la financiación del terrorismo (AMLR) | Parlamento Europeo y Consejo (Oficina de Publicaciones de la Unión Europea) | Texto publicado, no consolidado: «DO L de 19.6.2024». No declara fecha de modificación. Art. 90: aplicable a partir del 10 de julio de 2027 (10 de julio de 2029 para las entidades del art. 3, punto 3, letras n) y o)) | 2026-09-15 | https://eur-lex.europa.eu/legal-content/ES/TXT/PDF/?uri=OJ:L_202401624 (comprobado el 22/09/2026 por descarga) · ELI impreso en el documento: http://data.europa.eu/eli/reg/2024/1624/oj |
| `DOUE-L-2016-80807.pdf` | Reglamento (UE) 2016/679 del Parlamento Europeo y del Consejo, de 27 de abril de 2016, relativo a la protección de las personas físicas en lo que respecta al tratamiento de datos personales y a la libre circulación de estos datos y por el que se deroga la Directiva 95/46/CE (Reglamento general de protección de datos) | Parlamento Europeo y Consejo (Publications Office) | Texto original publicado, no consolidado: «Diario Oficial de la Unión Europea» L 119/1, «4.5.2016». No incluye correcciones de errores posteriores a esa publicación. Art. 99.2: «Será aplicable a partir del 25 de mayo de 2018» | 2026-09-17 | https://www.boe.es/doue/2016/119/L00001-00088.pdf · ficha en el BOE: https://www.boe.es/buscar/doc.php?id=DOUE-L-2016-80807 |

## Huellas SHA-256

Sirven para comprobar que una copia local es la misma versión con la que se hizo el análisis. El BOE y EUR-Lex regeneran los PDF cuando cambia el texto consolidado, así que una huella distinta indica una versión distinta.

```
4782a40bcf44165a97bc361520fd2b348acf7efbdfaa0a8d876c58332ff8601d  BOE-A-2010-6737-consolidado.pdf
59d7be80313780a8cf48e1f3f87b5bd2860855a126472c0374e1c30c7fc19f0d  BOE-A-2014-4742-consolidado.pdf
666f18e1b5d4dd6bb7e927328bd8d84420d0919e692288f0b917c357df690974  OJ_L_202401624_ES_TXT.pdf
a2fa3289de2f124c92748a181ad1499411b24ee3d26c74bd12781afa43cfa481  DOUE-L-2016-80807.pdf
```

Para comprobarlas: `cd docs/fuentes && shasum -a 256 -c` pegando el bloque anterior en la entrada estándar.

## Datos para la vigilancia automática

Repite en formato legible por máquina el fichero, la URL de descarga y la huella SHA-256 de cada documento de las secciones anteriores. Lo lee el script de `vigilancia-fuentes`, que comprueba que coincida con el texto. Si difieren, prevalece el texto.

```json
{
  "documentos": [
    {
      "fichero": "BOE-A-2010-6737-consolidado.pdf",
      "url": "https://www.boe.es/buscar/pdf/2010/BOE-A-2010-6737-consolidado.pdf",
      "sha256": "4782a40bcf44165a97bc361520fd2b348acf7efbdfaa0a8d876c58332ff8601d"
    },
    {
      "fichero": "BOE-A-2014-4742-consolidado.pdf",
      "url": "https://www.boe.es/buscar/pdf/2014/BOE-A-2014-4742-consolidado.pdf",
      "sha256": "59d7be80313780a8cf48e1f3f87b5bd2860855a126472c0374e1c30c7fc19f0d"
    },
    {
      "fichero": "OJ_L_202401624_ES_TXT.pdf",
      "url": "https://eur-lex.europa.eu/legal-content/ES/TXT/PDF/?uri=OJ:L_202401624",
      "sha256": "666f18e1b5d4dd6bb7e927328bd8d84420d0919e692288f0b917c357df690974"
    },
    {
      "fichero": "DOUE-L-2016-80807.pdf",
      "url": "https://www.boe.es/doue/2016/119/L00001-00088.pdf",
      "sha256": "a2fa3289de2f124c92748a181ad1499411b24ee3d26c74bd12781afa43cfa481"
    }
  ]
}
```
