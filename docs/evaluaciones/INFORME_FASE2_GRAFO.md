# Informe — Fase 2: un grafo para indexar el conocimiento

**Contexto:** es la capa que en el informe de viabilidad quedó como el **techo real** de Warp: a medida que el corpus crece, los dos índices dejan de bastar para orientarse y para consultar relaciones. Este documento aterriza qué construir, con qué opciones y cuándo. En lenguaje llano.

**Aviso de fondo (el mismo de siempre):** no construir esto todavía. El disparador es empírico —cuando midas que orientarse falla—, no una fecha. El informe termina con esos disparadores.

---

## 1. Primero, separar dos necesidades que se confunden

Bajo "grafo de conocimiento" se mezclan dos problemas distintos que se resuelven de forma distinta:

- **Recuperar contenido:** encontrar *el documento relevante* aunque la conversación use otras palabras. ("Se habla de sequías" → traer el doc de precipitaciones, aunque no diga "sequía".) Esto se resuelve con **búsqueda**, no necesariamente con un grafo.
- **Consultar relaciones:** responder *qué se conecta con qué* ("¿qué depende de este dato?", "¿qué decisiones afecta este cambio?", "¿de qué hilo nació este otro?"). Esto sí es un **grafo**.

Un grafo resuelve sobre todo la **segunda**. La primera se puede resolver más barato sin grafo. La pregunta que decide el diseño: **¿cuál te duele más?** Probablemente las dos, pero en distinto grado, y el orden en que las ataques cambia según eso.

---

## 2. Las opciones, de la más ligera a la más pesada

| Opción | Qué resuelve | Coste y mantenimiento | Cuándo |
|---|---|---|---|
| **0. Búsqueda del agente** (grep / herramientas) | recuperar contenido, básico | nulo (lee los archivos vivos) | ya; es "el grafo que no construyes" |
| **1. Grafo de relaciones derivado** de los metadatos de Warp | consultar relaciones | bajo, determinista, sin IA | cuando duelan las preguntas de relación |
| **2. Búsqueda por significado** (embeddings) | recuperar contenido, fino | medio (hay que mantener) | cuando falle *encontrar* contenido |
| **3. GraphRAG** (grafo extraído por IA + recuperación) | preguntas complejas multi-salto | alto, no determinista | casi seguro, nunca (para tu caso) |

**Opción 0 — la que ya tienes casi gratis.** El agente, cuando necesita algo, busca en el repo (como hace Claude Code). Sin construir nada, siempre actualizado. Límite: es por palabra clave (se pierde sinónimos) y no traversa relaciones. Empieza por explotar esto bien.

**Opción 3 — el extremo de moda.** Construir un grafo donde una IA extrae entidades y relaciones del texto, y se usa para responder preguntas complejas. Potente en corpus enormes, pero es una tubería pesada, cara, no determinista y con errores de extracción. **Para Warp es sobredimensionado.** Lo nombro para descartarlo con conocimiento.

Las dos del medio son las que importan. Y la que de verdad pides —"un grafo para indexar"— es la **Opción 1**.

---

## 3. Cómo sería la Opción 1 en concreto (la recomendada como núcleo)

La idea encaja con la filosofía de Warp como un guante: **el grafo es derivado**, se reconstruye desde los documentos fuente, igual que los índices. No es una fuente de verdad nueva; es una *vista consultable* de las relaciones que ya declaras.

**Nodos:** los THREAD, los documentos y (opcional) las decisiones (commits).

**Aristas** (las relaciones que Warp ya tiene, casi todas):
- `posee` — de un THREAD a los documentos bajo su autoría (del DOCUMENT_INDEX).
- `depende_de` — de un documento/hilo a otro (de las dependencias del MANIFEST).
- `nace_de` — de un THREAD a otro (del `origin.source_id`).
- `aporta_a` — de un THREAD a otro (de las entradas del HANDOFF).
- `sustituye` — de una decisión a otra (del historial de git).

**De dónde se sacan:** parseando los MANIFEST, el DOCUMENT_INDEX, los HANDOFF y el log de git. **Es el mismo parseo que ya hace el comprobador** (`check_knowledge.py`); el constructor del grafo es un script hermano que reutiliza ese código.

**Qué produce:**
- Una forma **consultable**: una pequeña base de datos SQLite reconstruida desde las fuentes (puedes preguntarle "¿qué depende de este documento?" con una consulta). Es exactamente el patrón que ya vimos en Fossil/Forgejo: reconstruir un índice de consulta desde el almacén canónico. **Precedente sólido, bajo riesgo.**
- Una forma **visual/legible**: un diagrama (Mermaid o Graphviz) generado, para ti y para el agente.

**Cómo se mantiene:** un script (`build_graph.py`) que se ejecuta en local o al consolidar, como la regeneración de índices. Determinista, sin IA, **derivado y regenerable** (nunca se edita a mano; si se edita a mano, deriva, y volvemos al problema de siempre).

---

## 4. El trabajo de verdad no es el script, es la disciplina previa

Aquí está la parte incómoda y honesta: **el grafo solo es tan bueno como las relaciones que declares en campos legibles por máquina.** Si las dependencias o las sustituciones viven en prosa ("esto reemplaza al modelo anterior"), el extractor no las verá. Así que la precondición real de la Opción 1 no es programar el grafo —eso es un rato—, sino **declarar las relaciones en campos estructurados** (por ejemplo, `depende_de: [rutas]` en el MANIFEST, `sustituye:` como campo, no como frase).

Es el mismo principio que ya aplicaste con las reglas de commit: lo que quieres consultar, decláralo estructurado; lo que dejas en prosa, no se puede consultar. Sin esa disciplina, el grafo saldrá lleno de huecos.

---

## 5. Camino por fases y disparadores

No lo hagas de golpe. Orden y señal que lo dispara:

1. **Ahora — Opción 0.** Explota la búsqueda del agente + los dos índices. Mide (la prueba barata del informe de viabilidad: 10 preguntas reales).
2. **Cuando duelan las preguntas de relación** ("no sé qué afecta a qué sin leerme medio repo") → **Opción 1** (grafo derivado). Precondición: empezar a declarar relaciones en campos.
3. **Cuando falle encontrar contenido** (el agente no da con el doc bueno aunque exista) → **Opción 2** (búsqueda por significado / embeddings), como capa aparte de recuperación.
4. **Opción 3:** archivada salvo que Warp cambie de propósito por completo.

Nota sobre la Opción 2: cuando llegue, elige la herramienta concreta (modelo de embeddings, almacén de vectores) *en ese momento*, según lo que exista entonces; el patrón no cambia, las herramientas sí. No te cases hoy con una.

---

## 6. Riesgos y límites (honestos)

- **Derivado = tan bueno como lo declarado.** Sin relaciones estructuradas, el grafo tiene agujeros. La disciplina es el 80% del trabajo.
- **Nunca a mano.** El grafo y la base de consulta son artefactos regenerables; editarlos a mano reintroduce la deriva que Warp evita.
- **No confundir con el "grafo de conocimiento" de la publicidad.** Lo que necesitas es un grafo *estructural* de tus propios hilos/documentos/decisiones (barato y fiable), no una extracción de entidades por IA (cara y con errores).
- **Relaciones, no verdad.** El grafo dice *cómo se conecta* el conocimiento, no si es *correcto*. Eso sigue siendo tu criterio.
- **Recuperar ≠ relacionar.** La Opción 1 no encuentra contenido por significado; para eso es la 2. No esperes que el grafo resuelva el problema de "encontrar el doc".

---

## 7. Conclusión

Lo que pides —un grafo para indexar el conocimiento— es, bien entendido, la **Opción 1: un grafo de relaciones derivado de los metadatos que Warp ya produce**, reconstruible como los índices, consultable vía SQLite y visualizable. Es barato, determinista, encaja con la filosofía del proyecto y tiene precedente probado (Fossil/Forgejo). Su coste real no está en el código, sino en la **disciplina de declarar las relaciones en campos**, no en prosa.

Recomendación: **no construirlo aún**; primero exprimir la búsqueda del agente y medir. Cuando lo construyas, la Opción 1 primero; la búsqueda por significado (Opción 2) solo si el dolor es *encontrar contenido*, no *relacionarlo*; y la Opción 3, fuera.

*(Confianza: alta en el diseño y en el encaje con Warp. Las herramientas concretas de la Opción 2 son cambiantes y se eligen al construir, no ahora.)*
