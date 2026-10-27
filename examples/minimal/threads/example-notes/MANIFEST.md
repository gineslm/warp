# example-notes — MANIFEST

**Versión:** 1.0.4  
**Idioma:** español (España)

## Identidad

```yaml
thread_id: example-notes
domain: ejemplo de uso de la metodología Warp
status: ACTIVE
owner: usuario-ejemplo
current_cycle: 1
origin:
  type: USER_DECLARED
  source_id: conversation
repository:
  knowledge_branch: knowledge
handoff:
  path: threads/example-notes/handoff/
```

## Responsabilidad

Servir como THREAD de ejemplo, genérico e inventado, para mostrar cómo se relacionan el MANIFEST, el HANDOFF y el corpus documental bajo la metodología Warp. No representa ningún dominio real.

## Dentro de alcance

- mantener `corpus/NOTES.md` como documento de ejemplo bajo su autoridad;
- ilustrar el formato mínimo de MANIFEST y del buzón de entradas definido en `warp/core/THREAD_ARCHITECTURE.md`.

## Fuera de alcance

- cualquier conocimiento de dominio real: este THREAD es puramente ilustrativo.

## Dependencias

- `warp/core/THREAD_ARCHITECTURE.md` — modelo de THREADs.
- `warp/core/PROJECT_WORKING_RULES.md` — reglas permanentes.

## Autoridad documental vigente

- `corpus/NOTES.md`

## Historial

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-09-09 | Alta del THREAD de ejemplo para validar la estructura del repositorio Warp. |
| 1.0.1 | 2026-10-27 | El ejemplo pasa a `examples/minimal/` con la estructura `warp/`; NOTES.md se mueve al corpus. |
| 1.0.2 | 2026-10-27 | `owner` pasa a ser un participante de `warp/USERS.md`. |
| 1.0.3 | 2026-10-27 | El HANDOFF pasa a ser el buzón `handoff/`, con una entrada de ejemplo. |
| 1.0.4 | 2026-10-27 | Rutas del proyecto en la raíz de la instancia. |
