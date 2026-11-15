#!/usr/bin/env python3
# AI-assisted: Claude Code (claude-opus-5-5), reviewed by jofavalle, cesarp03, PabloBernal-CPU
"""Repository hygiene: what must not get into a team repository.

Run it before opening a PR; it also runs in CI on every push. It exits with 1 if
anything fails, and names the file and, when it can, the line. It uses only the
standard library, and needs git.

On the tracked files it checks:

1. that there are no symbolic links: in someone else's clone they are broken, and Git
   for Windows checks them out as text files that contain the target path;
2. that there are no personal files: CLAUDE.local.md, secrets files (.env, .dev.vars
   and .streamlit/secrets.toml; their .example templates are allowed), and what Claude
   Code keeps inside .claude/ for a single person (the local settings, the local
   memory of its agents, its worktrees and its runtime state);
3. that no file contains the path of a personal directory (Linux, macOS, Windows,
   the WSL folder seen from Windows), not even with the escaped slashes of a JSON,
   inside a binary or in a UTF-16 text. Compressed files are not opened;
4. that text files are UTF-8: the Windows PowerShell that ships with the system saves
   with '>' in UTF-16, which cannot be read in a diff;
5. that the team layer exists: CLAUDE.md and .claude/settings.json.

Usage:  python3 .github/higiene.py      (on Windows: py .github/higiene.py)
"""

import re
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# The start of a personal directory path: the users folder and the first letter of the
# name, without requiring a trailing slash or looking at what follows (a Windows name
# may contain spaces or accents). The letter excludes the placeholders of examples,
# such as '$' or '<', and the lookbehind excludes a URL whose path goes through a
# folder with that name. The Windows path has no lookbehind: a drive letter followed
# by the users folder is already unmistakable, and once the nulls of a binary are
# stripped the letter may end up stuck to whatever preceded it. Each folder name is
# written with a character class in the middle, so that this file does not match
# itself.
LETRA = rb"[A-Za-z0-9_\x80-\xff]"
HOGARES = re.compile(
    rb"(?<![\w.-])\\?/h[o]me\\?/" + LETRA
    + rb"|(?<![\w.-])\\?/U[s]ers\\?/" + LETRA
    + rb"|/mnt/[a-z]/U[s]ers/" + LETRA
    + rb"|(?i:[a-z]:[\\/]+u[s]ers[\\/]+)" + LETRA
    + rb"|(?i:\\\\wsl(?:\.localhost|\$)\\[^\\\r\n]+\\h[o]me\\)" + LETRA
)

TEXTO = {
    ".md", ".txt", ".py", ".ipynb", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx",
    ".json", ".html", ".htm", ".css", ".yml", ".yaml", ".toml", ".csv", ".tsv",
    ".sh", ".ps1", ".sql", ".r", ".tex", ".bib", ".svg", ".xml", ".ini", ".cfg",
}
TEXTO_POR_NOMBRE = {".gitignore", ".gitattributes", ".env.example", "LICENSE", "README"}

# What Claude Code keeps inside a .claude/ folder for a single person. It is the same
# list as the repository's .gitignore.
LOCALES_CLAUDE = {
    "settings.local.json", "agent-memory-local", "worktrees", "checkpoints", "mailbox",
    "scheduled_tasks.lock", "scheduled_tasks.json", "agent-registry.json", "first-run",
    "assistant-daemon-state.json",
}

# Secrets files. The same ones the .gitignore ignores: if one gets in with git add -f,
# the hygiene check stops it. Those in the first list allow variants (.env.local) and
# an .example template without real secrets; those in the second only count in their
# folder.
CLAVES = (".env", ".dev.vars")
CLAVES_EN_CARPETA = {(".streamlit", "secrets.toml")}

CAPA = ("CLAUDE.md", ".claude/settings.json")


def git(*args):
    return subprocess.run(
        ["git", *args], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ).stdout


def versionados():
    """(mode, path) of each index entry."""
    salida = git("ls-files", "-s", "-z")
    for entrada in salida.split(b"\0"):
        if not entrada:
            continue
        cabecera, ruta = entrada.split(b"\t", 1)
        yield cabecera.split(b" ")[0].decode(), ruta.decode("utf-8", "surrogateescape")


def es_de_cada_uno(ruta):
    partes = ruta.split("/")
    nombre = partes[-1]
    if nombre == "CLAUDE.local.md":
        return True
    for clave in CLAVES:
        if nombre == clave or (nombre.startswith(clave + ".") and nombre != clave + ".example"):
            return True
    if len(partes) >= 2 and (partes[-2], nombre) in CLAVES_EN_CARPETA:
        return True
    for i, parte in enumerate(partes[:-1]):
        if parte != ".claude":
            continue
        siguiente = partes[i + 1]
        if siguiente in LOCALES_CLAUDE:
            return True
        if siguiente == "routines" and len(partes) > i + 2 and partes[i + 2] == ".state":
            return True
    return False


def es_texto(ruta):
    nombre = ruta.rsplit("/", 1)[-1]
    return Path(nombre).suffix.lower() in TEXTO or nombre in TEXTO_POR_NOMBRE


def lecturas(datos):
    """The bytes as they are and, if they contain null bytes, also without them.

    Stripping the nulls turns UTF-16 text (with or without a BOM, at any offset and
    even with a stray character that cannot be decoded) into something the expression
    above does see.
    """
    yield datos
    if b"\0" in datos:
        yield datos.replace(b"\0", b"")


def lineas_con_ruta(datos):
    vistas = set()
    for lectura in lecturas(datos):
        for coincidencia in HOGARES.finditer(lectura):
            vistas.add(lectura.count(b"\n", 0, coincidencia.start()) + 1)
    return sorted(vistas)


def main():
    raiz = git("rev-parse", "--show-toplevel").decode().strip()
    problemas = []
    rutas = []

    for modo, ruta in versionados():
        rutas.append(ruta)
        if modo == "120000":
            problemas.append(f"{ruta}: tracked symbolic link (broken in another clone)")
            continue
        if es_de_cada_uno(ruta):
            problemas.append(f"{ruta}: personal file, must not be tracked (git rm --cached)")
        archivo = Path(raiz, ruta)
        if not archivo.is_file():
            continue
        datos = archivo.read_bytes()

        for linea in lineas_con_ruta(datos):
            if es_texto(ruta):
                problemas.append(f"{ruta}:{linea}: personal directory path (use relative paths)")
            else:
                problemas.append(f"{ruta}: personal directory path inside a binary")
                break

        if es_texto(ruta):
            if datos.startswith((b"\xff\xfe", b"\xfe\xff")):
                problemas.append(f"{ruta}: UTF-16 text (save it as UTF-8; on Windows, from PowerShell 7)")
            elif b"\0" in datos:
                problemas.append(f"{ruta}: text with null bytes, probably UTF-16 without a BOM (save it as UTF-8)")
            else:
                try:
                    datos.decode("utf-8")
                except UnicodeDecodeError as error:
                    problemas.append(f"{ruta}: not UTF-8 (byte {error.start})")

    for ruta in CAPA:
        if ruta not in rutas:
            problemas.append(f"{ruta}: team layer missing")

    for problema in problemas:
        print(problema)
    if problemas:
        print(f"\nhygiene: {len(problemas)} problems in {len(rutas)} tracked files")
        return 1
    print(f"hygiene ok: {len(rutas)} tracked files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
