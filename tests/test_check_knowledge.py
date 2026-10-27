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

    def assert_error(self, fragment):
        code, out = self.run_checker()
        self.assertEqual(code, 1, out)
        self.assertIn(fragment, out)

    def test_layout_no_valido(self):
        self.replace("warp.yaml", "layout: knowledge-only", "layout: mixto")
        self.assert_error("layout 'mixto' no válido")

    def test_warp_yaml_sin_campo_de_proyecto(self):
        self.replace("warp.yaml", "  repository: ejemplo/warp-minimal\n", "")
        self.assert_error("falta project.repository")

    def test_usuario_con_status_no_valido(self):
        self.replace(os.path.join("warp", "USERS.md"), "| `active` |", "| `baja` |")
        self.assert_error("status 'baja' no válido")

    def test_usuario_duplicado(self):
        row = "| `usuario-ejemplo` | `Persona de ejemplo` | `active` |\n"
        self.replace(os.path.join("warp", "USERS.md"), row, row + row)
        self.assert_error("github duplicado 'usuario-ejemplo'")

    def test_sin_participantes_activos(self):
        self.replace(os.path.join("warp", "USERS.md"), "| `active` |", "| `inactive` |")
        self.assert_error("no hay ningún participante active")

    def test_falta_governance(self):
        shutil.rmtree(os.path.join(self.root, "warp", "threads", "governance"))
        self.replace(os.path.join("warp", "index", "THREAD_INDEX.md"),
                     "| `governance` |", "| `x` |")
        self.assert_error("exactamente un THREAD 'governance' (hay 0)")

    def test_governance_archivado(self):
        gov = os.path.join("warp", "threads", "governance", "MANIFEST.md")
        self.replace(gov, "status: ACTIVE", "status: ARCHIVED")
        self.replace(os.path.join("warp", "index", "THREAD_INDEX.md"),
                     "| `governance` | `ACTIVE` |", "| `governance` | `ARCHIVED` |")
        self.assert_error("governance no puede estar ARCHIVED")

    def test_governance_sin_autoridad_sobre_users(self):
        self.replace(os.path.join("warp", "threads", "governance", "MANIFEST.md"),
                     "- `warp/USERS.md`\n", "")
        self.assert_error("governance debe tener autoridad sobre 'warp/USERS.md'")

    def test_otro_hilo_reclama_configuracion(self):
        self.replace(os.path.join(THREAD, "MANIFEST.md"),
                     "- `warp/corpus/NOTES.md`\n",
                     "- `warp/corpus/NOTES.md`\n- `warp.yaml`\n")
        self.assert_error("'warp.yaml' es configuración del proyecto")

    def test_documento_del_corpus_sin_indexar(self):
        with open(os.path.join(self.root, "warp", "corpus", "HUERFANO.md"), "w",
                  encoding="utf-8") as f:
            f.write("# huérfano\n")
        self.assert_error("falta el documento del corpus 'warp/corpus/HUERFANO.md'")

    def test_gitkeep_en_el_corpus_no_es_un_documento(self):
        open(os.path.join(self.root, "warp", "corpus", ".gitkeep"), "w").close()
        code, out = self.run_checker()
        self.assertEqual(code, 0, out)

    def test_enforcement_no_valido(self):
        self.replace("warp.yaml", "enforcement: advisory", "enforcement: total")
        self.assert_error("enforcement 'total' no válido")

    def test_owner_desconocido_advisory_avisa(self):
        self.replace(os.path.join(THREAD, "MANIFEST.md"),
                     "owner: usuario-ejemplo", "owner: alguien")
        code, out = self.run_checker()
        self.assertEqual(code, 0, out)
        self.assertIn("[WARN]  warp/threads/example-notes/MANIFEST.md: owner 'alguien' no figura", out)

    def test_owner_desconocido_strict_falla(self):
        self.replace("warp.yaml", "enforcement: advisory", "enforcement: strict")
        self.replace(os.path.join(THREAD, "MANIFEST.md"),
                     "owner: usuario-ejemplo", "owner: alguien")
        self.assert_error("owner 'alguien' no figura en warp/USERS.md")

    def add_inactive_user(self):
        self.replace(os.path.join("warp", "USERS.md"),
                     "| `usuario-ejemplo` | `Persona de ejemplo` | `active` |\n",
                     "| `usuario-ejemplo` | `Persona de ejemplo` | `active` |\n"
                     "| `antiguo` | `Persona que se fue` | `inactive` |\n")
        self.replace(os.path.join(THREAD, "MANIFEST.md"),
                     "owner: usuario-ejemplo", "owner: antiguo")

    def test_owner_inactivo_en_hilo_activo(self):
        self.replace("warp.yaml", "enforcement: advisory", "enforcement: strict")
        self.add_inactive_user()
        self.assert_error("owner 'antiguo' no está active")

    def test_owner_inactivo_en_hilo_archivado_es_valido(self):
        self.replace("warp.yaml", "enforcement: advisory", "enforcement: strict")
        self.add_inactive_user()
        self.replace(os.path.join(THREAD, "MANIFEST.md"),
                     "status: ACTIVE", "status: ARCHIVED")
        self.replace(os.path.join("warp", "index", "THREAD_INDEX.md"),
                     "| `example-notes` | `ACTIVE` |", "| `example-notes` | `ARCHIVED` |")
        code, out = self.run_checker()
        self.assertEqual(code, 0, out)

    def test_documento_index_fuera_del_corpus(self):
        self.replace(os.path.join("warp", "index", "DOCUMENT_INDEX.md"),
                     "| `warp/corpus/NOTES.md` |", "| `warp/USERS.md` |")
        self.assert_error("'warp/USERS.md' no pertenece al corpus")


if __name__ == "__main__":
    unittest.main()
