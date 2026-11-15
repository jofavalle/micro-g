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
integrantes pasaron la comprobación del primer día (#1). Todavía no hay idea, enfoque ni código
del producto.

## Siguiente paso

- **Planificación principal del producto, en la próxima sesión.** El equipo discute el
  producto, el enfoque y la idea de solución, y lo que decida se escribe en una issue antes de
  abrir órdenes. La idea la pone el equipo: Claude ayuda a ordenar la discusión y a convertir
  las decisiones en órdenes, pero no la propone (ver "Reglas del reto" en `CLAUDE.md`).
- **Con la idea decidida:** el stack y el servicio de despliegue, con su archivo local de claves
  en el `.gitignore`, en las denegaciones de `Read` y en la higiene; la `LICENSE` (OSI, la elige
  el equipo) y el `README.md` en inglés; y la primera orden del producto.
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
