# -*- coding: utf-8 -*-
"""El guion del recorrido: que se ve en cada cuadro y que dice el rotulo.

Cada paso dice a que caso de uso pertenece y que tiene que hacer la persona,
en segunda persona y sin jerga: el video es para mostrarlo en la defensa, no
para el que escribio el codigo.

`armar_video.py` lo usa para componer los rotulos sobre las capturas.
"""

# Los casos de uso que recorre el video, en orden. Cada uno abre con una placa.
CASOS = {
    "CU-017-001": {
        "nombre": "Iniciar sesión en la plataforma",
        "resumen": "El sistema reconoce a la persona y la lleva al panel que "
                   "le corresponde según su rol.",
    },
    "CU-011-001": {
        "nombre": "Consultar el tablero de indicadores del centro",
        "resumen": "Tráfico, conversión, ventas y vacancia, calculados sobre "
                   "los datos que llegan de las fuentes.",
    },
    "CU-004-001": {
        "nombre": "Consultar el mapa del centro y sus zonas",
        "resumen": "La circulación de personas por zona y qué zonas tienen "
                   "cobertura de sensores.",
    },
    "CU-001-001": {
        "nombre": "Monitorear el estado de las integraciones",
        "resumen": "Ver qué fuentes están trayendo datos y actuar sobre las "
                   "que dejaron de hacerlo.",
    },
    "CU-006-001": {
        "nombre": "Configurar una alerta por umbral",
        "resumen": "Definir sobre qué indicador, con qué condición y a quién "
                   "avisarle cuando se cumpla.",
    },
    "CU-026-001": {
        "nombre": "Monitorear el centro de alertas críticas",
        "resumen": "La bandeja de alertas ordenada por gravedad, con el tiempo "
                   "que queda para atender cada una.",
    },
    "CU-007-001": {
        "nombre": "Atender y resolver una alerta",
        "resumen": "Tomar la alerta, recorrer el checklist de verificación y "
                   "registrar qué se encontró y qué se hizo.",
    },
}

# Un paso por captura. `nota` es la observacion al pie, para lo que conviene
# mirar en esa pantalla y no se explica solo.
PASOS = [
    ("v01", "CU-017-001", "Abrí el sistema",
     "La pantalla de acceso es la misma para los cuatro perfiles: "
     "administrador, gerente, operaciones y locatario.", None),

    ("v02", "CU-017-001", "Escribí tu correo y tu contraseña",
     "La contraseña necesita ocho caracteres, una mayúscula y un número.",
     "Si el correo o la clave están mal, el sistema dice lo mismo en los dos "
     "casos: decir cuál de los dos falló le regalaría a un atacante la lista "
     "de correos dados de alta."),

    ("v03", "CU-017-001", "Apretá Entrar",
     "El sistema te lleva al panel que corresponde a tu rol. Acá entramos "
     "como administrador del centro.",
     "El menú de la izquierda sólo muestra las secciones que tu rol puede "
     "abrir. Un operario no vería Integraciones ni Reglas de alerta."),

    ("v04", "CU-011-001", "Mirá los cuatro indicadores del centro",
     "Tráfico, conversión, ventas y vacancia. Elegí el período arriba a la "
     "derecha: hoy, siete días o treinta.",
     "Cada indicador muestra cuánto cambió contra el período anterior. La "
     "conversión trae un aviso: se calculó sobre 10 de las 12 horas con "
     "tráfico, porque en las otras dos ningún punto de venta reportó."),

    ("v05", "CU-011-001", "Abrí el detalle hora por hora",
     "Los botones de la derecha del gráfico cambian qué indicador se está "
     "mirando: tráfico, ventas o conversión.",
     "La conversión se calcula por franja horaria —tickets sobre entradas de "
     "esa misma hora— y nunca persona por persona. Eso la hace anónima por "
     "construcción."),

    ("v06", "CU-004-001", "Entrá a Mapa del centro",
     "Cada zona muestra su superficie, cuántos sensores la cubren, cuánta "
     "gente circuló y la densidad por metro cuadrado.",
     "El patio de comidas tiene casi el doble de densidad que la planta baja "
     "sobre un tercio de la superficie. Una zona sin sensores saldría en rojo "
     "y con la sugerencia de registrar uno."),

    ("v07", "CU-001-001", "Entrá a Integraciones",
     "Las ocho fuentes del centro: cinco puntos de venta y tres sensores de "
     "conteo, con la hora de su última sincronización.",
     "La fecha de la última sincronización no sale de un campo guardado: sale "
     "del dato más reciente que trajo esa fuente, así que no puede mentir."),

    ("v08", "CU-001-001", "Detectá una caída",
     "Los cinco puntos de venta dejaron de responder. El semáforo pasa a rojo "
     "y debajo de cada uno se lee el motivo.",
     "Los tres sensores de conteo siguen en verde: son otra fuente y no "
     "dependen de los puntos de venta."),

    ("v09", "CU-001-001", "Elegí una acción correctiva",
     "En la columna Acción podés reintentar la conexión, reiniciar el "
     "conector o suspender la ingesta.",
     "Si la acción no resuelve, el sistema lo dice con el motivo. No finge "
     "que anduvo: es el curso alternativo CA-1 del caso de uso."),

    ("v10", "CU-001-001", "Reintentá una vez resuelto el problema",
     "Con el sistema externo de vuelta en línea, la misma acción recupera el "
     "conector.",
     "Se recuperó sólo el conector sobre el que se actuó. Los otros cuatro "
     "vuelven solos en la próxima sincronización automática."),

    ("v11", "CU-006-001", "Entrá a Reglas de alerta",
     "Una regla dice: este indicador, comparado así contra este valor, en "
     "este período y estos días.",
     "Debajo del indicador el sistema te muestra entre qué valores viene "
     "moviéndose en el último mes, para que no elijas un umbral a ciegas."),

    ("v12", "CU-006-001", "Elegí el indicador a vigilar",
     "Al cambiarlo, los rangos típicos se actualizan y el campo del valor de "
     "corte cambia su unidad.",
     "El tráfico se mide en personas y estuvo entre 70 y 1.714 por hora en el "
     "último mes. La conversión se mediría en porcentaje."),

    ("v13", "CU-006-001", "Completá la condición y el destinatario",
     "Poné el valor de corte, marcá los días en que la regla se aplica y "
     "elegí a quién avisarle y por qué canal.",
     "No se puede elegir como destinatario a alguien cuyo rol no le permite "
     "ver esos datos: recibiría un aviso que al abrirlo le daría un error de "
     "permisos."),

    ("v14", "CU-006-001", "Creá la regla",
     "La regla queda activa y el sistema empieza a evaluarla junto con la "
     "sincronización automática.",
     "Si el valor de corte quedara fuera de los rangos históricos, la regla "
     "se crearía igual pero con un aviso: es probable que se haya equivocado "
     "de escala."),

    ("v15", "CU-026-001", "Entrá al centro de alertas",
     "La regla se cumplió y nació una alerta. La bandeja las ordena por "
     "gravedad y, dentro de cada gravedad, primero las más viejas.",
     "La columna Objetivo dice cuánto tiempo queda para atenderla. Una alerta "
     "alta tiene media hora; una baja, ocho."),

    ("v16", "CU-026-001", "Abrí la alerta",
     "La ficha se abre al costado de la lista, no en otra página: el gerente "
     "está mirando varias alertas a la vez.",
     "Arriba, el detalle: qué zona, qué indicador, cuándo nació y cuánto "
     "tiempo queda. Abajo, qué se puede hacer con ella."),

    ("v17", "CU-007-001", "Asigná un responsable",
     "Al asignarla, la alerta pasa de «nueva» a «en revisión»: tener "
     "responsable ya es haber empezado a trabajarla.",
     "El cambio se ve en la ficha y en la fila de la lista al mismo tiempo. "
     "Al responsable le llega un aviso."),

    ("v18", "CU-007-001", "Recorré el checklist de verificación",
     "Cuatro puntos a revisar en la zona: escaleras mecánicas, climatización, "
     "pasillos bloqueados y los sensores. Marcá el resultado de cada uno.",
     "En este caso la climatización tenía un problema. Lo que se marca acá "
     "queda guardado junto con la resolución."),

    ("v19", "CU-007-001", "Escribí la causa y la acción tomada",
     "Hay tres formas de cerrar: resolver, marcarla como falso positivo o "
     "escalarla a otra persona.",
     "Un falso positivo también deja traza. Es información tan valiosa como "
     "un problema real: es lo que después sirve para ajustar el umbral."),

    ("v20", "CU-007-001", "Registrá el cierre",
     "La alerta queda resuelta, con el tiempo que tardó en atenderse y la "
     "traza completa de quién hizo qué.",
     "Una alerta no vuelve de resuelta: reabrirla borraría el tiempo de "
     "respuesta ya medido. Si el problema sigue, la regla genera una nueva."),

    ("v21", "CU-026-001", "Verificá que no quede nada abierto",
     "Sin alertas pendientes, el sistema no muestra una tabla vacía: muestra "
     "«Todo en orden» con la hora del último chequeo.",
     "Una lista vacía sin explicación dejaría la duda de si no hay nada o si "
     "la consulta falló."),
]
