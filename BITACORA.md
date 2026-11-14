# Bitácora de micro-g

Estado del proyecto entre sesiones, para todo el equipo. Se versiona y la escribe quien
coordina, por PR como todo lo demás. El estado de cada tarea no va aquí: vive en las issues y
en sus PR. **Se mantiene corta a propósito**: lo que deje de estar vigente se borra, no se
acumula.

## Estado actual

**2026-11-14.**
La capa del equipo recoge las reglas oficiales del reto, las denegaciones para la herramienta
PowerShell y los archivos de claves (#3), y la denegación de `gh pr merge` (#5). El registro
de uso de IA vive en `ai-log/`. Todavía no hay código del producto.

## Siguiente paso

- **Cada integrante comprueba su clon:** abre `claude` en la raíz, mira con `/memory` que carga
  este `CLAUDE.md`, escribe `/` sin Enter para ver que las skills están en la lista, y ejecuta
  la higiene (`py .github/higiene.py` en Windows, `python3 .github/higiene.py` en lo demás),
  que tiene que pasar en su máquina.
- **Cada integrante anota desde hoy su cuota y su uso de IA** en su archivo de `ai-log/`.

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
