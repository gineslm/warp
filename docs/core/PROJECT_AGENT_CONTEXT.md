# Warp — Contexto mínimo del proyecto para agentes

**Versión:** 2.1.0  
**Estado:** Activo  
**Idioma:** español (España)  
**Repositorio:** `tu-organización/tu-repositorio`  
**Rama raíz de conocimiento:** `knowledge`

## 1. Función

Este documento es la **superficie mínima que un agente debe leer siempre** para incorporarse a Warp. No reproduce la arquitectura ni las reglas completas: expone el contrato operativo imprescindible y dirige a las fuentes extensas sólo cuando la operación lo requiere.

La conversación/agente es temporal. El repositorio es la memoria duradera.

## 2. Reglas duras que aplican siempre

1. Un THREAD existe si y sólo si existe su MANIFEST en `knowledge`.
2. El agente se incorpora a un THREAD mediante su MANIFEST.
3. El corpus es global para lectura; un THREAD sólo modifica documentos bajo su autoridad.
4. Para cambiar conocimiento bajo autoridad ajena se registra un input en el HANDOFF del THREAD responsable.
5. El HANDOFF contiene exclusivamente inputs pendientes procedentes de **otros THREADs**; el trabajo propio no se encola.
6. Una entrada resuelta sale del HANDOFF en el mismo commit que aplica o registra la decisión; Git conserva el historial.
7. Un commit representa una decisión; antes de guardar cambios se aplica `docs/core/GIT_COMMIT_RULES.md`.
8. Ninguna llave, token, contraseña o secreto se guarda en archivos versionados.

## 3. Entrada por defecto

Toda sesión comienza conceptualmente en `knowledge`.

Secuencia ordinaria:

```text
knowledge
  ↓
PROJECT_AGENT_CONTEXT.md
  ↓
THREAD_INDEX.md / DOCUMENT_INDEX.md
  ↓
MANIFEST del THREAD
  ↓
HANDOFF del THREAD
  ↓
corpus relevante
  ↓
rama de trabajo, si procede
```

Para trabajo ordinario dentro de un THREAD ya existente, esta superficie es suficiente: no es necesario cargar por defecto `THREAD_ARCHITECTURE.md` ni `PROJECT_WORKING_RULES.md` completos.

## 4. Cuándo leer más

| Si vas a… | Lee antes |
|---|---|
| crear un THREAD o formalizar una responsabilidad nueva | `THREAD_ARCHITECTURE.md` §5–§6 y `THREAD_CONTEXT_BOOTSTRAP.md` §3 |
| proponer algo a otro THREAD o resolver una entrada HANDOFF | `THREAD_ARCHITECTURE.md` §7 y §9; `THREAD_CONTEXT_BOOTSTRAP.md` §7–§8 |
| cambiar autoridad documental o gobernar un documento transversal | `THREAD_ARCHITECTURE.md` §11 |
| cerrar, archivar o reabrir un THREAD | `THREAD_ARCHITECTURE.md` §15 y `THREAD_CONTEXT_BOOTSTRAP.md` §10 |
| cambiar arquitectura, reglas, bootstrap o convenciones del sistema | `THREAD_ARCHITECTURE.md` + `PROJECT_WORKING_RULES.md` completos |
| guardar cambios | `GIT_COMMIT_RULES.md` |
| modificar MANIFESTs, HANDOFFs, índices o autoridad documental | además ejecutar `python scripts/check_knowledge.py` antes de consolidar |
| trabajar dentro de tu THREAD en documentos bajo su autoridad | nada más: MANIFEST + HANDOFF + corpus relevante bastan |

La divulgación progresiva reduce contexto, pero no reduce autoridad ni obligaciones. Si existe duda sobre una operación, se consulta la fuente canónica extensa antes de actuar.

## 5. Fuentes canónicas bajo demanda

- Arquitectura: `docs/core/THREAD_ARCHITECTURE.md`.
- Reglas permanentes: `docs/core/PROJECT_WORKING_RULES.md`.
- Bootstrap detallado: `docs/core/THREAD_CONTEXT_BOOTSTRAP.md`.
- Estrategia Git: `docs/core/GIT_COMMIT_RULES.md`.
- Índice de THREADs: `docs/core/THREAD_INDEX.md`.
- Índice documental: `docs/core/DOCUMENT_INDEX.md`.
- Plantilla de índice de THREADs: `docs/core/THREAD_INDEX_TEMPLATE.md`.
- Plantilla de índice documental: `docs/core/DOCUMENT_INDEX_TEMPLATE.md`.
- Comprobador estructural: `scripts/check_knowledge.py`.

## 6. Comandos de entrada

### «Conecta con el hilo `<thread_id>`»

1. localizar el THREAD en `THREAD_INDEX.md`;
2. leer su MANIFEST;
3. comprobar responsabilidad, estado y autoridad documental;
4. leer su HANDOFF;
5. consultar el corpus relevante mediante `DOCUMENT_INDEX.md` y referencias del MANIFEST;
6. operar dentro de esa responsabilidad.

### «Parte del handoff `<id>`»

El HANDOFF es una referencia de descubrimiento. Se localiza el THREAD receptor y la incorporación se realiza mediante su MANIFEST. Si el HANDOFF es provisional y no existe MANIFEST, el THREAD todavía no existe: antes de crearlo se cargan las reglas indicadas en §4.

### «Declaro una responsabilidad nueva»

Comprobar primero `THREAD_INDEX.md`. Si no existe THREAD compatible, cargar la arquitectura/bootstrap indicados en §4 antes de crear MANIFEST + HANDOFF.

### «Reincorpórate al contexto del proyecto»

Reconstruir el estado desde `knowledge`, resolver el THREAD compatible y comparar el trabajo previo con el repositorio antes de modificar conocimiento autoritativo.

## 7. Validación estructural

`scripts/check_knowledge.py` es una red de seguridad determinista para invariantes estructurales. No sustituye criterio humano ni análisis semántico.

Ejecutar:

```text
python scripts/check_knowledge.py
```

antes de consolidar cambios que afecten a MANIFESTs, HANDOFFs, índices, rutas o autoridad documental.

## 8. Cierre de una sesión ordinaria

Finalizar una conversación no crea un nuevo HANDOFF.

Antes de terminar:

- consolidar el conocimiento vigente dentro de la autoridad del THREAD;
- registrar en HANDOFFs receptores sólo inputs inter-THREAD que sigan pendientes;
- no usar el HANDOFF propio como lista de trabajo interna;
- retirar entradas resueltas en el mismo commit que materializa la decisión;
- aplicar `GIT_COMMIT_RULES.md` al guardar.

## 9. Bloque compacto

> Repositorio: `tu-organización/tu-repositorio`. Fuente de verdad: `knowledge`. Lee primero `docs/core/PROJECT_AGENT_CONTEXT.md`; después usa `THREAD_INDEX.md` / `DOCUMENT_INDEX.md`, conéctate mediante el MANIFEST y consulta el HANDOFF sólo como cola de inputs pendientes procedentes de otros THREADs. Lee el corpus necesario; sólo modifica documentos bajo autoridad de tu THREAD. Para operaciones estructurales o excepcionales, carga las fuentes indicadas en la tabla «Cuándo leer más». Un commit = una decisión y los secretos nunca se versionan.

## 10. Historial

| Versión | Fecha | Cambio |
|---|---|---|
| 2.0.0 | 2026-09-08 | Consolidación del contexto de agente conforme al modelo de HANDOFF persistente, índices separados y autoridad documental única. |
| 2.1.0 | 2026-09-08 | Se adopta divulgación progresiva: el agente carga por defecto sólo el contexto mínimo y consulta arquitectura/reglas completas según la operación. |
