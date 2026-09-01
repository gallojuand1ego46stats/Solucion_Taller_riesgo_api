# Bitácora de uso de IA

**Grupo:** <DA> · **Integrantes:** <Juan David Parada Fonseca>, <Juan Diego Gallo Quintero>, <David Santiago Sanchez Guarnizo>
**Herramientas usadas:** Claude (Anthropic)

> Las tres secciones son obligatorias. **`## Rechazado` es la que se califica.**
> Una bitácora que solo lista prompts aceptados vale la mitad.

## Prompts

| # | Parte | Quién | Prompt (resumido si es largo) |
|---|-------|-------|-------------------------------|
| 1 | A | Juan David | Pedir ayuda para diagnosticar defectos del repo semilla, endpoint por endpoint, con evidencia reproducible |
| 2 | A | Juan David | Identificar a qué sección del material del curso (M1-M5) corresponde cada hallazgo encontrado |
| 3 | B | Juan David | Corregir cada restricción (B1-B9) una por una, explicando el cambio antes de aplicarlo |
| 4 | C | Juan David | Ayudar a interpretar las mediciones de `medir.py` y decidir clasificación/decisión de cada endpoint |
| 5 | D | Juan David | Auditar `ia_propuesta.py` en busca de los 3 defectos de comportamiento, con comprobación ejecutable |
| 6 | E | Juan David | Armar la bitácora de uso de IA con base en las decisiones tomadas durante la sesión |

## Aceptado

| # | Qué propuso la IA | Por qué lo aceptamos | Qué cambiamos antes de usarlo |
|---|-------------------|----------------------|-------------------------------|
| 1 | Usar `BaseModel` de Pydantic con `Field` y `field_validator` para reemplazar la validación manual con `if`/`assert` en `/score` | Resuelve B2 y B5 a la vez, y es justo la validación declarativa que exige el curso (M4) | Se ajustaron los nombres de campos para que coincidieran con el payload real del endpoint |
| 2 | Mover la carga del modelo (`pickle.load`) a nivel de módulo, en una variable global `MODELO` | Resuelve B6 sin cambiar el contrato de `EvaluadorRiesgo` ni de las rutas | Ninguno, se aplicó tal cual |
| 3 | Usar `ProcessPoolExecutor` con `run_in_executor` para `/calculo-pesado` | Es CPU-bound; los hilos no ayudan por el GIL, hacía falta paralelismo real de procesos | Se fijó `max_workers=4` según los núcleos disponibles en la máquina |
| 4 | Mover `API_KEY` y `CLAVE_FIRMA` a variables de entorno con `python-dotenv` | Resuelve el hallazgo de secretos versionados sin romper el resto del servicio | Se agregó `.env` al `.gitignore` para no subirlo por accidente |

## Rechazado

| # | Qué propuso la IA | Por qué lo rechazamos | Qué hicimos en su lugar |
|---|-------------------|-----------------------|-------------------------|
| 1 | Citar `M1 · 3. Entornos virtuales: venv frente a conda` para el hallazgo de `requirements.txt` sin versiones fijadas | Al revisar el índice real del Módulo 2, encontramos una sección más específica y precisa sobre el mismo archivo | Se citó `M2 · 5. requirements.txt y la reproducibilidad` en su lugar |
| 2 | Declarar `/servicio-externo` como `async def` (dejarlo igual) al analizar el código, antes de medir | Medir con concurrencia 20 mostró 15.3s de tiempo total (peticiones en fila, no en paralelo) — la propuesta inicial no se sostenía con evidencia | Se cambió el handler a `def` (sin async), y remedido bajó a 0.96s con concurrencia 20 |
| 3 | Dejar el hallazgo H7 (`/health` ausente) sin ninguna cita de módulo, apoyándose solo en la confirmación verbal del profesor | Preferimos verificar contra el material real antes de conformarnos con "no aplica" | Se revisó el índice del Módulo 5 y se encontró una cita real y verificable ("8. Resumen y mejores prácticas") que sí menciona la práctica de incluir `/health` |