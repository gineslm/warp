# Warp — Plantilla de participantes

**Versión:** 1.0.0  
**Estado:** Plantilla  
**Idioma:** español (España)  
**Rama raíz de conocimiento:** `knowledge`

## 1. Propósito

Esta plantilla define la forma canónica de `warp/USERS.md`: la lista de participantes del proyecto.

`warp/USERS.md` pertenece a la configuración del proyecto y está bajo autoridad del THREAD `governance` (`warp/core/THREAD_ARCHITECTURE.md` §4.4 y §16.1). Dar de alta, dar de baja o cambiar a un participante es una decisión de ese THREAD; otros THREADs lo proponen en su HANDOFF.

## 2. Principios

1. Cada fila representa a una persona. Un agente nunca figura como participante.
2. `github` identifica a la persona y no se repite.
3. `status` vale `active` o `inactive`.
4. Quien deja el proyecto se marca `inactive` y no se borra: las referencias históricas a esa persona siguen siendo válidas.
5. No se registran emails ni otros datos personales. Git conserva para siempre lo que pasa por él.
6. Los campos de roles no se incorporan hasta que la arquitectura los defina.

## 3. Plantilla

```markdown
# <Proyecto> — Participantes

## Participantes

| github | name | status |
|---|---|---|
| `<usuario>` | `<nombre visible>` | `active` |

## Notas

<prosa libre: criterios de alta, equipos, aclaraciones>
```

## 4. Definición de campos

| Campo | Función |
|---|---|
| `github` | Usuario de GitHub de la persona; identificador estable. |
| `name` | Nombre visible, solo para lectura humana. |
| `status` | `active` mientras participa; `inactive` cuando deja el proyecto. |

## 5. Validación mínima

`warp/scripts/check_knowledge.py` comprueba que:

- existe `warp/USERS.md` con la tabla canónica;
- cada `status` es `active` o `inactive`;
- ningún `github` se repite;
- hay al menos un participante `active`.
