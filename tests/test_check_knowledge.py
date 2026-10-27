#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Warp: pruebas del comprobador estructural sobre copias temporales de la
instancia de ejemplo (`examples/minimal/`).

Ejecutar: python tests/test_check_knowledge.py
"""

import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CHECKER = os.path.join(ROOT, "warp", "scripts", "check_knowledge.py")
INSTANCE = os.path.join(ROOT, "examples", "minimal")
THREAD = os.path.join("warp", "threads", "example-notes")


def entry(origin, with_type=True):
    lines = ["origin_thread: %s" % origin]
    if with_type: lines.append("type: proposal")
    lines += ["summary: s", "status: proposed"]
    return "\n```yaml\n%s\n```\n" % "\n".join(lines)


def writable(path):
    # copytree copia el atributo de solo lectura (p. ej. carpetas de OneDrive),
    # que impediría modificar y borrar la copia temporal.
    for base, dirs, files in os.walk(path):
        for name in dirs + files:
            os.chmod(os.path.join(base, name), stat.S_IREAD | stat.S_IWRITE)


class CheckKnowledge(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = os.path.join(self.tmp, "instancia")
        shutil.copytree(INSTANCE, self.root)
        writable(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def append(self, rel, text):
        with open(os.path.join(self.root, rel), "a", encoding="utf-8") as f:
            f.write(text)

    def replace(self, rel, old, new):
        p = os.path.join(self.root, rel)
        with open(p, encoding="utf-8") as f: t = f.read()
        self.assertIn(old, t)
        with open(p, "w", encoding="utf-8") as f: f.write(t.replace(old, new))

    def run_checker(self, target=None):
        p = subprocess.run([sys.executable, "-X", "utf8", CHECKER,
                            target or self.root],
                           capture_output=True, text=True, encoding="utf-8")
        return p.returncode, p.stdout

    def test_base_valida(self):
        # Incluye las referencias del MANIFEST a warp/core/, que se resuelven
        # contra la capa de sistema del checker.
        code, out = self.run_checker()
        self.assertEqual(code, 0, out)

    def test_referencia_inexistente_a_la_capa_de_sistema(self):
        self.replace(os.path.join(THREAD, "MANIFEST.md"),
                     "`warp/core/PROJECT_WORKING_RULES.md`",
                     "`warp/core/NO_EXISTE.md`")
        code, out = self.run_checker()
        self.assertEqual(code, 1, out)
        self.assertIn("referencia inexistente 'warp/core/NO_EXISTE.md'", out)

    def test_handoff_rechaza_trabajo_propio(self):
        # La clave por directorio debe coincidir en cualquier sistema operativo.
        self.append(os.path.join(THREAD, "HANDOFF.md"), entry("example-notes"))
        code, out = self.run_checker()
        self.assertEqual(code, 1, out)
        self.assertIn("no admite trabajo propio", out)

    def test_entrada_sin_type_no_se_ignora(self):
        self.append(os.path.join(THREAD, "HANDOFF.md"),
                    entry("example-notes", with_type=False))
        code, out = self.run_checker()
        self.assertEqual(code, 1, out)
        self.assertIn("type HANDOFF no válido", out)

    def test_ningun_no_anula_rutas_declaradas(self):
        self.replace(os.path.join(THREAD, "MANIFEST.md"),
                     "- `warp/corpus/NOTES.md`\n",
                     "- `warp/corpus/NOTES.md`\n\nNingún otro documento.\n")
        code, out = self.run_checker()
        self.assertEqual(code, 0, out)

    def test_falta_fila_en_thread_index(self):
        self.replace(os.path.join("warp", "index", "THREAD_INDEX.md"),
                     "| `example-notes` |", "| `otro` |")
        code, out = self.run_checker()
        self.assertEqual(code, 1, out)

    def test_sin_instancia(self):
        code, out = self.run_checker(self.tmp)
        self.assertEqual(code, 2, out)


if __name__ == "__main__":
    unittest.main()
