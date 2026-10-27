#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Warp: comprobador estructural de `knowledge`. Solo lee; no modifica."""

import os
import re
import subprocess
import sys

STATUS = {"PROPOSED", "ACTIVE", "BLOCKED", "CLOSED", "ARCHIVED"}
ORIGINS = {"USER_DECLARED", "THREAD_DERIVED", "MIGRATED"}
IDENTITY = {"thread_id", "domain", "status", "owner", "current_cycle",
            "origin", "repository", "handoff"}
H_TYPES = {"proposal", "review", "need", "request"}
H_STATUS = {"proposed", "in_review", "deferred", "ready_to_apply"}
H_FIELDS = ("origin_thread", "type", "summary", "target_scope", "status")
H_SECTIONS = ("Contexto", "Evidencia")
TEXT_EXTS = {".md", ".py", ".yml", ".yaml", ".txt", ".toml", ".ini",
             ".cfg", ".sh", ".example"}
SPECIAL = {"requirements.txt", ".env", ".env.example", "Dockerfile"}
SKIP = {".git", "data", "results", "__pycache__", ".pytest_cache"}
REF_EXTS = {"md", "py", "csv", "json", "yml", "yaml", "txt", "toml"}
MAX_SCAN = 2_000_000
LAYOUTS = {"knowledge-only", "with-code"}
ENFORCEMENT = {"advisory", "strict"}
USER_STATUS = {"active", "inactive"}
GOVERNANCE = "governance"
CONFIG_DOCS = {"warp.yaml", "warp/USERS.md"}
CORPUS = "warp/corpus/"
PLACEHOLDERS = {".gitkeep"}
SECRETS = [
    ("GitHub token", re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}")),
    ("GitHub PAT", re.compile(r"github_pat_[A-Za-z0-9_]{30,}")),
    ("AWS access key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("Clave privada", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("token/secret/password",
     re.compile(r"(?i)\b(token|secret|password|passwd)\s*[:=]\s*"
                r"['\"]?[A-Za-z0-9/\+_\-]{20,}")),
]


class Report:
    def __init__(self):
        self.errors, self.warns = [], []

    def error(self, msg): self.errors.append(msg)
    def warn(self, msg): self.warns.append(msg)

    def dump(self):
        if self.errors:
            print("\nERRORES:")
            for x in self.errors: print("  [ERROR] " + x)
        if self.warns:
            print("\nAVISOS:")
            for x in self.warns: print("  [WARN]  " + x)
        print("\nResumen: %d error(es), %d aviso(s)." %
              (len(self.errors), len(self.warns)))
        return 1 if self.errors else 0


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def rel(root, path):
    return os.path.relpath(path, root).replace(os.sep, "/")


SYSTEM_BASE = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
SYSTEM_PREFIXES = ("warp/core/", "warp/scripts/")


def ref_base(root, token):
    # La capa de sistema se resuelve donde vive este checker: en una
    # instancia coincide con la raíz; en la distribución, es el propio repo.
    return SYSTEM_BASE if token.startswith(SYSTEM_PREFIXES) else root


def find_root(start):
    p = os.path.abspath(start)
    while True:
        if os.path.isfile(os.path.join(p, "warp.yaml")):
            return p
        q = os.path.dirname(p)
        if q == p: return None
        p = q


def yaml_block(text):
    m = re.search(r"```ya?ml\s*\n(.*?)\n```", text, re.S)
    if not m: return None
    out, parent = {}, None
    for raw in m.group(1).splitlines():
        if not raw.strip() or raw.strip().startswith("#"): continue
        indent = len(raw) - len(raw.lstrip())
        key, sep, val = raw.strip().partition(":")
        if not sep: continue
        val = re.sub(r"\s+#.*$", "", val).strip()
        if indent == 0:
            out[key] = {} if not val else val
            parent = key if not val else None
        elif parent:
            out[parent][key] = val
    return out


def section(text, title):
    m = re.search(r"^##\s+" + re.escape(title) +
                  r"\s*$\n(.*?)(?=^##\s+|\Z)", text, re.M | re.S)
    return None if not m else m.group(1).strip()


def tables(text):
    lines, out, i = text.splitlines(), [], 0
    while i < len(lines):
        if not lines[i].lstrip().startswith("|"):
            i += 1; continue
        block = []
        while i < len(lines) and lines[i].lstrip().startswith("|"):
            block.append([c.strip() for c in
                          lines[i].strip().strip("|").split("|")])
            i += 1
        block = [r for r in block
                 if not all(re.fullmatch(r":?-+:?", c or "-") for c in r)]
        if block: out.append((block[0], block[1:]))
    return out


def clean(cell):
    x = cell.strip()
    return x[1:-1].strip() if len(x) >= 2 and x[0] == x[-1] == "`" else x


def thread_dirs(root):
    out = []
    for base, dirs, files in os.walk(os.path.join(root, "warp", "threads")):
        dirs[:] = [d for d in dirs if d not in SKIP]
        if "MANIFEST.md" in files: out.append(base)
    return sorted(out)


def authority_paths(text):
    body = section(text, "Autoridad documental vigente")
    if body is None: return set(), False
    return {x.strip() for x in re.findall(r"`([^`]+)`", body)
            if "/" in x or "." in x}, True


def check_threads(root, rep):
    ids, mpaths, data, texts = {}, set(), {}, {}
    for d in thread_dirs(root):
        mp, hp = os.path.join(d, "MANIFEST.md"), os.path.join(d, "handoff")
        mr = rel(root, mp); mpaths.add(mr)
        if not os.path.isdir(hp):
            rep.error("%s: falta el buzón handoff/." % rel(root, d))
        text = read(mp); texts[mr] = text
        y = yaml_block(text)
        if y is None:
            rep.error("%s: falta bloque ```yaml de identidad." % mr); continue
        data[mr] = y
        for k in IDENTITY:
            if k not in y or y[k] in ("", None, {}):
                rep.error("%s: falta campo estructurado '%s'." % (mr, k))
        if not section(text, "Responsabilidad"):
            rep.error("%s: falta `## Responsabilidad` no vacía." % mr)
        if y.get("status") not in STATUS:
            rep.error("%s: status '%s' no válido." % (mr, y.get("status")))
        origin = y.get("origin")
        if not isinstance(origin, dict) or origin.get("type") not in ORIGINS:
            rep.error("%s: origin.type no válido." % mr)
        elif origin["type"] in {"THREAD_DERIVED", "MIGRATED"} and \
                not origin.get("source_id"):
            rep.error("%s: origin.type=%s requiere source_id." %
                      (mr, origin["type"]))
        repo = y.get("repository")
        if not isinstance(repo, dict) or not repo.get("knowledge_branch"):
            rep.error("%s: repository.knowledge_branch es obligatorio." % mr)
        elif repo.get("created_from_knowledge_commit") and not re.fullmatch(
                r"[0-9a-f]{7,40}", repo["created_from_knowledge_commit"]):
            rep.warn("%s: created_from_knowledge_commit no parece SHA." % mr)
        ho = y.get("handoff")
        canonical = rel(root, hp) + "/"
        if not isinstance(ho, dict) or not ho.get("path"):
            rep.error("%s: falta handoff.path." % mr)
        elif ho["path"] != canonical:
            rep.error("%s: handoff.path debe ser '%s'." % (mr, canonical))
        tid = y.get("thread_id")
        if tid in ids:
            rep.error("thread_id duplicado '%s'." % tid)
        elif tid:
            ids[tid] = mr
        nofence = re.sub(r"```.*?```", "", text, flags=re.S)
        for token in re.findall(r"`([^`]+)`", nofence):
            token = token.strip()
            if "/" in token and "." in token and \
                    token.rsplit(".", 1)[-1].lower() in REF_EXTS and \
                    not os.path.exists(os.path.join(ref_base(root, token), token)):
                rep.error("%s: referencia inexistente '%s'." % (mr, token))
    return ids, mpaths, data, texts


def check_thread_index(root, rep, mpaths, data):
    p = os.path.join(root, "warp", "index", "THREAD_INDEX.md")
    if not os.path.isfile(p):
        rep.error("Falta warp/index/THREAD_INDEX.md."); return
    target = None
    for head, rows in tables(read(p)):
        low = [x.lower() for x in head]
        if {"thread_id", "status", "manifest", "handoff"} <= set(low):
            target = low, rows; break
    if not target:
        rep.error("THREAD_INDEX.md: falta tabla canónica."); return
    head, rows = target
    ix = {k: head.index(k) for k in ("thread_id", "status", "manifest", "handoff")}
    seen = set()
    for r in rows:
        if len(r) <= max(ix.values()): continue
        tid, st, mp, hp = [clean(r[ix[k]]) for k in
                           ("thread_id", "status", "manifest", "handoff")]
        seen.add(mp)
        if mp not in mpaths:
            rep.error("THREAD_INDEX.md: MANIFEST inexistente '%s'." % mp); continue
        y = data.get(mp, {})
        if tid != y.get("thread_id"):
            rep.error("THREAD_INDEX.md: thread_id no coincide en %s." % mp)
        if st != y.get("status"):
            rep.error("THREAD_INDEX.md: status no coincide en %s." % mp)
        if hp != (y.get("handoff") or {}).get("path"):
            rep.error("THREAD_INDEX.md: HANDOFF no coincide en %s." % mp)
    for mp in mpaths - seen:
        rep.error("THREAD_INDEX.md: falta '%s'." % mp)


def check_document_index(root, rep, ids, data, texts):
    p = os.path.join(root, "warp", "index", "DOCUMENT_INDEX.md")
    if not os.path.isfile(p):
        rep.error("Falta warp/index/DOCUMENT_INDEX.md."); return
    target = None
    for head, rows in tables(read(p)):
        low = [x.lower() for x in head]
        if {"path", "authority_thread", "authority_manifest"} <= set(low):
            target = low, rows; break
    if not target:
        rep.error("DOCUMENT_INDEX.md: falta tabla canónica."); return
    head, rows = target
    ix = {k: head.index(k) for k in
          ("path", "authority_thread", "authority_manifest")}
    seen = set()
    for r in rows:
        if len(r) <= max(ix.values()): continue
        doc, tid, mp = [clean(r[ix[k]]) for k in
                        ("path", "authority_thread", "authority_manifest")]
        if doc in seen: rep.error("DOCUMENT_INDEX.md: duplicado '%s'." % doc)
        seen.add(doc)
        if not doc.startswith(CORPUS):
            rep.error("DOCUMENT_INDEX.md: '%s' no pertenece al corpus (%s)." %
                      (doc, CORPUS))
        if not os.path.isfile(os.path.join(root, doc)):
            rep.error("DOCUMENT_INDEX.md: documento inexistente '%s'." % doc)
        if tid not in ids:
            rep.error("DOCUMENT_INDEX.md: authority_thread inexistente '%s'." % tid)
        if mp not in data:
            rep.error("DOCUMENT_INDEX.md: authority_manifest inexistente '%s'." % mp)
            continue
        if data[mp].get("thread_id") != tid:
            rep.error("DOCUMENT_INDEX.md: authority_thread/manifest no coinciden en '%s'." % doc)
        paths, ok = authority_paths(texts[mp])
        if not ok:
            rep.error("%s: falta `## Autoridad documental vigente`." % mp)
        elif doc not in paths:
            rep.error("DOCUMENT_INDEX.md: '%s' no está bajo autoridad en %s." %
                      (doc, mp))
    corpus = os.path.join(root, *CORPUS.split("/"))
    for base, dirs, files in os.walk(corpus):
        for f in files:
            doc = rel(root, os.path.join(base, f))
            if f not in PLACEHOLDERS and doc not in seen:
                rep.error("DOCUMENT_INDEX.md: falta el documento del corpus '%s'." % doc)


def check_config(root, rep):
    y = yaml_block("```yaml\n" + read(os.path.join(root, "warp.yaml")) + "\n```") or {}
    if not re.fullmatch(r"\d+\.\d+\.\d+", y.get("warp_version") or ""):
        rep.error("warp.yaml: warp_version debe ser una versión X.Y.Z.")
    project = y.get("project")
    for k in ("name", "repository", "language"):
        if not isinstance(project, dict) or not project.get(k):
            rep.error("warp.yaml: falta project.%s." % k)
    if y.get("layout") not in LAYOUTS:
        rep.error("warp.yaml: layout '%s' no válido." % y.get("layout"))
    enforcement = y.get("enforcement")
    if enforcement not in ENFORCEMENT:
        rep.error("warp.yaml: enforcement '%s' no válido." % enforcement)
    users = {}
    p = os.path.join(root, "warp", "USERS.md")
    if not os.path.isfile(p):
        rep.error("Falta warp/USERS.md."); return enforcement, users
    target = None
    for head, rows in tables(read(p)):
        low = [x.lower() for x in head]
        if {"github", "name", "status"} <= set(low):
            target = low, rows; break
    if not target:
        rep.error("USERS.md: falta tabla canónica."); return enforcement, users
    head, rows = target
    ix = {k: head.index(k) for k in ("github", "status")}
    for r in rows:
        if len(r) <= max(ix.values()): continue
        gh, st = clean(r[ix["github"]]), clean(r[ix["status"]])
        if gh in users: rep.error("USERS.md: github duplicado '%s'." % gh)
        users[gh] = st
        if st not in USER_STATUS:
            rep.error("USERS.md: status '%s' no válido para '%s'." % (st, gh))
    if "active" not in users.values():
        rep.error("USERS.md: no hay ningún participante active.")
    return enforcement, users


def check_owners(rep, data, users, enforcement):
    # Comprobaciones sobre personas: su severidad depende de `enforcement`.
    report = rep.error if enforcement == "strict" else rep.warn
    for mp, y in sorted(data.items()):
        owner = y.get("owner")
        if not owner: continue
        if owner not in users:
            report("%s: owner '%s' no figura en warp/USERS.md." % (mp, owner))
        elif users[owner] != "active" and \
                y.get("status") not in {"CLOSED", "ARCHIVED"}:
            report("%s: owner '%s' no está active." % (mp, owner))


def check_governance(rep, data, texts):
    gov = [mp for mp, y in data.items() if y.get("thread_id") == GOVERNANCE]
    if len(gov) != 1:
        rep.error("Debe existir exactamente un THREAD '%s' (hay %d)." %
                  (GOVERNANCE, len(gov)))
    for mp, y in data.items():
        paths, _ = authority_paths(texts[mp])
        if y.get("thread_id") == GOVERNANCE:
            if y.get("status") in {"CLOSED", "ARCHIVED"}:
                rep.error("%s: el THREAD governance no puede estar %s." %
                          (mp, y.get("status")))
            for doc in sorted(CONFIG_DOCS - paths):
                rep.error("%s: governance debe tener autoridad sobre '%s'." % (mp, doc))
            for doc in sorted(x for x in paths if x.startswith(CORPUS)):
                rep.warn("%s: governance no gobierna el corpus ('%s')." % (mp, doc))
        else:
            for doc in sorted(paths & CONFIG_DOCS):
                rep.error("%s: '%s' es configuración del proyecto y pertenece a governance." %
                          (mp, doc))


def check_handoffs(root, rep, ids, data):
    by_dir = {os.path.normpath(os.path.dirname(os.path.join(root, mp))): y
              for mp, y in data.items()}
    for d in thread_dirs(root):
        box = os.path.join(d, "handoff")
        if not os.path.isdir(box): continue
        receiver = by_dir.get(os.path.normpath(d), {}).get("thread_id")
        for f in sorted(os.listdir(box)):
            hp = os.path.join(box, f); hr = rel(root, hp)
            if f in PLACEHOLDERS: continue
            if not f.endswith(".md") or not os.path.isfile(hp):
                rep.error("%s: el buzón solo admite entradas .md." % hr); continue
            text = read(hp)
            blocks = re.findall(r"```ya?ml\s*\n(.*?)\n```", text, re.S)
            if len(blocks) != 1:
                rep.error("%s: una entrada debe tener exactamente un bloque yaml (tiene %d)." %
                          (hr, len(blocks))); continue
            e = yaml_block("```yaml\n" + blocks[0] + "\n```") or {}
            for k in H_FIELDS:
                if not e.get(k):
                    rep.error("%s: falta el campo '%s'." % (hr, k))
            for title in H_SECTIONS:
                if not section(text, title):
                    rep.error("%s: falta `## %s` no vacía." % (hr, title))
            if e.get("type") and e["type"] not in H_TYPES:
                rep.error("%s: type '%s' no válido." % (hr, e["type"]))
            if e.get("status") and e["status"] not in H_STATUS:
                rep.error("%s: status '%s' no válido." % (hr, e["status"]))
            origin = e.get("origin_thread")
            if not origin:
                continue
            elif origin not in ids:
                rep.error("%s: origin_thread inexistente '%s'." % (hr, origin))
            elif origin == receiver:
                rep.error("%s: HANDOFF no admite trabajo propio del receptor." % hr)


def versioned_text_files(root):
    try:
        p = subprocess.run(["git", "-C", root, "ls-files", "-z"], check=True,
                           stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        paths = [x.decode() for x in p.stdout.split(b"\0") if x]
    except (OSError, subprocess.CalledProcessError, UnicodeDecodeError):
        paths = []
        for base, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in SKIP]
            paths += [rel(root, os.path.join(base, f)) for f in files]
    for rp in paths:
        if set(rp.replace("\\", "/").split("/")) & SKIP: continue
        fn = os.path.basename(rp); ext = os.path.splitext(fn)[1].lower()
        if ext in TEXT_EXTS or fn in SPECIAL:
            yield os.path.join(root, rp)


def git_toplevel(root):
    try:
        p = subprocess.run(["git", "-C", root, "rev-parse", "--show-toplevel"],
                           check=True, stdout=subprocess.PIPE,
                           stderr=subprocess.DEVNULL)
        return os.path.normpath(p.stdout.decode().strip())
    except (OSError, subprocess.CalledProcessError, UnicodeDecodeError):
        return root


def check_secrets(root, rep):
    # Todo el repositorio, no solo la instancia: en la distribución la
    # instancia de ejemplo es un subdirectorio.
    base = git_toplevel(root)
    for full in versioned_text_files(base):
        if os.path.basename(full) == "check_knowledge.py": continue
        try:
            if os.path.getsize(full) > MAX_SCAN:
                rep.warn("No se escanea por tamaño '%s'." % rel(base, full)); continue
            text = read(full)
        except Exception:
            continue
        for name, pattern in SECRETS:
            if pattern.search(text):
                rep.error("Posible credencial (%s) en '%s'." %
                          (name, rel(base, full)))
                break


def main(argv):
    root = find_root(argv[1] if len(argv) > 1 else os.getcwd())
    if not root:
        print("No se encontró una instancia Warp (warp.yaml)."); return 2
    print("Comprobando coherencia del conocimiento en: %s" % root)
    rep = Report()
    enforcement, users = check_config(root, rep)
    ids, mpaths, data, texts = check_threads(root, rep)
    check_owners(rep, data, users, enforcement)
    check_governance(rep, data, texts)
    check_thread_index(root, rep, mpaths, data)
    check_document_index(root, rep, ids, data, texts)
    check_handoffs(root, rep, ids, data)
    check_secrets(root, rep)
    print("THREADs encontrados: %d." % len(mpaths))
    return rep.dump()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
