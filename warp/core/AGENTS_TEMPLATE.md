# Warp — Plantilla de AGENTS.md

**Versión:** 1.0.0  
**Estado:** Plantilla  
**Idioma:** español (España)  
**Rama raíz de conocimiento:** `knowledge`

## 1. Propósito

Esta plantilla define la forma canónica de `AGENTS.md` en la raíz de la rama `knowledge` de una instancia: el archivo que los agentes de programación leen al empezar a trabajar en el repositorio.

`AGENTS.md` pertenece a la configuración del proyecto y está bajo autoridad del THREAD `governance` (`warp/core/THREAD_ARCHITECTURE.md` §4.4 y §16.1).

## 2. Principios

1. **Remite, no duplica.** Las reglas viven en el core. `AGENTS.md` dirige al contexto mínimo (`warp/core/PROJECT_AGENT_CONTEXT.md`), que es la superficie que todo agente lee siempre.
2. **Una sola excepción operativa:** el destino de las ramas y los PRs. En `layout: with-code` la rama principal del repositorio es la del código, y un PR abierto sin indicar destino iría contra ella. Es el único error que no se ve hasta que ya está hecho, por eso se explicita.
3. **La línea `@`** hace que Claude Code cargue el contexto mínimo completo al empezar. Otros agentes no la expanden: para ellos es texto inocuo, y les basta la frase que la precede.
4. **En `layout: with-code`**, este archivo vive en la rama `knowledge`. El `AGENTS.md` de las ramas del código es del equipo de software; como mucho, se le añade una línea que apunte a `knowledge` y diga que consultarla es libre.

## 3. Plantilla

```markdown
# Instrucciones para agentes

Este repositorio gestiona su conocimiento con Warp. Antes de trabajar,
lee `warp/core/PROJECT_AGENT_CONTEXT.md` y sigue su secuencia de entrada:
contiene las reglas que aplican siempre y cuándo leer más.

Las ramas de trabajo nacen de `knowledge` y sus PRs se dirigen a
`knowledge` (`gh pr create --base knowledge`), aunque la rama principal
del repositorio sea otra.

@warp/core/PROJECT_AGENT_CONTEXT.md
```

## 4. Qué no debe contener

- reglas del método, que se desactualizarían respecto al core;
- información del proyecto, que vive en `warp.yaml` y en el corpus;
- estado de trabajo o notas de sesión (`PROJECT_AGENT_CONTEXT.md`, regla dura 9).
