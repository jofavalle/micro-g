# micro-g

Team project for the NASA Space Apps Challenge 2026, Flame in Freefall challenge, San Salvador local event.

Esta capa (`CLAUDE.md`, `BITACORA.md` y `.claude/`) se versiona y es la misma para todo el
equipo: un cambio en ella se propone por PR, como cualquier otro. Lo de cada uno va en
`CLAUDE.local.md` o en `.claude/settings.local.json`, que no se versionan.

## Comandos

- Ejecutar: todavía no hay producto; lo añade aquí el PR que cree el primero.
- Verificar: `python3 .github/higiene.py` (en Windows, `py .github/higiene.py`)
- Higiene del repositorio: `python3 .github/higiene.py` (en Windows, `py .github/higiene.py`).
  Corre también en CI en cada push y en cada PR.
- Tablero: `gh issue list --label orden`. Cola de revisión: `gh pr list`.

**La puerta de verificación es `python3 .github/higiene.py`** (en Windows,
`py .github/higiene.py`).

## Convenciones

### Cómo se trabaja: órdenes, ramas y PR

- **Una orden es una issue** con la etiqueta `orden` y la plantilla de `.github/ISSUE_TEMPLATE/`.
  Tiene que bastar por sí sola: quien la ejecuta no estuvo cuando se decidió, y su sesión de
  Claude tampoco. Su estado va en etiquetas: `lista`, `en-curso` y `en-revision`.
- **Una orden se nombra por el número de su issue**, `#N`, y no por una numeración propia:
  issues y PR comparten numeración en GitHub, y una "OT-02" escrita a mano acabaría siendo la
  issue #3.
- **Una orden por sesión.** Al terminar, `/clear` o una sesión nueva. Para tomarla y devolverla
  está `/tomar-orden`; para dejarla a medias, `/relevo`; para revisar un PR, `/revisar-pr`.
- **Una rama por orden**, `<usuario>/orden-N`, desde `main` recién actualizado. A `main` no se
  escribe directamente: todo entra por PR.
- **El PR lleva evidencia** (`.github/pull_request_template.md`): el comando del criterio de
  aceptación con su salida literal, y el uso de IA. Cierra su orden con `Closes #N`, en inglés:
  GitHub no reconoce "Cierra #N", y la orden se quedaría abierta.
- **Trabajo abierto limitado:** una orden en curso por persona, y como mucho tres PR esperando
  revisión. Con la cola llena no se empieza otra orden: se prueba lo publicado.
- **Lo que se acuerda de palabra se escribe en la issue.** La sesión de Claude y quien haga un
  relevo no lo oyeron.

### Lo que no se hace

- `git add -A` ni `git add .`: los archivos se añaden por nombre, después de leer el diff.
- Commit sin que la persona haya leído el diff: por eso `git commit` pide permiso a propósito, y
  no se añade a la lista de lo permitido. En modo auto, la pregunta la garantiza la regla ask de
  `.claude/settings.json`, que también cubre `git push` y `gh pr review`.
- Que Claude apruebe o fusione un PR: fusionar lo hace siempre una persona desde GitHub, después
  de aprobar. `gh pr merge` está denegado, pero fusionar por otra vía (como `gh api`) no lo
  está, y la regla vale igual.
- Borrados (`rm -r`, `git reset --hard`, `git clean`, `git branch -D`) ni `git push --force`.
  Si alguno hace falta, lo ejecuta una persona. `.claude/settings.json` niega sus formas
  habituales, pero es una red y no una garantía: la misma orden escrita de otra manera puede
  pasar, y la regla vale igual.
- Claves en el código: van en `.env`, que no se versiona. Si hace falta una plantilla, se
  versiona `.env.example`, sin claves reales.
- Rutas absolutas de un directorio personal: siempre rutas relativas. La higiene las rechaza.
- Que el modelo lea datos enteros: un script los resume, y el modelo lee el resumen.

### Fuentes, licencias e IA

- Todo dato, código o texto de terceros se cita en el README, con su licencia.
- El uso de IA se declara en cada PR: qué se pidió, con qué herramienta y modelo, y qué se
  corrigió. Las órdenes y sus PR son el registro. Los commits no llevan atribución a la
  herramienta (`attribution` vacío en `.claude/settings.json`): la declaración va en el PR.

### Del proyecto

- **Commits y títulos de PR, en inglés** (2026-11-14), un cambio lógico por commit. El
  repositorio será material enlazado de la entrega (ver "Reglas del reto"), y su portada muestra
  junto a cada archivo el mensaje del último commit que lo tocó. Issues, cuerpos de PR y
  revisiones siguen en español.
- **Solo merge commit, sin squash ni rebase** (2026-11-14; GitHub lo impone). Un squash pondría
  el título del PR como mensaje en `main`, y el merge commit lleva ese título en su cuerpo,
  porque GitHub no admite dejarlo vacío: por eso el título del PR va en inglés.

#### Reglas del reto

Resumen propio de las reglas oficiales de Space Apps 2026 que condicionan el trabajo. Ante la
duda, manda la fuente que cita cada punto; sus URL van al final de esta lista.

- **La idea de la solución la pone el equipo.** La IA está permitida como herramienta, pero la
  guía de entrega dice que no se use para "come up with your idea of how to solve the
  challenge". Si se le pide esa idea, Claude se detiene y remite al equipo; ayudar a construir
  la idea que el equipo ya trae sí vale. [Submission Guide][entrega]
- **Lo generado con IA se marca dentro del proyecto.** Código, datos y audio, en el texto
  descriptivo y en los metadatos; imágenes y videos, con una marca de agua visible.
  [Submission Guide][entrega] La convención del equipo:
  - en cada archivo de código generado o asistido, una línea de cabecera en inglés, con la
    sintaxis de comentario del lenguaje:
    `AI-assisted: <tool> (<model>), reviewed by <github-user>`;
  - en los datos generados, un campo de metadatos con lo mismo;
  - en los archivos que no admiten comentarios, como un JSON, la marca va en `ai-log/` y en el
    PR;
  - y siempre, la sección "Uso de IA" del PR y una fila en `ai-log/`.
- **Nada de marca de NASA en lo generado**: ni logos, ni banderas, ni identificadores de misión.
  [Submission Guide][entrega], [NASA Brand Guidelines][marca]
- **Inglés en la página del proyecto y en todo lo enlazado**: README, interfaz, documentación
  del producto y diapositivas; un video puede hablarse en otro idioma con subtítulos en inglés.
  El repositorio también es material enlazado: el código y sus comentarios van en inglés desde
  el principio, y esta capa se traduce antes de publicarlo. [Judging Guide][evaluacion],
  [Submission Guide][entrega]
- **Todo se cita, también lo abierto**: código, texto, imágenes, datos y herramientas. Lo que no
  es de NASA va con su licencia, y nada con copyright sin permiso. Lo original del proyecto
  queda bajo una licencia OSI (si no se especifica, NASA lo distribuye bajo Apache 2.0); lo de
  terceros tiene que ser libre o tener licencia OSI; y los datos de un sitio que no es del
  gobierno de EE. UU. se usan con las condiciones de ese sitio. [Terms and Conditions][tyc],
  [Judging Guide][evaluacion], [Resources del reto][recursos]
- **Al menos un dato o recurso de NASA**: sin él no se opta a un premio global.
  [Submission Guide][entrega]
- **Lo que no se incluye**: información personal identificable; el nombre, la imagen o la voz
  reconocibles de un menor de 18 años; información propietaria; información sujeta a control
  de exportaciones, como la de ITAR o la de EAR; ni material que promocione servicios o
  productos comerciales. Nadie participa en relación con una afiliación a China o a una
  entidad de propiedad china. [Terms and Conditions][tyc], [Judging Guide][evaluacion] Como
  lectura prudente del equipo, que no es texto literal de las reglas: tampoco se usan servicios
  de empresas de propiedad china.
- **Los enlaces se abren sin contraseña, login, permisos ni registro**, y lo publicado tiene que
  seguir funcionando hasta el anuncio de los ganadores globales, el 26 de enero de 2027. Ninguna
  clave va en el repositorio, que será público, ni en el código que llega al navegador; un
  servicio externo con clave necesita límite de gasto y una clave que no caduque antes de esa
  fecha. [Submission Guide][entrega], [Judging Guide][evaluacion]
- **El demo**: un video de 30 segundos o menos, o hasta siete diapositivas contando la portada y
  la introducción. Pasarse de cualquiera de los dos límites deja el proyecto fuera de la
  evaluación global. [Submission Guide][entrega]

[entrega]: https://www.spaceappschallenge.org/resources/project-submission-guide/
[evaluacion]: https://www.spaceappschallenge.org/resources/judging-awards-guide/
[tyc]: https://www.spaceappschallenge.org/legal/
[recursos]: https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/?tab=resources
[marca]: https://www.nasa.gov/nasa-brand-center/brand-guidelines/

## Gotchas

- En Windows se trabaja en PowerShell 7, no en la Windows PowerShell que trae el sistema: esa
  guarda con `>` en UTF-16, y la higiene lo rechaza. Se instala con
  `winget install --id Microsoft.PowerShell --source winget`.
- En Windows, Claude Code ejecuta con la herramienta PowerShell cuando no hay Git para Windows,
  y con Git instalado la tiene junto a Bash ([instalación][cc-instalacion]). Sus permisos son
  reglas `PowerShell(...)` aparte ([permisos][cc-permisos]), y la documentación no dice que una
  regla `Bash(...)` la cubra: toda denegación de `.claude/settings.json` se escribe en las dos
  formas. Con otros asistentes no hay esa red, y lo de "Lo que no se hace" vale igual.
- En Windows, `python3` a secas puede abrir el alias de la Microsoft Store en vez de Python: se
  usa `py`.

[cc-instalacion]: https://code.claude.com/docs/en/setup#install-on-native-windows
[cc-permisos]: https://code.claude.com/docs/en/permissions#powershell
