# Warp — instrucciones para agentes en este repositorio

Este repositorio es la **distribución** del método Warp, no una instancia: aquí no hay THREADs propios. Se trabaja en mejorar el método.

Las instrucciones para agentes de un proyecto que usa Warp son otras: las define `warp/core/AGENTS_TEMPLATE.md`.

## Qué hay

- `warp/core/` — el método, lo que se instala en cada proyecto.
- `warp/scripts/` — herramientas.
- `examples/minimal/` — instancia de ejemplo y corpus de prueba.
- `tests/` — pruebas del checker.
- `docs/evaluaciones/` — evaluaciones y propuestas; no son metodología vigente.

## Cómo se trabaja

1. Una decisión = un PR, en una rama `agent/<tema>` desde `main`.
2. Antes de cambiar `warp/core/`, lee completos `warp/core/THREAD_ARCHITECTURE.md` y `warp/core/PROJECT_WORKING_RULES.md`.
3. Para cambios de fondo en el core, enseña antes la redacción y espera el visto bueno.
4. Antes de cada commit, enseña el mensaje (formato de `warp/core/GIT_COMMIT_RULES.md` §8) y espera confirmación.
5. Mantén la coherencia: versión e historial de cada documento, referencias cruzadas, ejemplo y README si cambia la estructura, y la nota de promoción en la propuesta de `docs/evaluaciones/` si procede.
6. Valida antes de integrar:
   - `python warp/scripts/check_knowledge.py examples/minimal`
   - `python tests/test_check_knowledge.py`
   - `python tests/test_warp_init.py`
7. Integra solo con merge commit (`gh pr merge <n> --merge`); la persona confirma en el terminal. Nunca squash, rebase ni force-push.
8. Después del merge: `main` actualizado y la rama local borrada.

## Qué no se hace

- No reescribir las rutas de `docs/evaluaciones/`: describen el repositorio en su fecha.
- Ni secretos ni información sensible, ni siquiera en borradores.
- No usar la memoria del agente como fuente de verdad (está desactivada en `.claude/settings.json`).
