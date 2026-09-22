# Correcciones pendientes en el modelo de Enterprise Architect

Este archivo se escribe desde la Mac, donde no hay Enterprise Architect. Las
correcciones hay que aplicarlas en la máquina con Windows, sobre
`modelo-ea/shopMetrics.eapx`, y después volver a exportar los PNG a
`modelo-ea/export/`.

Cada hallazgo dice **qué dice cada fuente**, **por qué es un problema** y **qué
hacer**. El criterio que se usó para decidir cuál manda:

1. La **especificación del caso de uso** (punto 10.5.3) es la fuente principal:
   es lo que se acordó con la cátedra y lo que describe el comportamiento.
2. El **diccionario de datos** (punto 10.5.8) manda sobre la estructura.
3. Los **diagramas** tienen que reflejar a los dos. Cuando un diagrama dice algo
   distinto, se corrige el diagrama.

Los hallazgos 8 y 9 no son diferencias entre el diagrama y el modelo, sino
huecos del propio diccionario y del propio caso de uso: la corrección no está en
Enterprise Architect sino en el Word. Quedan acá igual, para tenerlos todos
juntos.

Estado al 22 de septiembre de 2026. Revisados en detalle: CU-017-001, CU-018-001,
CU-002-001, CU-003-001, CU-001-001, CU-004-001 y CU-011-001. Los demás se revisan
a medida que se construyen.

---

## 1. El doble factor no tiene dónde guardarse

**Dónde aparece**

| Fuente | Qué dice |
|---|---|
| CU-017-001, actores secundarios | "proveedor de 2FA" |
| CU-017-001, curso alternativo CA-2 | "Se requiere segundo factor (2FA): el sistema solicita el código de verificación antes de crear la sesión." |
| Diagrama de secuencia CU-017-001 | Fragmento `alt Requiere 2FA (A-2)` con cuatro mensajes: solicita código, pide el segundo factor, ingresa el código, verifica el código. |
| Diagrama de clases CU-017-001 | `AutenticacionService.verificar2FA(): boolean` |
| Diccionario de datos, entidad `usuario` | `id`, `nombre`, `email`, `password_hash`. **Nada más.** |

**El problema**

No es una diferencia entre el código y el documento: es una **inconsistencia
dentro del documento**. Los diagramas de comportamiento describen un segundo
factor que el modelo de datos no puede sostener: no hay dónde guardar el
secreto del usuario, ni si lo tiene activado, ni los códigos de recuperación.

**Qué hacer**

Se decidió **no implementar 2FA**. Para que el documento quede coherente con esa
decisión hay dos caminos, y hay que elegir uno:

- **Dejarlo como alternativa diferida.** En el diagrama de secuencia, renombrar
  el fragmento a `alt Requiere 2FA (A-2) — fuera del alcance de esta entrega`, y
  en el diagrama de clases sacar `verificar2FA()` de `AutenticacionService`. En
  el CU-017-001, agregar al final del CA-2 la frase "Este curso alternativo no
  se implementa en esta entrega".
- **Sostenerlo.** Agregar al diccionario de datos, en la entidad `usuario`, los
  campos `doble_factor_activo` (BOOLEAN) y `doble_factor_secreto` (VARCHAR), y
  regenerar el DER. Implica implementarlo.

Lo primero es más barato y honesto. Lo segundo deja un trabajo más completo.

---

## 2. `Rol` figura como enumeración y en el modelo de datos es una tabla

**Dónde aparece**

| Fuente | Qué dice |
|---|---|
| Diagrama de clases CU-017-001 | `Rol` con estereotipo **«enumeration»**, valores `ADMIN_CENTRO`, `GERENTE`, `LOCATARIO`, `OPERARIO`. Y `Usuario.rol: Rol`, **uno solo**. |
| Diccionario de datos | `rol` es una **tabla** con `id` (PK) y `nombre`. Y existe `usuario_rol`, tabla asociativa con PK compuesta `(usuario_id, rol_id)`: un usuario puede tener **varios** roles. |
| CU-018-001 | El administrador **crea y edita roles** en tiempo de ejecución. Una enumeración es fija en tiempo de compilación: no se puede crear un rol nuevo. |

**El problema**

Tres contradicciones encadenadas. El diagrama dice que los roles son un conjunto
cerrado, el modelo de datos dice que son registros, y el CU-018 dice que se
crean desde la aplicación. Además, el diagrama da un rol por usuario y el modelo
permite varios.

**Qué hacer**

Corregir el **diagrama de clases de CU-017-001**:

- Cambiar `Rol` de «enumeration» a clase común, con `id: UUID` y `nombre: String`.
- Cambiar `Usuario.rol: Rol` por `Usuario.roles: List<Rol>`.
- Dibujar la asociación `Usuario 0..* — 0..* Rol` con la clase asociativa
  `UsuarioRol`, o al menos con multiplicidad muchos a muchos.

El mismo cambio aplica al diagrama de clases de CU-018-001, que ya muestra
`Usuario.roles: List<Rol>` correctamente: ahí está bien, y por eso los dos
diagramas se contradicen entre sí.

---

## 3. El acceso a los centros no muestra su clase asociativa

**Dónde aparece**

| Fuente | Qué dice |
|---|---|
| Diagrama de clases CU-017-001 | `Usuario 1..* — 0..* CentroComercial`, una asociación simple. |
| Diccionario de datos | `centro_acceso`, con PK compuesta `(usuario_id, centro_id, rol_id)`. El rol **depende del centro**: el mismo usuario puede ser gerente en uno y locatario en otro. |
| CU-017-001, paso 4 | "Verifica el rol y el centro asignado". |

**El problema**

La asociación simple pierde el dato esencial: que el rol se ejerce *en un
centro*. Tal como está dibujado, el rol es global al usuario.

**Qué hacer**

En el diagrama de clases de CU-017-001, reemplazar la asociación simple por la
clase asociativa `CentroAcceso` con los tres extremos, o dibujar
`Usuario 1 — 0..* CentroAcceso 0..* — 1 CentroComercial` y
`CentroAcceso 0..* — 1 Rol`.

---

## 4. La enumeración de operaciones dice `SIN_ACCESO` donde el caso de uso dice `eliminación`

**Dónde aparece**

| Fuente | Qué dice |
|---|---|
| CU-018-001, paso 4 | "por nivel de acceso (solo lectura, selector **[lectura / escritura / eliminación / exportación]**, se almacena la operación del permiso)" |
| Diagrama de clases CU-018-001 | `Operacion` «enumeration»: `ESCRITURA`, `EXPORTACION`, `LECTURA`, **`SIN_ACCESO`** |

**El problema**

El diagrama cambió una de las cuatro operaciones. Y el reemplazo no es
equivalente: `SIN_ACCESO` no es una operación que se otorgue, es la ausencia de
permiso. Guardarlo como una fila de `permiso` contradice el modelo, donde un
registro en `rol_permiso` significa justamente que el permiso está concedido.

**Qué hacer**

En el diagrama de clases de CU-018-001, reemplazar `SIN_ACCESO` por
`ELIMINACION`.

El código ya usa las cuatro del caso de uso: `lectura`, `escritura`,
`eliminacion`, `exportacion`.

---

## 5. `Rol.descripcion` está en el caso de uso y en el diagrama, pero no en el modelo de datos

**Dónde aparece**

| Fuente | Qué dice |
|---|---|
| CU-018-001, paso 2 | "Muestra la lista de roles existentes: nombre del rol, **descripción** (solo lectura, texto, solo visualización) y cantidad de usuarios asignados" |
| Diagrama de clases CU-018-001 | `Rol` con `descripcion: String` |
| Diccionario de datos, entidad `rol` | `id` y `nombre`. **Falta `descripcion`.** |

**El problema**

El caso de uso y el diagrama coinciden; el que quedó corto es el diccionario. Es
un campo faltante, no una contradicción de criterio.

**Qué hacer**

Agregar al diccionario de datos, entidad `rol`, el campo:

| Campo | Tipo | Clave | Descripción |
|---|---|---|---|
| `descripcion` | VARCHAR | | Texto que explica el alcance del rol. |

Regenerar el DER y volver a exportar. El esquema de la base se regenera solo con
`make esquema`.

---

## 6. El atributo del permiso se llama distinto en el diagrama y en el modelo

**Dónde aparece**

| Fuente | Qué dice |
|---|---|
| Diagrama de clases CU-018-001 | `Permiso.categoria: CategoriaRecurso` |
| Diccionario de datos, entidad `permiso` | `recurso` y `operacion` |

**El problema**

Dos nombres para lo mismo. No cambia el comportamiento, pero obliga a traducir
mentalmente al leer los dos documentos juntos, que es justamente lo que las
convenciones del proyecto buscan evitar.

**Qué hacer**

En el diagrama de clases de CU-018-001, renombrar `categoria` a `recurso`. El
tipo `CategoriaRecurso` puede quedarse con ese nombre: describe el conjunto de
valores, no el atributo.

---

## 7. La notificación de cambio de permisos no está en el diagrama de secuencia

**Dónde aparece**

| Fuente | Qué dice |
|---|---|
| CU-018-001, paso 10 | "Notifica a los usuarios afectados sobre el cambio en sus permisos: destinatario, ..." |
| Diagrama de clases CU-018-001 | `ServicioNotificaciones.notificarCambioPermisos(): void` — **sí está** |
| Diagrama de secuencia CU-018-001 | Hay que verificarlo en la máquina con EA: si el mensaje no aparece, falta. |

**Qué hacer**

Abrir el diagrama de secuencia de CU-018-001 y confirmar que exista el mensaje
hacia `ServicioNotificaciones` después de registrar en auditoría. Si no está,
agregarlo.

En el código, la notificación todavía no se implementa: llega con el dominio de
notificaciones, que el plan no ubica en ninguna semana explícita. Conviene
decidir en qué semana entra.

---

## 8. Un local vacante no se puede representar, y la vacancia es uno de los KPIs

**Dónde aparece**

| Fuente | Qué dice |
|---|---|
| Punto 4, tablero del centro | "Indicadores clave (tráfico actual, conversión, ventas del día, **vacancia**)" |
| CU-011-001, paso 2 | "vacancia: solo lectura, decimal, expresada como porcentaje, calculado, no se almacena" |
| Diccionario de datos, entidad `local` | `locatario_id` — "Locatario que ocupa el local." Sin marca de nulo, así que el esquema lo genera `NOT NULL`. |

**El problema**

Si todo local tiene que tener un locatario, un local vacío no existe en el
modelo. La vacancia calculada sobre esa base da cero siempre, y no porque el
centro esté lleno: porque la pregunta no se puede formular.

Es el único de los cuatro indicadores del tablero que el modelo de datos no
sostiene. Los otros tres --tráfico, conversión y ventas-- salen de las series y
ya están calculándose contra datos reales.

**Qué hacer**

Hay dos caminos y conviene elegir a conciencia, porque significan cosas
distintas:

1. **`locatario_id` pasa a admitir nulos.** Un local sin locatario es un local
   vacante. Es lo más simple y no agrega entidades.
2. **Agregar `local.estado`** con los valores `ocupado`, `vacante` y `en obra`.
   Distingue el local que se está refaccionando del que está disponible para
   alquilar, que para un centro comercial no es lo mismo.

Si se elige el primero, en el diccionario de datos, entidad `local`, la
descripción del campo pasa a:

| Campo | Tipo | Clave | Descripción |
|---|---|---|---|
| `locatario_id` | UUID | FK | Locatario que ocupa el local. Nulo si el local está vacante. |

La palabra «nulo» en la descripción es lo que hace que el generador del esquema
emita la columna sin `NOT NULL`, así que el texto importa.

En el diagrama de clases, la multiplicidad de `Locatario` hacia `Local` pasa de
`1` a `0..1`.

El cálculo ya está escrito y no hay que tocarlo: `dominios/metricas/servicio.py`
cuenta los locales sin locatario sobre el total. Mientras tanto el indicador
viaja marcado como dato parcial, con el aviso que nombra esta corrección, que es
el curso alternativo CA-1 del propio caso de uso.

---

## 9. La latencia promedio del paso 5 del CU-001-001 no tiene dónde guardarse

**Dónde aparece**

| Fuente | Qué dice |
|---|---|
| CU-001-001, paso 5 | "latencia promedio (solo lectura, decimal, en milisegundos, **calculado, no se almacena**)" |
| Diccionario de datos | No hay ninguna entidad que registre los tiempos de respuesta de un conector. |

**El problema**

Un **promedio** es de varias mediciones, y sin guardarlas no hay sobre qué
promediar. El caso de uso pide las dos cosas a la vez: que sea promedio y que no
se almacene.

**Qué hacer**

Lo implementado hoy es lo único consistente con "no se almacena": la latencia
que muestra el detalle es la del sondeo de ese momento --el ida y vuelta real
contra el sistema externo-- y no un promedio. Alcanza para lo que el paso
necesita, que es diagnosticar.

Si se quiere el promedio de verdad hay que decidirlo y agregarlo al diccionario,
por ejemplo una entidad `sondeo_integracion` con `conector_id`, `ts`,
`latencia_ms` y `resultado`, que además daría el "historial de errores recientes"
que el mismo paso 5 pide y que hoy tampoco tiene dónde vivir.

Mientras no se decida, conviene cambiar el texto del caso de uso de "latencia
promedio" a "latencia del último sondeo", para que el documento describa lo que
el sistema hace.

---

## Lo que sí está bien

Para que quede constancia de lo revisado y no se vuelva a mirar:

- **CU-002-001.** El diagrama de secuencia está completo y es implementable tal
  cual: los cinco participantes, la validación contra el POS externo antes de
  guardar, el cifrado de las credenciales, el arranque de la ingesta, el
  registro en auditoría y el curso alternativo CA-1 por credenciales inválidas o
  tiempo agotado. No hay nada que corregir.
- **Los 31 casos de uso tienen su diagrama de secuencia y su diagrama de
  clases.** Verificado por `scripts/diagramas/balanceo.py`, control B.
- **El diccionario de datos coincide con el esquema de la base**, entidad por
  entidad y campo por campo. Verificado por `api/nivelacion.py`, control A, del
  repositorio de implementación.

---

## Cómo verificar después de corregir

Desde el repositorio de documentación:

```
python3 scripts/diagramas/balanceo.py
```

Desde el de implementación, con Docker levantado:

```
make esquema && make limpiar && make arriba && make probar && make nivelar
```
