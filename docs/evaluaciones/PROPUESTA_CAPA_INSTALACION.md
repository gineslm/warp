# Propuesta — Capa de instalación de Warp

**Fecha:** 2026-10-27
**Estado:** propuesta. Fuera del core; no es metodología vigente. Se promueve a `warp/core/` y a la raíz cuando se construya.
**Origen:** decisiones tomadas al evaluar `EVALUACION_2026-10-27.md` (§4.20 y revisiones posteriores).
**Promovido al core:** estructura `warp/` (arquitectura 2.2.0); rama `knowledge` y `layout`, THREAD `governance`, categorías de archivo, `warp.yaml` y `warp/USERS.md` (arquitectura 2.3.0, §3, §4.4 y §16); modelo de autoridad y `enforcement` (arquitectura 2.4.0, §4.1, §4.5 y §16.2); buzón por entradas (arquitectura 2.5.0, §7), con el tipo `task` renombrado a `request`. Tareas y ramas de trabajo (arquitectura 2.6.0, §9.4). Merge commit, dos niveles de mensaje y `Sustituye:` (`GIT_COMMIT_RULES.md` 1.1.0). `USERS.md` se adoptó con formato de **tabla**, no de bloque YAML (§7 de esta propuesta). La forma vigente es la del core.

---

## 1. Decisiones adoptadas

| Decisión | Consecuencia |
|---|---|
| El repo `warp` es la **distribución** del método, no una instancia gobernada por hilos. | El core se gobierna con el proceso normal del repo: PRs y versiones. `docs/evaluaciones/` es documentación del proyecto `warp` y no necesita hilo. |
| Las mejoras al método llegan a `warp` **por PR**. | Una instancia que detecte una mejora abre un issue o un PR en `warp`. El HANDOFF sigue siendo solo intra-proyecto. |
| El **piloto es una instancia nueva** creada con el instalador. | El instalador es lo primero que prueba el piloto. |
| Instalador: **script de Python con solo la biblioteca estándar**, que también actualiza. | Coherente con `check_knowledge.py`. |
| El conocimiento vive en una **rama `knowledge` con árbol propio**, independiente del código. El instalador **solo crea `knowledge`**. | Instrucciones de agente, memoria desactivada y merge commit obligatorio se aplican solo a `knowledge`, sin limitar a los desarrolladores. Las ramas del software (`main`, `develop`…) son del equipo que lo desarrolla. Ver §3.1. |
| Parámetro **`layout: knowledge-only | with-code`** en `warp.yaml`. | En `knowledge-only`, `knowledge` es la rama principal del repo y no existe `main`. En `with-code`, `knowledge` convive con las ramas del código sin tocarlas. |
| En `knowledge`, todo Warp vive bajo **un espacio de nombres `warp/`**. | Ya no es imprescindible con árbol propio, pero no estorba y deja abierta una disposición con árbol compartido. |
| El conocimiento vive en **`warp/corpus/`**, separado de los hilos. | Transferir autoridad no mueve archivos. `warp/threads/` solo guarda artefactos operativos. |
| El ejemplo pasa a ser **una instancia completa** en `examples/minimal/`. | El checker solo tiene que entender instancias, y el ejemplo sirve de corpus de prueba. |
| La configuración del proyecto vive en **`warp.yaml`, en la raíz**, y las personas en **`warp/USERS.md`**. | Ambos son documentos gobernados por el hilo `governance`. |
| Existe un **hilo de gobierno** con identificador reservado `governance`, creado por el instalador. | Tiene autoridad sobre toda la configuración del proyecto. Ver §4. |
| **Autoridad flexible:** cualquier usuario activo trabaja en cualquier hilo; integrar exige ser el `owner` o tener su aprobación. Rigidez configurable con `enforcement`. | Revisa D2 y 4.11 de la auditoría. Ver §5. |
| **Integración desde el agente con confirmación humana:** reglas de permiso de Claude Code en `.claude/settings.json` (preguntar en cada merge, denegar los demás métodos y las operaciones destructivas). | El ciclo completo (rama, PR, validación, merge y limpieza) se hace sin pasar por la web de GitHub, y la puerta humana se mantiene en el terminal. Ver §8.3. |
| Las instrucciones de uso van en **`INSTALL.md`, en la raíz** de `warp`, enlazado desde el README. | Ver §10. |

---

## 2. Dos capas

| | Distribución (`warp`) | Instancia (proyecto) |
|---|---|---|
| Qué es | el método: reglas, plantillas, herramientas | el conocimiento de un proyecto |
| Quién la evoluciona | quien mantiene `warp`, por PR | los hilos del proyecto, según el core |
| Versionado | versiones publicadas del método | decisiones (un commit = una decisión) |

En una instancia hay tres categorías de archivo:

1. **Capa de sistema** (`warp/core/`, `warp/scripts/`): viene de `warp`, es de solo lectura y ningún hilo tiene autoridad sobre ella. Se cambia solo actualizando de versión.
2. **Derivados** (`warp.lock`, `warp/index/`): se regeneran y nunca se editan a mano. Ningún hilo tiene autoridad sobre ellos.
3. **Capa del proyecto**: todo lo demás. Cada archivo tiene exactamente un hilo con autoridad.

---

## 3. Estructura de carpetas

### 3.1 Ramas

| | `layout: knowledge-only` | `layout: with-code` |
|---|---|---|
| Ramas que crea el instalador | `knowledge` | `knowledge`, con árbol propio, sin historia común con el código |
| Rama principal del repo en GitHub | `knowledge` | la del código; no se toca |
| Ramas del software | no existen | no se tocan; si el repo está vacío, las crea el equipo de software |
| Regla «no fusionar `knowledge` en las ramas del código» | no aplica | sí, para que el conocimiento no entre en el árbol del código |
| Consultar el corpus desde el código | — | con una segunda copia de trabajo de `knowledge` (`git worktree`), o en GitHub. Leer es libre y no exige conectarse a ningún hilo |

- En un repo solo de conocimiento no se crea `main`: estaría vacía o duplicaría `knowledge`, y permitiría escribir por error saltándose sus reglas.
- Las ramas `agent/<hilo>/<tarea>` no las crea el instalador; nacen de `knowledge` con cada tarea.
- Cambiar de `knowledge-only` a `with-code` cuando un proyecto incorpora código es una decisión de `governance`.

### 3.2 Árbol de la rama `knowledge`

```text
instancia/
├── warp.yaml              configuración del proyecto         → governance
├── warp.lock              huellas de la capa de sistema      (derivado)
├── AGENTS.md              remite al contexto mínimo          → governance
├── .claude/settings.json  memoria off + reglas de permiso    → governance
├── .github/workflows/     CI (opcional)                      → governance
└── warp/
    ├── core/              método                             (sistema)
    ├── scripts/           checker, instalador                (sistema)
    ├── index/             THREAD_INDEX.md, DOCUMENT_INDEX.md (derivado)
    ├── threads/
    │   ├── governance/    MANIFEST.md + handoff/
    │   └── <thread_id>/   MANIFEST.md + handoff/
    ├── corpus/            conocimiento, organizado por tema  → según DOCUMENT_INDEX
    └── USERS.md           participantes                      → governance
```

- **`warp/corpus/`** se organiza por tema, nunca por hilo. La autoridad de cada documento la declara el MANIFEST de su hilo y la muestra el `DOCUMENT_INDEX`, no la ruta.
- **`warp/threads/<id>/handoff/`** es el buzón por entradas: un archivo por entrada (evaluación, 4.4).
- **`warp/index/`** también acogerá el futuro grafo derivado (opción 1 de `INFORME_FASE2_GRAFO.md`).

- El árbol de las ramas del código es del equipo de software, incluido su propio `AGENTS.md`. Con `with-code`, el instalador solo **sugiere** añadirle una línea del tipo «el conocimiento del proyecto está en la rama `knowledge`; consultarlo es libre».
- Los workflows de `.github/workflows/` de `knowledge` se aplican a los PRs dirigidos a `knowledge`.

### 3.3 Distribución

```text
warp/  (repo)
├── README.md, README.es.md, INSTALL.md
├── LICENSE, LICENSE-CODE, LICENSE-DOCS
├── warp/
│   ├── core/              ← lo que se instala
│   └── scripts/           ← lo que se instala
├── examples/
│   └── minimal/           instancia completa de ejemplo y corpus de prueba
└── docs/
    └── evaluaciones/      documentación del proyecto warp (no se instala)
```

`examples/minimal/` tiene su propio `warp.yaml`, `warp/USERS.md` (con usuarios ficticios), el hilo `governance`, el hilo `example-notes` y el corpus correspondiente. La CI de `warp` ejecuta el checker sobre él. Podrá crecer con más hilos y entradas cruzadas hasta reproducir los escenarios 7.2–7.6 de la auditoría.

---

## 4. El hilo `governance`

**Responsabilidad:** la configuración del sistema Warp en este proyecto y sus participantes. No gobierna el contenido del corpus: los temas transversales del conocimiento tienen sus propios hilos gestores (`THREAD_ARCHITECTURE.md` §11.3).

**Autoridad documental:** `warp.yaml`, `warp/USERS.md`, `AGENTS.md`, `.claude/settings.json` y los workflows de CI.

**No es un «tipo» de hilo.** La arquitectura deja la taxonomía de tipos como cuestión abierta (§11.3, §17), y esta propuesta no la formaliza. `governance` es un hilo corriente con un identificador reservado y tres invariantes en el checker:

1. existe exactamente un hilo `governance`;
2. tiene autoridad sobre los archivos de la lista anterior;
3. no puede estar `CLOSED` ni `ARCHIVED`.

**Último recurso, fuera del modelo:** si el `owner` de `governance` desaparece, nadie dentro de Warp puede reasignarlo. La salida es la administración del repo en GitHub. Se documenta como límite explícito, sin inventar un mecanismo adicional.

---

## 5. Modelo de autoridad

### 5.1 Separar conectar, trabajar y decidir

| Acción | Quién |
|---|---|
| Leer el corpus y conectar un agente a cualquier hilo | cualquiera |
| Trabajar en una rama de un hilo (`agent/<hilo>/<tarea>`) | cualquier usuario `active` de `USERS.md` |
| Registrar una entrada en el buzón de otro hilo | cualquiera (regla vigente, `THREAD_ARCHITECTURE.md` §7.2) |
| Integrar en `knowledge` cambios sobre documentos de un hilo | su `owner`, o cualquiera con **aprobación del `owner`** en el PR |
| Cambiar el `owner` de un hilo | el `owner` actual, o el `owner` de `governance` |

- Hay **un responsable por hilo**, que es quien da por buena cada decisión, y **muchos contribuidores posibles**. No hace falta una lista de miembros por hilo.
- El usuario de GitHub sirve para **identificar**, no para controlar el acceso. Quién puede subir ramas lo deciden los permisos del repo. Warp actúa solo al integrar.
- Que dos personas no resuelvan la misma petición lo garantiza «una rama activa por tarea» (auditoría, 4.12), no restringir quién trabaja.
- Se mantiene la **autoridad única por documento** entre hilos. Es el núcleo del diseño, y su vía flexible ya existe: proponer en el buzón del otro hilo.

### 5.2 `enforcement`

Parámetro de `warp.yaml`, gobernado por `governance`:

- **`advisory`**: las comprobaciones de **quién** («no eres el `owner` y falta su aprobación», «el `owner` no es un usuario activo») son avisos;
- **`strict`**: son errores y requisito de merge en la CI.

Las **invariantes estructurales** (MANIFEST, índices, buzones, capa de sistema) son siempre errores, sea cual sea el valor. `enforcement` solo regula la autoridad sobre personas.

Uso previsto: `advisory` para proyectos de una persona y en la subfase 4a del piloto; `strict` en la 4b, con CI. Que la rigidez haga falta se decide con datos.

`strict` con CI como requisito de merge necesita protección de ramas, que en repos privados requiere GitHub Pro o Team (evaluación, §8c). En un repo privado gratuito, `strict` solo puede aplicarse en el checker local y en las reglas del agente, no en GitHub.

---

## 6. `warp.yaml`

```yaml
warp_version: 2.2.0          # versión del método instalada
project:
  name: Portal de autoservicio
  repository: mi-org/portal-autoservicio
  language: es-ES
layout: with-code            # knowledge-only | with-code
enforcement: advisory        # advisory | strict
```

- La rama de conocimiento queda **fija como `knowledge`**: forma parte del método y no es configurable.
- **`layout`** dice si el repo contiene también software (§3.1). Lo usan el instalador, el checker (qué reglas de rama recomendar) y los agentes (si existe código y dónde).
- **`warp.lock`** (derivado) registra la versión instalada y una huella SHA-256 de cada archivo de `warp/core/` y `warp/scripts/`.

---

## 7. `warp/USERS.md`

~~~markdown
# Participantes

```yaml
users:
  - github: usuario-ux
    name: Responsable de UX
    status: active
  - github: usuario-ing
    name: Responsable de ingeniería
    status: active
```

(prosa libre: notas sobre el equipo, criterios de alta…)
~~~

- **`status: active | inactive`** desde el principio. Si alguien se va, se marca `inactive`, no se borra. Así los MANIFEST de los hilos cerrados que tenía siguen siendo válidos, y el checker puede exigir que el `owner` de un hilo **activo** sea un usuario activo.
- **Sin campo `roles` todavía.** Mismo principio que `THREAD_INDEX_TEMPLATE.md` §2.8: no se incorporan campos que la arquitectura no haya definido. El formato permite añadirlo cuando se diseñe el sistema de roles.
- **Sin emails ni otros datos personales.** Git conserva para siempre todo lo que pasa por él (mismo argumento que `GIT_COMMIT_RULES.md` §1).
- **Dar de alta a una persona** es una operación Warp normal: una entrada en el buzón de `governance`, o un cambio directo de su `owner`.

---

## 8. El instalador (`warp/scripts/warp.py`)

### 8.1 `init <destino>`

1. Comprueba que el destino es un directorio vacío o un repo Git sin capa Warp.
2. Pide o lee (`--config`):
   - los datos de `warp.yaml`;
   - la **lista inicial de usuarios** (como mínimo uno);
   - quién de ellos es el `owner` de `governance`.
3. Copia la capa de sistema y escribe `warp.lock`.
4. Genera:
   - `warp.yaml` y `warp/USERS.md`;
   - el hilo `governance` (MANIFEST y buzón vacío, `origin: USER_DECLARED`, autoridad sobre su lista de §4);
   - los índices desde las plantillas;
   - `AGENTS.md` y `.claude/settings.json`, con la memoria desactivada y las reglas de permiso de §8.3;
   - la CI, solo con `--ci`.
5. Crea la rama `knowledge` según `layout` (§3.1): como única rama y principal en `knowledge-only`, o con árbol propio, sin tocar las ramas existentes, en `with-code`. No crea `main` ni `develop`.
6. Ejecuta el checker.
7. **No hace commit.** Muestra el mensaje propuesto, del tipo `chore(warp): adoptar Warp 2.2.0`, con su «Por qué:», para que la persona lo confirme.
8. **No toca el remoto.** Imprime la protección recomendada para `knowledge`: sin force-push, checks requeridos (incluido el escaneo de secretos de cada commit del PR), merge commit como único método (squash y rebase desactivados), mensaje «PR title and description» y borrado automático de las ramas fusionadas. Con `with-code`, añade la prohibición de fusionar `knowledge` en las ramas del código y, para el `AGENTS.md` del código, la línea sugerida en §3.2. Recomienda aplicar el método de merge con una regla limitada a `knowledge`, para no afectar al software (verificar en la fase 1 que GitHub lo permite). La persona lo aplica.

### 8.2 `upgrade --from <ruta a un clon de warp>`

1. Comprueba que la capa de sistema coincide con `warp.lock`. Si alguien la editó, se detiene y lo indica.
2. Reemplaza la capa de sistema y actualiza `warp.lock` y `warp_version`. Cambiar `warp_version` modifica `warp.yaml`, así que es una decisión del hilo `governance`.
3. Si la versión nueva cambia el esquema de MANIFEST, buzón, índices o `USERS.md`, lo informa. No migra el conocimiento por su cuenta.
4. Ejecuta el checker y muestra el mensaje propuesto. Sin commit.

Sin red: la persona trae la versión nueva con `git clone` o `git fetch`. Así el script no maneja credenciales.

### 8.3 Integración desde Claude Code

Con estas reglas, el agente completa el ciclo de cada decisión sin pasar por la web de GitHub: rama, commit, PR, validación con el checker, merge y limpieza. La confirmación humana se mantiene en el terminal.

```json
{
  "autoMemoryEnabled": false,
  "permissions": {
    "ask":   ["Bash(gh pr merge *)"],
    "deny":  ["Bash(gh pr merge *--squash*)", "Bash(gh pr merge * -s*)",
              "Bash(gh pr merge *--rebase*)", "Bash(gh pr merge * -r*)",
              "Bash(git branch -D *)", "Bash(git branch --delete --force*)",
              "Bash(git push *--force*)", "Bash(git push -f*)", "Bash(git push * -f*)",
              "Bash(git reset --hard*)", "Bash(git reset * --hard*)"],
    "allow": ["Bash(git branch -d *)", "Bash(git fetch --prune*)"]
  }
}
```

- **Preguntar en cada merge** es la puerta humana: Claude Code muestra el comando y espera confirmación. No se usa «permitir», por dos razones: una decisión entraría en `knowledge` sin validación, y un texto del corpus o de un buzón podría inducir al agente a fusionar.
- **Denegar** los métodos distintos del merge commit y las operaciones que destruyen trabajo o historia. Las reglas comparan el texto del comando: cubren los casos normales, no variantes rebuscadas. La protección de fondo son los ajustes de GitHub de §8.1, paso 8.
- **Permitir** `git branch -d`, que Git rechaza si la rama no está fusionada, y `git fetch --prune`. El borrado de la rama remota lo hace GitHub al fusionar; no se permite borrar ramas en remoto desde el agente.
- **Antes de cada merge** el agente ejecuta el checker y las pruebas. Mientras no haya CI, esto lo garantiza el protocolo, no la máquina.
- **Validado en `warp`** (PR #5, 2026-10-27): el aviso de confirmación aparece aunque Claude Code esté en modo automático; el merge commit, el borrado automático de la rama remota y la limpieza local funcionaron sin intervención en GitHub.
- Las reglas son específicas de Claude Code. Otros agentes necesitan su mecanismo equivalente o la integración desde la web, y la puerta humana es la misma en ambos casos.

---

## 9. Cambios que exige en el core y en el checker

### 9.1 Rutas (en `warp`)

| Hoy | Pasa a |
|---|---|
| `docs/core/*.md` (salvo índices) | `warp/core/*.md` |
| `docs/core/THREAD_INDEX.md`, `DOCUMENT_INDEX.md` | `examples/minimal/warp/index/` (en `warp/core/` quedan solo las plantillas) |
| `scripts/check_knowledge.py` | `warp/scripts/check_knowledge.py` |
| `docs/threads/example/MANIFEST.md`, `HANDOFF.md` | `examples/minimal/warp/threads/example-notes/` (buzón como `handoff/`) |
| `docs/threads/example/NOTES.md` | `examples/minimal/warp/corpus/NOTES.md` |
| `docs/evaluaciones/` | sin cambio |

Hay que actualizar todas las rutas `docs/core/…` del core y del README. Aparecen en los seis documentos del core y en las dos plantillas.

### 9.2 Contenido del core

1. **`THREAD_ARCHITECTURE.md`:**
   - §16 se reescribe con la estructura de §3, las tres categorías de archivo (§2) y el hilo `governance` (§4);
   - §17 retira «organización física futura del corpus», que queda resuelta;
   - §4.1 define `owner` como un `github` de `USERS.md`;
   - una sección nueva recoge el modelo de autoridad de §5.
2. **Datos de proyecto fuera del core:**
   - se quita la línea `**Repositorio:** tu-organización/tu-repositorio` de las cabeceras de los siete documentos que la llevan;
   - los bloques compactos (`PROJECT_AGENT_CONTEXT.md:126`, `THREAD_CONTEXT_BOOTSTRAP.md:191`) remiten a `warp.yaml`.
3. **Plantillas nuevas en `warp/core/`:** el instalador necesita formas canónicas que hoy no existen. Solo hay un MANIFEST de ejemplo, no una plantilla. Hacen falta `MANIFEST_TEMPLATE.md`, `HANDOFF_ENTRY_TEMPLATE.md` (formato `yaml`, evaluación 4.14) y `USERS_TEMPLATE.md`.
4. **`PROJECT_AGENT_CONTEXT.md` §2:** añadir la regla dura de estado fuera del repo (evaluación, 4.5), la regla de criterio sobre información sensible (evaluación, §8b) y el modelo de autoridad en una línea.
5. **`THREAD_ARCHITECTURE.md` §3 y `PROJECT_WORKING_RULES.md` §2:** hoy dan por hecho tres ramas. Pasan a decir que Warp solo exige `knowledge`, con árbol propio, y que las ramas del software pertenecen a su propio ciclo cuando existe (§3.1).
6. **`GIT_COMMIT_RULES.md`:** la integración en `knowledge` se hace con merge commit; los dos niveles de mensaje (decisión y deliberación); y la lectura de las decisiones con `--first-parent` (evaluación, §8b).

### 9.3 Checker

1. **Raíz:** se reconoce por `warp.yaml` más `warp/core/THREAD_ARCHITECTURE.md`, no por `docs/core/…` (`check_knowledge.py:61-69`).
2. **Hilos:** se buscan solo en `warp/threads/*/`, no en cualquier `MANIFEST.md` bajo `docs/` (`:117-122`).
3. **Índices** en `warp/index/` (`:190`, `:222`).
4. **Rutas de autoridad:** aceptar cualquier ruta, incluidas `warp.yaml` y `AGENTS.md` en la raíz. Hoy exige `/` o `.md` (`:130-131`).
5. **Invariantes nuevas:**
   - `warp.yaml` válido;
   - la capa de sistema coincide con `warp.lock`;
   - `USERS.md` válido;
   - el `owner` de cada MANIFEST es un `github` de `USERS.md`, y si el hilo está activo, de un usuario `active` (según `enforcement`);
   - las tres invariantes de `governance` (§4).
6. Las correcciones de la fase 0b (evaluación, 4.15–4.17) se hacen antes y por separado.

---

## 10. Documentación de uso

- **`INSTALL.md`, en la raíz de `warp`**, enlazado desde `README.md` y `README.es.md`. El README presenta el método a quien quizá nunca lo instale; las instrucciones cambian con cada versión del instalador; y `INSTALL.md` no se copia a las instancias.
- **Cuándo:** en el **mismo PR que el instalador**, porque es la misma decisión. Mientras tanto el README no cambia.
- **Idioma:** español, como el resto de la documentación, con un resumen de uso en inglés dentro de `README.md`.
- **Contenido mínimo:**
  - requisitos: Git y Python 3.x;
  - `init`, con un ejemplo de `warp.yaml` y de la lista de usuarios;
  - la protección de `knowledge`;
  - `enforcement`;
  - el primer hilo, remitiendo al core;
  - `upgrade`;
  - cómo proponer mejoras a `warp`.
- **README:** en ese mismo PR se actualizan el §13 (estado) y el §14 (estructura).

---

## 11. Cuestiones abiertas

1. **`repository.knowledge_branch` en el MANIFEST:** con `knowledge` fijo, el campo sobra. ¿Se retira o se deja verificando que vale `knowledge`?
2. **Versión del conjunto:** hoy cada documento del core tiene su propia versión. Falta la versión del método, como etiqueta de release en `warp`, que es la que registra `warp_version`.
3. **¿La CI va incluida por defecto en `init`?**
4. **Aprobación del `owner` en `strict`:** comprobarla exige consultar la API de GitHub desde la CI. Hacerla obligatoria para el merge requiere protección de ramas: en repos privados, GitHub Pro o Team (evaluación, §8c).

---

## 12. Encaje en la hoja de ruta

- **Fase 0b** (correcciones del checker y memoria): PR a `warp` sobre la estructura actual. Es el primer uso del flujo «mejoras por PR».
- **Fase 2:** se añade la reestructuración de §9.1–§9.2. Va **antes** de los demás cambios del core, para no escribirlos dos veces sobre rutas que van a cambiar. Las plantillas nuevas (§9.2.3) se integran con el buzón por entradas (evaluación, 4.4).
- **Fase 3:** se añaden el checker de §9.3 y el instalador (`init`, `upgrade`). El instalador va antes de la CI, porque la CI la instala `init --ci`.
- **Fase 4a:** el piloto empieza con `warp.py init` en un repo nuevo, con `enforcement: advisory`, válido con cualquier plan de GitHub. **4b:** `strict` con CI obligatoria, que en un repo privado requiere GitHub Pro o Team.
