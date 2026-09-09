# Warp — Arquitectura de THREADs y conocimiento

**Versión:** 2.1.0  
**Estado:** Especificación operativa  
**Idioma:** español (España)  
**Repositorio:** `tu-organización/tu-repositorio`  
**Rama raíz de conocimiento:** `knowledge`

## 1. Propósito

Warp organiza la producción y validación de conocimiento apoyada por agentes de IA mediante **THREADs persistentes**.

Un THREAD no es un chat. Es una línea de trabajo, investigación o gestión que conserva una responsabilidad definida y puede ser atendida por distintas conversaciones o agentes a lo largo del tiempo.

El sistema está diseñado para potenciar trabajo y validación humana, no para automatizar de forma autónoma todas las decisiones.

## 2. Principios fundamentales

1. La conversación/agente es temporal; el repositorio es la memoria duradera.
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

## 3. Ramas del proyecto

```text
knowledge → conocimiento y estructura consolidados
develop   → integración del software
main      → software estable/desplegable
```

### `knowledge`

Es la raíz de bootstrap y la referencia autoritativa para:

- arquitectura y reglas;
- THREADs, MANIFESTs y HANDOFFs;
- índices derivados;
- documentos de conocimiento;
- decisiones consolidadas.

### `develop` y `main`

Pertenecen al ciclo del software. Una implementación puede fijar explícitamente una base histórica de conocimiento mediante un SHA cuando sea necesario para reproducibilidad.

Las ramas de trabajo (`agent/*`, `feature/*`, etc.) son espacios operativos y nunca sustituyen a `knowledge` como fuente global de verdad.

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

Cada THREAD tiene exactamente un HANDOFF persistente.

El HANDOFF es la **cola de inputs pendientes** dirigidos a la responsabilidad del THREAD:

- propuestas;
- revisiones;
- necesidades;
- tareas inter-THREAD.

El HANDOFF recoge exclusivamente inputs procedentes de otros THREADs. El trabajo propio de un THREAD no se encola aquí: se resuelve y se escribe directamente en los documentos bajo su autoridad.

No es:

- resumen de conversación;
- memoria de sesión;
- documento de continuidad de agente;
- archivo de decisiones terminadas;
- mecanismo de transferencia de responsabilidad.

### 7.2 Autoridad

Cualquier THREAD distinto del receptor puede registrar una entrada en el HANDOFF receptor con contexto y evidencia suficientes.

Sólo el THREAD propietario del HANDOFF puede:

- evaluar la entrada;
- cambiar su estado operativo;
- resolverla;
- modificar el conocimiento bajo su responsabilidad.

### 7.3 Estructura conceptual

Una entrada es similar a un ADR en cuanto conserva el contexto de una decisión potencial mientras está abierta, aunque no todas las entradas sean decisiones arquitectónicas.

Estructura mínima orientativa:

```yaml
origin_thread:
type: proposal | review | need | task
summary:
context:
evidence:
target_scope:
status: proposed | in_review | deferred | ready_to_apply
working_notes:
```

Puede representarse como dos zonas lógicas:

| Entrada / propuesta | Estado / trabajo receptor |
|---|---|
| escribible por el emisor | gestionado exclusivamente por el THREAD receptor |

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
retirar entrada del HANDOFF
    ↓
MISMO COMMIT
```

Una entrada `deferred` sigue pendiente y permanece en el HANDOFF.

Cuando se resuelve, desaparece del HANDOFF. Git conserva la entrada retirada, la decisión y su motivo.

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

La reducción de contexto no reduce obligaciones. Los cambios estructurales se validan con `scripts/check_knowledge.py`, que comprueba invariantes mecánicas sin sustituir el juicio semántico.

## 9. Crear, conectar y proponer

### Crear

Crear MANIFEST + HANDOFF y consolidarlos en `knowledge`. Antes de hacerlo, cargar las secciones de arquitectura/bootstrap indicadas en `PROJECT_AGENT_CONTEXT.md`.

### Conectar

Localizar el THREAD, leer el MANIFEST, incorporarse a su responsabilidad y consultar después HANDOFF y corpus relevante. Para este caso ordinario basta la superficie mínima salvo que la operación posterior requiera reglas adicionales.

### Proponer a otro THREAD

Cuando un THREAD detecta una necesidad fuera de su autoridad:

1. identifica el THREAD responsable mediante `THREAD_INDEX.md` / `DOCUMENT_INDEX.md`;
2. no modifica el documento externo;
3. registra una propuesta en el HANDOFF receptor;
4. conserva evidencia y contexto;
5. continúa dentro de su responsabilidad salvo bloqueo explícito.

Antes de crear o resolver una entrada HANDOFF se cargan las reglas específicas indicadas en `PROJECT_AGENT_CONTEXT.md`.

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

`docs/core/THREAD_INDEX.md`

Descubre:

- THREADs existentes;
- estado;
- dominio/responsabilidad;
- MANIFEST;
- HANDOFF.

Forma canónica: `docs/core/THREAD_INDEX_TEMPLATE.md`.

La fuente autoritativa son los MANIFESTs.

### DOCUMENT_INDEX

`docs/core/DOCUMENT_INDEX.md`

Descubre:

- documento;
- propósito/ámbito;
- THREAD con autoridad;
- MANIFEST que permite verificarla.

Forma canónica: `docs/core/DOCUMENT_INDEX_TEMPLATE.md`.

Los índices no son un segundo corpus ni una segunda fuente de verdad.

## 13. Git y decisiones

La estrategia canónica vive en `docs/core/GIT_COMMIT_RULES.md`.

Principio:

> **un commit = una decisión**

La lista de pendientes conserva sólo el presente abierto. Git conserva el pasado resuelto.

No se mantienen registros paralelos de decisiones terminadas salvo que documenten información que Git y el conocimiento vigente no puedan expresar.

## 14. Autoridad de fuentes

| Información | Fuente principal |
|---|---|
| arquitectura | `THREAD_ARCHITECTURE.md` |
| reglas operativas | `PROJECT_WORKING_RULES.md` |
| superficie mínima del agente | `PROJECT_AGENT_CONTEXT.md` |
| bootstrap detallado | `THREAD_CONTEXT_BOOTSTRAP.md` |
| estrategia Git | `GIT_COMMIT_RULES.md` |
| identidad/estado de THREAD | MANIFEST |
| inputs pendientes | HANDOFF |
| descubrimiento de THREADs | `THREAD_INDEX.md` (derivado) |
| descubrimiento del corpus/autoridad | `DOCUMENT_INDEX.md` (derivado) |
| validación estructural | `scripts/check_knowledge.py` |
| conocimiento vigente | documentos del corpus |
| historial de decisiones/evolución | Git |
| software en integración | `develop` |
| software estable | `main` |

## 15. Cierre de un THREAD

Antes de cerrar:

1. cargar las reglas de cierre indicadas en `PROJECT_AGENT_CONTEXT.md`;
2. revisar su HANDOFF;
3. resolver o clasificar entradas abiertas;
4. consolidar conocimiento vigente;
5. transferir explícitamente autoridad documental que no pueda quedar sin responsable;
6. actualizar MANIFEST e índices;
7. ejecutar `scripts/check_knowledge.py`;
8. validar/testear cuando proceda.

El THREAD cerrado mantiene su MANIFEST y su HANDOFF persistente. El HANDOFF puede quedar vacío/cerrado y las nuevas propuestas deben dirigirse a la responsabilidad sucesora cuando exista.

## 16. Disposición física actual

```text
docs/
├── core/
│   └── threads/
└── threads/
```

La ubicación física no determina la autoridad documental. La organización futura del corpus puede evolucionar sin cambiar el principio de corpus común + autoridad única.

Los artefactos operativos de un THREAD se nombran por rol (`MANIFEST.md`, `HANDOFF.md`). Los documentos de conocimiento pueden estar físicamente próximos al THREAD responsable, pero no se consideran silos privados.

## 17. Cuestiones abiertas

La arquitectura considera abiertas únicamente cuestiones que no alteran las invariantes anteriores:

- futura taxonomía de THREADs (investigación, gestión u otros);
- organización física futura del corpus;
- reglas de agrupación de autoridad para conjuntos de documentos, manteniendo un único THREAD efectivo por documento;
- posible integración futura de `scripts/check_knowledge.py` en CI o protecciones de `knowledge`;
- evolución futura hacia modelos de grafo si aportan valor real sin complejidad innecesaria.

## 18. Historial

| Versión | Fecha | Cambio |
|---|---|---|
| 2.0.0 | 2026-09-08 | Consolidación posterior a la migración: MANIFEST como entrada, HANDOFF único y pendiente, índices separados, corpus común y autoridad documental única. |
| 2.0.1 | 2026-09-08 | Se aclara que el HANDOFF recoge exclusivamente inputs procedentes de otros THREADs; el trabajo propio no se encola. |
| 2.0.2 | 2026-09-08 | Se alinea el contrato del MANIFEST: identidad estructurada en YAML y responsabilidad obligatoria como sección Markdown no duplicada. |
| 2.1.0 | 2026-09-08 | Se adopta divulgación progresiva: el agente carga una superficie mínima por defecto y consulta arquitectura/reglas completas sólo según la operación, apoyado por validación estructural automática. |
