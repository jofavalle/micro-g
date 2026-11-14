---
name: revisar-pr
description: Revisa el PR de una orden antes de fusionarlo, contra la orden y su criterio de aceptación. Úsala cuando haya que revisar, aprobar o fusionar un PR, o mirar la cola de revisión.
---

# Revisar un PR

Lo mecánico ya lo comprobó quien ejecutó la orden; quien revisa se queda con lo que exige juicio.

1. **La cola**: `gh pr list`. Con tres o más esperando, se revisa antes de publicar órdenes
   nuevas.
2. **Contra la orden**: `gh pr view N` y la issue que cierra. ¿Hace lo que pide, y nada de lo
   que dice "no tocar"?
3. **La evidencia**: la salida del criterio de aceptación tiene que estar en el PR, literal. Si
   hay dudas, se repite el comando en su rama (`gh pr checkout N`) y se compara.
4. **El diff entero**: `gh pr diff N`. Sobre todo lo que exige juicio: cifras, unidades, lo que
   dice el modelo. Y que no entren claves, rutas personales ni archivos de cada uno. Los checks
   de CI, en verde: `gh pr checks N`.
5. **Redactar, no publicar**: Claude escribe la revisión y se la enseña a la persona, que la lee
   entera. Claude no la publica por su cuenta (`gh pr comment`, `gh pr review`): la publica la
   persona, o Claude con su OK después de leerla. La revisión termina con la herramienta y el
   modelo, y con que la persona la leyó antes de publicarla.
6. **Decidir**: si falta algo, se comenta en el PR qué, de forma concreta, para que se corrija
   en la misma rama. Si todo cuadra, Claude lo dice y nada más: no aprueba ni fusiona. La
   persona aprueba en GitHub: en la pestaña "Files changed", botón "Review changes" (en algunas
   versiones de la interfaz, "Submit review"), marca la opción "Approve" y pulsa
   "Submit review". Con la opción "Comment" marcada no se aprueba, aunque el texto diga
   "Approve": el PR tiene que mostrar "Approved". Después fusiona desde la pestaña
   "Conversation", con "Merge pull request" y "Confirm merge".
