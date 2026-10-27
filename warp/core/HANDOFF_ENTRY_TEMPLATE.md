# Warp — Plantilla de entrada de HANDOFF

**Versión:** 1.0.0  
**Estado:** Plantilla  
**Idioma:** español (España)  
**Rama raíz de conocimiento:** `knowledge`

## 1. Propósito

Esta plantilla define la forma canónica de una entrada del buzón de un THREAD: un archivo `warp/threads/<thread_id receptor>/handoff/<nombre>.md` (`warp/core/THREAD_ARCHITECTURE.md` §7).

## 2. Principios

1. Una entrada es un input de **otro** THREAD. El trabajo propio no se encola.
2. `<nombre>` es descriptivo, en minúsculas con guiones, y único en el buzón. No es un código de catalogación.
3. El archivo contiene **un único** bloque `yaml` de identidad.
4. El emisor escribe la identidad (salvo `status`), `## Contexto` y `## Evidencia`, mientras la entrada esté en `proposed`.
5. El receptor escribe `status` y `## Notas del receptor`, y es el único que resuelve la entrada.
6. Al resolverse, el archivo se borra en la misma decisión que aplica el cambio o registra el rechazo.

## 3. Plantilla

````markdown
# <resumen corto de la entrada>

```yaml
origin_thread: <thread_id emisor>
type: proposal
summary: <una frase>
target_scope: <documentos o ámbito afectados>
status: proposed
```

## Contexto

<qué se ha observado y por qué afecta a la responsabilidad del receptor; si bloquea el trabajo del emisor>

## Evidencia

<datos, documentos o razonamiento que lo sostienen>

## Notas del receptor

<reservado al THREAD receptor>
````

## 4. Definición de campos

| Campo | Valores | Zona |
|---|---|---|
| `origin_thread` | `thread_id` existente y distinto del receptor | emisor |
| `type` | `proposal` (cambio propuesto), `review` (revisión), `need` (necesidad), `request` (petición de trabajo) | emisor |
| `summary` | una frase | emisor |
| `target_scope` | documentos o ámbito del receptor afectados | emisor |
| `status` | `proposed`, `in_review`, `deferred`, `ready_to_apply` | receptor |

## 5. Validación mínima

`warp/scripts/check_knowledge.py` comprueba que:

- el archivo tiene exactamente un bloque `yaml` con los cinco campos;
- `type` y `status` tienen valores válidos;
- `origin_thread` existe y no es el propio receptor;
- `## Contexto` y `## Evidencia` existen y no están vacías.

El checker comprueba que el contenido está, no que sea suficiente: eso sigue siendo criterio del receptor.
