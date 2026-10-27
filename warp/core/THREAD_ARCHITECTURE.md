# Warp — Arquitectura de THREADs y conocimiento

**Versión:** 2.8.0  
**Estado:** Especificación operativa  
**Idioma:** español (España)  
**Rama raíz de conocimiento:** `knowledge`

## 1. Propósito

Warp organiza la producción y validación de conocimiento apoyada por agentes de IA mediante **THREADs persistentes**.

Un THREAD no es un chat. Es una línea de trabajo, investigación o gestión que conserva una responsabilidad definida y puede ser atendida por distintas conversaciones o agentes a lo largo del tiempo.

El sistema está diseñado para potenciar trabajo y validación humana, no para automatizar de forma autónoma todas las decisiones.

## 2. Principios fundamentales

1. La conversación/agente es temporal; el repositorio es la memoria duradera. Ninguna memoria externa al repositorio (de agentes, de proyectos de chat o local) es fuente de verdad.
2. Un THREAD existe si y sólo si existe su MANIFEST en `knowledge`.
3. El agente se incorpora a un THREAD mediante su MANIFEST.
4. Todo THREAD existente tiene exactamente un HANDOFF persistente.
5. El HANDOFF no es transición de sesión: contiene únicamente inputs todavía no resueltos procedentes de otros THREADs.
6. Git conserva la evolución histórica; los documentos representan el conocimiento vigente.
7. El corpus documental es común para lectura.
8. Cada documento tiene un único THREAD con autoridad de evolución.
9. Un THREAD no modifica directamente conocimiento bajo autoridad de otro THREAD; registra una propuesta en su HANDOFF.
10. Si un documento requiere una gobernanza transversal estable, se crea un THREAD gestor en vez de compartir la autoridad de edición.
11. Una propuesta no es una decisión ni una dependencia por el mero hecho de existir.
12. El proyecto es un sistema híbrido: el agente ayuda a investigar, estructurar, contrastar y registrar; la validación y las decisiones permanecen gobernadas por la responsabilidad correspondiente.

## 3. Ramas

Warp sólo exige una rama: **`knowledge`**.

`knowledge` tiene **árbol propio**: contiene únicamente la capa Warp de la instancia y no comparte historia con el código del proyecto, si lo hay. Es la raíz de bootstrap y la referencia autoritativa para:

- arquitectura y reglas;
- THREADs, MANIFESTs y HANDOFFs;
- índices derivados;
- documentos de conocimiento;
- decisiones consolidadas.

El parámetro `layout` de `warp.yaml` (§16.2) declara si el repositorio contiene también software:

- **`knowledge-only`**: `knowledge` es la rama principal del repositorio y no existen ramas de software.
- **`with-code`**: las ramas del software (`main`, `develop`…) pertenecen a su propio ciclo y al equipo que lo desarrolla. **`knowledge` nunca se fusiona en ellas.** Una implementación puede fijar una base de conocimiento mediante un SHA de `knowledge` cuando lo necesite para reproducibilidad.

Leer el corpus desde el código es libre y no exige conectarse a ningún THREAD.

Las ramas de trabajo (`agent/<thread_id>/<tarea>`, §9.4) nacen de `knowledge`. Son espacios operativos y nunca sustituyen a `knowledge` como fuente global de verdad.

## 4. THREAD

Un THREAD custodia el **estado de un problema o línea de trabajo** y gobierna la evolución del conocimiento dentro de su responsabilidad.

No es propietario de todo el conocimiento que consulta. Puede leer el corpus completo.

### 4.1 Identidad mínima

El bloque estructurado de identidad del MANIFEST debe expresar al menos:

```yaml
thread_id:
domain:
status:
owner:
current_cycle:
origin:
repository:
handoff:
```

Además, todo MANIFEST debe contener una sección `## Responsabilidad` no vacía que describa la responsabilidad vigente del THREAD. No se duplica ese texto en el bloque YAML.

`thread_id` permanece estable durante la vida del THREAD.

`owner` es el `github` de una persona listada en `warp/USERS.md` (§16.3). Un agente nunca es `owner`. Mientras el THREAD no esté `CLOSED` ni `ARCHIVED`, su `owner` debe estar `active`.

### 4.2 Origen

```yaml
origin:
  type: USER_DECLARED | THREAD_DERIVED | MIGRATED
  source_id:
```

- `USER_DECLARED`: responsabilidad identificada directamente por el usuario.
- `THREAD_DERIVED`: responsabilidad nueva detectada durante el trabajo de otro THREAD.
- `MIGRATED`: responsabilidad/conocimiento externo incorporado al sistema tras revisar compatibilidad.

El origen describe procedencia de la responsabilidad, no el mecanismo de incorporación de un agente.

### 4.3 Estados

```text
PROPOSED
ACTIVE
BLOCKED
CLOSED
ARCHIVED
```

No existe `READY_FOR_HANDOFF`: el HANDOFF no representa una transferencia.

### 4.4 THREAD de gobierno

Toda instancia tiene exactamente un THREAD con `thread_id: governance`.

Su responsabilidad es la configuración del sistema Warp en el proyecto y sus participantes. Tiene autoridad sobre la configuración del proyecto (§16.1): `warp.yaml`, `warp/USERS.md` y la configuración de agentes y de CI que exista en `knowledge`. No gobierna el contenido del corpus: los documentos transversales del corpus siguen el §11.3.

No puede estar `CLOSED` ni `ARCHIVED` mientras exista la instancia.

No es un tipo de THREAD: es un THREAD ordinario con un identificador reservado. La taxonomía de THREADs sigue abierta (§17).

Si su responsable deja de estar disponible y nadie dentro del modelo puede reasignarlo, el último recurso es la administración del repositorio, fuera de Warp.

### 4.5 Responsable y participación

Un THREAD tiene un único responsable, su `owner`, y puede tener muchos contribuidores.

| Acción | Quién |
|---|---|
| Leer el corpus y conectar un agente a cualquier THREAD | cualquiera |
| Trabajar en una rama del THREAD | cualquier participante `active` |
| Registrar una entrada en el HANDOFF de otro THREAD | cualquier THREAD (§7.3) |
| Integrar en `knowledge` cambios bajo autoridad del THREAD | su `owner`, o cualquier participante con aprobación del `owner` |
| Cambiar el `owner` | el `owner` actual, o el `owner` de `governance` |

- La responsabilidad se ejerce al **integrar**, no al conectarse ni al trabajar. No existe una lista de miembros por THREAD.
- El usuario de GitHub sirve para comprobar autoría y aprobación. Quién puede subir ramas lo deciden los permisos del repositorio.
- La autoridad única por documento entre THREADs (§11.2) no cambia: para modificar conocimiento de otro THREAD se sigue proponiendo en su HANDOFF.

## 5. Alta de un THREAD

Crear un THREAD significa crear y consolidar su MANIFEST.

El alta crea simultáneamente su único HANDOFF persistente.

```text
nueva responsabilidad
       ↓
MANIFEST + HANDOFF
       ↓
commit en knowledge
       ↓
THREAD existente
```

Puede existir un HANDOFF provisional antes del MANIFEST si otro THREAD detecta una responsabilidad todavía no formalizada. Ese artefacto no constituye todavía un THREAD. Al crear el MANIFEST, pasa a ser el HANDOFF persistente del nuevo THREAD.

## 6. MANIFEST

El MANIFEST es el contrato autoritativo del THREAD y el mecanismo de incorporación de nuevas instancias/agentes.

Debe resolver, cuando proceda:

- identidad y estado;
- responsabilidad;
- dentro/fuera de alcance;
- autoridad documental;
- dependencias relevantes;
- HANDOFF asociado;
- rama de trabajo, si existe;
- cuestiones abiertas.

### Referencias Git con significado semántico

Puede registrar un SHA cuando ese valor expresa una relación del modelo, por ejemplo:

```yaml
repository:
  knowledge_branch: knowledge
  created_from_knowledge_commit: <sha>
```

`created_from_knowledge_commit` fija el estado de `knowledge` utilizado al dar de alta el THREAD. Es histórico e inmutable.

Git ya conserva autor, fecha, diff e historial; no deben duplicarse sin una función semántica específica.

## 7. HANDOFF

### 7.1 Definición

Cada THREAD tiene exactamente un HANDOFF persistente: el **buzón** `warp/threads/<thread_id>/handoff/`.

El HANDOFF es la **cola de inputs pendientes** dirigidos a la responsabilidad del THREAD: propuestas, revisiones, necesidades y peticiones de otros THREADs. Cada input es una **entrada**, y cada entrada es un archivo.

El HANDOFF recoge exclusivamente inputs procedentes de otros THREADs. El trabajo propio de un THREAD no se encola aquí: se resuelve y se escribe directamente en los documentos bajo su autoridad.

No es:

- resumen de conversación;
- memoria de sesión;
- documento de continuidad de agente;
- archivo de decisiones terminadas;
- mecanismo de transferencia de responsabilidad.

### 7.2 Entradas

Una entrada es un archivo `warp/threads/<thread_id>/handoff/<nombre>.md`. El `<nombre>` es descriptivo y en minúsculas con guiones (`formulario-pago-un-paso.md`), es único en el buzón y no es un código de catalogación (`warp/core/GIT_COMMIT_RULES.md` §4). Forma canónica: `warp/core/HANDOFF_ENTRY_TEMPLATE.md`.

Una entrada es similar a un ADR en cuanto conserva el contexto de una decisión potencial mientras está abierta, aunque no todas las entradas sean decisiones arquitectónicas.

Contiene un único bloque de identidad:

```yaml
origin_thread: <thread_id emisor>
type: proposal | review | need | request
summary: <una frase>
target_scope: <documentos o ámbito afectados>
status: proposed | in_review | deferred | ready_to_apply
```

Le siguen dos secciones del emisor, `## Contexto` y `## Evidencia`, y una del receptor, `## Notas del receptor`. El contexto y la evidencia van en prosa porque suelen ser extensos; el bloque de identidad contiene sólo campos cortos y comprobables.

Un buzón sin entradas puede contener un `.gitkeep` para que el directorio exista.

### 7.3 Dos zonas y autoridad

| Zona | Contenido | Quién la escribe |
|---|---|---|
| emisor | todos los campos salvo `status`; `## Contexto` y `## Evidencia` | el THREAD emisor, mientras la entrada esté en `proposed` |
| receptor | `status` y `## Notas del receptor` | exclusivamente el THREAD receptor |

- **Registrar** es añadir un archivo nuevo al buzón receptor, con contexto y evidencia suficientes. No requiere aprobación del receptor.
- Sólo el THREAD receptor evalúa la entrada, cambia su estado, la resuelve y modifica el conocimiento bajo su autoridad.
- Una entrada no es una decisión ni una dependencia por el mero hecho de existir.

### 7.4 Resolución

```text
entrada abierta
    ↓
evaluación
    ↓
decisión terminal
    ↓
cambio real o rechazo
    ↓
borrar el archivo de la entrada
    ↓
MISMA DECISIÓN integrada en knowledge
```

Una entrada `deferred` sigue pendiente y permanece en el buzón.

Cuando se resuelve, su archivo desaparece. Git conserva la entrada retirada, la decisión y su motivo.

Como cada entrada es un archivo propio, registrar y resolver entradas distintas en paralelo no genera conflictos de fusión.

## 8. Bootstrap de un agente y divulgación progresiva

Toda incorporación comienza en `knowledge`, pero **no requiere cargar por defecto la arquitectura y las reglas completas**.

La superficie mínima es:

```text
knowledge
  ↓
PROJECT_AGENT_CONTEXT.md
  ↓
THREAD_INDEX.md + DOCUMENT_INDEX.md
  ↓
MANIFEST
  ↓
HANDOFF
  ↓
corpus relevante
  ↓
rama de trabajo, si procede
```

`PROJECT_AGENT_CONTEXT.md` contiene las reglas duras que aplican siempre y la tabla de **cuándo leer más**. `THREAD_ARCHITECTURE.md`, `PROJECT_WORKING_RULES.md`, `THREAD_CONTEXT_BOOTSTRAP.md` y `GIT_COMMIT_RULES.md` se cargan bajo demanda según la operación.

El principio es **divulgación progresiva**: el caso ordinario trabaja con el contrato mínimo; crear/cerrar THREADs, cambiar autoridad documental, operar sobre HANDOFFs, cambiar reglas o consolidar decisiones exige cargar previamente la fuente canónica correspondiente.

La reducción de contexto no reduce obligaciones. Los cambios estructurales se validan con `warp/scripts/check_knowledge.py`, que comprueba invariantes mecánicas sin sustituir el juicio semántico.

## 9. Crear, conectar, proponer y trabajar

### 9.1 Crear

Crear el MANIFEST y el buzón `handoff/` y consolidarlos en `knowledge`. Antes de hacerlo, cargar las secciones de arquitectura/bootstrap indicadas en `PROJECT_AGENT_CONTEXT.md`.

### 9.2 Conectar

Localizar el THREAD, leer el MANIFEST, incorporarse a su responsabilidad y consultar después HANDOFF y corpus relevante. Para este caso ordinario basta la superficie mínima salvo que la operación posterior requiera reglas adicionales.

### 9.3 Proponer a otro THREAD

Cuando un THREAD detecta una necesidad fuera de su autoridad:

1. identifica el THREAD responsable mediante `THREAD_INDEX.md` / `DOCUMENT_INDEX.md`;
2. no modifica el documento externo;
3. registra una entrada en el buzón del THREAD receptor (§7.2);
4. conserva evidencia y contexto;
5. continúa dentro de su responsabilidad salvo bloqueo explícito.

Antes de crear o resolver una entrada HANDOFF se cargan las reglas específicas indicadas en `PROJECT_AGENT_CONTEXT.md`.

### 9.4 Tareas y ramas de trabajo

Una **tarea** es una unidad de trabajo con un resultado concreto dentro de un THREAD: resolver una entrada de su buzón, o desarrollar un documento o una decisión propios.

- Cada tarea se trabaja en una rama `agent/<thread_id>/<tarea>`, nacida de `knowledge`. Una tarea tiene como máximo **una rama activa**.
- Si la tarea **resuelve una entrada**, `<tarea>` es el nombre del archivo de la entrada sin extensión, por ejemplo `agent/ing-frontend/formulario-pago-un-paso`. Así cualquiera puede comprobar si una entrada ya se está trabajando.
- Si la tarea **desarrolla documentos propios**, `<tarea>` es un nombre descriptivo, y el PR declara en su descripción los documentos que toca.
- **Antes de empezar**, se comprueba si ya existe una rama, local o remota, o un PR abierto para esa tarea. Si es el mismo trabajo, se retoma; si es un aporte distinto, se abre otra tarea.
- Una instancia de agente trabaja en **un único THREAD**. Si necesita algo de otro, registra una entrada en su buzón (§7).
- Varias instancias en paralelo usan **directorios de trabajo distintos** (`git worktree` o clones), nunca la misma copia.
- Si dos tareas del mismo THREAD tocan el mismo documento, se integran **en serie**: la segunda se actualiza con `knowledge` antes de integrarse.
- Registrar una entrada en el buzón de otro THREAD puede ir en la misma rama y en la misma decisión que el trabajo propio que la origina, cuando ambos responden a una sola causa.
- Una tarea termina al integrarse en `knowledge`, que es una decisión (§13), o al abandonarse. Después se borra su rama.

## 10. Dependencias y propuestas

Una propuesta no es una dependencia.

Una dependencia existe cuando el trabajo del THREAD está condicionado por conocimiento o artefactos de otra responsabilidad.

Cuando la reproducibilidad lo requiera, una dependencia puede fijarse a versión o commit. Esa referencia debe tener significado operativo, no actuar como historial manual.

## 11. Capa documental

### 11.1 Corpus común

Todos los THREADs pueden leer todo el corpus.

La transversalidad de un documento no implica autoridad compartida.

### 11.2 Autoridad única

Cada documento tiene exactamente un THREAD con autoridad de evolución.

La autoridad significa capacidad de aceptar y aplicar cambios sobre el conocimiento vigente; no significa autoría histórica ni propiedad intelectual.

Git conserva la historia de creación y modificación.

### 11.3 Documento transversal

Si varias responsabilidades necesitan gobernar establemente un documento y ninguna debe dominar a las demás:

```text
THREAD A ──propuesta──┐
THREAD B ──propuesta──┼──► HANDOFF del THREAD gestor ──► documento
THREAD C ──propuesta──┘
```

Se crea un THREAD gestor. Esto abre la posibilidad futura de tipos de THREAD, pero la taxonomía todavía no se formaliza.

### 11.4 Transferencia de autoridad

Un documento puede sobrevivir al THREAD que lo creó.

Si cambia la responsabilidad:

1. el nuevo THREAD declara autoridad en su MANIFEST;
2. se actualiza el documento si procede;
3. se regenera `DOCUMENT_INDEX.md`;
4. no se añade `created_by` para preservar historia: Git ya la conserva.

## 12. Índices derivados

### THREAD_INDEX

`warp/index/THREAD_INDEX.md`

Descubre:

- THREADs existentes;
- estado;
- dominio/responsabilidad;
- MANIFEST;
- HANDOFF.

Forma canónica: `warp/core/THREAD_INDEX_TEMPLATE.md`.

La fuente autoritativa son los MANIFESTs.

### DOCUMENT_INDEX

`warp/index/DOCUMENT_INDEX.md`

Descubre:

- documento;
- propósito/ámbito;
- THREAD con autoridad;
- MANIFEST que permite verificarla.

Lista exclusivamente los documentos del corpus (`warp/corpus/`). Todo documento del corpus figura en él. La configuración del proyecto, el método y los artefactos de THREAD no se listan (§16.1).

Forma canónica: `warp/core/DOCUMENT_INDEX_TEMPLATE.md`.

Los índices no son un segundo corpus ni una segunda fuente de verdad.

## 13. Git y decisiones

La estrategia canónica vive en `warp/core/GIT_COMMIT_RULES.md`.

Principio:

> **un commit = una decisión**

La lista de pendientes conserva sólo el presente abierto. Git conserva el pasado resuelto.

No se mantienen registros paralelos de decisiones terminadas salvo que documenten información que Git y el conocimiento vigente no puedan expresar.

La decisión es el guardado de unión (merge commit) con que una tarea entra en `knowledge`; los guardados de su rama conservan la deliberación. Ambos niveles quedan en Git y se leen por separado con `--first-parent` (`warp/core/GIT_COMMIT_RULES.md` §2 y §6).

## 14. Autoridad de fuentes

| Información | Fuente principal |
|---|---|
| arquitectura | `THREAD_ARCHITECTURE.md` |
| reglas operativas | `PROJECT_WORKING_RULES.md` |
| superficie mínima del agente | `PROJECT_AGENT_CONTEXT.md` |
| bootstrap detallado | `THREAD_CONTEXT_BOOTSTRAP.md` |
| estrategia Git | `GIT_COMMIT_RULES.md` |
| configuración del proyecto | `warp.yaml` |
| participantes | `warp/USERS.md` |
| identidad/estado de THREAD | MANIFEST |
| inputs pendientes | HANDOFF |
| descubrimiento de THREADs | `THREAD_INDEX.md` (derivado) |
| descubrimiento del corpus/autoridad | `DOCUMENT_INDEX.md` (derivado) |
| validación estructural | `warp/scripts/check_knowledge.py` |
| conocimiento vigente | documentos del corpus |
| historial de decisiones/evolución | Git |
| software, si existe | sus propias ramas (§3) |

## 15. Cierre de un THREAD

Antes de cerrar:

1. cargar las reglas de cierre indicadas en `PROJECT_AGENT_CONTEXT.md`;
2. revisar su HANDOFF;
3. resolver o clasificar entradas abiertas;
4. consolidar conocimiento vigente;
5. transferir explícitamente autoridad documental que no pueda quedar sin responsable;
6. actualizar MANIFEST e índices;
7. ejecutar `warp/scripts/check_knowledge.py`;
8. validar/testear cuando proceda.

El THREAD cerrado mantiene su MANIFEST y su HANDOFF persistente. El HANDOFF puede quedar vacío/cerrado y las nuevas propuestas deben dirigirse a la responsabilidad sucesora cuando exista.

## 16. Disposición física y capas

Todo Warp vive en la rama `knowledge`, bajo el espacio de nombres `warp/`, salvo los archivos que las herramientas exigen en la raíz:

```text
warp.yaml               configuración del proyecto
(configuración de agentes y CI, p. ej. AGENTS.md, .claude/, .github/)
warp/
├── core/               método: arquitectura, reglas, bootstrap, plantillas
├── scripts/            herramientas: comprobador estructural
├── index/              índices derivados (THREAD_INDEX.md, DOCUMENT_INDEX.md)
├── threads/
│   └── <thread_id>/    artefactos operativos: MANIFEST.md, handoff/
├── corpus/             documentos de conocimiento, organizados por tema
└── USERS.md            participantes del proyecto
```

La ubicación física no determina la autoridad documental: la declara el MANIFEST del THREAD responsable y la muestra `warp/index/DOCUMENT_INDEX.md`.

Los artefactos operativos de un THREAD se nombran por rol (`MANIFEST.md` y el buzón `handoff/`) y viven en `warp/threads/<thread_id>/`. Los documentos de conocimiento viven en `warp/corpus/`, organizados por tema y nunca por THREAD: así se refuerza que no son silos privados, y transferir su autoridad (§11.4) no obliga a moverlos ni rompe sus rutas.

### 16.1 Categorías de archivo

| Categoría | Archivos | Autoridad |
|---|---|---|
| **sistema** | método (`warp/core/`) y herramientas (`warp/scripts/`) | ninguna en la instancia: viene de la distribución de Warp, es de solo lectura y solo cambia al actualizar de versión |
| **derivados** | `warp/index/` | ninguna: se regeneran y nunca se editan a mano |
| **corpus** | `warp/corpus/` | el THREAD que la declare en su MANIFEST; se descubre en `warp/index/DOCUMENT_INDEX.md` y es transferible (§11.4) |
| **artefactos de THREAD** | `warp/threads/<thread_id>/` | el propio THREAD; su HANDOFF admite entradas de otros THREADs (§7.3) |
| **configuración del proyecto** | `warp.yaml`, `warp/USERS.md` y la configuración de agentes y CI | el THREAD `governance` (§4.4) |

La regla de autoridad única (§11.2) se cumple en las tres últimas categorías, cada una con su forma de asignarla.

Los documentos del método no forman parte del corpus ni figuran en `DOCUMENT_INDEX.md`: el corpus es el conocimiento del proyecto, y el método es la forma de gestionarlo. Las mejoras al método no se proponen en un HANDOFF: se proponen a la distribución de Warp.

### 16.2 `warp.yaml`

```yaml
warp_version: 2.8.0          # versión del método
project:
  name: <nombre>
  repository: <organización/repositorio>
  language: es-ES
layout: knowledge-only       # knowledge-only | with-code
enforcement: advisory        # advisory | strict
```

El nombre de la rama de conocimiento no es configurable: es `knowledge`.

`enforcement` regula solo las comprobaciones sobre **personas**: que el `owner` sea un participante activo y que la integración la haga o la apruebe el `owner` (§4.5). Con `advisory` son avisos; con `strict`, errores y requisito de merge. Las invariantes estructurales son siempre errores. En repos privados, hacer `strict` obligatorio en GitHub requiere un plan con protección de ramas.

### 16.3 `warp/USERS.md`

Lista de participantes del proyecto. Forma canónica: `warp/core/USERS_TEMPLATE.md`.

| github | name | status |
|---|---|---|
| `<usuario>` | `<nombre visible>` | `active` |

- `status` vale `active` o `inactive`. Quien deja el proyecto se marca `inactive` y no se borra, para que las referencias históricas sigan siendo válidas.
- No se registran emails ni otros datos personales: Git conserva para siempre lo que pasa por él.
- Los campos de roles no se incorporan hasta que la arquitectura los defina.

## 17. Cuestiones abiertas

La arquitectura considera abiertas únicamente cuestiones que no alteran las invariantes anteriores:

- futura taxonomía de THREADs (investigación, gestión u otros);
- organización temática interna de `warp/corpus/`;
- reglas de agrupación de autoridad para conjuntos de documentos, manteniendo un único THREAD efectivo por documento;
- posible integración futura de `warp/scripts/check_knowledge.py` en CI o protecciones de `knowledge`;
- evolución futura hacia modelos de grafo si aportan valor real sin complejidad innecesaria.

## 18. Historial

| Versión | Fecha | Cambio |
|---|---|---|
| 2.0.0 | 2026-09-08 | Consolidación posterior a la migración: MANIFEST como entrada, HANDOFF único y pendiente, índices separados, corpus común y autoridad documental única. |
| 2.0.1 | 2026-09-08 | Se aclara que el HANDOFF recoge exclusivamente inputs procedentes de otros THREADs; el trabajo propio no se encola. |
| 2.0.2 | 2026-09-08 | Se alinea el contrato del MANIFEST: identidad estructurada en YAML y responsabilidad obligatoria como sección Markdown no duplicada. |
| 2.1.0 | 2026-09-08 | Se adopta divulgación progresiva: el agente carga una superficie mínima por defecto y consulta arquitectura/reglas completas sólo según la operación, apoyado por validación estructural automática. |
| 2.2.0 | 2026-10-27 | Todo Warp pasa al espacio de nombres `warp/`; el corpus vive en `warp/corpus/`, separado de los THREADs y organizado por tema, para que transferir autoridad no mueva documentos. |
| 2.3.0 | 2026-10-27 | `knowledge` como única rama exigida, con árbol propio y `layout`; THREAD `governance`; cinco categorías de archivo; `warp.yaml` y `warp/USERS.md`; `DOCUMENT_INDEX` limitado al corpus; los datos del proyecto salen del core. |
| 2.4.0 | 2026-10-27 | `owner` es un participante de `warp/USERS.md`, nunca un agente; §4.5 separa leer, trabajar e integrar, y la responsabilidad se ejerce al integrar; `enforcement` en `warp.yaml`. |
| 2.5.0 | 2026-10-27 | HANDOFF como buzón por entradas: un archivo por entrada en `warp/threads/<thread_id>/handoff/`, con bloque de identidad, contexto y evidencia en prosa y dos zonas de escritura; el tipo `task` pasa a `request`. |
| 2.6.0 | 2026-10-27 | §9.4 tareas y ramas de trabajo: una rama activa por tarea, nombre de la tarea igual al de la entrada que resuelve, una instancia por THREAD y directorios de trabajo separados; subsecciones del §9 numeradas. |
| 2.7.0 | 2026-10-27 | §13: la decisión es el guardado de unión en `knowledge` y la rama conserva la deliberación. |
| 2.8.0 | 2026-10-27 | El principio 1 excluye como fuente de verdad cualquier memoria externa al repositorio. |
