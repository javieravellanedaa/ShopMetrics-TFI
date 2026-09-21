# Scripts de Enterprise Architect

Scripts con los que se corrigió y se regeneró el modelo de datos (DER) dentro de
`shopMetrics/shopMetrics/enterprise_architect/shopMetrics.eapx`.

Los `.ps1` usan la API COM de Enterprise Architect (`EA.Repository`), así que
necesitan EA instalado y **el proyecto cerrado** mientras corren. Los `.py`
necesitan `python-docx`, `Pillow` y `PyMuPDF`.

## 1. Análisis (solo lectura)

| Archivo | Qué hace |
|---|---|
| `_dump.py` | Extrae los 31 casos de uso del Word a `casos_uso.txt` |
| `_dic.py` | Extrae el diccionario de datos del Word a `dic.json` |
| `ea_inspect.ps1` | Lista los diagramas del proyecto |
| `ea_der.ps1` | Lista entidades, conectores y cardinalidades del DER |
| `ea_attr.ps1` | Lista los atributos de cada entidad |

## 2. Corrección del modelo

| Archivo | Qué hace |
|---|---|
| `ea_fix1.ps1` | Notación pata de gallo, corrige 3 cardinalidades y agrega las FK faltantes |
| `ea_fix2.ps1` | Crea las 5 entidades nuevas y los 19 conectores |
| `ea_fix3.ps1` | Ordena atributos (PK, FK, resto) y agrega las entidades nuevas al diagrama |
| `ea_fix4.ps1` | Primera grilla por áreas del DER maestro |
| `ea_fix5.ps1` | Borra la geometría vieja de los conectores (`t_diagramlinks`) |
| `ea_fix6.ps1` | Elimina un atributo corrupto y muestra los campos en orden |

## 3. Diagramas

| Archivo | Qué hace |
|---|---|
| `ea_sub2.ps1` | Genera los 8 DER por área (`export/der/`) — versión final |
| `ea_completo.ps1` | Genera el **DER completo** con todas las columnas y tipos — versión final |
| `layout2.py`, `layout4.py`, `refina.py` | Optimizador de la grilla del DER integrado (evita líneas sobre cajas y cruces) |
| `ea_final3.ps1` | Aplica en EA la grilla que sale del optimizador (`grilla.json`) |
| `medir.py` | Calcula qué tamaño de hoja necesita el DER completo |
| `recorta2.py`, `crop_completo.py` | Recortan el marco y el espacio blanco del PNG exportado |
| `generar_pdf_A3.py` | Arma `DER_ShopMetrics_completo_A3.pdf` |

## 4. Verificación

| Archivo | Qué hace |
|---|---|
| `ea_export_model.ps1` | Exporta el modelo a `modelo_ea.txt` para compararlo contra el diccionario del Word |

## Versiones descartadas

`ea_sub.ps1`, `ea_final.ps1`, `ea_final2.ps1`, `layout.py` y `pack.py` son intentos
anteriores que se reemplazaron por las versiones de arriba. Se conservan como
registro del proceso.

## Datos

`dic.json`, `casos_uso.txt`, `grilla.json`, `grilla4.json`, `pack.json`,
`altos.json` y `modelo_ea.txt` son las entradas y salidas intermedias de los scripts.
