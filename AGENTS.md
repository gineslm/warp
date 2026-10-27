# Warp — instrucciones para agentes en este repositorio

Este repositorio es la **distribución** del método Warp, no una instancia: aquí no hay THREADs propios. Se trabaja en mejorar el método.

Las instrucciones para agentes de un proyecto que usa Warp son otras: las define `warp/core/AGENTS_TEMPLATE.md`.

## Qué hay

- `warp/core/` — el método, lo que se instala en cada proyecto.
- `warp/scripts/` — herramientas.
- `examples/minimal/` — instancia de ejemplo y corpus de prueba.
- `tests/` — pruebas del checker, del instalador y del paquete.
- `tools/` — herramientas de la distribución (no se instalan): `build_package.py` genera el paquete descargable.
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
   - `python tests/test_build_package.py` (desde un árbol sin cambios pendientes en `warp/`)
7. Integra solo con merge commit (`gh pr merge <n> --merge`); la persona confirma en el terminal. Nunca squash, rebase ni force-push.
8. Después del merge: `main` actualizado y la rama local borrada.

## Publicar una versión

Cuando `main` acumula un conjunto coherente de cambios en el método, y solo si la persona lo decide:

1. Sube `warp/VERSION` en su propio PR, según el esquema de `warp/core/THREAD_ARCHITECTURE.md` §16.2 (MAJOR si las instancias deben migrar), y ajusta el `warp_version` del ejemplo.
2. Tras el merge, con `main` actualizado: `python tools/build_package.py`.
3. Enseña las notas de la versión y espera confirmación.
4. Etiqueta anotada sobre el merge: `git tag -a vX.Y.Z <sha> -F <notas>` y `git push origin vX.Y.Z`.
5. Release con el paquete adjunto: `gh release create vX.Y.Z dist/warp-X.Y.Z.zip --title "Warp X.Y.Z" --notes-file <notas>`. Claude Code pide confirmación en el terminal: publicar es una decisión de la persona.

## Qué no se hace

- No reescribir las rutas de `docs/evaluaciones/`: describen el repositorio en su fecha.
- Ni secretos ni información sensible, ni siquiera en borradores.
- No usar la memoria del agente como fuente de verdad (está desactivada en `.claude/settings.json`).
