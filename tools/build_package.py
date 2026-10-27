#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Warp: genera el paquete descargable de una versión del método.

  python tools/build_package.py [--out <carpeta>]

Crea `warp-<versión>.zip` (por defecto en `dist/`) con una sola carpeta,
`warp/`: el método (`warp/core/`, `warp/scripts/`, `warp/VERSION`) y sus dos
licencias. Es lo que se descomprime en la carpeta de un proyecto antes de
ejecutar el instalador.

Se empaqueta lo versionado en Git, no el disco: así el paquete corresponde a
un commit concreto y no arrastra archivos locales. Herramienta de la
distribución: no forma parte del método y no se instala.
"""

import argparse
import os
import subprocess
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LICENSES = ("LICENSE-DOCS", "LICENSE-CODE")


def git(*args):
    p = subprocess.run(["git", "-C", ROOT] + list(args), stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    if p.returncode != 0:
        sys.exit("ERROR: git %s\n%s" % (" ".join(args), p.stderr.decode("utf-8", "replace")))
    return p.stdout


def main(argv):
    parser = argparse.ArgumentParser(prog="build_package.py",
                                     description="Genera el paquete descargable de Warp.")
    parser.add_argument("--out", default=os.path.join(ROOT, "dist"),
                        help="carpeta de salida (por defecto, dist/)")
    args = parser.parse_args(argv[1:])

    dirty = git("status", "--porcelain", "--", "warp", *LICENSES).decode().strip()
    if dirty:
        sys.exit("ERROR: hay cambios sin commit en warp/ o en las licencias:\n" + dirty)
    version = git("show", "HEAD:warp/VERSION").decode().strip()
    files = [f for f in git("ls-files", "-z", "--", "warp").decode().split("\0") if f]

    os.makedirs(args.out, exist_ok=True)
    target = os.path.join(args.out, "warp-%s.zip" % version)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        for path in sorted(files):
            # Contenido del commit, con finales de línea LF.
            z.writestr(path, git("show", "HEAD:" + path))
        for name in LICENSES:
            z.writestr("warp/" + name, git("show", "HEAD:" + name))
    print("Paquete: %s (%d archivos, versión %s, commit %s)" %
          (target, len(files) + len(LICENSES), version,
           git("rev-parse", "--short", "HEAD").decode().strip()))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
