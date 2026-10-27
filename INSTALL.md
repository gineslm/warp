# Instalar Warp en un proyecto

Esta guía crea una **instancia** de Warp: un repositorio cuya rama `knowledge` contiene el método y el conocimiento de un proyecto. El repositorio `warp` es la distribución del método; no se trabaja en él para gestionar un proyecto.

> El instalador solo admite, por ahora, repositorios **solo de conocimiento** (`layout: knowledge-only`). La instalación en un repositorio que ya contiene código (`with-code`) llegará en una versión posterior.

## 1. Requisitos

- Git 2.20 o posterior, con identidad configurada (`git config user.name` y `user.email`).
- Python 3.8 o posterior. Solo usa la biblioteca estándar.
- Opcional, para crear el repositorio en GitHub: [GitHub CLI](https://cli.github.com/) con la sesión iniciada (`gh auth login`). El instalador nunca pide ni guarda credenciales: usa la sesión de `gh`.

## 2. Obtener una versión del método

Instala siempre desde una versión publicada, no desde `main`:

```bash
git clone --branch v3.1.0 https://github.com/gineslm/warp.git
```

Las versiones publicadas son las etiquetas `vX.Y.Z` del repositorio; sus notas explican qué cambia en cada una.

## 3. Preparar la instancia: `init`

```bash
python warp/warp/scripts/warp.py init ../mi-proyecto
```

El destino debe ser un directorio vacío o que no exista. El instalador pregunta:

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

Para un agente o una instalación automatizada, los mismos datos pueden darse en un archivo JSON:

```bash
python warp/warp/scripts/warp.py init ../mi-proyecto --config instalacion.json
```

```json
{
  "project": {"name": "Portal de autoservicio", "language": "es-ES"},
  "github": {"owner": "mi-org", "repo": "portal-conocimiento",
             "create_remote": true, "visibility": "private"},
  "layout": "knowledge-only",
  "enforcement": "advisory",
  "users": [
    {"github": "usuario-ux", "name": "Responsable de UX"},
    {"github": "usuario-ing", "name": "Responsable de ingeniería"}
  ],
  "governance_owner": "usuario-ux"
}
```

`init` crea la instancia en la rama `knowledge`, **sin hacer commit**, ejecuta el checker y muestra el mensaje propuesto para el commit inicial.

### Qué crea

| Archivo | Qué es |
|---|---|
| `warp/core/`, `warp/scripts/`, `warp/VERSION`, `warp/LICENSE-*` | el método, de solo lectura en la instancia |
| `warp.lock` | huellas de la capa de sistema; el checker comprueba que no se ha editado |
| `warp.yaml` | configuración del proyecto |
| `warp/USERS.md` | participantes |
| `warp/threads/governance/` | THREAD de gobierno, con su buzón vacío |
| `warp/index/` | índices de THREADs y del corpus |
| `warp/corpus/` | el corpus, vacío |
| `AGENTS.md` | entrada para agentes de programación |
| `.claude/settings.json` | memoria automática desactivada y reglas de permiso de Claude Code |

## 4. Confirmar y publicar: `publish`

Revisa el mensaje propuesto. Si es correcto:

```bash
cd ../mi-proyecto
python warp/scripts/warp.py publish
```

`publish`:

1. vuelve a ejecutar el checker y hace el commit inicial en `knowledge`;
2. si se pidió, crea el repositorio en GitHub (o enlaza uno existente y vacío) y sube `knowledge`;
3. aplica los ajustes de integración: `knowledge` como rama principal, solo merge commit, mensaje del merge igual al título y la descripción del PR, y borrado automático de las ramas fusionadas.

Si no se pidió repositorio remoto, el commit queda en local y puedes publicarlo más tarde.

### Recomendado, a mano

Proteger `knowledge` en GitHub (*Settings → Branches*): sin force-push y, cuando haya CI, con checks obligatorios. En repositorios privados, la protección de ramas requiere GitHub Pro o Team.

## 5. Después de instalar

- **Primer THREAD:** crea su MANIFEST y su buzón a partir de `warp/core/MANIFEST_TEMPLATE.md`, siguiendo `warp/core/THREAD_ARCHITECTURE.md` §5–§6.
- **Trabajar con agentes:** el agente lee `AGENTS.md`, que remite al contexto mínimo (`warp/core/PROJECT_AGENT_CONTEXT.md`).
- **Comprobar la estructura:** `python warp/scripts/check_knowledge.py` desde la raíz de la instancia.

## 6. Proponer mejoras al método

El método no se edita en la instancia: `warp.lock` lo detecta. Las mejoras se proponen al repositorio [`gineslm/warp`](https://github.com/gineslm/warp) mediante un issue o un PR.
