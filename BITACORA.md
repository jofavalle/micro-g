# Bitácora de micro-g

Estado del proyecto entre sesiones, para todo el equipo. Se versiona y la escribe quien
coordina, por PR como todo lo demás. El estado de cada tarea no va aquí: vive en las issues y
en sus PR. **Se mantiene corta a propósito**: lo que deje de estar vigente se borra, no se
acumula.

## Estado actual

**2026-11-14, hito de preparación cerrado.**
El repositorio y la capa del equipo están listos: las reglas oficiales del reto, las
denegaciones para PowerShell y los archivos de claves (#3); el registro de uso de IA en
`ai-log/` (#8, #9); la denegación de `gh pr merge` y lo que el modo auto no garantiza antes de
un commit (#5, #7); y el paso de `revisar-pr` que dice cómo se aprueba (#12). Los cuatro
integrantes pasaron la comprobación del primer día (#1).

**2026-11-14, noche: producto decidido y órdenes publicadas.** Todavía no hay código del
producto en `main`.

- **La decisión está en #16**: un dashboard para investigadores e ingenieros sobre las 24
  investigaciones de combustión del repositorio PSI de NASA, ordenadas por tres niveles de
  prioridad que asigna el equipo; una ficha por investigación generada con un LLM antes de
  publicar, con el pasaje literal de cada dato; una capa cuantitativa sobre una sola
  investigación; y una línea de corte entre lo que se entrega pase lo que pase y lo que solo
  entra si lo anterior está publicado el domingo a las 13:00.
- **PSI se consulta sin login**: el buscador, el listado de archivos y la descarga (las
  direcciones están en #21). Son unos 14 TB, y las condiciones de ensayo casi no aparecen en
  los registros: salen de las matrices de ensayos y de los recursos descriptivos de NASA.
- **Exploración**: #17 (guía del investigador y páginas de NASA), #18 (BASS, BASS-II y
  Saffire) y #19 (FLEX, CFI, SAME y DAFT). **Plataforma**: #20, con Cloudflare Pages.
- **Construcción**: #21 (instantánea de PSI), #22 (contrato de datos), #23 (niveles y
  catálogo), #24 (fichas y verificación) y #25 (interfaz).

## Siguiente paso

- **Lo que bloquea el domingo: #21 y #22.** No dependen de nada, y sin ellas no arrancan #23,
  #24 ni #25. Las toma quien quede libre primero.
- **Domingo a las 9:00, en quince minutos:** con los hallazgos de #18 y #19, elegir la
  investigación y la relación física de la capa cuantitativa, escribirlo en #16 y redactar esa
  orden.
- **Órdenes que faltan por redactar:** la cuantitativa, el `README.md` en inglés con las
  fuentes y sus licencias, y la pasada de la capa al inglés.
- **Puntos de #16 sin rellenar:** la pregunta que responde el dashboard, qué ve un juez en 30
  segundos, la licencia, quién hace el demo, quién edita la página del proyecto y de quién es
  la clave del LLM. Este último hace falta antes de #24.
- **Puntos de control del domingo:** a las 13:00, recorrido completo con datos reales en la URL
  publicada; a las 16:00, repositorio público y auditado; a las 18:00, primer envío; a las
  20:00, congelación; a las 22:00, envío final.
- **Lo que no viaja por git:** #24 necesita la clave del LLM en un `.env` local, con el nombre
  `LLM_API_KEY`; #18 y #19 necesitan un `.venv` con lo que declara el `requirements.txt` de su
  carpeta.
- **Cada integrante:** después de cada `git pull`, sesión nueva de Claude Code; y su cuota y su
  uso de IA en `ai-log/`.
- **Plazos.** La entrega cierra el domingo 15 a las 23:59, en la hora del evento local del
  equipo, que es la de San Salvador ([agenda del evento local][agenda];
  [Project Submission Guide][entrega]). Antes de publicar el repositorio: pasar la capa al
  inglés, revisar el historial entero y activar la protección de `main` con una aprobación
  obligatoria, que en un repositorio público es gratuita.

[agenda]: https://www.spaceappschallenge.org/2026/local-events/san-salvador/?tab=schedule
[entrega]: https://www.spaceappschallenge.org/resources/project-submission-guide/

## Decisiones vigentes

- **2026-11-14. La capa de Claude Code se versiona.** `CLAUDE.md`, `BITACORA.md` y `.claude/`
  son del equipo, para que cada sesión arranque con las mismas reglas. Lo de cada uno
  (`CLAUDE.local.md`, `.claude/settings.local.json`) queda fuera por el `.gitignore`.
- **2026-11-14. El repositorio nace privado**, y se hace público solo después de revisar su
  historial entero. En un repositorio público, reescribir el historial no retira nada: GitHub
  sigue sirviendo los commits viejos por SHA.
- **2026-11-14. Ni modelo ni atribución en la capa.** El `.claude/settings.json` del proyecto se
  impone al de cada uno: un modelo fijado ahí obligaría a todas las cuentas, así que cada uno lo
  elige con `/model`. La atribución va vacía y el uso de IA se declara en cada PR.
- **2026-11-14. Commits y títulos de PR en inglés; fusión solo con merge commit.** El
  repositorio será material enlazado de la entrega, que va entera en inglés, y un mensaje de
  commit no se cambia sin reescribir el historial. Issues, cuerpos de PR y revisiones siguen en
  español. El merge commit lleva el título del PR en su cuerpo y GitHub no admite dejarlo
  vacío con la primera línea por defecto (lo rechazó con un 422), así que el título va en
  inglés.
- **2026-11-14. Fusionar es cosa de una persona, después de aprobar.** Claude no aprueba ni
  fusiona (`gh pr merge` está denegado), y en modo auto la regla ask no garantiza que el commit
  pregunte (#4, #6): la red es la revisión humana, con la opción "Approve" marcada antes del
  botón verde (#12). Mientras el repositorio sea privado GitHub no lo impone: de los siete PR
  fusionados el 14 antes de #12, solo #5, #10 y #11 tenían aprobación.
- **2026-11-14. Sitio estático con datos precalculados, en Cloudflare Pages.** El proyecto está
  conectado por Git desde la cuenta de jofavalle, porque Cloudflare solo lista los repositorios
  de quien conecta: cada fusión a `main` se publica sola. Lo que se ve no depende de la función
  de `/api/`, para que siga en pie hasta el 26 de enero de 2027.
- **2026-11-14. El LLM genera las fichas antes de publicar y no decide el orden.** Un solo
  modelo (Gemini, en capa gratuita). Las cifras de las gráficas salen de código; los niveles
  los asigna el equipo a mano; y el dashboard no genera medidas de seguridad ni escenarios.
  Las preguntas en vivo solo entran si lo comprometido está publicado a tiempo (#16).
- **2026-11-14. Los archivos originales de PSI no se versionan**: llevan metadatos con nombres
  de personas. Se versionan los scripts y lo que producen.
