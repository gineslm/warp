#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Warp: pruebas del instalador (`warp/scripts/warp.py`).

Cada prueba simula una descarga: una carpeta vacía con solo `warp/` (el método
y sus licencias) donde se ejecuta `init` en el sitio, sin repositorio remoto.

Ejecutar: python tests/test_warp_init.py
"""

import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GIT_ENV = dict(os.environ, GIT_AUTHOR_NAME="Prueba", GIT_AUTHOR_EMAIL="prueba@example.invalid",
               GIT_COMMITTER_NAME="Prueba", GIT_COMMITTER_EMAIL="prueba@example.invalid")

CONFIG = {
    "project": {"name": "Proyecto de prueba", "language": "es-ES"},
    "github": {"owner": "usuario-prueba", "repo": "warp-prueba", "create_remote": False},
    "layout": "knowledge-only",
    "enforcement": "advisory",
    "users": [{"github": "usuario-prueba", "name": "Persona de prueba"}],
    "governance_owner": "usuario-prueba",
}


def force_rmtree(path):
    # Git y OneDrive marcan archivos de solo lectura: hay que quitarlo para borrar.
    def retry(func, p, _):
        os.chmod(p, stat.S_IWRITE); func(p)
    if sys.version_info >= (3, 12):
        shutil.rmtree(path, onexc=retry)
    else:
        shutil.rmtree(path, onerror=retry)


def download(dest):
    """Lo que deja descomprimir el paquete de una versión: solo warp/."""
    shutil.copytree(os.path.join(ROOT, "warp"), os.path.join(dest, "warp"),
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
                    copy_function=shutil.copyfile)
    for name in ("LICENSE-DOCS", "LICENSE-CODE"):
        shutil.copyfile(os.path.join(ROOT, name), os.path.join(dest, "warp", name))


class WarpInit(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.dest = os.path.join(self.tmp, "proyecto")
        os.makedirs(self.dest)
        download(self.dest)
        self.warp = os.path.join(self.dest, "warp", "scripts", "warp.py")

    def tearDown(self):
        force_rmtree(self.tmp)

    def run_cmd(self, *args):
        p = subprocess.run([sys.executable, "-X", "utf8"] + list(args), cwd=self.dest,
                           env=GIT_ENV, stdin=subprocess.DEVNULL,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return p.returncode, p.stdout.decode("utf-8", "replace")

    def init(self, **changes):
        cfg = json.loads(json.dumps(CONFIG))
        for k, v in changes.items(): cfg[k] = v
        path = os.path.join(self.tmp, "config.json")
        with open(path, "w", encoding="utf-8") as f: json.dump(cfg, f)
        return self.run_cmd(self.warp, "init", "--config", path)

    def check(self):
        return self.run_cmd(os.path.join(self.dest, "warp", "scripts", "check_knowledge.py"))

    def git(self, *args):
        p = subprocess.run(["git"] + list(args), cwd=self.dest, env=GIT_ENV,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return p.stdout.decode("utf-8", "replace").strip()

    def edit(self, rel, fn):
        p = os.path.join(self.dest, *rel.split("/"))
        with open(p, encoding="utf-8") as f: t = f.read()
        with open(p, "w", encoding="utf-8", newline="") as f: f.write(fn(t))

    def test_init_crea_lo_propio_del_proyecto_junto_al_metodo(self):
        code, out = self.init()
        self.assertEqual(code, 0, out)
        self.assertIn("Resumen: 0 error(es)", out)
        for rel in ("warp.yaml", "warp.lock", "AGENTS.md", ".claude/settings.json", "USERS.md",
                    "threads/governance/MANIFEST.md", "threads/governance/handoff/.gitkeep",
                    "index/THREAD_INDEX.md", "index/DOCUMENT_INDEX.md", "corpus/.gitkeep"):
            self.assertTrue(os.path.isfile(os.path.join(self.dest, *rel.split("/"))), rel)
        self.assertEqual(self.git("symbolic-ref", "--short", "HEAD"), "knowledge")
        self.assertEqual(self.git("rev-list", "--all"), "")

    def test_init_no_copia_el_metodo(self):
        self.assertEqual(self.init()[0], 0)
        entries = sorted(os.listdir(self.dest))
        self.assertEqual(entries, sorted([".claude", ".git", "AGENTS.md", "USERS.md", "corpus",
                                          "index", "threads", "warp", "warp.lock", "warp.yaml"]))
        self.assertFalse(os.path.exists(os.path.join(self.dest, "warp", "corpus")))

    def test_publish_hace_el_commit_inicial(self):
        self.assertEqual(self.init()[0], 0)
        code, out = self.run_cmd(self.warp, "publish")
        self.assertEqual(code, 0, out)
        with open(os.path.join(ROOT, "warp", "VERSION"), encoding="utf-8") as f:
            version = f.read().strip()
        self.assertEqual(self.git("log", "-1", "--format=%s"),
                         "chore(warp): adoptar Warp %s en Proyecto de prueba" % version)
        files = self.git("ls-files").splitlines()
        self.assertFalse([f for f in files if "__pycache__" in f], files)
        self.assertIn("warp/LICENSE-DOCS", files)
        self.assertFalse(os.path.exists(os.path.join(self.dest, ".git", "warp-init.json")))
        self.assertEqual(self.check()[0], 0)

    def test_publish_dos_veces_indica_publish_remote(self):
        self.assertEqual(self.init()[0], 0)
        self.assertEqual(self.run_cmd(self.warp, "publish")[0], 0)
        code, out = self.run_cmd(self.warp, "publish")
        self.assertEqual(code, 1, out)
        self.assertIn("publish --remote", out)

    def test_publish_sin_instalacion(self):
        code, out = self.run_cmd(self.warp, "publish")
        self.assertEqual(code, 1, out)
        self.assertIn("falta warp.yaml", out)

    def test_publish_remote_con_origin_ya_configurado(self):
        self.assertEqual(self.init()[0], 0)
        self.assertEqual(self.run_cmd(self.warp, "publish")[0], 0)
        self.git("remote", "add", "origin", "https://example.invalid/x.git")
        code, out = self.run_cmd(self.warp, "publish", "--remote")
        self.assertEqual(code, 1, out)
        if shutil.which("gh") and "sesión" not in out:
            self.assertIn("ya tiene un repositorio remoto", out)

    def test_publish_visibilidad_no_valida(self):
        code, out = self.run_cmd(self.warp, "publish", "--remote", "--visibility", "interna")
        self.assertEqual(code, 2, out)

    def test_carpeta_con_otros_archivos(self):
        open(os.path.join(self.dest, "algo.txt"), "w").close()
        code, out = self.init()
        self.assertEqual(code, 1, out)
        self.assertIn("solo debe contener warp/", out)
        self.assertIn("algo.txt", out)

    def test_sin_terminal_y_sin_config(self):
        code, out = self.run_cmd(self.warp, "init")
        self.assertEqual(code, 1, out)
        self.assertIn("usa --config", out)
        self.assertEqual(os.listdir(self.dest), ["warp"])

    def test_config_dentro_de_la_carpeta(self):
        path = os.path.join(self.dest, "config.json")
        with open(path, "w", encoding="utf-8") as f: json.dump(CONFIG, f)
        code, out = self.run_cmd(self.warp, "init", "--config", path)
        self.assertEqual(code, 1, out)

    def test_with_code_aun_no_soportado(self):
        code, out = self.init(layout="with-code")
        self.assertEqual(code, 1, out)
        self.assertIn("todavía no está soportado", out)

    def test_sin_participantes(self):
        code, out = self.init(users=[])
        self.assertEqual(code, 1, out)
        self.assertIn("al menos un participante", out)

    def test_responsable_de_governance_fuera_de_la_lista(self):
        code, out = self.init(governance_owner="alguien")
        self.assertEqual(code, 1, out)
        self.assertIn("no está entre los participantes", out)

    def test_capa_de_sistema_editada(self):
        self.assertEqual(self.init()[0], 0)
        self.edit("warp/core/THREAD_ARCHITECTURE.md", lambda t: t + "\nCambio local.\n")
        code, out = self.check()
        self.assertEqual(code, 1, out)
        self.assertIn("'warp/core/THREAD_ARCHITECTURE.md' no coincide con su huella", out)

    def test_archivo_ajeno_en_la_capa_de_sistema(self):
        self.assertEqual(self.init()[0], 0)
        with open(os.path.join(self.dest, "warp", "core", "LOCAL.md"), "w") as f: f.write("x\n")
        code, out = self.check()
        self.assertEqual(code, 1, out)
        self.assertIn("'warp/core/LOCAL.md' no está registrado", out)

    def test_finales_de_linea_crlf_no_alteran_la_huella(self):
        self.assertEqual(self.init()[0], 0)
        self.edit("warp/core/GIT_COMMIT_RULES.md",
                  lambda t: t.replace("\r\n", "\n").replace("\n", "\r\n"))
        code, out = self.check()
        self.assertEqual(code, 0, out)


if __name__ == "__main__":
    unittest.main()
