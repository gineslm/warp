# example-notes — HANDOFF

Cola de inputs pendientes dirigidos a `example-notes`. Cualquier otro THREAD puede añadir aquí una entrada con contexto y evidencia; solo `example-notes` la resuelve y la retira, en el mismo commit que aplica la decisión.

Actualmente no hay entradas pendientes.

Estructura orientativa de una entrada (ver `docs/core/THREAD_ARCHITECTURE.md`, §7.3), a título ilustrativo — no es una entrada real:

```text
origin_thread: <thread-id emisor>
type: proposal | review | need | task
summary: ...
context: ...
evidence: ...
target_scope: ...
status: proposed | in_review | deferred | ready_to_apply
working_notes: ...
```
