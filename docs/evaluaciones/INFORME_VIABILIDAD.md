# Informe de viabilidad — arquitectura Warp

**Propósito:** un barrido honesto de posibles problemas de diseño e ingeniería del modelo Warp, escrito en lenguaje llano (sin dar por supuesto conocimiento de ingeniería de IA).

**Marco de lectura:** casi todo en Warp es **sólido para lo que es hoy** —un vehículo de pensamiento, un solo mantenedor, un corpus pequeño—. Los riesgos serios aparecen **a escala** (muchos documentos/hilos) o **con varios agentes a la vez**. Y aviso clave: varias de tus dudas (coste, recuperación) son **empíricas** —se responden midiendo sobre tu repo real, no discutiendo—. Están marcadas como *[medir]*.

---

## Antes de nada: tres términos

- **Ventana de contexto.** Lo que el modelo puede "ver" de una vez. Hoy es grande (del orden de cientos de miles a millones de palabras según el modelo). Por eso "¿cabe?" casi nunca es el problema; el problema es el **coste** y que, cuanto más metes, **peor atiende** a lo relevante. *(confianza alta)*
- **Tokens y su coste.** Pagas por cada trozo de texto que entra y sale en cada llamada. En un agente que trabaja "a saltos" (lee un archivo, piensa, lee otro), el contexto **se reenvía en cada paso**, así que el coste se acumula más rápido de lo que parece. El motor del coste es **cuánto corpus carga** por sesión.
- **Recuperación (RAG).** La forma estándar de no cargarlo todo: traer solo los pocos documentos relevantes, buscándolos por palabra clave o por significado. Warp hoy hace una versión ligera: el agente lee los índices y decide qué documentos abrir.

---

## Tus tres dudas, respondidas

### 1. ¿Coste excesivo de tokens al acceder a un hilo?

Depende, y menos de lo que temes en el estado actual. Al conectar a un hilo, lo fijo que se carga es pequeño: el contexto mínimo del agente (que ya adelgazaste), el MANIFEST y el HANDOFF del hilo (cortos) y los índices. Eso son pocos tokens. **El coste de verdad lo mete el corpus**: cuántos documentos, y cómo de grandes, abre el agente. Si abre solo los 1–3 relevantes, el coste es razonable; si tiene que leerse medio corpus para encontrar lo que sirve, se dispara. Es decir: **la duda 1 es en realidad la duda 3** (saber recuperar solo lo justo). *[medir]* con tu repo: instrumenta cuántos tokens gasta una sesión típica.

### 2. ¿Es funcional que el corpus viva en documentos que el agente lee?

Sí, sin duda: es exactamente como funcionan las herramientas de agentes sobre repositorios (Claude Code, Cursor, etc.). "El agente lee archivos markdown de un repo" es un patrón probado y funcional. La pega no es la funcionalidad, es que la prosa markdown es **legible pero no consultable por máquina**: no puedes "preguntarle" al corpus como a una base de datos; las relaciones entre documentos viven en texto y en los índices, no en algo interrogable. Funcional hoy; el límite aparece cuando quieres *consultar* relaciones a escala (ver duda 3).

### 3. ¿Bastan los dos índices para orientarse y establecer relaciones?

Aquí está el punto realmente crítico, y tu instinto acierta. Los dos índices dan un buen **índice de contenidos**: qué hilos existen y quién responde (THREAD_INDEX), y qué documentos hay, para qué son y qué hilo los posee (DOCUMENT_INDEX). Con eso:

- **Sí basta** para un corpus pequeño: el agente lee el índice entero, ve la descripción de cada documento y decide cuál abrir cuando la conversación deriva a ese tema. Funciona porque cabe leerlo todo y las descripciones bastan para acertar.
- **Deja de bastar al crecer**, por dos motivos: (a) leer el índice entero cada vez vuelve a ser coste, y acertar "por descripción" es impreciso —no hay búsqueda por *significado*, solo por lo que diga la línea del índice—; y (b) los índices dan **propiedad** (quién posee qué), no el **grafo de relaciones** (que la conclusión de A depende del dato de B). Esa información de dependencia está en los MANIFEST, pero no en algo que se pueda *consultar* de golpe.

Traducido: los índices son un buen mapa de "qué hay y de quién es", no un buscador ni un grafo de relaciones. Y eso es **exactamente la capa de consulta/grafo que ya parcaste como fase 2**. Tu duda 3 apunta justo al techo real del diseño.

---

## Barrido de riesgos

| Riesgo | Hoy (solo, corpus pequeño) | A escala / varios agentes | Mitigación / camino |
|---|---|---|---|
| **Recuperación y orientación** | bajo | **alto** | capa de consulta (búsqueda por significado o grafo) = la fase 2 parcada; mientras, docs pequeños + buenas descripciones de índice |
| **Coste por sesión** *[medir]* | bajo | medio-alto | carga selectiva; medir tokens reales |
| **Fiabilidad del agente** (que siga el protocolo, respete autorías) | medio | medio-alto | el comprobador (estructura) + revisión humana; protocolo corto |
| **Concurrencia** (dos agentes a la vez) | bajo (trabajas en serie) | **alto** | bloqueo por hilo (tipo "claim") si algún día hay simultaneidad |
| **Cuello humano** (solo el dueño resuelve) | esperado / by design | alto | inherente; aceptable en un vehículo de pensamiento |
| **Verificación** (el comprobador valida estructura, no verdad) | medio | medio | revisión humana; asumir que Warp da trazabilidad, no corrección |
| **Crecimiento del HANDOFF** (backlog en hilos dormidos) | bajo | medio | higiene de cola; resolver o descartar, no aplazar indefinido |
| **Impactos no detectados** (nadie ve que A afecta a B) | bajo | medio | el "Caso 1" parcado (aviso de dependencias declaradas) cubre parte |
| **Sobrecarga conceptual** (curva de entrada) | bajo (lo hiciste tú) | medio | superficie mínima + buenos docs; importa si entra otra gente |
| **Prosa vs. consulta** (markdown no es interrogable) | bajo | medio | si algún día haces el grafo, habrá que extraerlo de la prosa (trabajo) |
| **Seguridad / secretos** | bajo | bajo | ya cubierto (.env fuera + escaneo del comprobador) |

**Los tres que más miraría, por orden:**

1. **Recuperación a escala (el techo real).** No es un fallo, es un límite de diseño: el modelo actual "lee el índice y elige" tiene un tope. Cuando notes que orientarse cuesta —el agente falla al encontrar el documento bueno, o cargarlo todo sale caro—, ese es el disparador para la fase 2. Ni antes ni después.
2. **Fiabilidad del agente.** Todo el modelo confía en que el agente siga el protocolo y respete las autorías. El comprobador atrapa los fallos *de estructura*; no atrapa los *de criterio* (que el agente resuelva algo plausible pero equivocado). Es el límite de fondo de cualquier "norma para un ejecutor estocástico"; se acota con el comprobador y tu revisión, no se elimina.
3. **Concurrencia.** Hoy no existe porque trabajas en serie. En el momento en que quieras dos agentes a la vez sobre hilos relacionados, necesitas un bloqueo o tendrás pisotones. Tenlo fichado como condición, no como tarea.

---

## Qué medir (lo empírico, barato)

Estas no las resuelvas discutiendo; instrumenta:

- **Coste por sesión:** en una sesión típica, cuántos tokens entran/salen. Así sabes si "acceder a un hilo" es caro *de verdad* o es un miedo teórico.
- **Calidad de recuperación:** haz 10 preguntas reales que deriven a áreas del corpus y mira si el agente, con solo los índices, abre el documento correcto. El % de acierto te dice cuánto te queda hasta necesitar la fase 2.
- **Tamaño de los índices:** vigila cuándo el índice deja de caber cómodo de leer entero.

---

## Conclusión

Para su propósito declarado —un vehículo para pensar la gestión de conocimiento con agentes, con un mantenedor— **el diseño es sólido**. Ninguno de los riesgos es fatal en ese contexto; casi todos son riesgos de *escala* o de *concurrencia* que no aplican todavía.

El **techo real** del modelo es lo que tú mismo intuiste: la **recuperación y la orientación en el corpus a medida que crece**, que es la capa de consulta/grafo de la fase 2. Buen instinto. La recomendación es **no construirla aún**: mantén los documentos pequeños y las descripciones de índice afiladas, mide la calidad de recuperación de vez en cuando, y deja que sea la propia dificultad de orientarse la que dispare la fase 2 cuando llegue.

Y una honesta de fondo: Warp da **trazabilidad y coordinación**, no **corrección**. Ninguna comprobación automática dirá si el conocimiento es *cierto*; eso lo sostiene tu criterio. Es una virtud si se tiene clara, y un espejismo si se olvida.

*(Confianza: alta en el análisis estructural; las cifras de coste y recuperación son empíricas y hay que medirlas en tu repo.)*
