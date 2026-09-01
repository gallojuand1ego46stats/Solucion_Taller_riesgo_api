# Dictamen sobre `ia_propuesta.py` — Parte D

**Grupo:** <DA> · **Integrantes:** <Juan David Parada Fonseca>, <Juan Diego Gallo Quintero>, <David Santiago Sanchez Guarnizo>

> Tres defectos. Las cuatro secciones de cada uno son obligatorias y se parsean.
> El peso está en **«Cómo lo comprobamos»**: afirmar que algo está mal no vale;
> demostrarlo, sí.

## Defecto 1

- **Qué está mal:** El validador `redondear_monto` calcula `round(v, 2)` pero no lo retorna, así que la función devuelve `None` implícitamente. Pydantic reemplaza el valor del campo `monto` con ese `None`.
- **Por qué es un defecto** (módulo · sección): M4 · 6. Validadores de campo — un `field_validator` debe retornar el valor validado o transformado; omitir el `return` corrompe el campo en vez de limpiarlo.
- **Cómo lo comprobamos:**

```python
python3 -c "from ia_propuesta import SolicitudPuntuacion; s = SolicitudPuntuacion(poliza='POL-20260001', correo_analista='ana@aseguradora.com', monto=1000.567, antiguedad=5, siniestros_previos=1); print(s.monto)"
```
- **Corrección:** Agregar `return round(v, 2)` al final de la función.

## Defecto 2

- **Qué está mal:** `_puntuar` usa `time.sleep(0.2)` (bloqueante) dentro de una función `async def`, así que `evaluar_lote` no ejecuta las tareas en paralelo pese a usar `asyncio.gather`.
- **Por qué es un defecto** (módulo · sección): M5 · 8. Resumen y mejores prácticas — "Usar `async def` para tareas CPU-bound sin executor" / un bloqueante dentro de una corrutina congela el bucle de eventos completo.
- **Cómo lo comprobamos:**

```python
import asyncio, time
from ia_propuesta import evaluar_lote, SolicitudPuntuacion

sols = [SolicitudPuntuacion(poliza='POL-20260001', correo_analista='ana@aseguradora.com', monto=1000, antiguedad=5, siniestros_previos=i) for i in range(5)]
t0 = time.perf_counter()
asyncio.run(evaluar_lote(sols))
print(f'tiempo total: {time.perf_counter() - t0:.2f}s')
```

- **Corrección:** Reemplazar `time.sleep(0.2)` por `await asyncio.sleep(0.2)` (o, si simulara una llamada HTTP real, usar `httpx.AsyncClient`).

## Defecto 3

- **Qué está mal:** El patrón regex de `correo_analista` (`\.[A-Za-z]{2,3}$`) no admite dominios con más de un punto (subdominios), rechazando correos institucionales válidos como los de `.edu.co`.
- **Por qué es un defecto** (módulo · sección): M4 · 6. Validadores de campo — una validación demasiado restrictiva rechaza datos válidos de negocio.
- **Cómo lo comprobamos:**

```python
from ia_propuesta import SolicitudPuntuacion
s = SolicitudPuntuacion(poliza='POL-20260001', correo_analista='ana@usantotomas.edu.co', monto=1000, antiguedad=5, siniestros_previos=1)
```

- **Corrección:** Usar un patrón más permisivo, ej. `r"^[A-Za-z0-9_.+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"` (permite subdominios y dominios de 2+ letras).