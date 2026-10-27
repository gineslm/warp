#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Warp: instalador de instancias.

  init <destino> [--config archivo.json]
      Prepara una instancia en local, en la rama `knowledge`, sin hacer commit,
      y muestra el mensaje del commit inicial para que la persona lo confirme.
  publish [<destino>]
      Tras la confirmación: hace el commit inicial y, si se pidió, crea el
      repositorio en GitHub, sube `knowledge` y aplica los ajustes de merge.

Solo biblioteca estándar. Para el repositorio remoto usa la sesión de `gh`:
el script nunca maneja credenciales.
"""

import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys

# Sin __pycache__: no debe aparecer en la capa de sistema ni colarse en el commit.
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_knowledge import digest, system_files  # noqa: E402

SOURCE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATE = "warp-init.json"  # vive en .git/: nunca se versiona
GITHUB_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]{0,38}$")
REPO_NAME = re.compile(r"^[A-Za-z0-9._-]{1,100}$")
UNSAFE = re.compile(r"[|`]|\s#")
LAYOUTS = ("knowledge-only", "with-code")
ENFORCEMENT = ("advisory", "strict")
VISIBILITY = ("private", "public")

SETTINGS = {
    "autoMemoryEnabled": False,
    "permissions": {
        "ask": ["Bash(gh pr merge *)"],
        "deny": [
            "Bash(gh pr merge *--squash*)", "Bash(gh pr merge * -s*)",
            "Bash(gh pr merge *--rebase*)", "Bash(gh pr merge * -r*)",
            "Bash(git branch -D *)", "Bash(git branch --delete --force*)",
            "Bash(git push *--force*)", "Bash(git push -f*)", "Bash(git push * -f*)",
            "Bash(git reset --hard*)", "Bash(git reset * --hard*)",
        ],
        "allow": ["Bash(git branch -d *)", "Bash(git fetch --prune*)"],
    },
}

MERGE_SETTINGS = [
    "-f", "default_branch=knowledge",
    "-F", "allow_merge_commit=true",
    "-F", "allow_squash_merge=false",
    "-F", "allow_rebase_merge=false",
    "-f", "merge_commit_title=PR_TITLE",
    "-f", "merge_commit_message=PR_BODY",
    "-F", "delete_branch_on_merge=true",
]


def fail(msg):
    print("ERROR: " + msg)
    sys.exit(1)


def run(cmd, cwd=None, check=True):
    p = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = p.stdout.decode("utf-8", "replace").strip()
    if check and p.returncode != 0:
        fail("%s\n%s" % (" ".join(cmd), p.stderr.decode("utf-8", "replace").strip()))
    return p.returncode, out


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


# --- Datos de la instalación -------------------------------------------------

def ask(question, default=None):
    suffix = " [%s]" % default if default else ""
    answer = input("%s%s: " % (question, suffix)).strip()
    return answer or default or ""


def gh_login():
    if not shutil.which("gh"): return None
    code, out = run(["gh", "api", "user", "--jq", ".login"], check=False)
    return out if code == 0 and out else None


def interactive():
    print("Instalación de Warp. Deja vacío para aceptar el valor entre corchetes.\n")
    cfg = {"project": {}, "github": {}, "users": []}
    cfg["project"]["name"] = ask("Nombre del proyecto")
    cfg["project"]["language"] = ask("Idioma", "es-ES")
    cfg["github"]["owner"] = ask("Propietario en GitHub (usuario u organización)", gh_login())
    cfg["github"]["repo"] = ask("Nombre del repositorio")
    cfg["github"]["create_remote"] = ask("¿Crear el repositorio en GitHub? (s/n)", "n").lower() in ("s", "si", "sí", "y", "yes")
    if cfg["github"]["create_remote"]:
        cfg["github"]["visibility"] = ask("Visibilidad (private/public)", "private")
    cfg["layout"] = ask("Layout (knowledge-only/with-code)", "knowledge-only")
    cfg["enforcement"] = ask("Enforcement (advisory/strict)", "advisory")
    print("\nParticipantes (usuario de GitHub y nombre visible). Deja el usuario vacío para terminar.")
    while True:
        gh = ask("  Usuario de GitHub")
        if not gh: break
        cfg["users"].append({"github": gh, "name": ask("  Nombre visible", gh)})
    first = cfg["users"][0]["github"] if cfg["users"] else None
    cfg["governance_owner"] = ask("Responsable del THREAD governance", first)
    return cfg


def validate(cfg):
    project, github = cfg.get("project") or {}, cfg.get("github") or {}
    name, language = (project.get("name") or "").strip(), (project.get("language") or "").strip()
    if not name: fail("falta el nombre del proyecto.")
    if UNSAFE.search(name): fail("el nombre del proyecto no puede contener '|', '`' ni ' #'.")
    if not language: fail("falta el idioma.")
    owner, repo = (github.get("owner") or "").strip(), (github.get("repo") or "").strip()
    if not GITHUB_NAME.fullmatch(owner): fail("propietario de GitHub no válido: '%s'." % owner)
    if not REPO_NAME.fullmatch(repo): fail("nombre de repositorio no válido: '%s'." % repo)
    visibility = github.get("visibility") or "private"
    if visibility not in VISIBILITY: fail("visibilidad no válida: '%s'." % visibility)
    layout = cfg.get("layout") or "knowledge-only"
    if layout not in LAYOUTS: fail("layout no válido: '%s'." % layout)
    if layout == "with-code":
        fail("layout 'with-code' todavía no está soportado por el instalador.")
    enforcement = cfg.get("enforcement") or "advisory"
    if enforcement not in ENFORCEMENT: fail("enforcement no válido: '%s'." % enforcement)
    users, seen = [], set()
    for u in cfg.get("users") or []:
        gh, label = (u.get("github") or "").strip(), (u.get("name") or "").strip() or None
        if not GITHUB_NAME.fullmatch(gh): fail("usuario de GitHub no válido: '%s'." % gh)
        if gh in seen: fail("usuario repetido: '%s'." % gh)
        if UNSAFE.search(label or ""): fail("el nombre de '%s' no puede contener '|', '`' ni ' #'." % gh)
        seen.add(gh); users.append({"github": gh, "name": label or gh})
    if not users: fail("hace falta al menos un participante.")
    gov = (cfg.get("governance_owner") or users[0]["github"]).strip()
    if gov not in seen: fail("el responsable de governance '%s' no está entre los participantes." % gov)
    return {"name": name, "language": language, "owner": owner, "repo": repo,
            "create_remote": bool(github.get("create_remote")), "visibility": visibility,
            "layout": layout, "enforcement": enforcement, "users": users,
            "governance_owner": gov}


# --- Archivos de la instancia ------------------------------------------------

def warp_yaml(c, version):
    return ("warp_version: %s          # versión del método\n"
            "project:\n  name: %s\n  repository: %s/%s\n  language: %s\n"
            "layout: %s       # knowledge-only | with-code\n"
            "enforcement: %s        # advisory | strict\n"
            % (version, c["name"], c["owner"], c["repo"], c["language"],
               c["layout"], c["enforcement"]))


def users_md(c):
    rows = "".join("| `%s` | `%s` | `active` |\n" % (u["github"], u["name"]) for u in c["users"])
    return ("# %s — Participantes\n\n## Participantes\n\n| github | name | status |\n"
            "|---|---|---|\n%s\n## Notas\n\nForma canónica: `warp/core/USERS_TEMPLATE.md`. "
            "Dar de alta o de baja a una persona es una decisión del THREAD `governance`.\n"
            % (c["name"], rows))


def governance_manifest(c, today):
    return """# governance — MANIFEST

**Versión:** 1.0.0
**Idioma:** {lang}

## Identidad

```yaml
thread_id: governance
domain: gobierno del proyecto
status: ACTIVE
owner: {owner}
current_cycle: 1
origin:
  type: USER_DECLARED
  source_id: instalación
repository:
  knowledge_branch: knowledge
handoff:
  path: warp/threads/governance/handoff/
```

## Responsabilidad

Gobernar la configuración del sistema Warp en este proyecto y sus participantes (`warp/core/THREAD_ARCHITECTURE.md` §4.4). No gobierna el contenido del corpus.

## Dentro de alcance

- mantener la configuración del proyecto en `warp.yaml`;
- mantener la lista de participantes en `warp/USERS.md`;
- mantener la configuración de agentes (`AGENTS.md`, `.claude/settings.json`) y de CI.

## Fuera de alcance

- el contenido de `warp/corpus/`, que gobiernan los THREADs que declaran su autoridad;
- el método (`warp/core/`, `warp/scripts/`), que se cambia actualizando de versión.

## Autoridad documental vigente

- `warp.yaml`
- `warp/USERS.md`
- `AGENTS.md`
- `.claude/settings.json`

## Historial

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | {today} | Alta del THREAD de gobierno al instalar Warp. |
""".format(lang=c["language"], owner=c["governance_owner"], today=today)


INDEX_HEAD = """# {name} — {title}

**Versión:** 1.0.0
**Estado:** Activo
**Rama raíz de conocimiento:** `knowledge`

## Naturaleza

{nature}

"""


def thread_index(c):
    return INDEX_HEAD.format(
        name=c["name"], title="Índice de THREADs",
        nature="Artefacto derivado y no autoritativo de descubrimiento. Se reconstruye desde los MANIFEST. Si existe discrepancia, prevalece el MANIFEST.") + \
        """## THREADs

| thread_id | status | domain | responsibility | MANIFEST | HANDOFF |
|---|---|---|---|---|---|
| `governance` | `ACTIVE` | `gobierno del proyecto` | `Configuración del sistema Warp en el proyecto y sus participantes.` | `warp/threads/governance/MANIFEST.md` | `warp/threads/governance/handoff/` |

## Mantenimiento

Regenerar cuando se cree, archive/cierre, reactive o cambie de responsabilidad un THREAD, o cuando cambie la ruta de su MANIFEST/HANDOFF.
"""


def document_index(c):
    return INDEX_HEAD.format(
        name=c["name"], title="Índice documental",
        nature="Artefacto derivado y no autoritativo de descubrimiento del corpus (`warp/corpus/`). Todos los THREADs pueden leer el corpus; la columna `authority_thread` indica exclusivamente quién puede evolucionar directamente cada documento.") + \
        """## Documentos

| path | purpose / scope | authority_thread | authority_manifest |
|---|---|---|---|

## Mantenimiento

Regenerar cuando se cree, elimine o mueva un documento del corpus, cuando cambie sustancialmente su ámbito, o cuando se transfiera su autoridad de evolución a otro THREAD.
"""


def agents_md(dest):
    template = read(os.path.join(dest, "warp", "core", "AGENTS_TEMPLATE.md"))
    m = re.search(r"```markdown\n(.*?)\n```", template, re.S)
    if not m: fail("warp/core/AGENTS_TEMPLATE.md no contiene la plantilla.")
    return m.group(1) + "\n"


def commit_message(c, version):
    return ("chore(warp): adoptar Warp %s en %s\n\n"
            "Por qué:\n"
            "Se instala el método Warp para gestionar el conocimiento del proyecto:\n"
            "capa de sistema en warp/, configuración en warp.yaml, participantes en\n"
            "warp/USERS.md y el THREAD governance como responsable de la\n"
            "configuración. Responsable de governance: %s.\n"
            % (version, c["name"], c["governance_owner"]))


def copy_system_layer(dest):
    for path in system_files(SOURCE):
        target = os.path.join(dest, *path.split("/"))
        os.makedirs(os.path.dirname(target), exist_ok=True)
        # copyfile y no copy2: no se copian atributos como el de solo lectura.
        shutil.copyfile(os.path.join(SOURCE, *path.split("/")), target)
    for name in ("LICENSE-DOCS", "LICENSE-CODE"):
        if not os.path.isfile(os.path.join(dest, "warp", name)):
            src = os.path.join(SOURCE, name)
            if not os.path.isfile(src): fail("no se encuentra %s en la distribución." % name)
            shutil.copyfile(src, os.path.join(dest, "warp", name))


def lock_text(dest, version):
    lines = ["# Generado por warp.py: huellas de la capa de sistema. No se edita a mano.",
             "warp_version: %s" % version]
    lines += ["%s  %s" % (digest(os.path.join(dest, *p.split("/"))), p)
              for p in system_files(dest)]
    return "\n".join(lines) + "\n"


def run_checker(dest):
    p = subprocess.run([sys.executable, "-X", "utf8",
                        os.path.join(dest, "warp", "scripts", "check_knowledge.py"), dest],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout.decode("utf-8", "replace").rstrip())
    return p.returncode


# --- Comandos ----------------------------------------------------------------

def cmd_init(args):
    dest = os.path.abspath(args.destino)
    if os.path.exists(dest) and (not os.path.isdir(dest) or os.listdir(dest)):
        fail("el destino debe ser un directorio vacío o inexistente: %s" % dest)
    if args.config:
        with open(args.config, encoding="utf-8") as f:
            cfg = json.load(f)
    else:
        cfg = interactive()
    c = validate(cfg)
    version = read(os.path.join(SOURCE, "warp", "VERSION")).strip()
    today = datetime.date.today().isoformat()

    os.makedirs(dest, exist_ok=True)
    run(["git", "init", "-q"], cwd=dest)
    run(["git", "symbolic-ref", "HEAD", "refs/heads/knowledge"], cwd=dest)
    copy_system_layer(dest)
    j = lambda *p: os.path.join(dest, *p)
    write(j("warp.yaml"), warp_yaml(c, version))
    write(j("warp", "USERS.md"), users_md(c))
    write(j("warp", "threads", "governance", "MANIFEST.md"), governance_manifest(c, today))
    write(j("warp", "threads", "governance", "handoff", ".gitkeep"), "")
    write(j("warp", "index", "THREAD_INDEX.md"), thread_index(c))
    write(j("warp", "index", "DOCUMENT_INDEX.md"), document_index(c))
    write(j("warp", "corpus", ".gitkeep"), "")
    write(j("AGENTS.md"), agents_md(dest))
    write(j(".claude", "settings.json"), json.dumps(SETTINGS, indent=2, ensure_ascii=False) + "\n")
    write(j("warp.lock"), lock_text(dest, version))
    message = commit_message(c, version)
    write(j(".git", STATE), json.dumps({"config": c, "message": message},
                                       indent=2, ensure_ascii=False))

    print("\nInstancia creada en %s (rama knowledge, sin commit).\n" % dest)
    code = run_checker(dest)
    print("\nMensaje propuesto para el commit inicial:\n")
    print("    " + message.replace("\n", "\n    ").rstrip())
    remote = ("y crear el repositorio %s %s/%s en GitHub" %
              ("privado" if c["visibility"] == "private" else "PÚBLICO", c["owner"], c["repo"])
              if c["create_remote"] else "(sin repositorio remoto)")
    print("\nSi el mensaje es correcto, confirma con:\n\n    python warp/scripts/warp.py publish %s\n\n"
          "para hacer el commit %s." % (dest, remote))
    return code


def cmd_publish(args):
    dest = os.path.abspath(args.destino or os.getcwd())
    state_path = os.path.join(dest, ".git", STATE)
    if not os.path.isfile(state_path):
        fail("no hay una instalación pendiente en %s (ejecuta antes `init`)." % dest)
    state = json.loads(read(state_path))
    c, message = state["config"], state["message"]
    code, branch = run(["git", "symbolic-ref", "--short", "HEAD"], cwd=dest, check=False)
    if branch != "knowledge": fail("la rama actual debe ser knowledge (es '%s')." % branch)
    if c["create_remote"]:
        if not shutil.which("gh"): fail("hace falta GitHub CLI (gh) para crear el repositorio.")
        if run(["gh", "auth", "status"], check=False)[0] != 0:
            fail("gh no tiene sesión iniciada: ejecuta `gh auth login`.")

    committed = run(["git", "rev-parse", "--verify", "-q", "HEAD"], cwd=dest, check=False)[0] == 0
    if not committed:
        if not run(["git", "config", "user.email"], cwd=dest, check=False)[1]:
            fail("Git no tiene identidad configurada (git config user.name / user.email).")
        run(["git", "add", "-A"], cwd=dest)
        if run_checker(dest) != 0:
            run(["git", "reset", "-q"], cwd=dest, check=False)
            fail("el checker encontró errores; no se hace el commit.")
        msg_path = os.path.join(dest, ".git", "WARP_INIT_MSG")
        write(msg_path, message)
        run(["git", "commit", "-q", "-F", msg_path], cwd=dest)
        os.remove(msg_path)
        print("\nCommit inicial creado en knowledge.")

    if c["create_remote"]:
        slug = "%s/%s" % (c["owner"], c["repo"])
        code, out = run(["gh", "repo", "view", slug, "--json", "isEmpty", "--jq", ".isEmpty"],
                        check=False)
        if code == 0:
            if out != "true": fail("el repositorio %s ya existe y no está vacío." % slug)
            print("El repositorio %s ya existe y está vacío: se enlaza." % slug)
        else:
            run(["gh", "repo", "create", slug, "--" + c["visibility"]])
            print("Repositorio %s creado (%s)." % (slug, c["visibility"]))
        if run(["git", "remote", "get-url", "origin"], cwd=dest, check=False)[0] != 0:
            run(["git", "remote", "add", "origin", "https://github.com/%s.git" % slug], cwd=dest)
        run(["git", "push", "-q", "-u", "origin", "knowledge"], cwd=dest)
        run(["gh", "api", "-X", "PATCH", "repos/" + slug] + MERGE_SETTINGS + ["--silent"])
        print("Rama knowledge subida y ajustes aplicados: knowledge como rama principal, "
              "solo merge commit, mensaje del PR y borrado automático de ramas.")
        print("\nRecomendado, a mano: proteger knowledge (sin force-push, checks obligatorios). "
              "En repositorios privados requiere GitHub Pro o Team.")
    else:
        print("\nSin repositorio remoto. Para publicarlo más tarde: crea el repositorio, "
              "`git remote add origin <url>` y `git push -u origin knowledge`.")
    os.remove(state_path)
    print("\nInstalación completada.")
    return 0


def main(argv):
    parser = argparse.ArgumentParser(prog="warp.py", description="Instalador de Warp.")
    sub = parser.add_subparsers(dest="command", required=True)
    p_init = sub.add_parser("init", help="prepara una instancia en local, sin commit")
    p_init.add_argument("destino")
    p_init.add_argument("--config", help="archivo JSON con los datos de la instalación")
    p_pub = sub.add_parser("publish", help="hace el commit inicial y, si se pidió, crea el remoto")
    p_pub.add_argument("destino", nargs="?")
    args = parser.parse_args(argv[1:])
    return cmd_init(args) if args.command == "init" else cmd_publish(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
