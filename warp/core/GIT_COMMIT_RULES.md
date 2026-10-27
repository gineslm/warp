# Cómo guardamos las decisiones en git

**Versión:** 1.0.0  
**Estado:** Activo  
**Idioma:** español (España)  
**Repositorio:** `tu-organización/tu-repositorio`  
**Rama raíz de conocimiento:** `knowledge`

Idea de fondo: **git ya guarda casi todo por su cuenta.** Nosotros solo añadimos lo único que git no puede saber: el *porqué* de cada decisión. Todo lo demás (fechas, quién, qué archivos cambiaron, el historial completo) lo lleva git solo, así que no lo copiamos a mano.

## 1. La llave de acceso nunca va dentro de un archivo

La llave que da acceso al repositorio (el "token") **no se escribe en ningún documento**, ni siquiera como ejemplo. Motivo: git conserva para siempre todo lo que pasa por él; si algún día se guarda la llave de verdad, queda en el historial y ya no se borra de forma fiable, a la vista de cualquiera con acceso.

La llave vive **fuera del repositorio** (en la configuración del ordenador o en un archivo que git tiene orden de ignorar). Aquí, como mucho, se dice que la llave se lee de fuera.

## 2. Idea central: un guardado = una decisión

La unidad no es "un documento", sino **una decisión o revisión**.

- Un mismo guardado (commit) puede tocar varios documentos, siempre que todos los cambios respondan a **una sola causa**.
- Nunca se mezclan decisiones distintas en el mismo guardado.
- El mensaje del guardado describe la **decisión** (el resultado), no el proceso de edición.

**Bien:** una decisión sobre la forma de identificarse toca `requisitos.md`, `arquitectura.md` y `api.md` → un solo guardado.  
**Mal:** el mismo guardado mezcla eso + rediseñar la base de datos + corregir erratas sueltas → son decisiones distintas → varios guardados.

## 3. Lo que git ya guarda solo (no lo repitas)

No hace falta anotar nada de esto en el mensaje, porque git lo registra sin fallo:

- fecha y hora;
- quién lo hizo;
- el identificador permanente del cambio;
- las diferencias exactas (qué se quitó y qué se puso);
- **qué archivos cambiaron**;
- el historial completo.

El mensaje aporta **solo lo que git no conoce**: por qué se tomó la decisión.

### Referencias Git con significado semántico

Esta regla evita duplicar metadatos de Git al **registrar una decisión**. No elimina referencias explícitas a commits cuando el SHA tiene significado semántico en el modelo, por ejemplo para fijar:

- una base histórica de conocimiento;
- una dependencia reproducible;
- una relación explícita entre estados del proyecto.

En esos casos la referencia no duplica el historial: expresa una relación que Git no puede inferir por sí solo.

## 4. No usamos códigos de referencia para catalogar decisiones

Para referirse a una decisión, se la nombra **por lo que es** o por el documento donde vive ("la decisión de usar OAuth2", "el modelo de acceso de `arquitectura.md`"), no por un código tipo R-012. Los códigos obligan a llevar una lista aparte que acaba desincronizándose, y aportan menos que una frase con sentido.

Esta regla se refiere a **códigos artificiales usados únicamente para catalogar decisiones**. No afecta a identificadores que formen parte del modelo de entidades o de la trazabilidad del sistema (`thread_id`, identificadores de estaciones u otros identificadores con función propia).

## 5. Dos sitios separados que no se pisan

**Lista de pendientes** → solo lo que *falta por hacer*, más su estado (por ejemplo: por decidir / en estudio / listo para aplicar). Nada más. Cuando algo se hace, **sale de la lista**.

**Historial de git** → lo que *ya está hecho*.

El enlace entre los dos es automático y es la parte importante: **el mismo guardado que cambia el estado de un pendiente es el que trae el cambio real en los documentos.** Por eso ese guardado es, a la vez, la prueba de "esto se dio por hecho" y de "esto es lo que se hizo y a qué afectó". No hay que apuntar en ningún sitio "resuelto en tal guardado": el historial de la lista ya te lleva al guardado correcto.

> **Regla de la que depende todo esto:** cambiar el estado en la lista y hacer el cambio real van **juntos, en el mismo guardado**. Si se separan, se rompe el enlace.

Riesgo a evitar: que la lista de pendientes intente además guardar para siempre lo ya terminado. Si hace eso, tienes dos historiales que se contradicen. La lista solo guarda lo pendiente; lo terminado es del historial.

## 6. Cómo ver la evolución de un documento (sin llevar listas)

git lleva, por cada documento, el registro de todos sus cambios en orden. Es como el "historial de versiones" de un documento de Google. Y puede bajar al detalle de una línea concreta: para una frase, te dice qué guardado la puso o la tocó por última vez.

Con eso se responde solo, sin códigos:
- cómo ha evolucionado un documento → su historial;
- qué guardado introdujo un requisito → el historial de esa línea;
- qué se cambió en tal guardado y a qué archivos afectó → el propio guardado.

## 7. Excepción rara: cuando una decisión anula a otra sin que se note en el texto

A veces la idea vieja está en un documento y la nueva se escribe en otro, y en los cambios de texto no queda claro que la nueva **deja sin efecto** a la vieja. Solo en ese caso se añade **una frase** en el mensaje, con nombres reales ("esta decisión sustituye al modelo de acceso propio de `arquitectura.md`"). Una frase, no un código, y solo cuando esté claro. No es obligatorio en el resto de casos.

## 8. Formato del mensaje

```text
tipo(area): qué se decide, en una frase clara

Por qué:
Explicación breve de la decisión y su motivo.

(opcional, solo si aplica) Esta decisión deja sin efecto <algo concreto, con su nombre>.
```

- La primera línea expresa la **decisión**, no la edición. Nunca "editar documento" o "actualizar archivo".
- No se lista a mano qué archivos cambiaron (lo da git).
- No se pone el estado aquí (el estado vive en la lista de pendientes, que sí se puede editar; el mensaje no se puede cambiar después).

### Tipos

| Tipo | Uso |
|------|-----|
| docs | cambios en la documentación |
| feat | documento o funcionalidad nueva importante |
| refactor | reorganizar sin cambiar el significado |
| fix | corregir errores o incoherencias |
| chore | organización, índices, metadatos |

Nota: `feat` y `fix` tienen un significado especial en el lado del *software* (afectan a la numeración de versiones). En el lado del conocimiento son solo descriptivos.

## 9. Ejemplo

```text
docs(acceso): unificar la forma de identificarse en todas las apps

Por qué:
Se adopta OAuth2 como único sistema de acceso en todo el proyecto.
Se retira el sistema propio anterior porque duplicaba trabajo y era
más difícil de mantener.

Esta decisión deja sin efecto el modelo de acceso propio descrito
en docs/arquitectura.md.
```

Fíjate en lo que **no** lleva: ni lista de archivos, ni estado, ni código de referencia. Solo la decisión y su porqué.

## 10. Resumen de lo que NO se hace

- No escribir la llave de acceso en ningún archivo.
- No listar a mano los archivos afectados (lo da git).
- No poner el estado dentro del mensaje (va en la lista de pendientes).
- No usar códigos artificiales para catalogar decisiones.
- No mezclar decisiones distintas en un mismo guardado.
