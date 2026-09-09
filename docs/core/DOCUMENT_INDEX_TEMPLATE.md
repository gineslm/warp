# Warp — Plantilla de índice documental

**Versión:** 1.0.0  
**Estado:** Plantilla  
**Idioma:** español (España)  
**Repositorio:** `tu-organización/tu-repositorio`  
**Rama raíz de conocimiento:** `knowledge`

## 1. Propósito

Esta plantilla define la forma canónica de un índice materializado del corpus documental.

El índice documental es un artefacto de **descubrimiento**: permite a un agente o persona saber qué documentos existen, qué ámbito describen y qué THREAD tiene autoridad para evolucionarlos.

El corpus es común para lectura. El índice **no limita el acceso** a un documento ni enumera qué THREADs pueden consultarlo: todos los THREADs pueden leer cualquier documento necesario para razonar dentro de su responsabilidad.

El índice es **derivado y no autoritativo**. La autoridad de evolución debe poder verificarse en el MANIFEST del THREAD responsable. Si el índice contradice a la fuente canónica de responsabilidad, prevalece ésta.

## 2. Principios

1. Cada documento del corpus puede ser potencialmente transversal para lectura.
2. Cada documento tiene **un único THREAD responsable de su evolución**.
3. Si un documento recae semánticamente sobre varias responsabilidades, no se reparte la autoridad de edición: debe existir un THREAD específico de gestión que centralice su evolución y reciba inputs de los demás mediante su HANDOFF.
4. El índice describe autoridad de evolución, no propiedad intelectual ni autoría histórica.
5. No se registra `created_by`, commit de creación ni historial de responsables: Git conserva la evolución histórica.
6. No se enumeran los THREADs consumidores o lectores de cada documento.
7. El resumen de ámbito sirve sólo para descubrimiento; el conocimiento autoritativo está en el propio documento.
8. Transferir la autoridad de evolución de un documento implica actualizar la responsabilidad/autoridad canónica correspondiente y después regenerar este índice.

## 3. Plantilla

```markdown
# <Proyecto> — Índice documental

**Versión:** <versión>  
**Estado:** Activo  
**Rama raíz de conocimiento:** `knowledge`

## Naturaleza

Artefacto derivado y no autoritativo de descubrimiento del corpus. Todos los THREADs pueden leer el corpus; la columna `authority_thread` indica exclusivamente quién puede evolucionar directamente cada documento.

## Documentos

| path | purpose / scope | authority_thread | authority_manifest |
|---|---|---|---|
| `<ruta/documento.md>` | `<tema o ámbito que describe>` | `<thread-id>` | `<ruta/MANIFEST.md>` |

## Mantenimiento

Regenerar cuando se cree, elimine o mueva un documento, cuando cambie sustancialmente su ámbito, o cuando se transfiera su autoridad de evolución a otro THREAD.
```

## 4. Definición de campos

| Campo | Función | Fuente |
|---|---|---|
| `path` | Ruta estable de descubrimiento del documento en el repositorio. | estructura del repositorio |
| `purpose / scope` | Resumen breve del tema o función del documento. | documento; sólo para descubrimiento |
| `authority_thread` | Único THREAD autorizado para evolucionar directamente el documento. | MANIFEST / responsabilidad canónica |
| `authority_manifest` | Ruta al MANIFEST que permite verificar esa autoridad. | estructura del repositorio / MANIFEST |

## 5. Regla de autoridad única

La autoridad de evolución de un documento **no puede pertenecer simultáneamente a varios THREADs**.

Si varios THREADs necesitan influir sobre un mismo documento:

```text
THREAD A ──propuesta──┐
THREAD B ──propuesta──┼──► HANDOFF del THREAD gestor ──► documento
THREAD C ──propuesta──┘
```

El THREAD gestor evalúa los inputs y centraliza la edición. Esta regla permite que el documento sea transversal sin convertir su edición en responsabilidad compartida.

La existencia futura de distintos tipos de THREAD —por ejemplo investigación frente a gestión— queda fuera de esta plantilla mientras no se formalice en la arquitectura.

## 6. Qué no debe contener

El índice documental no debe convertirse en un segundo corpus ni en un historial. No debe copiar:

- contenido o conclusiones del documento;
- lista de todos los THREADs que lo consultan;
- historial de autores o responsables;
- SHAs de creación/modificación;
- decisiones que llevaron al estado vigente;
- relaciones detalladas que ya estén expresadas en los documentos o en el modelo de conocimiento.

Git conserva la evolución; el documento conserva el conocimiento vigente; el índice sólo permite descubrirlo y localizar su autoridad de evolución.

## 7. Validación mínima

Antes de considerar válido un índice materializado:

- cada `path` debe resolver a un documento existente en `knowledge`;
- cada documento debe tener exactamente un `authority_thread`;
- cada `authority_thread` debe resolver a un MANIFEST existente;
- `authority_manifest` debe corresponder al THREAD indicado;
- ningún documento debe declarar autoridad simultánea de varios THREADs;
- si la autoridad real no puede determinarse, la incoherencia debe resolverse en la arquitectura/los MANIFEST antes de presentar el índice como válido.
