#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Warp: pruebas del comprobador estructural sobre copias temporales de `docs/`.

Ejecutar: python scripts/test_check_knowledge.py
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CHECKER = os.path.join(HERE, "check_knowledge.py")
EXAMPLE = os.path.join("docs", "threads", "example")


def entry(origin, with_type=True):
    lines = ["origin_thread: %s" % origin]
    if with_type: lines.append("type: proposal")
    lines += ["summary: s", "status: proposed"]
    return "\n```yaml\n%s\n```\n" % "\n".join(lines)


class CheckKnowledge(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        shutil.copytree(os.path.join(ROOT, "docs"), os.path.join(self.tmp, "docs"))

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def append(self, rel, text):
        with open(os.path.join(self.tmp, rel), "a", encoding="utf-8") as f:
            f.write(text)

    def replace(self, rel, old, new):
        p = os.path.join(self.tmp, rel)
        with open(p, encoding="utf-8") as f: t = f.read()
        self.assertIn(old, t)
        with open(p, "w", encoding="utf-8") as f: f.write(t.replace(old, new))

    def run_checker(self):
        p = subprocess.run([sys.executable, "-X", "utf8", CHECKER, self.tmp],
                           capture_output=True, text=True, encoding="utf-8")
        return p.returncode, p.stdout

    def test_base_valida(self):
        code, out = self.run_checker()
        self.assertEqual(code, 0, out)

    def test_handoff_rechaza_trabajo_propio(self):
        # La clave por directorio debe coincidir en cualquier sistema operativo.
        self.append(os.path.join(EXAMPLE, "HANDOFF.md"), entry("example-notes"))
        code, out = self.run_checker()
        self.assertEqual(code, 1, out)
        self.assertIn("no admite trabajo propio", out)

    def test_entrada_sin_type_no_se_ignora(self):
        self.append(os.path.join(EXAMPLE, "HANDOFF.md"),
                    entry("example-notes", with_type=False))
        code, out = self.run_checker()
        self.assertEqual(code, 1, out)
        self.assertIn("type HANDOFF no válido", out)

    def test_ningun_no_anula_rutas_declaradas(self):
        self.replace(os.path.join(EXAMPLE, "MANIFEST.md"),
                     "- `docs/threads/example/NOTES.md`\n",
                     "- `docs/threads/example/NOTES.md`\n\nNingún otro documento.\n")
        code, out = self.run_checker()
        self.assertEqual(code, 0, out)

    def test_falta_fila_en_thread_index(self):
        self.replace(os.path.join("docs", "core", "THREAD_INDEX.md"),
                     "| `example-notes` |", "| `otro` |")
        code, out = self.run_checker()
        self.assertEqual(code, 1, out)


if __name__ == "__main__":
    unittest.main()
