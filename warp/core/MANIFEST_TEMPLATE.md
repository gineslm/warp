# Warp — Plantilla de MANIFEST

**Versión:** 1.0.1  
**Estado:** Plantilla  
**Idioma:** español (España)  
**Rama raíz de conocimiento:** `knowledge`

## 1. Propósito

Esta plantilla define la forma canónica de `threads/<thread_id>/MANIFEST.md`: el contrato autoritativo de un THREAD y su mecanismo de incorporación (`warp/core/THREAD_ARCHITECTURE.md` §4–§6).

Crear un THREAD es crear su MANIFEST y su buzón `threads/<thread_id>/handoff/` en la misma decisión.

## 2. Plantilla

````markdown
# <thread_id> — MANIFEST

**Versión:** 1.0.0  
**Idioma:** <idioma>

## Identidad

```yaml
thread_id: <thread_id>
domain: <dominio o área>
status: ACTIVE
owner: <github de un participante de USERS.md>
current_cycle: 1
origin:
  type: USER_DECLARED
  source_id: <origen>
repository:
  knowledge_branch: knowledge
handoff:
  path: threads/<thread_id>/handoff/
```

## Responsabilidad

<responsabilidad vigente del THREAD>

## Dentro de alcance

- <…>

## Fuera de alcance

- <…>

## Dependencias

- <documentos o THREADs de los que depende, si los hay>

## Autoridad documental vigente

- `corpus/<documento>.md`

## Historial

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | <fecha> | Alta del THREAD. |
````

## 3. Campos de identidad

| Campo | Valores |
|---|---|
| `thread_id` | identificador estable; `governance` está reservado (§4.4) |
| `status` | `PROPOSED`, `ACTIVE`, `BLOCKED`, `CLOSED`, `ARCHIVED` |
| `owner` | `github` de un participante de `USERS.md`; nunca un agente (§4.1) |
| `origin.type` | `USER_DECLARED`, `THREAD_DERIVED`, `MIGRATED`; los dos últimos exigen `source_id` |
| `handoff.path` | siempre `threads/<thread_id>/handoff/` |

`## Responsabilidad` es obligatoria y no se duplica en el bloque de identidad. Si el THREAD no tiene documentos bajo su autoridad, `## Autoridad documental vigente` lo indica en prosa.
