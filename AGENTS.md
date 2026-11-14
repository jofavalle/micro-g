# Instrucciones para asistentes de IA

Este archivo es para los asistentes que no son Claude Code (Codex, OpenCode, Devin u otros).
Claude Code lee `CLAUDE.md` por su cuenta.

1. **Lee `CLAUDE.md` antes de trabajar.** Son las reglas del equipo, valen para cualquier
   asistente y mandan sobre lo que diga este archivo.
2. **Las skills de `.claude/skills/`** (`tomar-orden`, `relevo` y `revisar-pr`) son comandos de
   Claude Code. Con otro asistente, lee su `SKILL.md` y sigue los pasos con las herramientas que
   tengas; no supongas que esos comandos existen.
3. **Las denegaciones de `.claude/settings.json` solo las aplica Claude Code.** Contigo no hay
   esa red: lo de "Lo que no se hace" en `CLAUDE.md` rige igual, y quien te usa revisa cada
   orden antes de aprobarla.
4. **Una orden por sesión**, en su rama y sin tocar nada fuera de su alcance.
5. **Ningún commit sin enseñar antes el diff y la evidencia** a la persona que te usa. Ni
   subagentes ni tareas en paralelo, salvo que esa persona los pida: gastan su cuota.
6. **No leas secretos** (`.env` y parecidos) ni los copies a ningún archivo.
