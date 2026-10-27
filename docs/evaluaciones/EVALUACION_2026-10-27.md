# Evaluación — Auditoría de integración con agentes (v0.4)

**Fecha:** 2026-10-27
**Estado:** propuesta (D6). Fuera del core; no es metodología vigente.
**Evalúa:** `warp-auditoria-integracion-agentes.md` v0.4 (2026-10-26), documento externo al corpus.
**Base evaluada:** `main` en `43e6fb2` (clon completo, 6 commits; no superficial).
**Evaluador:** Claude Code (Opus 5.5) sobre copia local. Sin cambios en el repo salvo este archivo, sin commit.

---

## 0. Resumen

- **La auditoría es sólida.** De 14 hallazgos: 9 **confirmados**, 5 con **matiz**, ninguno refutado.
- **Faltan defectos del checker actual** que ninguna lectura del código detectaba y que salieron al ejecutar pruebas negativas (§2.2). El más grave: **en Windows nunca se comprueba la regla «el HANDOFF no admite trabajo propio»** (§4.15).
- **Tres correcciones de diseño importantes:**
  1. Los hooks sobre `git commit` (4.3, capas 3–4) **contradicen D5**: con squash, los commits de trabajo no se validan; lo que importa es el título y la descripción del PR. Propongo retirarlos.
  2. El generador de índices tras el merge (4.10, opción a) **choca con el checker actual**: un PR que crea un hilo sin tocar `THREAD_INDEX.md` falla el checker (§2.2, T13). Generador y checker se diseñan juntos; propongo una alternativa sin commits automáticos.
  3. La hoja de ruta pone el piloto **después** de todas las herramientas, cuando D4 lo quiere **durante** su construcción, con integración central (§5).
- **Hallazgos nuevos:** §4.15–§4.21. El más estructural: el propio repo `warp` no se gobierna con Warp (§4.20), lo que afecta a D6 y a la pregunta abierta 2.

---

## 1. Método

1. Lectura completa de `README.md`, `docs/core/*.md`, `docs/threads/example/*`, `docs/evaluaciones/*` y `scripts/check_knowledge.py`.
2. Historial: `git log`, `git log -S "Caso 1"`, `git grep` de términos de integración, `owner`, `tarea` y memoria.
3. Ejecución del checker sobre una **copia temporal fuera del repo** y batería de 16 pruebas, cada una sobre una copia limpia (§2).
4. Verificación externa de lo que cambia el veredicto: documentación oficial de Claude Code (memoria, hooks) y de GitHub (squash, ramas protegidas). Lo no verificado queda marcado.

Convención: **Confirmado / Refutado / Matiz**. Las referencias `archivo:línea` corresponden a `43e6fb2`.

---

## 2. Checker: ejecución y pruebas

### 2.1 Ejecución sobre el repo

```text
python scripts/check_knowledge.py
THREADs encontrados: 1.
Resumen: 0 error(es), 0 aviso(s).
código de salida: 0
```

### 2.2 Pruebas negativas (copia temporal, Windows 11, Python 3.13)

| Prueba | Resultado | Esperado según la especificación | Hallazgo |
|---|---|---|---|
| T01 dos MANIFEST reclaman `NOTES.md` | **0, sin errores** | error (`THREAD_ARCHITECTURE.md:299`) | 4.14 ✔ |
| T02 documento huérfano (ni índice ni MANIFEST) | **0** | aviso como mínimo | 4.14 ✔ |
| T03 `domain` distinto en `THREAD_INDEX` | **0** | error (`THREAD_INDEX_TEMPLATE.md:84`) | 4.14 ✔ |
| T04 entrada en bloque `text` con origen = receptor | **0** (el bloque no se lee) | error | 4.14 ✔ |
| T05 entrada en bloque `yaml` con origen = receptor | **0** ⚠ | error `check_knowledge.py:278-279` | **nuevo, 4.15** |
| T06 entrada yaml sin `context` / `evidence` / `target_scope` | **0** | — (no exigido hoy) | 4.14 ✔ |
| T07 entrada yaml sin `type` y `status` inválido | **0** (se ignora entera) | error | **nuevo, 4.16** |
| T08 «Ningún otro documento.» en Autoridad | **1**, NOTES deja de estar bajo autoridad | 0 | **nuevo, 4.17** |
| T09 `THREAD_DERIVED` con `source_id` inexistente | **0** | error o aviso | **nuevo, 4.18** |
| T10 `handoff.path` apunta a un directorio | **1** (2 errores) | — | 4.4 ✔ (qué rompe) |
| T11 `owner: ???` | **0** | — | 4.11 ✔ |
| T12 documento bajo autoridad de un hilo `ARCHIVED` | **0** | aviso (`THREAD_ARCHITECTURE.md:400`) | **nuevo, 4.18** |
| T13 falta la fila del hilo en `THREAD_INDEX` | **1** | 1 | 4.10 ⚠ (ver matiz) |
| T14 falta la fila de NOTES en `DOCUMENT_INDEX` | **0** | error | **nuevo, 4.19** |
| T15 directorio sin raíz Warp | **2** | 2 | 4.14 ✔ |

**T05 con la ruta normalizada** (`os.path.normpath` en la línea 260): la regla se dispara correctamente (`HANDOFF no admite trabajo propio del receptor`). Es un bug de rutas, no de diseño.

---

## 3. Evaluación de los hallazgos

### 4.1 Divulgación progresiva y perfil de agente — **Matiz**

- **Confirmado:** la secuencia de entrada presupone abrir archivos a demanda (`PROJECT_AGENT_CONTEXT.md:30-48`). Los informes la apoyan en el patrón «agente sobre repo» (`INFORME_VIABILIDAD.md:25`, `INFORME_FASE2_GRAFO.md:29`).
- **Matiz:** D7 describe un tercer caso que la propuesta no distingue. Un proyecto de chat con **solo** `PROJECT_AGENT_CONTEXT.md` adjunto no es una «instantánea del repo»: **no tiene repo**. No ve índices, MANIFEST ni buzón, así que ni siquiera puede seguir la secuencia de §3. Propongo **tres** perfiles:
  1. **con herramientas sobre el repo**: el perfil nativo, el único que escribe;
  2. **instantánea**: repo sincronizado, solo lectura. Su riesgo principal es la obsolescencia, más que perder la divulgación progresiva: con un corpus pequeño, cargarlo todo no es un problema;
  3. **solo contexto**: redacta borradores; no puede afirmar nada sobre el estado.
- **Ubicación:** `THREAD_CONTEXT_BOOTSTRAP.md` (nueva sección), con una línea en `PROJECT_AGENT_CONTEXT.md` §3.
- **Recomendación:** adoptar, **fusionado con 4.8**: son el mismo tema.

### 4.2 Archivo de entrada para agentes — **Confirmado, con matiz en el contenido**

- **Confirmado:** el repo no tiene `AGENTS.md` ni `CLAUDE.md`.
- **Verificado (documentación oficial de Claude Code, memoria):**
  - `AGENTS.md` se lee si no hay `CLAUDE.md` ni `CLAUDE.local.md` en el directorio o por encima. Requiere v2.1.277 o posterior.
  - `@ruta` se expande y carga el archivo entero. Una ruta entre acentos graves queda literal.
  - Se recomienda no pasar de 200 líneas por archivo. Los imports **no reducen** el coste de contexto.
- **Matiz 1, a favor de `@`:** `PROJECT_AGENT_CONTEXT.md` tiene 133 líneas y 6,6 KB, y se define como «la superficie mínima que un agente debe leer **siempre**» (`PROJECT_AGENT_CONTEXT.md:11`). Importarlo con `@` **no rompe** la divulgación progresiva: es exactamente su nivel 0. Las fuentes extensas siguen como rutas literales, y así ya están escritas (§5).
- **Matiz 2, agnosticismo:** otros agentes no expanden `@`. Propuesta: un `AGENTS.md` que diga en prosa «lee primero `docs/core/PROJECT_AGENT_CONTEXT.md`» y añada la línea `@docs/core/PROJECT_AGENT_CONTEXT.md`. Para un agente que no la expanda es texto inocuo; para Claude Code, carga garantizada. No hace falta `CLAUDE.md`.
- **Matiz 3, contra duplicar:** la auditoría pide que `AGENTS.md` incluya el protocolo de D5 y las reglas de D2 y D8. Eso crea una **segunda fuente** de reglas duras. Esas reglas van a `PROJECT_AGENT_CONTEXT.md` §2 (fase 2), y `AGENTS.md` solo remite. Si se adelanta `AGENTS.md` a la fase 2, debe contener solo la remisión.
- **Recomendación:** adoptar con los matices 2 y 3.

### 4.3 Cumplimiento mecánico de invariantes — **Confirmado, con corrección**

- **Confirmado:** el cumplimiento depende hoy del agente (`PROJECT_AGENT_CONTEXT.md:100-110`), y la CI es una cuestión abierta (`THREAD_ARCHITECTURE.md:427`). Los códigos de salida se verificaron: 0, 1 y 2 (§2.2, T15; `check_knowledge.py:49,318`).
- **Verificado:**
  - Los hooks `PreToolUse` admiten `permissionDecision: allow | deny | ask | defer`. El código de salida 2 bloquea.
  - El filtro `if` se documenta como «best-effort», con la recomendación de usar el sistema de permisos para bloqueos duros.
  - GitHub permite fijar el mensaje por defecto del squash a «**Pull request title and description**».
- **Corrección 1, las capas 3 y 4 contradicen D5.** D5 valida «el mensaje que entra a `knowledge` … no los commits de trabajo de las ramas `agent/*`», y 4.6.2 declara libres los commits WIP. Un hook de pre-commit o de Claude Code sobre `git commit` valida precisamente esos commits. **Propuesta:** retirar ambas capas. La puerta humana se aplica al **título y la descripción del PR**: el agente los muestra y espera confirmación antes de `gh pr create` o `gh pr edit`.
- **Corrección 2, ajuste de squash obligatorio.** La opción por defecto de GitHub usa el **mensaje del commit** cuando el PR tiene un solo commit, no la descripción. Así, un PR de un solo commit WIP entraría en `knowledge` con un mensaje no validado. La regla debe fijar «Pull request title and description».
- **Confirmado:** la capa 5 es necesaria. El mensaje se puede editar en el diálogo de merge **después** de pasar la CI. Que la página de squash no lo diga explícitamente es conocimiento previo; verificarlo en la fase 1.
- **Recomendación:** adoptar las capas 1, 2 y 5. Retirar la 3 y la 4.

### 4.4 `HANDOFF.md` como punto de conflicto — **Confirmado, con tensiones adicionales**

- **Confirmado:** cualquier hilo escribe en el buzón receptor (`THREAD_ARCHITECTURE.md:179`). Las dos zonas lógicas comparten archivo (`:205-209`) y la resolución se hace en el mismo commit (`:211-229`). T10 muestra qué rompe cambiar `handoff.path`: `check_knowledge.py:166-173` y `:215-216`.
- **El buzón por entradas es compatible con §7.2.** Registrar sin aprobación del receptor ya es la regla vigente. Y el squash **refuerza** §7.4: aunque haya varios commits WIP, en `knowledge` aplicar la decisión y retirar la entrada caen en un solo commit.
- **Tensiones que la propuesta no cubre:**
  1. **Las dos zonas siguen existiendo.** El receptor cambia `status` y `working_notes` de una entrada abierta, es decir, **modifica** el archivo. Y el emisor puede querer ampliar la evidencia de su propia entrada. «Solo añadir» es demasiado estricto. La regla correcta: el emisor añade o modifica **sus** entradas, mientras sigan en `proposed`; el receptor modifica y borra cualquiera.
  2. **No generar `HANDOFF.md` como vista.** Si el buzón es un directorio, el directorio **es** la vista. Generar un `HANDOFF.md` reintroduce el problema del índice derivado (§4.10). `handoff.path` pasa a apuntar al directorio.
  3. **El nombre del archivo de entrada sirve de identificador natural de la tarea** (ver 4.12), sin códigos de catalogación: un slug descriptivo, nunca `R-012`.
  4. **HANDOFF provisional** (`THREAD_ARCHITECTURE.md:123`): con directorios, un buzón sin MANIFEST es invisible para el checker, porque `thread_dirs` busca `MANIFEST.md` (`check_knowledge.py:117-122`). Hay que decidir si debe avisar.
- **Recomendación:** adoptar con las tensiones 1 y 2 resueltas en la especificación.

### 4.5 Memoria fuera del repo — **Confirmado**

- **Verificado (oficial, no de terceros):**
  - La memoria automática está activa por defecto, es «per repository, shared across worktrees» y se guarda en `~/.claude/projects/<project>/memory/`.
  - Se desactiva por proyecto con `"autoMemoryEnabled": false` en el `settings.json` del proyecto, o con `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`.
- **Matiz:** es «machine-local». No se comparte entre personas ni entre máquinas. El riesgo real es **entre hilos de la misma persona**, porque todos los hilos viven en el mismo repo y comparten un único directorio de memoria. Es peor de lo que sugiere la auditoría: no hace falta paralelismo, basta con cambiar de hilo.
- **Evidencia directa:** esta misma sesión de evaluación se ejecuta con memoria automática activa sobre este repo (no se ha escrito nada en ella).
- **Ubicación:** `.claude/settings.json` versionado con `autoMemoryEnabled: false` aplica a todo el que use Claude Code en el repo. Es el mecanismo, no una recomendación. La regla dura propuesta («ningún estado persistente fuera del repo es fuente de verdad») es la generalización agnóstica correcta para `PROJECT_AGENT_CONTEXT.md` §2.
- **Recomendación:** adoptar. Y **adelantar**: no depende de nada (ver §5).

### 4.6 Quién integra en `knowledge` — **Confirmado**

- **Confirmado por grep:** no hay ninguna regla sobre merge, PR, integración o «escritor» en el core. Las únicas coincidencias de «integración» se refieren a `develop` y a la cuestión abierta de CI.
- **Matiz 1, un PR = una decisión.** El squash convierte el PR en la unidad de decisión. Falta decidir si una decisión de A que genera una propuesta a B va en **un** PR (decisión en A más entrada nueva en el buzón de B) o en dos. La arquitectura sugiere que es una sola causa (`THREAD_ARCHITECTURE.md:271-277`, `GIT_COMMIT_RULES.md:21-22`). Si es un PR, la comprobación de CI de 4.11 debe permitir «documentos propios más entradas propias en buzones ajenos».
- **Matiz 2, la rama `knowledge` no existe.** El repo solo tiene `main`. Es coherente, porque este repo publica el método (§4.20), pero el piloto la necesita creada y protegida: sin force-push, ya que los trailers `Sustituye:` dependen de SHAs estables.
- **Recomendación:** adoptar.

### 4.7 Multiequipo como escenario objetivo — **Confirmado**

- `INFORME_VIABILIDAD.md:5` («un solo mantenedor»), `:45` y `:58` (concurrencia). `README.md:525` (múltiples usuarios como dirección futura).
- **Recomendación:** adoptar. El cambio de marco justifica sacar del estado «diferido» la concurrencia y el cuello humano.

### 4.8 Papel de claude.ai — **Confirmado; fusionar con 4.1**

Los tres riesgos (obsolescencia, memoria de proyecto, RAG) son propiedades de los perfiles 2 y 3 de 4.1. La memoria de proyecto de claude.ai y la de ChatGPT entran en la regla dura de 4.5.

### 4.9 Orientación en el corpus — **Confirmado, con matices puntuales**

1. **Opción 0 y Claude Code:** confirmado.
2. **`sustituye`:** confirmada la tensión (`INFORME_FASE2_GRAFO.md:48,62` frente a `GIT_COMMIT_RULES.md:78-80`). **Matiz:** el trailer con SHA no requiere excepción a §4. Ya está cubierto por `GIT_COMMIT_RULES.md:41-49` («referencias Git con significado semántico … expresa una relación que Git no puede inferir»). D9 es coherente con la regla vigente; basta con añadir el formato del trailer a §7–§8.
3. **Dependencias sin esquema:** confirmado (`MANIFEST.md:36-39`). No se puede verificar «en MANIFESTs reales»: en este repo solo existe el ejemplo.
4. **Disparadores sin instrumentar:** confirmado. Índices de 784 y 814 bytes.
5. **«Caso 1»:** confirmado. `git log -S "Caso 1"` lo sitúa solo en `8d60d9e`, el commit que añadió los informes, y no se define en ningún punto del historial. Por el contexto (`INFORME_VIABILIDAD.md:49`) parece ser el aviso de dependencias declaradas que el README lista como dirección futura («dependency warnings», `README.md:522`). Propuesta: sustituir la referencia por esa descripción.
6. **Base de datos derivada sí, fuente no:** confirmado.

### 4.10 Generador de índices y creación paralela de hilos — **Confirmado, con conflicto de diseño**

- **Confirmado:** no hay generador. El checker exige que cada MANIFEST tenga su fila (T13; `check_knowledge.py:217-218`). Dos ramas que añaden una fila antes de `## Mantenimiento` editan la misma zona y entran en conflicto.
- **Conflicto con la opción (a):** si el PR que crea un hilo no toca el índice y un job lo regenera tras el merge, **la CI del PR falla** (T13). La opción (a) exige además un modo «PR» del checker que tolere índices desfasados, y una excepción a la puerta humana para el commit del bot.
- **Alternativa propuesta (c):** el generador se ejecuta **en la rama**, y la regla de rama exige estar al día con `knowledge`. Si otra integración entra antes, se resuelve con `rebase` más regenerar, y el conflicto se resuelve volviendo a generar, no a mano. Sin commits automáticos, sin excepción a D5 y sin modo especial del checker. El coste es serializar las integraciones que tocan índices, que es un coste aceptable en el piloto.
- La opción (b), no versionar los índices, perjudica a los perfiles 2 y 3 de 4.1.
- **Recomendación:** adoptar el generador con la opción (c). Revisar la (a) solo si la serialización molesta en la fase 5.

### 4.11 Semántica de `owner` — **Confirmado; el repo contradice la premisa**

- **Confirmado:** `owner` solo aparece como clave del YAML (`THREAD_ARCHITECTURE.md:70`), sin definición.
- **Contradicción:** el MANIFEST de ejemplo dice `owner: persona o agente que mantiene este ejemplo` (`MANIFEST.md:12`), en contra de la nomenclatura 1.2 («una instancia de agente nunca es responsable»). Hay que corregir el ejemplo en la fase 2.
- **Matiz sobre la comprobación en CI:** en un PR se puede verificar el **autor** (`pull_request.user.login`), pero no quién lo fusionará. Las reglas de rama de GitHub no restringen el merge por rutas. Por eso «el responsable integra» es aplicable sobre la autoría y, para el merge, por convención. Conviene escribirlo así para no prometer más de lo que se puede imponer.
- **CODEOWNERS:** que el autor no puede aprobar su propio PR, y que por tanto «Require review from Code Owners» bloquea a un propietario único, es conocimiento previo. La página oficial consultada no lo dice explícitamente. Verificarlo en la fase 1. La conclusión (CI propia en vez de revisión de propietario) no depende de ello.
- **Recomendación:** adoptar.

### 4.12 Tarea, rama y directorio — **Confirmado, con propuesta de identificador**

- **Confirmado:** la especificación solo menciona «rama de trabajo, si procede» (`THREAD_CONTEXT_BOOTSTRAP.md:94`) y no menciona directorios.
- **Matiz, detección por nombre:** `<tarea>` es un slug libre. Dos instancias pueden nombrar la misma tarea de forma distinta, y la detección por prefijo falla. Propuesta:
  - una tarea que **resuelve una entrada** usa el nombre del archivo de entrada (4.4.3) como nombre de rama. La detección se vuelve determinista;
  - una tarea que **desarrolla documentos propios** declara los documentos en la descripción del PR, como propone la auditoría, y el solapamiento se detecta por documentos, no por nombre.
- **PR en borrador como reserva:** sirve si se abre al **empezar**, no al terminar. Requiere un remoto y `gh`, que no está disponible en el perfil 3.

### 4.13 Contradicciones semánticas entre hilos — **Confirmado**

Ver 4.9.5 para «Caso 1». Medir en el piloto es lo correcto.

### 4.14 Cobertura del checker — **Confirmado, e incompleto**

- Todas las afirmaciones de «Valida» y «No valida» se confirman con pruebas (§2.2): T01, T02, T03, T06, T10, T11 y T15.
- **Implicación 3 confirmada:** el único ejemplo de entrada del repo usa un bloque `text` (`HANDOFF.md:9-18`) y el checker solo lee bloques `yaml` (`check_knowledge.py:265`). Un agente que copie el ejemplo produce entradas que el checker no ve (T04). Hay que fijar el formato a `yaml` en la especificación y en el ejemplo.
- **Implicación 1 confirmada:** el checker no extrae relaciones, aunque `yaml_block` (`:72-87`) sí es reutilizable para el parseo de identidad.
- **Le faltan los defectos de §4.15–§4.19.**

---

## 4. Hallazgos nuevos

### 4.15 Bug: en Windows no se comprueba «el HANDOFF no admite trabajo propio» — alta

- `check_knowledge.py:260` construye la clave con `os.path.join(root, mp)`, donde `mp` usa `/`. En Windows, `docs/threads/example` no coincide con `docs\threads\example`, que es lo que devuelve `os.walk` (`:119`). `receiver` vale siempre `None` y la comparación de `:278` nunca es cierta.
- **Evidencia:** T05 devuelve 0. Con `os.path.normpath` devuelve el error esperado.
- **Impacto:** el responsable trabaja en Windows. En local, el checker da un **falso negativo** sobre una de las reglas duras (`PROJECT_AGENT_CONTEXT.md:21`). En una CI con Linux sí funcionaría, así que el mismo commit da resultados distintos según la máquina.
- **Corrección:** una línea, `os.path.normpath`. Corregirlo **ya**, antes de cualquier rediseño, con su prueba.

### 4.16 Las entradas sin `type` se ignoran por completo — media

`check_knowledge.py:267`: `if not e or "type" not in e: continue`. Una entrada sin `type` no es inválida para el checker: es invisible, y tampoco se validan su `status` ni su `origin_thread` (T07). Debería ser un error: todo bloque yaml de un buzón es una entrada.

### 4.17 La palabra «Ningún» anula la autoridad declarada — media

`check_knowledge.py:128-129`: si el cuerpo de `## Autoridad documental vigente` contiene «Ningún» o «Ninguno» en cualquier posición, devuelve el conjunto vacío aunque haya rutas listadas (T08). «Ningún otro documento» o «ninguno compartido» rompen la autoridad. Debería devolver vacío solo si no hay rutas.

### 4.18 Procedencia y estado no se cruzan — baja

- `origin.source_id` de `THREAD_DERIVED` no se valida contra los `thread_id` existentes (T09; `:156-159`). Es la arista `nace_de` del grafo (`INFORME_FASE2_GRAFO.md:46`).
- Un documento puede seguir bajo autoridad de un hilo `CLOSED` o `ARCHIVED` sin aviso (T12), aunque §15 pide transferirla (`THREAD_ARCHITECTURE.md:400`). Debería ser aviso, no error, porque la arquitectura dice «que no pueda quedar sin responsable».

### 4.19 `DOCUMENT_INDEX` incompleto no se detecta — media

El checker comprueba índice → MANIFEST, pero no MANIFEST → índice (T14). Un documento declarado en «Autoridad documental vigente» sin fila en el índice pasa. Con `THREAD_INDEX` sí se comprueba en ambos sentidos (`:217-218`): es una asimetría. Encaja con el generador (4.10): si el generador existe, la comprobación es «el índice coincide con lo que generaría».

### 4.20 El repo `warp` no se gobierna con Warp — estructural

- `DOCUMENT_INDEX.md` solo lista `NOTES.md`. `docs/core/*`, `docs/evaluaciones/*` y `README*` no tienen hilo con autoridad, lo que contradice literalmente `THREAD_ARCHITECTURE.md:299` («cada documento tiene exactamente un THREAD con autoridad»). Tampoco existe la rama `knowledge`.
- Es coherente si se declara: este repo **publica** la metodología y no es una instancia. Pero hoy no está declarado, y por eso D6 tiene que argumentar que las evaluaciones «no requieren hilo».
- **Propuesta:** decidir una de dos opciones:
  - (a) declarar en el README que el repo es la publicación y no una instancia;
  - (b) gobernarlo con Warp: un hilo gestor del core y otro de evaluaciones.

  La (b) convierte la evolución del propio core en el **primer piloto real**: cada mejora de esta auditoría sería una entrada en el buzón del hilo del core. Responde a la pregunta abierta 2 y al matiz de D6.
- **Decidido (2026-10-27):** ni (a) tal cual ni (b). `warp` es la **distribución** del método, con una capa de instalación (`warp.yaml` en la raíz de cada instancia). El core es de solo lectura en las instancias, las mejoras llegan a `warp` por PR y el piloto es una instancia nueva. Esto resuelve también D6 y la pregunta abierta 2. Detalle en `PROPUESTA_CAPA_INSTALACION.md`.

### 4.21 Uso previo de «tarea» en el core — baja (afecta a 1.3)

`PROJECT_WORKING_RULES.md:100` («Antes de cerrar una tarea o sesión sustantiva») ya usa «tarea» y «sesión» de forma informal. Renombrar el tipo `task` del buzón es más limpio que restringir una palabra de uso común. Propuesta: el tipo de entrada pasa a `request` y la palabra «tarea» queda para la unidad de trabajo. El checker cambia en `H_TYPES` (`:14`).

---

## 5. Escenarios (sección 7)

| Escenario | Paso no soportado hoy | ¿Recogido? |
|---|---|---|
| 7.2 dos hilos, misma persona | directorio por instancia (sin especificar); CI de autoría (no existe); integración (sin especificar); memoria compartida entre los dos hilos **aunque no hubiera paralelismo** | 4.12, 4.11, 4.6, 4.5 (con el matiz de 4.5) |
| 7.3 dos tareas, mismo hilo | si ambas resuelven entradas, conflicto en `HANDOFF.md`; solapamiento de documentos no detectado | 4.4, 4.12 |
| 7.4 UX → ingeniería | paso 2: buzón por entradas inexistente; «solo añadir» no existe en CI. Paso 4: el trailer no está en `GIT_COMMIT_RULES.md` §8, y el ejemplo pone «Por qué:» en la misma línea, mientras §8 la pone en línea propia (`GIT_COMMIT_RULES.md:87-88`), así que el validador debe fijar una sola forma. **Nuevo:** si el mismo PR de UX registra la entrada y cambia documentos de UX, falta decidir si es una decisión o dos | 4.4, 4.11, D9; **nuevo:** 4.6 matiz 1 |
| 7.5 retomar | no hay marca de reserva; **los nombres de tarea son libres y la detección por prefijo falla** | 4.12 (con el matiz de identificador) |
| 7.6 dos hilos nuevos a la vez | conflicto en `THREAD_INDEX`; **con la opción (a) la CI del PR falla por T13** | 4.10 (con el matiz) |
| 7.7 agente sin herramientas | sin repo no ve el buzón ni el MANIFEST receptor: **no puede redactar una entrada con `target_scope` correcto** | 4.1 (perfil 3, nuevo) |

---

## 6. Hoja de ruta (sección 8)

### Problemas de orden

1. **El piloto va detrás de todas las herramientas, en contra de D4.** D4 prevé un «piloto previo con integración central mientras se construyen las piezas». La subfase 4a solo tiene sentido si el piloto empieza **antes** de completar la fase 3. Propuesta: 4a empieza tras la fase 2 y la fase 3.0, y transcurre en paralelo con el resto de la fase 3; 4b, al terminar la fase 3.
2. **Faltan correcciones inmediatas** que no dependen de ninguna decisión. Propuesta de **fase 0b**: corregir 4.15, 4.16 y 4.17 en el checker con pruebas, y desactivar la memoria automática (4.5). Son cambios pequeños y, en el caso de 4.15, protegen las reglas duras vigentes.
3. **Generador y checker se diseñan juntos** (4.10): los puntos 3.1 y 3.2 son la misma tarea.
4. **La medición empieza tarde.** Sin línea base de tokens y orientación al **inicio** de 4a, la fase 5 no tiene con qué comparar. La instrumentación manual de D10 debe arrancar con el piloto.

### Validaciones que no demuestran lo que dicen

- **Fase 2: «el checker sigue pasando sobre el ejemplo».** El ejemplo tiene un hilo, un documento y ningún buzón con entradas, así que pasa siempre y no demuestra nada. Propuesta: crear en la fase 2 un **corpus de prueba**, con 3 hilos, entradas cruzadas y una propuesta resuelta, que reproduzca los escenarios 7.2–7.6, y usarlo como prueba positiva. Las pruebas negativas de §2.2 sirven de semilla para las de la fase 3.
- **Fase 4: «sin intervención manual en Git fuera de lo previsto».** No es medible si no se lista lo previsto. Propuesta: enumerar las operaciones manuales esperadas (rebase con regeneración de índices, confirmación del mensaje) y contar las demás.

### Pasos que faltan

- Crear y proteger `knowledge` en el repo del piloto: sin force-push, con checks requeridos, squash como único método y mensaje «PR title and description».
- Verificar en la fase 1 qué ofrece el plan de GitHub para **repos privados**. Que las reglas de rama en privados requieran un plan de pago es conocimiento previo, no verificado aquí.
- Decidir 4.20 antes de la fase 2, porque determina dónde se ejercitan los cambios del core.

### Retirar

- Fase 3.6, hooks locales y de Claude Code sobre `git commit`: ver 4.3, corrección 1.

---

## 7. Afirmaciones de la auditoría que el repo o las fuentes corrigen

| Afirmación | Corrección |
|---|---|
| 4.5: el ajuste de memoria lo cita «una guía de terceros» | Es oficial: `autoMemoryEnabled` y `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`. |
| 4.5: el riesgo aparece «con varias instancias en paralelo» | Aparece también en serie: la memoria es una por repo y todos los hilos comparten repo. |
| 4.11: `owner` debe ser una persona (premisa) | El ejemplo dice «persona o agente» (`MANIFEST.md:12`). |
| 4.9.2: el trailer exige comprobar §4 | Ya lo cubre `GIT_COMMIT_RULES.md:41-49`. |
| 4.3: los hooks sobre `git commit` como capas | Contradicen el alcance de D5 (validar lo que entra a `knowledge`). |
| 4.10 (a): job de índices tras el merge | Incompatible con el checker actual (T13) sin un modo PR. |
| D6: las evaluaciones no necesitan hilo «hoy» | Tampoco lo tiene el core: es una propiedad del repo entero (4.20), no de las evaluaciones. |
| §5: «clon superficial» | Esta evaluación usa el historial completo (6 commits); «Caso 1» queda verificado. |

---

## 8. Propuesta de decisión por hallazgo

| Hallazgo | Propuesta |
|---|---|
| 4.15, 4.16, 4.17 | Corregir ya (fase 0b). |
| 4.5 | Adoptar ya (fase 0b). |
| 4.20 | **Decidido (2026-10-27):** `warp` es la distribución, no una instancia; el core es de solo lectura en las instancias. Ver `PROPUESTA_CAPA_INSTALACION.md`. |
| 4.1 + 4.8 | Adoptar fusionados, con tres perfiles. |
| 4.2 | Adoptar: solo remisión, `@` más prosa. |
| 4.3 | Adoptar las capas 1, 2 y 5; retirar la 3 y la 4; fijar el ajuste de squash. |
| 4.4 | Adoptar, con las dos zonas y sin vista generada. |
| 4.6, 4.7, 4.12 | Adoptar con los matices indicados. |
| 4.11 | Adoptar con la regla revisada en §8b (autor = `owner` o aprobación del `owner`). |
| 4.9 | Adoptar los puntos 2, 3 y 5; los puntos 4 y 6 ya quedan resueltos por D10 y por la propia auditoría. |
| 4.10 | Adoptar el generador con la opción (c). |
| 4.13 | Medir en el piloto. |
| 4.14, 4.18, 4.19 | Incorporar a la fase 3.1. |
| 4.21 | Renombrar `task` → `request` (pregunta abierta 1). |

---

## 8b. Revisiones posteriores a la evaluación (2026-10-27)

Decisiones tomadas al discutir esta evaluación. Detalle en `PROPUESTA_CAPA_INSTALACION.md`.

- **4.20:** `warp` es la distribución, no una instancia. Ver la decisión en §4.20.
- **D2 de la auditoría, revisada:** se mantiene un responsable único por hilo y una rama activa por tarea. **Se retira** la comprobación de que «quien empieza es el responsable». Cualquier usuario activo puede conectarse a cualquier hilo y trabajar en él; la responsabilidad se ejerce al integrar.
- **4.11, revisado:** la regla de CI pasa de «el autor del PR es el `owner`» a «**el autor es el `owner` o el `owner` aprobó el PR**». Desaparece así la tensión de CODEOWNERS cuando contribuye otra persona. `owner` es un `github` de `warp/USERS.md`. La rigidez se regula con `enforcement: advisory | strict` en `warp.yaml`; las invariantes estructurales son siempre errores.
- **Gobierno del proyecto:** un hilo con identificador reservado `governance` tiene autoridad sobre `warp.yaml`, `warp/USERS.md`, `AGENTS.md`, `.claude/settings.json` y la CI de cada instancia.

---

## 9. Fuentes

- Claude Code, memoria y `AGENTS.md`: https://code.claude.com/docs/en/memory (consultado 2026-10-27).
- Claude Code, hooks: https://code.claude.com/docs/en/hooks (consultado 2026-10-27; página leída de forma parcial, hasta 100.000 caracteres).
- GitHub, squash de PRs: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/configuring-commit-squashing-for-pull-requests
- GitHub, ramas protegidas: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
- Pruebas: script fuera del repo; reproducibles bajo petición.
