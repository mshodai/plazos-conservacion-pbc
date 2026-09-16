# Fuentes

Documentos oficiales que usa el proyecto. Los PDF no se redistribuyen (están en `.gitignore`), así que cada uno debe descargarse de su URL y guardarse en `docs/fuentes/` con el nombre indicado.

Estas copias proceden del proyecto `calculo-titularidad-real` (`docs/fuentes/`). Su SHA-256 coincide con el que figura allí para los mismos ficheros, así que son la misma versión.

**Qué significa cada columna:**

- **Autor.** Órgano emisor, tal como figura en la cabecera del documento. Entre paréntesis, el editor del PDF según sus metadatos (`pdfinfo`).
- **Versión o fecha declarada.** Copiada literalmente del documento.
- **Fecha de descarga.** Es la de la descarga original: la fecha de creación de los ficheros en `calculo-titularidad-real`. Las copias de este repositorio se crearon el 2026-09-16 al copiarlas. Los metadatos de origen de macOS (`kMDItemWhereFroms`) confirman que se descargaron de `https://www.boe.es/` o de `https://eur-lex.europa.eu/`, pero no guardan la URL completa.
- **URL.** Es la dirección canónica deducida del identificador de cada documento, tomada de `calculo-titularidad-real`. Allí se comprobó el 2026-09-15:
  - las del BOE devuelven un fichero idéntico al local (mismo SHA-256);
  - EUR-Lex respondió a la descarga automática con `202` y un cuerpo vacío, así que su URL **no se ha podido comprobar**.

  En este repositorio no se han vuelto a comprobar.

## Documentos

| Fichero | Título | Autor | Versión o fecha declarada | Descarga | URL |
|---|---|---|---|---|---|
| `BOE-A-2010-6737-consolidado.pdf` | Ley 10/2010, de 28 de abril, de prevención del blanqueo de capitales y de la financiación del terrorismo | Jefatura del Estado (Agencia Estatal Boletín Oficial del Estado) | Texto consolidado. «Última modificación: 21 de marzo de 2026». Original: «BOE» núm. 103, de 29 de abril de 2010 | 2026-09-15 | https://www.boe.es/buscar/pdf/2010/BOE-A-2010-6737-consolidado.pdf · ficha: https://www.boe.es/buscar/act.php?id=BOE-A-2010-6737 |
| `BOE-A-2014-4742-consolidado.pdf` | Real Decreto 304/2014, de 5 de mayo, por el que se aprueba el Reglamento de la Ley 10/2010, de 28 de abril, de prevención del blanqueo de capitales y de la financiación del terrorismo | Ministerio de Economía y Competitividad (Agencia Estatal Boletín Oficial del Estado) | Texto consolidado. «Última modificación: 24 de abril de 2024». Original: «BOE» núm. 110, de 06 de mayo de 2014 | 2026-09-15 | https://www.boe.es/buscar/pdf/2014/BOE-A-2014-4742-consolidado.pdf · ficha: https://www.boe.es/buscar/act.php?id=BOE-A-2014-4742 |
| `OJ_L_202401624_ES_TXT.pdf` | Reglamento (UE) 2024/1624 del Parlamento Europeo y del Consejo, de 31 de mayo de 2024, relativo a la prevención de la utilización del sistema financiero para el blanqueo de capitales o la financiación del terrorismo (AMLR) | Parlamento Europeo y Consejo (Oficina de Publicaciones de la Unión Europea) | Texto publicado, no consolidado: «DO L de 19.6.2024». No declara fecha de modificación. Art. 90: aplicable a partir del 10 de julio de 2027 (10 de julio de 2029 para las entidades del art. 3, punto 3, letras n) y o)) | 2026-09-15 | https://eur-lex.europa.eu/legal-content/ES/TXT/PDF/?uri=OJ:L_202401624 (sin comprobar) · ELI impreso en el documento: http://data.europa.eu/eli/reg/2024/1624/oj |

## Huellas SHA-256

Sirven para comprobar que una copia local es la misma versión con la que se hizo el análisis. El BOE y EUR-Lex regeneran los PDF cuando cambia el texto consolidado, así que una huella distinta indica una versión distinta.

```
4782a40bcf44165a97bc361520fd2b348acf7efbdfaa0a8d876c58332ff8601d  BOE-A-2010-6737-consolidado.pdf
59d7be80313780a8cf48e1f3f87b5bd2860855a126472c0374e1c30c7fc19f0d  BOE-A-2014-4742-consolidado.pdf
666f18e1b5d4dd6bb7e927328bd8d84420d0919e692288f0b917c357df690974  OJ_L_202401624_ES_TXT.pdf
```

Para comprobarlas: `cd docs/fuentes && shasum -a 256 -c` pegando el bloque anterior en la entrada estándar.
