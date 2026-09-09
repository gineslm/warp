# Warp — Plantilla de índice de THREADs

**Versión:** 1.1.0  
**Estado:** Plantilla  
**Idioma:** español (España)  
**Repositorio:** `tu-organización/tu-repositorio`  
**Rama raíz de conocimiento:** `knowledge`

## 1. Propósito

Esta plantilla define la forma canónica de un índice materializado de THREADs.

El índice es un artefacto de **descubrimiento**: permite localizar qué THREADs existen, cuál es su responsabilidad actual y dónde están sus artefactos operativos principales.

El índice es **derivado y no autoritativo**. Debe poder reconstruirse a partir de los MANIFEST consolidados en `knowledge`. Si una fila del índice contradice al MANIFEST correspondiente, **prevalece el MANIFEST**.

El índice no crea THREADs, no cambia su estado y no sustituye al MANIFEST.

## 2. Principios

1. Una fila representa un THREAD existente; por definición debe existir su MANIFEST.
2. Todo THREAD existente tiene exactamente un HANDOFF persistente y el índice debe referenciarlo.
3. El índice contiene únicamente información útil para descubrimiento y navegación.
4. No duplica historial que Git ya conserva.
5. No incluye `created_from_knowledge_commit` ni otros SHAs históricos salvo que exista una necesidad explícita de descubrimiento que lo justifique.
6. No existe el concepto de «handoff vigente» frente a handoffs históricos de sesión.
7. El estado, la responsabilidad y las rutas deben coincidir con el MANIFEST.
8. Los campos todavía no definidos por la arquitectura —por ejemplo futuros tipos de THREAD— no se incorporan a la plantilla hasta que exista una decisión canónica.

## 3. Plantilla

```markdown
# <Proyecto> — Índice de THREADs

**Versión:** <versión>  
**Estado:** Activo  
**Rama raíz de conocimiento:** `knowledge`

## Naturaleza

Artefacto derivado y no autoritativo de descubrimiento. Se reconstruye desde los MANIFEST. Si existe discrepancia, prevalece el MANIFEST.

## THREADs

| thread_id | status | domain | responsibility | MANIFEST | HANDOFF |
|---|---|---|---|---|---|
| `<thread-id>` | `<status>` | `<dominio>` | `<responsabilidad resumida>` | `<ruta/MANIFEST.md>` | `<ruta/HANDOFF.md>` |

## Mantenimiento

Regenerar cuando se cree, archive/cierre, reactive o cambie de responsabilidad un THREAD, o cuando cambie la ruta de su MANIFEST/HANDOFF.
```

## 4. Definición de campos

| Campo | Función | Fuente |
|---|---|---|
| `thread_id` | Identidad estable del THREAD. | MANIFEST |
| `status` | Estado operativo vigente. | MANIFEST |
| `domain` | Dominio o área general en la que opera. | MANIFEST |
| `responsibility` | Resumen corto de la responsabilidad vigente. | MANIFEST |
| `MANIFEST` | Ruta al contrato autoritativo del THREAD. | estructura del repositorio / MANIFEST |
| `HANDOFF` | Ruta al único HANDOFF persistente del THREAD. | MANIFEST |

## 5. Qué no debe contener

El índice no debe convertirse en un segundo MANIFEST. En particular, no debe copiar:

- historial del THREAD;
- commits de creación o consolidación;
- decisiones ya resueltas;
- dependencias detalladas;
- entregables;
- listas de documentos bajo autoridad;
- contenido del HANDOFF.

La información anterior se resuelve desde sus fuentes canónicas cuando sea necesaria.

## 6. Validación mínima

Antes de considerar válido un índice materializado:

- cada `thread_id` debe resolver a un MANIFEST existente en `knowledge`;
- `status`, `domain` y `responsibility` deben coincidir con el MANIFEST;
- cada ruta `MANIFEST` debe existir;
- cada ruta `HANDOFF` debe existir y corresponder al único HANDOFF persistente declarado por el MANIFEST;
- no debe existir una fila para una responsabilidad que todavía no tenga MANIFEST;
- no debe mantenerse información histórica sólo por conveniencia: Git conserva la evolución.

## 7. Historial

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-09-08 | Primera definición de la plantilla canónica de índice de THREADs. |
| 1.1.0 | 2026-09-08 | Se hace obligatoria la referencia al único HANDOFF persistente de cada THREAD. |
