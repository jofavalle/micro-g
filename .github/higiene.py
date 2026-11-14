#!/usr/bin/env python3
"""Higiene del repositorio: lo que no debe entrar en un repositorio de equipo.

Se ejecuta antes de abrir un PR y corre en CI en cada push. Sale con 1 si algo falla,
y dice el archivo y, cuando se puede, la línea. Solo usa la biblioteca estándar, y
necesita git.

Sobre los archivos versionados comprueba:

1. que no haya enlaces simbólicos: en el clon de otra persona están rotos, y Git para
   Windows los saca como archivos de texto que contienen la ruta;
2. que no haya archivos de cada uno: CLAUDE.local.md, .env (.env.example sí), y lo
   que Claude Code guarda dentro de .claude/ para una sola persona (la configuración
   local, la memoria local de sus agentes, sus worktrees y su estado de ejecución);
3. que ningún archivo lleve la ruta de un directorio personal (Linux, macOS, Windows,
   la carpeta de la WSL vista desde Windows), tampoco con las barras escapadas de un
   JSON, dentro de un binario ni en un texto en UTF-16. Lo comprimido no se abre;
4. que los textos estén en UTF-8: la Windows PowerShell que trae el sistema guarda
   con '>' en UTF-16, que en un diff no se lee;
5. que la capa del equipo exista: CLAUDE.md y .claude/settings.json.

Uso:  python3 .github/higiene.py      (en Windows: py .github/higiene.py)
"""

import re
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# El comienzo de la ruta de un directorio personal: la carpeta de los usuarios y la
# primera letra del nombre, sin exigir barra final ni mirar cómo sigue (un nombre de
# Windows puede llevar espacios o tildes). La letra excluye los marcadores de los
# ejemplos, como '$' o '<', y la búsqueda hacia atrás excluye una URL cuyo camino
# pase por una carpeta con ese nombre. La ruta de Windows no la lleva: una letra de
# unidad seguida de la carpeta de usuarios ya es inconfundible, y al quitar los nulos
# de un binario la letra puede quedar pegada a lo que la precedía. Cada nombre de
# carpeta va escrito con una clase de caracteres en medio, para que este archivo no
# case consigo mismo.
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

# Lo que Claude Code guarda dentro de una carpeta .claude/ para una sola persona. Es
# la misma lista que el .gitignore del repositorio.
LOCALES_CLAUDE = {
    "settings.local.json", "agent-memory-local", "worktrees", "checkpoints", "mailbox",
    "scheduled_tasks.lock", "scheduled_tasks.json", "agent-registry.json", "first-run",
    "assistant-daemon-state.json",
}

CAPA = ("CLAUDE.md", ".claude/settings.json")


def git(*args):
    return subprocess.run(
        ["git", *args], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ).stdout


def versionados():
    """(modo, ruta) de cada entrada del índice."""
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
    if nombre == ".env" or (nombre.startswith(".env.") and nombre != ".env.example"):
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
    """Los bytes tal cual y, si llevan bytes nulos, también sin ellos.

    Quitar los nulos convierte el texto en UTF-16 (con o sin marca, en cualquier
    desplazamiento y aunque haya un carácter suelto que no se pueda decodificar) en
    algo que la expresión de arriba sí ve.
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
            problemas.append(f"{ruta}: enlace simbólico versionado (en otro clon está roto)")
            continue
        if es_de_cada_uno(ruta):
            problemas.append(f"{ruta}: es de cada uno y no se versiona (git rm --cached)")
        archivo = Path(raiz, ruta)
        if not archivo.is_file():
            continue
        datos = archivo.read_bytes()

        for linea in lineas_con_ruta(datos):
            if es_texto(ruta):
                problemas.append(f"{ruta}:{linea}: ruta de un directorio personal (usa rutas relativas)")
            else:
                problemas.append(f"{ruta}: ruta de un directorio personal dentro de un binario")
                break

        if es_texto(ruta):
            if datos.startswith((b"\xff\xfe", b"\xfe\xff")):
                problemas.append(f"{ruta}: texto en UTF-16 (guárdalo en UTF-8; en Windows, desde PowerShell 7)")
            elif b"\0" in datos:
                problemas.append(f"{ruta}: texto con bytes nulos, probablemente UTF-16 sin marca (guárdalo en UTF-8)")
            else:
                try:
                    datos.decode("utf-8")
                except UnicodeDecodeError as error:
                    problemas.append(f"{ruta}: no está en UTF-8 (byte {error.start})")

    for ruta in CAPA:
        if ruta not in rutas:
            problemas.append(f"{ruta}: falta la capa del equipo")

    for problema in problemas:
        print(problema)
    if problemas:
        print(f"\nhigiene: {len(problemas)} problemas en {len(rutas)} archivos versionados")
        return 1
    print(f"higiene en orden: {len(rutas)} archivos versionados")
    return 0


if __name__ == "__main__":
    sys.exit(main())
