# Instalar Warp en un proyecto

Una **instancia** de Warp es la carpeta de un proyecto que gestiona su conocimiento con el método. Se crea en dos pasos: **descargar** el método en una carpeta vacía y **ejecutar el instalador** en esa misma carpeta. El método no se copia: el instalador crea a su lado lo propio del proyecto.

```text
mi-proyecto/
├── warp/        ← el método, tal como se descarga (no se edita)
├── warp.yaml    ← lo demás lo crea el instalador
├── USERS.md
├── threads/
├── corpus/
├── index/
└── AGENTS.md
```

> Por ahora el instalador solo admite repositorios **solo de conocimiento** (`layout: knowledge-only`). La instalación junto a código existente (`with-code`) llegará en una versión posterior.

## 1. Requisitos

- Git 2.20 o posterior, con identidad configurada (`git config user.name` y `user.email`).
- Python 3.8 o posterior. Solo usa la biblioteca estándar.
- Opcional, para crear el repositorio en GitHub: [GitHub CLI](https://cli.github.com/) con la sesión iniciada (`gh auth login`). El instalador nunca pide ni guarda credenciales.

## 2. Descargar el método

1. Crea una carpeta vacía para el proyecto, por ejemplo `mi-proyecto`.
2. Descarga el paquete de la última versión, `warp-<versión>.zip`, desde la página de [versiones de Warp](https://github.com/gineslm/warp/releases/latest).
3. Descomprímelo dentro de `mi-proyecto`. Debe quedar `mi-proyecto/warp/` y nada más.

Con GitHub CLI, desde la carpeta del proyecto:

```bash
gh release download --repo gineslm/warp --pattern "warp-*.zip"
```

y después descomprime el zip y bórralo.

No clones el repositorio `gineslm/warp`: trae la documentación y el historial de la distribución, que no pertenecen a tu proyecto.

## 3. Instalar con un agente (recomendado)

Abre un agente de programación (Claude Code, Codex…) **en la carpeta del proyecto** y pégale este prompt:

```text
Quiero instalar Warp en esta carpeta. Contiene solo la carpeta warp/, con el
método descargado. Hazlo así:

1. Ejecuta `python warp/scripts/warp.py init --help` para ver qué datos
   necesita el instalador y el formato del archivo de configuración.
2. Pregúntame esos datos uno a uno: nombre del proyecto; idioma (por defecto
   es-ES); propietario en GitHub (usuario u organización); nombre del
   repositorio; si quiero crear el repositorio en GitHub y, en ese caso, su
   visibilidad (por defecto privado); los participantes (usuario de GitHub y
   nombre visible de cada uno), y quién de ellos es el responsable del THREAD
   governance. Usa layout knowledge-only y enforcement advisory salvo que te
   diga otra cosa.
3. Con mis respuestas, escribe el archivo de configuración FUERA de esta
   carpeta (por ejemplo, en una carpeta temporal) y ejecuta
   `python warp/scripts/warp.py init --config <ese archivo>`.
4. Enséñame el resultado del checker y el mensaje propuesto para el commit
   inicial, y espera a que lo confirme. No ejecutes nada más hasta entonces.
5. Cuando lo confirme, ejecuta `python warp/scripts/warp.py publish`.
6. Al terminar, lee AGENTS.md y explícame en pocas líneas cómo empezar a
   trabajar: cómo crear el primer THREAD y su primer documento.
```

## 4. Instalar a mano

Desde la carpeta del proyecto:

```bash
python warp/scripts/warp.py init
```

El instalador pregunta:

| Dato | Ejemplo |
|---|---|
| nombre del proyecto | `Portal de autoservicio` |
| idioma | `es-ES` |
| propietario en GitHub (usuario u organización) | `mi-org` |
| nombre del repositorio | `portal-conocimiento` |
| ¿crear el repositorio en GitHub? | `s` / `n` |
| visibilidad, si se crea | `private` (por defecto) o `public` |
| layout | `knowledge-only` |
| enforcement | `advisory` (por defecto) o `strict` |
| participantes | usuario de GitHub y nombre visible de cada persona |
| responsable del THREAD `governance` | uno de los participantes |

Los mismos datos pueden darse en un archivo JSON, guardado fuera de la carpeta del proyecto. `python warp/scripts/warp.py init --help` muestra su formato:

```bash
python warp/scripts/warp.py init --config ../instalacion.json
```

`init` crea la instancia en la rama `knowledge`, **sin hacer commit**, ejecuta el checker y muestra el mensaje propuesto para el commit inicial.

### Qué crea

| Archivo | Qué es |
|---|---|
| `warp.yaml` | configuración del proyecto |
| `warp.lock` | huellas del método; el checker comprueba que `warp/` no se ha editado |
| `USERS.md` | participantes |
| `threads/governance/` | THREAD de gobierno, con su buzón vacío |
| `index/` | índices de THREADs y del corpus |
| `corpus/` | el corpus, vacío |
| `AGENTS.md` | entrada para agentes de programación |
| `.claude/settings.json` | memoria automática desactivada y reglas de permiso de Claude Code |

## 5. Confirmar y publicar

Revisa el mensaje propuesto. Si es correcto, desde la carpeta del proyecto:

```bash
python warp/scripts/warp.py publish
```

`publish`:

1. vuelve a ejecutar el checker y hace el commit inicial en `knowledge`;
2. si se pidió, crea el repositorio en GitHub (o enlaza uno existente y vacío) y sube `knowledge`;
3. aplica los ajustes de integración: `knowledge` como rama principal, solo merge commit, mensaje del merge igual al título y la descripción del PR, y borrado automático de las ramas fusionadas.

Si no se pidió repositorio remoto, el commit queda en local y puedes publicarlo más tarde.

**Recomendado, a mano:** proteger `knowledge` en GitHub (*Settings → Branches*): sin force-push y, cuando haya CI, con checks obligatorios. En repositorios privados, la protección de ramas requiere GitHub Pro o Team.

## 6. Después de instalar

- **Primer THREAD:** crea su MANIFEST y su buzón a partir de `warp/core/MANIFEST_TEMPLATE.md`, siguiendo `warp/core/THREAD_ARCHITECTURE.md` §5–§6.
- **Trabajar con agentes:** el agente lee `AGENTS.md`, que remite al contexto mínimo (`warp/core/PROJECT_AGENT_CONTEXT.md`).
- **Comprobar la estructura:** `python warp/scripts/check_knowledge.py` desde la carpeta del proyecto.
- **Actualizar el método:** descarga el paquete de la versión nueva y sustituye la carpeta `warp/`. Ajustar `warp_version` en `warp.yaml` y regenerar `warp.lock` será automático con `warp.py upgrade`, en una versión posterior.

## 7. Proponer mejoras al método

El método no se edita en la instancia: `warp.lock` lo detecta. Las mejoras se proponen al repositorio [`gineslm/warp`](https://github.com/gineslm/warp) mediante un issue o un PR.
