# -*- coding: utf-8 -*-
"""El guion del recorrido: que se ve en cada cuadro y que dice el rotulo.

Cada paso dice a que caso de uso pertenece y que tiene que hacer la persona,
en segunda persona y sin jerga: el video es para mostrarlo en la defensa, no
para el que escribio el codigo.

El recorrido pasa por los **cuatro roles** del sistema y toca **todos los
controles** de cada pantalla, incluidos los que rechazan: el ingreso con
credenciales que no sirven, el gerente que no puede escribir, la accion
correctiva que no resuelve, la validacion que rechaza un umbral imposible.

`armar_video.py` lo usa para componer los rotulos sobre las capturas.
"""

# Los casos de uso que recorre el video, en orden. Cada uno abre con una placa.
CASOS = {
    "CU-017-001": {
        "nombre": "Iniciar sesión en la plataforma",
        "resumen": "El sistema reconoce a la persona y la lleva al panel que "
                   "corresponde a su rol. Son cuatro roles y cuatro destinos.",
    },
    "CU-018-001": {
        "nombre": "Permisos granulares de acceso a datos",
        "resumen": "Cada rol ve y puede hacer lo que su fila de la matriz "
                   "permite. El menú se recorta y el backend rechaza lo demás.",
    },
    "CU-011-001": {
        "nombre": "Consultar el tablero de indicadores del centro",
        "resumen": "Tráfico, conversión, ventas y vacancia, con sus tres "
                   "períodos y el detalle hora por hora.",
    },
    "CU-004-001": {
        "nombre": "Consultar el mapa del centro y sus zonas",
        "resumen": "La circulación de personas por zona y qué zonas tienen "
                   "cobertura de sensores.",
    },
    "CU-001-001": {
        "nombre": "Monitorear el estado de las integraciones",
        "resumen": "Ver qué fuentes están trayendo datos y actuar sobre las "
                   "que dejaron de hacerlo, con las tres acciones correctivas.",
    },
    "CU-006-001": {
        "nombre": "Configurar una alerta por umbral",
        "resumen": "Definir sobre qué indicador, con qué condición y a quién "
                   "avisarle. Con las validaciones que rechazan.",
    },
    "CU-026-001": {
        "nombre": "Monitorear el centro de alertas críticas",
        "resumen": "La bandeja ordenada por gravedad, con sus tres filtros y "
                   "el tiempo que queda para atender cada alerta.",
    },
    "CU-007-001": {
        "nombre": "Atender y resolver una alerta",
        "resumen": "Tomar la alerta, recorrer el checklist y cerrarla. Hay "
                   "tres formas de cerrar y las tres dejan traza.",
    },
}

# Un paso por captura: (archivo, caso de uso, titulo, detalle, nota al pie).
PASOS = [
    # ---------------------------------------------- ingreso y los cuatro roles
    ("v01", "CU-017-001", "Abrí el sistema",
     "La pantalla de acceso es la misma para los cuatro perfiles: "
     "administrador, gerente, operaciones y locatario.", None),

    ("v02", "CU-017-001", "Probá con credenciales que no sirven",
     "El sistema rechaza el ingreso con un mensaje corto.",
     "Dice lo mismo si el correo no existe que si la clave está mal. Decir "
     "cuál de los dos falló le regalaría a un atacante la lista de correos "
     "dados de alta."),

    ("v03", "CU-017-001", "Entrá como administrador del centro",
     "Con las credenciales correctas, el sistema te lleva al panel que "
     "corresponde a tu rol.",
     "El administrador tiene las veinte celdas de la matriz de permisos, así "
     "que el menú le muestra las cinco secciones."),

    ("v04", "CU-018-001", "Ahora entrá como gerente",
     "El gerente ve el mismo menú: su rol lee los cinco recursos.",
     "Abajo a la izquierda cambia el nombre y el rol. Los indicadores son los "
     "mismos, porque el gerente supervisa el mismo centro."),

    ("v05", "CU-018-001", "Intentá una acción correctiva siendo gerente",
     "El gerente lee y exporta, pero no escribe. El sistema lo rechaza y "
     "explica por qué.",
     "«Tu rol no tiene permiso para escritura sobre configuracion.» La "
     "decisión la toma el backend, no la pantalla."),

    ("v06", "CU-017-001", "Entrá como operaciones",
     "Este rol va a otro destino: «Mi turno». La vista propia se construye en "
     "la semana 9, así que por ahora dice qué va a traer y a qué puede entrar "
     "hoy.",
     "El menú se recortó: sin Reglas de alerta ni Integraciones, porque "
     "operaciones no tiene permiso sobre configuración."),

    ("v07", "CU-018-001", "Forzá la URL de una sección que no te corresponde",
     "Aunque el menú no la muestre, escribiendo la dirección se llega a la "
     "pantalla. El backend la rechaza igual.",
     "Esconder del menú es cortesía, no seguridad. Quien decide es el "
     "backend, y por eso el resultado es el mismo por los dos caminos."),

    ("v08", "CU-017-001", "Entrá como locatario",
     "El cuarto rol va a «Mi local». Su portal se construye en la semana 8.",
     "La fila dice que los indicadores «todavía no están acotados a tu "
     "local». Es una limitación real del modelo de permisos, anotada como "
     "DT-16: la matriz dice sobre qué tipo de dato se puede operar, pero no "
     "sobre qué filas."),

    # ------------------------------------------------------ los indicadores
    ("v09", "CU-011-001", "Volvé como administrador y elegí el período «Hoy»",
     "Los cuatro indicadores del centro, con cuánto cambió cada uno contra el "
     "período anterior.",
     "El tráfico bajó 27,9 % y las ventas subieron 136,1 %. La vacancia dice "
     "que no hay con qué comparar, porque no es un indicador de período."),

    ("v10", "CU-011-001", "Probá los otros dos períodos",
     "Hoy, siete días y treinta. Al cambiarlo se recalcula todo: los cuatro "
     "indicadores, las variaciones y el gráfico.",
     "En treinta días ya no hay período anterior con datos, así que las "
     "variaciones desaparecen en vez de mostrar un número inventado."),

    ("v11", "CU-011-001", "Abrí la serie de Ventas",
     "Los botones de la derecha del gráfico cambian qué indicador se está "
     "mirando hora por hora.",
     "El eje cambia de unidad solo: acá muestra pesos, en tráfico muestra "
     "personas."),

    ("v12", "CU-011-001", "Y la de Conversión",
     "La conversión hora por hora, en porcentaje.",
     "Se calcula por franja horaria —tickets sobre entradas de esa misma "
     "hora— y nunca persona por persona. Eso la hace anónima por "
     "construcción, y es lo que sostiene el compromiso de privacidad."),

    ("v13", "CU-004-001", "Entrá a Mapa del centro",
     "Cada zona con su superficie, cuántos sensores la cubren, cuánta gente "
     "circuló y la densidad por metro cuadrado.",
     "El patio de comidas tiene casi el doble de densidad que la planta baja "
     "sobre un tercio de la superficie. Una zona sin sensores saldría en rojo "
     "y con la sugerencia de registrar uno."),

    # ------------------------------------------------------- integraciones
    ("v14", "CU-001-001", "Entrá a Integraciones",
     "Las ocho fuentes del centro: cinco puntos de venta y tres sensores de "
     "conteo, con la hora de su última sincronización.",
     "Esa fecha no sale de un campo guardado: sale del dato más reciente que "
     "trajo la fuente, así que no puede mentir."),

    ("v15", "CU-001-001", "Suspendé la ingesta de un conector",
     "Es una de las tres acciones correctivas. El conector pasa a amarillo y "
     "explica por qué.",
     "«La ingesta está suspendida a pedido del usuario.» No está roto: está "
     "apagado a propósito, y la sincronización automática lo saltea."),

    ("v16", "CU-001-001", "Reiniciá el conector para volver a activarlo",
     "La segunda acción correctiva vuelve a probar la conexión y lo devuelve "
     "a servicio.", None),

    ("v17", "CU-001-001", "Mirá qué pasa cuando el sistema externo se cae",
     "Los cinco puntos de venta dejaron de responder. El semáforo pasa a rojo "
     "y debajo de cada uno se lee el motivo.",
     "Los tres sensores de conteo siguen en verde: son otra fuente y no "
     "dependen de los puntos de venta."),

    ("v18", "CU-001-001", "Probá reintentar mientras sigue caído",
     "El sistema dice que no se resolvió, con el error exacto.",
     "No finge que anduvo: es el curso alternativo CA-1 del caso de uso. Un "
     "sistema que dijera «listo» acá haría perder tiempo buscando el problema "
     "en otro lado."),

    ("v19", "CU-001-001", "Reintentá una vez resuelto el problema",
     "Con el sistema externo de vuelta en línea, la misma acción recupera el "
     "conector.",
     "Se recuperó sólo el conector sobre el que se actuó. Los otros cuatro "
     "vuelven solos en la próxima sincronización automática."),

    # ------------------------------------------------------------- reglas
    ("v20", "CU-006-001", "Entrá a Reglas de alerta",
     "Una regla dice: este indicador, comparado así contra este valor, en "
     "este período y estos días, avisándole a esta persona por este canal.",
     "Debajo del indicador el sistema muestra entre qué valores viene "
     "moviéndose en el último mes, para que no elijas un umbral a ciegas."),

    ("v21", "CU-006-001", "Probá poner un umbral imposible",
     "Un corte de 300 sobre un indicador que se mide en porcentaje.",
     "«Un porcentaje no puede ser 300: la regla nunca se cumpliría.» Sin esta "
     "validación la regla se crearía y quedaría muda para siempre, sin que "
     "nadie se entere."),

    ("v22", "CU-006-001", "Cambiá el indicador a vigilar",
     "Al cambiarlo se actualizan los rangos típicos y el campo del valor de "
     "corte cambia su unidad.",
     "El tráfico se mide en personas y estuvo entre 78 y 1.714 por hora en el "
     "último mes."),

    ("v23", "CU-006-001", "Completá la regla y creala",
     "Marcá los días en que se aplica, elegí a quién avisarle y por qué canal "
     "—push, WhatsApp o correo— y confirmá.",
     "No se puede elegir como destinatario a alguien cuyo rol no le permite "
     "ver los datos sobre los que se dispara: recibiría un aviso que al "
     "abrirlo le daría un error de permisos."),

    ("v24", "CU-006-001", "Pausá la regla",
     "Una regla pausada deja de evaluarse, pero no se borra.",
     "Sirve para callar una alerta que está molestando sin perder cómo estaba "
     "configurada."),

    ("v25", "CU-006-001", "Y reanudala",
     "El mismo botón la vuelve a activar. Desde ese momento se evalúa junto "
     "con cada sincronización.", None),

    # --------------------------------------------------- centro de alertas
    ("v26", "CU-026-001", "Entrá al centro de alertas",
     "Las reglas se cumplieron y nacieron tres alertas. La bandeja las ordena "
     "por gravedad y, dentro de cada gravedad, primero las más viejas.",
     "La columna Objetivo dice cuánto queda para atenderla: media hora para "
     "una alta, ocho para una baja. La que lleva más esperando es la que está "
     "más cerca de pasarse."),

    ("v27", "CU-026-001", "Filtrá por severidad",
     "Tres filtros: severidad, origen y estado. Se combinan entre sí.",
     "Filtrando por alta quedan dos de las tres, y el contador de arriba "
     "acompaña."),

    ("v28", "CU-026-001", "Filtrá por origen del modelo",
     "Todas las alertas de hoy vienen de reglas por umbral. Las del modelo de "
     "Machine Learning llegan en la semana 7.",
     "Sin resultados el sistema no muestra una tabla vacía: muestra «Todo en "
     "orden» con la hora del último chequeo. Una lista vacía sin explicación "
     "deja la duda de si no hay nada o si la consulta falló."),

    # -------------------------------------------------------- atender
    ("v29", "CU-007-001", "Abrí una alerta y asignale un responsable",
     "La ficha se abre al costado de la lista, no en otra página: el gerente "
     "está mirando varias a la vez.",
     "Al asignarla pasa de «nueva» a «en revisión»: tener responsable ya es "
     "haber empezado a trabajarla. El cambio se ve en la fila y en la ficha al "
     "mismo tiempo."),

    ("v30", "CU-007-001", "Elegí «Escalar» si no la podés resolver",
     "Al elegir escalar aparece un campo nuevo: a quién se la pasás.",
     "Escalar es una de las tres formas de cerrar, y la única que no cierra "
     "la alerta: la pasa a otra persona y le sube la severidad, porque si "
     "hizo falta escalarla es más grave de lo que se pensó."),

    ("v31", "CU-007-001", "Completá el checklist, la causa y la acción",
     "Cuatro puntos a revisar en la zona, y dos campos de texto de hasta "
     "quinientos caracteres cada uno.", None),

    ("v32", "CU-007-001", "Registrá la escalada",
     "La alerta sigue abierta pero cambió de responsable, y el paso quedó en "
     "la traza con quién lo hizo y cuándo.",
     "La columna Objetivo sigue corriendo: escalarla no reinicia el reloj."),

    ("v33", "CU-007-001", "Cerrá otra alerta como falso positivo",
     "La segunda forma de cerrar. La alerta queda resuelta igual que si se "
     "hubiera resuelto de verdad.",
     "Un falso positivo es información tan valiosa como un problema real: es "
     "lo que después sirve para ajustar el umbral, y por eso deja la misma "
     "traza."),

    ("v34", "CU-007-001", "Volvé a la escalada y resolvela",
     "Los cuatro puntos del checklist con sus tres resultados posibles: "
     "verificado, problema encontrado y no aplica.", None),

    ("v35", "CU-007-001", "Mirá la traza completa",
     "La alerta quedó resuelta, con el tiempo que tardó en atenderse y los "
     "dos pasos que recorrió: primero escalada, después resuelta.",
     "Una alerta no vuelve de resuelta: reabrirla borraría el tiempo de "
     "respuesta ya medido. Si el problema sigue, la regla genera una nueva."),

    ("v36", "CU-026-001", "Verificá que no quede nada abierto",
     "Las tres alertas cerradas, cada una por su camino: una escalada y "
     "resuelta, una como falso positivo y una resuelta directo.",
     "El contador de arriba vuelve a cero. Las resueltas siguen en la lista "
     "con su traza, porque el historial es parte de la auditoría."),

    ("v37", "CU-018-001", "Todo esto también funciona en el celular",
     "Las mismas pantallas a 390 píxeles de ancho: el menú pasa a barra "
     "horizontal, los indicadores se apilan y las tablas se desplazan dentro "
     "de su caja.",
     "No hay una versión móvil aparte. Es la misma aplicación, y por eso la "
     "vista de operaciones de la semana 9 se construye sobre esto mismo."),
]
