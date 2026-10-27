# Hoja de ruta

**Estado:** documento vivo; se actualiza al cerrar cada paso. Fuera del core; no es metodología vigente.
**Última actualización:** 2026-10-27, con Warp 4.1.0 publicado.
**Origen:** hoja de ruta de `EVALUACION_2026-10-27.md` §6, reorganizada con lo aprendido al construir el instalador y en el primer piloto.

El trabajo se organiza en dos iteraciones:

- **Iteración 1 (actual): evaluar la arquitectura.** Comprobar en uso real, con varias personas y agentes, que el modelo funciona: THREADs, autoridad, buzones, tareas, decisión y deliberación. Las operaciones se hacen a mano, siguiendo el core, y cada fricción se registra.
- **Iteración 2: rendimiento y funcionalidad.** Automatizar lo que la iteración 1 haya validado.

**Por qué en este orden:** las herramientas encapsulan reglas de la arquitectura. Si la evaluación obliga a cambiarlas, construir antes las herramientas supondría rehacerlas. Además, hacer las operaciones a mano durante la evaluación es en sí una medida: muestra dónde está la fricción y qué automatizaciones merecen la pena.

---

## 1. Hecho

Las fases 1 (verificaciones externas) y 2 (especificación del core) están cerradas; su registro está en `EVALUACION_2026-10-27.md` §8b–§8c y en `git log --first-parent main`. De las herramientas, lo imprescindible para poder instalar y evaluar:

| Paso | Versión | PR |
|---|---|---|
| Versión del método en `warp/VERSION`, esquema MAJOR.MINOR.PATCH | 3.0.0 | #16 |
| Instalador `warp.py init` y `publish`; `warp.lock` comprobado por el checker | 3.1.0 | #17 |
| Instalación en el sitio: el método se descarga, no se copia; lo propio del proyecto en la raíz | 4.0.0 | #18 |
| Paquete descargable `warp-<versión>.zip` (`tools/build_package.py`) | 4.0.0 | #19 |
| Confirmación en el terminal al crear una release | — | #20 |
| `publish --remote` y enlace directo de descarga | 4.1.0 | #21 |

### Primer piloto: instalación (2026-10-27)

Un agente sin el contexto del diseño instaló Warp 4.1.0 desde el paquete descargado, siguiendo solo el prompt de `INSTALL.md` §3 y `warp.py init --help`. Preguntó los datos uno a uno, esperó la confirmación del mensaje antes de `publish` y, más tarde, publicó la instancia con `publish --remote` (`gineslm/piloto-4-1`). Resultado verificado en GitHub: repositorio privado, `knowledge` como rama principal, solo merge commit, mensaje del PR y borrado automático de ramas.

Hallazgos:

- **Codificación:** en Windows, cuando la salida va a una tubería (el caso de un agente), Python escribe con la codificación antigua de la consola y los acentos llegan rotos. El agente lo esquivó con `PYTHONIOENCODING=utf-8`.
- **Participantes sin acceso:** `publish --remote` crea el repositorio, pero no invita a los participantes de `USERS.md`.
- **Operaciones sin comando:** crear un THREAD, un documento o una entrada exige que el agente lea la arquitectura y las plantillas y escriba varios archivos a mano.

---

## 2. Iteración 1 (actual): evaluar la arquitectura

### 2.1 Corrección necesaria para el piloto

| Paso | Motivo |
|---|---|
| Salida UTF-8 forzada en `warp.py` y en el checker | es un fallo, no una mejora: los agentes reciben su salida con los acentos rotos, lo que distorsiona lo que se quiere medir. No toca la arquitectura. |

Ninguna otra herramienta se construye en esta iteración, salvo para corregir un fallo que impida el piloto.

### 2.2 Piloto con varias personas (fase 4)

Sobre una instancia instalada con Warp 4.1.0 (o posterior), con al menos 2 personas y 2–3 THREADs, todas las operaciones **a mano**, siguiendo el core:

| Escenario (auditoría §7) | Qué valida |
|---|---|
| 7.2 dos instancias en THREADs distintos, misma persona | una instancia por THREAD, directorios de trabajo separados (`THREAD_ARCHITECTURE.md` §9.4) |
| 7.3 dos tareas en el mismo THREAD en paralelo | una rama por tarea; integración en serie si tocan el mismo documento |
| 7.4 un hallazgo de un THREAD exige una decisión de otro | buzón por entradas, dos zonas, resolución en la misma decisión (§7) |
| 7.5 interrupción y retomada | detección de la rama o el PR de una tarea antes de empezar (§9.4) |
| 7.6 dos personas crean THREADs a la vez | conflictos en los índices sin generador |
| 7.7 agente sin herramientas (proyecto de chat) | perfiles de agente; qué puede hacer sin acceso al repositorio |

Primero con integración central y `enforcement: advisory`; después, si procede, distribuida.

### 2.3 Registro de fricciones

Durante el piloto se anota, por operación (crear un THREAD, un documento, una entrada; resolver una entrada; empezar una tarea; integrar):

- qué documentos tuvo que leer el agente y cuántos pasos hizo;
- dónde dudó, se equivocó o necesitó ayuda;
- qué regla del core resultó ambigua, insuficiente o innecesaria.

Las fricciones que apunten a la **arquitectura** se corrigen en el core en esta iteración. Las que apunten solo a **coste o comodidad** alimentan la prioridad de la iteración 2.

### 2.4 Medición (fase 5)

- prueba de orientación con 10 preguntas reales sobre el corpus;
- tokens por sesión típica;
- conflictos de fusión en buzones e índices;
- contradicciones entre THREADs detectadas.

**Criterio de cierre de la iteración 1:** los escenarios se completan sin cambios pendientes en la arquitectura, y las fricciones registradas están clasificadas.

---

## 3. Iteración 2: rendimiento y funcionalidad

Registrado, no planificado: el orden definitivo lo decide lo que mida la iteración 1.

### 3.1 Comandos para las operaciones habituales

**Principio:** los comandos hacen la parte **mecánica** (rutas, campos obligatorios, filas de índice, formato) y ejecutan el checker. **Nunca deciden ni hacen commit**: la responsabilidad, la redacción, el contenido y la confirmación del mensaje siguen siendo del agente y de la persona (`PROJECT_AGENT_CONTEXT.md`, regla dura 11).

**Por qué:** el agente necesita el `--help` del comando, no los documentos de reglas (menos contexto); la parte mecánica sale siempre igual (fiabilidad), y sirve igual para cualquier agente y para una persona.

| Comando | Qué hace | Hoy exige leer |
|---|---|---|
| `index` | regenera `THREAD_INDEX.md` y `DOCUMENT_INDEX.md` desde los MANIFEST; base de los demás | arquitectura §12 y plantillas |
| `thread new <id> --owner <github>` | MANIFEST desde la plantilla, buzón vacío y fila en el índice | arquitectura §5–§6, plantilla |
| `doc new <ruta> --thread <id>` | documento en `corpus/`, declarado en la autoridad del THREAD y en el índice | arquitectura §11–§12 |
| `entry new <receptor> <nombre> --from <id> --type <tipo>` | entrada en el buzón del receptor desde la plantilla | arquitectura §7, plantilla |
| `entry resolve <receptor> <nombre>` | borra la entrada; el cambio real lo hace el agente en la misma rama | arquitectura §7.4 |
| `task start <thread_id> <tarea>` | comprueba si ya existe rama o PR; si no, crea `agent/<thread_id>/<tarea>` desde `knowledge` | arquitectura §9.4 |
| `invite` | invita al repositorio a los participantes `active` de `USERS.md`, preguntando antes | — |

Al construirlos, la tabla «Cuándo leer más» de `PROJECT_AGENT_CONTEXT.md` pasa a remitir a cada comando, y la arquitectura se lee solo si el caso no encaja.

**Riesgo:** los comandos pasan a formar parte del método y pueden desincronizarse de la arquitectura. Se cubre con pruebas por comando y con el checker validando siempre su resultado.

### 3.2 Validación de las decisiones

| Paso | Qué hace |
|---|---|
| Validador de mensajes | formato `tipo(area): …`, línea «Por qué:», `Sustituye: <sha>` existente en `knowledge` (`GIT_COMMIT_RULES.md` §7–§8) |
| CI | checker, secretos en **cada** commit del PR, validador de mensajes, autoría («autor = `owner` o aprobación del `owner`», `THREAD_ARCHITECTURE.md` §4.5) y zonas de las entradas (§7.3). Obligatoria en GitHub solo con protección de ramas (Pro o Team en repositorios privados). |

### 3.3 Ciclo de vida de una instancia

| Paso | Qué hace |
|---|---|
| `warp.py upgrade` | sustituye `warp/` por la de una versión posterior, actualiza `warp_version` y `warp.lock`, e informa de cambios de esquema sin migrar el conocimiento por su cuenta |
| `layout: with-code` | instalar `knowledge` como rama con árbol propio en un repositorio que ya contiene código; verificar antes que GitHub permite limitar el método de merge solo a `knowledge` (`EVALUACION_2026-10-27.md` §8c) |

### 3.4 Más adelante

- grafo derivado de relaciones (opción 1 de `INFORME_FASE2_GRAFO.md`), si la medición de la iteración 1 muestra que orientarse en el corpus falla.
