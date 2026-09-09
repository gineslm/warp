# Warp — Bootstrap de contexto de THREADs

**Versión:** 2.1.0  
**Estado:** Activo  
**Idioma:** español (España)  
**Repositorio:** `tu-organización/tu-repositorio`  
**Rama raíz de conocimiento:** `knowledge`

## 1. Propósito

Este documento define la secuencia operativa detallada para incorporar una conversación/agente a Warp cuando la operación requiere más que la superficie mínima de `PROJECT_AGENT_CONTEXT.md`.

El modelo subyacente vive en `docs/core/THREAD_ARCHITECTURE.md`. La conversación es temporal; el THREAD y el corpus viven en el repositorio.

## 2. Secuencia por defecto

El arranque ordinario no exige cargar arquitectura y reglas completas.

```text
knowledge
  ↓
PROJECT_AGENT_CONTEXT.md
  ↓
THREAD_INDEX.md + DOCUMENT_INDEX.md
  ↓
MANIFEST del THREAD
  ↓
HANDOFF del THREAD
  ↓
corpus relevante
  ↓
rama de trabajo, si procede
```

Nunca reconstruir el estado global desde una rama de trabajo ni desde el histórico de una conversación.

## 3. Resolver o crear el THREAD

### THREAD existente

1. localizarlo en `docs/core/THREAD_INDEX.md`;
2. leer su MANIFEST;
3. verificar estado, responsabilidad y autoridad documental;
4. leer su único HANDOFF persistente;
5. descubrir documentos relevantes mediante `docs/core/DOCUMENT_INDEX.md` y referencias del MANIFEST.

Para este caso ordinario no es necesario leer la arquitectura completa.

### Responsabilidad nueva

Antes de crear un THREAD, leer `THREAD_ARCHITECTURE.md` §5–§6.

Si no existe un THREAD compatible:

1. crear su MANIFEST;
2. crear simultáneamente su único HANDOFF persistente;
3. declarar responsabilidad, alcance, autoridad documental y dependencias;
4. registrar `origin.type` y, cuando corresponda, `created_from_knowledge_commit`;
5. consolidar ambos artefactos en `knowledge`;
6. actualizar los índices derivados;
7. ejecutar `python scripts/check_knowledge.py`.

Un HANDOFF provisional puede preceder al MANIFEST cuando una responsabilidad nueva sea propuesta por otro THREAD. No existe THREAD hasta que se crea su MANIFEST.

## 4. Incorporación del agente

El agente se incorpora **mediante el MANIFEST**.

El HANDOFF no es un resumen de sesión ni una vía alternativa de incorporación. Se consulta después del MANIFEST para conocer únicamente inputs todavía no resueltos procedentes de otros THREADs.

## 5. Corpus documental

El corpus es común para lectura. `DOCUMENT_INDEX.md` permite descubrir documentos, ámbito y autoridad de evolución.

Un THREAD puede leer cualquier documento necesario, pero sólo puede modificar directamente los que estén bajo su autoridad. Si necesita cambiar otro documento, registra una propuesta en el HANDOFF del THREAD responsable.

La autoridad de un documento es única. Los documentos transversales se gobiernan mediante un THREAD gestor cuando sea necesario.

Antes de cambiar autoridad documental o gobernar un documento transversal, leer `THREAD_ARCHITECTURE.md` §11 y ejecutar el checker tras materializar el cambio.

## 6. Contrato de trabajo de la sesión

Antes de trabajo sustantivo, la conversación debe poder identificar:

```text
THREAD:
Responsabilidad:
Estado:
Dentro de alcance:
Fuera de alcance:
Documentos bajo autoridad directa:
Corpus/dependencias relevantes:
HANDOFF:
Rama de trabajo, si procede:
Validación requerida:
```

## 7. Propuestas fuera de alcance

Antes de proponer o modificar una entrada HANDOFF, aplicar `THREAD_ARCHITECTURE.md` §7 y §9.

Cuando aparezca una necesidad fuera de la autoridad del THREAD:

```text
PROPUESTA
Origen THREAD:
THREAD receptor:
Necesidad:
Contexto:
Evidencia:
¿Bloquea?: sí/no
```

Registrar la propuesta en el HANDOFF del receptor. El HANDOFF sólo admite inputs procedentes de otros THREADs; el trabajo propio no se encola. La entrada no implica aceptación ni dependencia automática.

## 8. Resolución de una entrada HANDOFF

Mientras está abierta, la entrada permanece en el HANDOFF.

Cuando el THREAD receptor adopta una decisión terminal:

```text
entrada pendiente
      ↓
decisión
      ↓
cambio real o rechazo
      ↓
retirar entrada
      ↓
MISMO COMMIT
```

Git conserva el historial; el HANDOFF vuelve a representar sólo el presente pendiente.

## 9. Disciplina Git

Antes de guardar cambios, leer/aplicar `docs/core/GIT_COMMIT_RULES.md`:

- un commit = una decisión;
- el mensaje explica el porqué;
- no duplicar metadatos que Git ya conserva;
- conservar SHAs explícitos sólo cuando tengan significado semántico o reproducible.

## 10. Cierre, archivo o reapertura de un THREAD

Antes de cerrar, archivar o reabrir un THREAD, leer `THREAD_ARCHITECTURE.md` §15.

Para cerrar:

1. revisar el HANDOFF;
2. resolver o clasificar entradas abiertas;
3. consolidar conocimiento vigente;
4. transferir autoridad documental que no pueda quedar sin responsable;
5. actualizar MANIFEST e índices;
6. ejecutar `python scripts/check_knowledge.py`;
7. validar/tests cuando proceda.

Finalizar una conversación ordinaria no equivale a cerrar el THREAD y no crea ni reemplaza su HANDOFF.

## 11. Comprobador de coherencia

`scripts/check_knowledge.py` verifica estructura e índices sin modificar el repositorio.

Ejecutar especialmente cuando se modifiquen:

- MANIFESTs;
- HANDOFFs;
- `THREAD_INDEX.md`;
- `DOCUMENT_INDEX.md`;
- rutas de documentos;
- autoridad documental.

El checker no juzga significado, calidad de responsabilidad, oportunidad de una propuesta ni si un commit representa realmente una única decisión.

## 12. Tabla de divulgación progresiva

| Operación | Fuente adicional obligatoria |
|---|---|
| trabajo ordinario en documentos propios | ninguna |
| crear THREAD | Arquitectura §5–§6 |
| proponer/resolver HANDOFF | Arquitectura §7 y §9 |
| cambiar autoridad documental | Arquitectura §11 |
| cerrar/archivar/reabrir THREAD | Arquitectura §15 |
| cambiar el sistema de THREADs/reglas/bootstrap | Arquitectura + `PROJECT_WORKING_RULES.md` completos |
| guardar cambios | `GIT_COMMIT_RULES.md` |
| cambio estructural | `scripts/check_knowledge.py` |

## 13. Versión compacta

> Trabaja contra `tu-organización/tu-repositorio`. Entra por `knowledge` y lee primero `PROJECT_AGENT_CONTEXT.md`. Usa los índices para localizar THREAD y documentos, conéctate mediante el MANIFEST, consulta el HANDOFF sólo como cola inter-THREAD pendiente y lee el corpus necesario. Para operaciones estructurales carga las reglas adicionales indicadas en la tabla de divulgación progresiva y ejecuta `scripts/check_knowledge.py` cuando corresponda.

## 14. Historial

| Versión | Fecha | Cambio |
|---|---|---|
| 2.0.0 | 2026-09-08 | Bootstrap consolidado conforme al modelo persistente de HANDOFF e índices materializados separados. |
| 2.1.0 | 2026-09-08 | Se adopta divulgación progresiva y se elimina la lectura obligatoria de arquitectura/reglas completas en el caso ordinario. |
