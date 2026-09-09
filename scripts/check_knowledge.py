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
H_TYPES = {"proposal", "review", "need", "task"}
H_STATUS = {"proposed", "in_review", "deferred", "ready_to_apply"}
TEXT_EXTS = {".md", ".py", ".yml", ".yaml", ".txt", ".toml", ".ini",
             ".cfg", ".sh", ".example"}
SPECIAL = {"requirements.txt", ".env", ".env.example", "Dockerfile"}
SKIP = {".git", "data", "results", "__pycache__", ".pytest_cache"}
REF_EXTS = {"md", "py", "csv", "json", "yml", "yaml", "txt", "toml"}
MAX_SCAN = 2_000_000
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


def find_root(start):
    p = os.path.abspath(start)
    while True:
        if os.path.isfile(os.path.join(
                p, "docs", "core", "THREAD_ARCHITECTURE.md")):
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
        val = val.strip()
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
    for base, dirs, files in os.walk(os.path.join(root, "docs")):
        dirs[:] = [d for d in dirs if d not in SKIP]
        if "MANIFEST.md" in files: out.append(base)
    return sorted(out)


def authority_paths(text):
    body = section(text, "Autoridad documental vigente")
    if body is None: return set(), False
    if re.search(r"\bNingún\b|\bNingun[ao]?\b", body, re.I):
        return set(), True
    return {x.strip() for x in re.findall(r"`([^`]+)`", body)
            if "/" in x or x.endswith(".md")}, True


def check_threads(root, rep):
    ids, mpaths, data, texts = {}, set(), {}, {}
    for d in thread_dirs(root):
        mp, hp = os.path.join(d, "MANIFEST.md"), os.path.join(d, "HANDOFF.md")
        mr = rel(root, mp); mpaths.add(mr)
        if not os.path.isfile(hp):
            rep.error("%s: falta HANDOFF.md." % rel(root, d))
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
        canonical = rel(root, hp)
        if not isinstance(ho, dict) or not ho.get("path"):
            rep.error("%s: falta handoff.path." % mr)
        elif ho["path"] != canonical:
            rep.error("%s: handoff.path debe ser '%s'." % (mr, canonical))
        elif not os.path.isfile(os.path.join(root, ho["path"])):
            rep.error("%s: handoff.path no existe." % mr)
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
                    not os.path.exists(os.path.join(root, token)):
                rep.error("%s: referencia inexistente '%s'." % (mr, token))
    return ids, mpaths, data, texts


def check_thread_index(root, rep, mpaths, data):
    p = os.path.join(root, "docs", "core", "THREAD_INDEX.md")
    if not os.path.isfile(p):
        rep.error("Falta docs/core/THREAD_INDEX.md."); return
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
    p = os.path.join(root, "docs", "core", "DOCUMENT_INDEX.md")
    if not os.path.isfile(p):
        rep.error("Falta docs/core/DOCUMENT_INDEX.md."); return
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


def check_handoffs(root, rep, ids, data):
    by_dir = {os.path.dirname(os.path.join(root, mp)): y for mp, y in data.items()}
    for d in thread_dirs(root):
        hp = os.path.join(d, "HANDOFF.md")
        if not os.path.isfile(hp): continue
        receiver = by_dir.get(d, {}).get("thread_id")
        for m in re.finditer(r"```ya?ml\s*\n(.*?)\n```", read(hp), re.S):
            e = yaml_block("```yaml\n" + m.group(1) + "\n```")
            if not e or "type" not in e: continue
            hr = rel(root, hp)
            if e.get("type") not in H_TYPES:
                rep.error("%s: type HANDOFF no válido." % hr)
            if e.get("status") and e["status"] not in H_STATUS:
                rep.error("%s: status HANDOFF no válido." % hr)
            origin = e.get("origin_thread")
            if not origin:
                rep.error("%s: falta origin_thread." % hr)
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


def check_secrets(root, rep):
    for full in versioned_text_files(root):
        if os.path.basename(full) == "check_knowledge.py": continue
        try:
            if os.path.getsize(full) > MAX_SCAN:
                rep.warn("No se escanea por tamaño '%s'." % rel(root, full)); continue
            text = read(full)
        except Exception:
            continue
        for name, pattern in SECRETS:
            if pattern.search(text):
                rep.error("Posible credencial (%s) en '%s'." %
                          (name, rel(root, full)))
                break


def main(argv):
    root = find_root(argv[1] if len(argv) > 1 else os.getcwd())
    if not root:
        print("No se encontró la raíz del repositorio."); return 2
    print("Comprobando coherencia del conocimiento en: %s" % root)
    rep = Report()
    ids, mpaths, data, texts = check_threads(root, rep)
    check_thread_index(root, rep, mpaths, data)
    check_document_index(root, rep, ids, data, texts)
    check_handoffs(root, rep, ids, data)
    check_secrets(root, rep)
    print("THREADs encontrados: %d." % len(mpaths))
    return rep.dump()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
