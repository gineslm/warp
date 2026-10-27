#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Warp: prueba de extremo a extremo del paquete descargable.

Genera el zip, lo descomprime en una carpeta vacía, instala con `init` y
comprueba la instancia con el checker, como haría quien descarga una versión.

Ejecutar: python tests/test_build_package.py
"""

import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BUILD = os.path.join(ROOT, "tools", "build_package.py")
GIT_ENV = dict(os.environ, GIT_AUTHOR_NAME="Prueba", GIT_AUTHOR_EMAIL="prueba@example.invalid",
               GIT_COMMITTER_NAME="Prueba", GIT_COMMITTER_EMAIL="prueba@example.invalid")
CONFIG = {
    "project": {"name": "Proyecto descargado", "language": "es-ES"},
    "github": {"owner": "usuario-prueba", "repo": "warp-descarga", "create_remote": False},
    "users": [{"github": "usuario-prueba", "name": "Persona de prueba"}],
    "governance_owner": "usuario-prueba",
}


def force_rmtree(path):
    def retry(func, p, _):
        os.chmod(p, stat.S_IWRITE); func(p)
    if sys.version_info >= (3, 12):
        shutil.rmtree(path, onexc=retry)
    else:
        shutil.rmtree(path, onerror=retry)


def py(*args, cwd=None):
    p = subprocess.run([sys.executable, "-X", "utf8"] + list(args), cwd=cwd, env=GIT_ENV,
                       stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return p.returncode, p.stdout.decode("utf-8", "replace")


class BuildPackage(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        force_rmtree(self.tmp)

    def build(self):
        out = os.path.join(self.tmp, "dist")
        code, msg = py(BUILD, "--out", out)
        if code != 0 and "cambios sin commit" in msg:
            self.skipTest("hay cambios sin commit en warp/: el paquete se genera desde HEAD")
        self.assertEqual(code, 0, msg)
        zips = os.listdir(out)
        self.assertEqual(len(zips), 1, zips)
        return os.path.join(out, zips[0])

    def test_el_paquete_solo_contiene_warp(self):
        with zipfile.ZipFile(self.build()) as z:
            names = z.namelist()
        self.assertTrue(names)
        self.assertEqual({n.split("/")[0] for n in names}, {"warp"})
        for need in ("warp/VERSION", "warp/LICENSE-DOCS", "warp/LICENSE-CODE",
                     "warp/scripts/warp.py", "warp/core/THREAD_ARCHITECTURE.md"):
            self.assertIn(need, names)
        self.assertFalse([n for n in names if "__pycache__" in n or n.endswith(".pyc")])

    def test_descargar_instalar_y_comprobar(self):
        dest = os.path.join(self.tmp, "proyecto")
        os.makedirs(dest)
        with zipfile.ZipFile(self.build()) as z:
            z.extractall(dest)
        cfg = os.path.join(self.tmp, "config.json")
        with open(cfg, "w", encoding="utf-8") as f: json.dump(CONFIG, f)
        warp = os.path.join(dest, "warp", "scripts", "warp.py")
        code, out = py(warp, "init", "--config", cfg, cwd=dest)
        self.assertEqual(code, 0, out)
        code, out = py(warp, "publish", cwd=dest)
        self.assertEqual(code, 0, out)
        code, out = py(os.path.join(dest, "warp", "scripts", "check_knowledge.py"), cwd=dest)
        self.assertEqual(code, 0, out)


if __name__ == "__main__":
    unittest.main()
