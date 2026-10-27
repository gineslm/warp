# Cómo guardamos las decisiones en git

**Versión:** 1.2.0  
**Estado:** Activo  
**Idioma:** español (España)  
**Rama raíz de conocimiento:** `knowledge`

Idea de fondo: **git ya guarda casi todo por su cuenta.** Nosotros solo añadimos lo único que git no puede saber: el *porqué* de cada decisión. Todo lo demás (fechas, quién, qué archivos cambiaron, el historial completo) lo lleva git solo, así que no lo copiamos a mano.

## 1. La llave de acceso nunca va dentro de un archivo

La llave que da acceso al repositorio (el "token") **no se escribe en ningún documento**, ni siquiera como ejemplo. Motivo: git conserva para siempre todo lo que pasa por él; si algún día se guarda la llave de verdad, queda en el historial y ya no se borra de forma fiable, a la vista de cualquiera con acceso.

La llave vive **fuera del repositorio** (en la configuración del ordenador o en un archivo que git tiene orden de ignorar). Aquí, como mucho, se dice que la llave se lee de fuera.

Lo mismo vale para cualquier información que no deba quedar para siempre: datos personales, información confidencial de clientes o contratos. Como `knowledge` conserva también los guardados de cada rama, no basta con borrarlo antes de integrar: **lo que no puede quedar para siempre no se escribe en el repositorio, ni siquiera en un borrador.**

## 2. Idea central: un guardado = una decisión

La unidad no es "un documento", sino **una decisión o revisión**.

- Un mismo guardado (commit) puede tocar varios documentos, siempre que todos los cambios respondan a **una sola causa**.
- Nunca se mezclan decisiones distintas en el mismo guardado.
- El mensaje del guardado describe la **decisión** (el resultado), no el proceso de edición.

**Bien:** una decisión sobre la forma de identificarse toca `requisitos.md`, `arquitectura.md` y `api.md` → un solo guardado.  
**Mal:** el mismo guardado mezcla eso + rediseñar la base de datos + corregir erratas sueltas → son decisiones distintas → varios guardados.

### Dos niveles: decisión y deliberación

Cada tarea se trabaja en su propia rama y entra en `knowledge` con un **guardado de unión** (merge commit). Así quedan dos niveles:

- **Decisión:** el guardado de unión en `knowledge`. Es *el* guardado de la decisión. Su mensaje es el título y la descripción del PR, y sigue el formato del §8.
- **Deliberación:** los guardados de la rama. Cuentan cómo se llegó a la decisión: qué alternativas se miraron, qué se descartó y qué se corrigió. No tienen que seguir el formato del §8, pero su mensaje dice qué se evaluó o descartó, no solo «wip».

Para integrar en `knowledge` no se usan ni *squash* ni *rebase*: el primero borraría la deliberación y el segundo la mezclaría con las decisiones.

Si la rama tiene un único guardado, la decisión y ese guardado dicen lo mismo. Es válido y no requiere nada especial.

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

El enlace entre los dos es automático y es la parte importante: **la misma decisión que cambia el estado de un pendiente es la que trae el cambio real en los documentos.** Por eso esa decisión es, a la vez, la prueba de "esto se dio por hecho" y de "esto es lo que se hizo y a qué afectó". No hay que apuntar en ningún sitio "resuelto en tal guardado": el historial de la lista ya te lleva al guardado correcto.

> **Regla de la que depende todo esto:** retirar el pendiente y hacer el cambio real van **juntos, en la misma decisión**, es decir, en el mismo guardado de unión. Dentro de la rama pueden ir en guardados distintos; lo que cuenta es que entren juntos en `knowledge`. Si se separan, se rompe el enlace.

Riesgo a evitar: que la lista de pendientes intente además guardar para siempre lo ya terminado. Si hace eso, tienes dos historiales que se contradicen. La lista solo guarda lo pendiente; lo terminado es del historial.

## 6. Cómo ver la evolución de un documento (sin llevar listas)

git lleva, por cada documento, el registro de todos sus cambios en orden. Es como el "historial de versiones" de un documento de Google. Y puede bajar al detalle de una línea concreta: para una frase, te dice qué guardado la puso o la tocó por última vez.

Con eso se responde solo, sin códigos:
- cómo ha evolucionado un documento → su historial;
- qué guardado introdujo un requisito → el historial de esa línea;
- qué se cambió en tal guardado y a qué archivos afectó → el propio guardado.

Como `knowledge` guarda los dos niveles (§2), git deja verlos por separado:

| Para ver… | Orden |
|---|---|
| solo las decisiones | `git log --first-parent knowledge` |
| las decisiones que tocaron un documento | `git log --first-parent -- <documento>` |
| qué decisión puso cada línea | `git blame --first-parent <documento>` |
| también la deliberación | las mismas órdenes sin `--first-parent` |

## 7. Excepción rara: cuando una decisión anula a otra sin que se note en el texto

A veces la idea vieja está en un documento y la nueva se escribe en otro, y en los cambios de texto no queda claro que la nueva **deja sin efecto** a la vieja. Solo en ese caso se añade **una frase** en el mensaje, con nombres reales ("esta decisión sustituye al modelo de acceso propio de `arquitectura.md`"). Una frase, no un código, y solo cuando esté claro. No es obligatorio en el resto de casos.

Además de la frase, se añade al final del mensaje una línea con el identificador de la decisión sustituida:

```text
Sustituye: <sha>
```

El `<sha>` es el del guardado de unión de esa decisión en `knowledge`, nunca el de una rama. No es un código de catalogación (§4): es una referencia de las del §3, que expresa una relación que git no puede deducir. La frase es para las personas; la línea es para las herramientas, que pueden comprobar que el identificador existe.

## 8. Formato del mensaje

```text
tipo(area): qué se decide, en una frase clara

Por qué:
Explicación breve de la decisión y su motivo.

(opcional, solo si aplica) Esta decisión deja sin efecto <algo concreto, con su nombre>.

(opcional, con la frase anterior) Sustituye: <sha de la decisión sustituida en knowledge>
```

- La primera línea expresa la **decisión**, no la edición. Nunca "editar documento" o "actualizar archivo".
- No se lista a mano qué archivos cambiaron (lo da git).
- No se pone el estado aquí (el estado vive en la lista de pendientes, que sí se puede editar; el mensaje no se puede cambiar después).
- GitHub añade el número del PR al final del título (`… (#12)`). Se acepta: no es un código de catalogación, sino un enlace a la deliberación.

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

Sustituye: 3f9c2a1
```

Fíjate en lo que **no** lleva: ni lista de archivos, ni estado, ni código de referencia. Solo la decisión, su porqué y, porque anula otra decisión, el identificador de la anulada.

## 10. Resumen de lo que NO se hace

- No escribir la llave de acceso en ningún archivo.
- No listar a mano los archivos afectados (lo da git).
- No poner el estado dentro del mensaje (va en la lista de pendientes).
- No usar códigos artificiales para catalogar decisiones.
- No mezclar decisiones distintas en un mismo guardado.
- No integrar en `knowledge` con *squash* ni *rebase*.
- No reescribir la historia de `knowledge` (*force-push*): los identificadores de las decisiones deben ser permanentes.
- No referenciar identificadores de ramas: solo de `knowledge`.

## 11. Historial

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-09-09 | Versión publicada con Warp: un guardado = una decisión, el porqué en el mensaje, sin duplicar lo que git ya conserva. |
| 1.0.1 | 2026-10-27 | Los datos del proyecto (repositorio) salen del documento y pasan a `warp.yaml`. |
| 1.1.0 | 2026-10-27 | Dos niveles, decisión (guardado de unión en `knowledge`) y deliberación (guardados de la rama); lectura con `--first-parent`; línea `Sustituye: <sha>`; sin *squash*, *rebase* ni reescritura de la historia de `knowledge`. |
| 1.2.0 | 2026-10-27 | §1 se extiende a toda información que no deba quedar para siempre, porque `knowledge` conserva también los guardados de la rama. |
