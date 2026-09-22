# ShopMetrics — Trabajo Final de Ingeniería (UAI)

Este repositorio guarda **la documentación** del trabajo final. La
implementación del sistema vive aparte, en
[javieravellanedaa/shopmetrics](https://github.com/javieravellanedaa/shopmetrics):
esquema de base de datos, entorno de desarrollo y código.

| Carpeta | Contenido |
|---|---|
| `documento/` | El informe (`.docx` y su PDF), el presupuesto financiero (`.xlsx`), las capturas del punto 8 (`img_punto8/`) y los diagramas en draw.io con sus exportaciones (`diagramas/`). |
| `modelo-ea/CORRECCIONES-PENDIENTES.md` | Diferencias encontradas entre los diagramas, las especificaciones de casos de uso y el diccionario de datos, con qué hacer en cada una. Se aplican desde la máquina con Enterprise Architect. |
| `modelo-ea/` | Proyecto de Enterprise Architect (`shopMetrics.eapx`) y sus exportaciones: DER por área, y diagramas de clases y de secuencia de los 31 casos de uso. |
| `scripts/diagramas/` | Generadores de los diagramas del punto 10 a partir del diccionario de datos del Word, más `validar.py` y `balanceo.py`. |
| `scripts/enterprise-architect/` | Scripts que construyeron el modelo de Enterprise Architect y sus DER. |
| `scripts/historico/` | Scripts de PowerShell y Python con los que se corrigieron el Word y el Excel desde la máquina Windows. Tienen rutas absolutas de esa máquina; se conservan como registro. |

## Verificaciones

Desde la raíz del repositorio:

```
python3 scripts/diagramas/balanceo.py
```

Cruza el diccionario de datos, el índice de casos de uso, los diagramas de
secuencia y de clases, las exportaciones de Enterprise Architect y los
`.drawio`. Controla integridad referencial, correspondencia uno a uno entre
casos de uso y diagramas, y que ninguna arista atraviese una caja. Devuelve
código 1 si algún control falla.

```
python3 scripts/diagramas/validar.py <archivo.drawio> <imagen.png> <escala>
```

Controla sobre un diagrama que el acomodo automático haya corrido, que ninguna
caja se superponga y que la exportación contenga el dibujo completo.
