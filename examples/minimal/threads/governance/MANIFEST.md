# governance — MANIFEST

**Versión:** 1.0.2  
**Idioma:** español (España)

## Identidad

```yaml
thread_id: governance
domain: gobierno del proyecto
status: ACTIVE
owner: usuario-ejemplo
current_cycle: 1
origin:
  type: USER_DECLARED
  source_id: instalación
repository:
  knowledge_branch: knowledge
handoff:
  path: threads/governance/handoff/
```

## Responsabilidad

Gobernar la configuración del sistema Warp en este proyecto y sus participantes (`warp/core/THREAD_ARCHITECTURE.md` §4.4). No gobierna el contenido del corpus.

## Dentro de alcance

- mantener la configuración del proyecto en `warp.yaml`;
- mantener la lista de participantes en `USERS.md`;
- mantener la configuración de agentes y de CI que exista en `knowledge`.

## Fuera de alcance

- el contenido de `corpus/`, que gobiernan los THREADs que declaran su autoridad;
- el método (`warp/core/`, `warp/scripts/`), que se cambia actualizando de versión.

## Autoridad documental vigente

- `warp.yaml`
- `USERS.md`

## Historial

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-10-27 | Alta del THREAD de gobierno de la instancia de ejemplo. |
| 1.0.1 | 2026-10-27 | El HANDOFF pasa a ser el buzón `handoff/`. |
| 1.0.2 | 2026-10-27 | Rutas del proyecto en la raíz de la instancia. |
