# Hallazgos — Parte A

**Grupo:** <DA> · **Integrantes:** <Juan David Parada Fonseca>, <Juan Diego Gallo Quintero>, <David Santiago Sanchez Guarnizo>

> No borren la fila de ejemplo hasta haber comprobado que su tabla se parsea.
> El formato es rígido: siete columnas, en este orden. Una tabla torcida se
> rechaza indicando la línea, no se «entiende igual».
>
> **Tuberías dentro de una celda:** si su comando lleva `|` —y varios lo llevarán,
> por `grep`, `head` o `jq`— escríbanlo `\|`. Sin escapar, Markdown lo lee como
> separador de columna y su fila pasa a tener ocho.

| ID | Síntoma observable | Causa | Módulo · Sección | SHA donde se observa | Comando de evidencia | Salida obtenida | Corrección aplicada |
|----|--------------------|-------|------------------|----------------------|----------------------|-----------------|---------------------|
| H1 | *(ejemplo de FORMATO, no un defecto de este repositorio)* `GET /ping` responde sin cabecera `Cache-Control` | El handler no declara política de caché | M2 · 2. El protocolo HTTP y la autenticación | `v0-semilla` | `curl -sI localhost:8000/ping \| grep -ci cache-control` | `0` | Se añade la cabecera en la respuesta |
| H2 | `pip install -r requirements.txt` instala versiones no fijadas de cada paquete (ej. fastapi 0.141.1, numpy 2.5.2) | Las dependencias en requirements.txt no especifican versión con `==` | M2 · 5. requirements.txt y la reproducibilidad | v0-semilla | `grep -c "==" requirements.txt` | 0 | Se fijan las versiones exactas en requirements.txt |
| H3 | `GET /siniestros/99999` (siniestro inexistente) responde `200 OK` con un cuerpo `{"error": "no existe el siniestro 99999"}` en vez de `404` | El handler retorna un diccionario de error sin fijar el código de estado HTTP | M2 · 2. El protocolo HTTP y la autenticación | v0-semilla | `curl -s -o /dev/null -w "%{http_code}" localhost:8000/siniestros/99999` | 200 | Se retorna HTTPException(404, ...) cuando el siniestro no existe |
| H4 | `POST /score` con payload `{"monto": 100}` (sin campo `poliza`) responde `200 OK` con `{"error": "falta el campo poliza"}` en vez de `422` | El endpoint recibe un `dict` sin tipar y valida a mano con `if`, sin usar un modelo Pydantic que dispare `ValidationError` | M4 · 7. Del ValidationError al error HTTP 422 | v0-semilla | `curl -s -o /dev/null -w "%{http_code}\n" -X POST localhost:8000/score -H "Content-Type: application/json" -d '{"monto": 100}'` | 200 | Se define un BaseModel para el payload de entrada; ValidationError se traduce a 422 |
| H5 | `POST /score` con `monto: -50` responde `500 Internal Server Error` en vez de `422` | El endpoint valida el monto con un `assert` en vez de una restricción declarativa; el `AssertionError` no se captura y FastAPI lo convierte en 500 | M4 · 7. Del ValidationError al error HTTP 422 | v0-semilla | `curl -s -o /dev/null -w "%{http_code}\n" -X POST localhost:8000/score -H "Content-Type: application/json" -d '{"poliza": "POL-2026-0001", "monto": -50}'` | 500 | Se reemplaza el assert por un Field con restricción gt=0 en el modelo Pydantic |
| H6 | `GET /exportar` responde con `Content-Type: application/octet-stream` (binario serializado con pickle) en vez de JSON | El handler usa `pickle.dumps()` para serializar la respuesta hacia el cliente | M2 · 3. JSON frente a Pickle | v0-semilla | `curl -s -o /dev/null -w "%{content_type}\n" localhost:8000/exportar` | application/octet-stream | Se serializa la respuesta con JSON en vez de pickle |
| H7 | `GET /health` responde `404 Not Found` — el endpoint no existe | El servicio no expone ningún endpoint de verificación de salud/disponibilidad | M5 · 8. Resumen y mejores prácticas | v0-semilla | `curl -s -o /dev/null -w "%{http_code}\n" localhost:8000/health` | 404 | Se crea el endpoint GET /health que responde 200 |
| H8 | El servicio arranca con `uvicorn.run(..., reload=True)`, configuración de desarrollo, no de producción | El código no distingue entre modo desarrollo y producción; `--reload` deja el proceso vulnerable a reinicios en caliente no controlados | M5 · 8. Resumen y mejores prácticas | v0-semilla | `grep -n "reload=True" main.py` | 90:    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) | Se documenta y arranca con `uvicorn main:app --workers N`, sin --reload |
| H9 | El modelo `.pkl` se abre y deserializa dentro del handler de `/score`, en cada petición, en vez de una sola vez al iniciar el servicio | `pickle.load(fh)` está dentro de la función `async def score()`, no a nivel de módulo | M5 · 8. Resumen y mejores prácticas | v0-semilla | `grep -n "pickle.load" main.py` | 29:        modelo = pickle.load(fh) | Se carga el modelo una sola vez al iniciar la app (ej. en un evento de startup o a nivel de módulo) |
| H10 | Dos instancias distintas de `EvaluadorRiesgo` comparten el mismo historial: `EvaluadorRiesgo("POL-B").historial` ve anotaciones hechas por `EvaluadorRiesgo("POL-A")` | `historial = []` está declarado como atributo de clase, no dentro de `__init__`, así que todas las instancias apuntan a la misma lista | M3 · 3. Componentes: atributos de clase | v0-semilla | `pytest tests/test_contrato.py::test_el_historial_no_se_comparte_entre_instancias -v` | `AssertionError: la instancia B ve 1 anotaciones que no hizo` | Se mueve `self.historial = []` dentro de `__init__` |
| H11 | El decorador `con_registro` hace que `puntuar.__name__` sea `"envoltura"` en vez de `"puntuar"`, y un error interno (ej. dato no numérico) se traga silenciosamente devolviendo `puntaje: null` con status 200 | El decorador no usa `functools.wraps`, y captura `except Exception` devolviendo `None` en vez de dejar propagar el error | M1 · 6. Decoradores como guardianes | v0-semilla | `pytest tests/test_contrato.py::test_el_decorador_conserva_la_identidad_de_la_funcion tests/test_contrato.py::test_un_fallo_al_puntuar_no_se_traga_en_silencio -v` | `AssertionError: la función dice llamarse 'envoltura'` / `AssertionError: devolvió 200 con puntaje nulo` | Se usa `@functools.wraps(func)`; se relanza la excepción o se traduce a un error HTTP claro |

**Reglas que se verifican automáticamente:**

- `Módulo · Sección` debe citar una lección que exista en los módulos 1 a 5, con el
  título tal como aparece en el menú lateral del material.
- **`SHA donde se observa`** es el commit donde el defecto todavía está: normalmente
  `v0-semilla`, la etiqueta del repositorio tal como se lo entregamos. El calificador hace
  *checkout* de ese commit para reproducir la evidencia. Si lo dejan en el commit final —donde
  ya está corregido— el comando no reproducirá nada y la fila no cuenta.
- `Comando de evidencia` se ejecuta ahí. Escríbanlo contra `localhost:8000`; el calificador
  sustituye el puerto por el que use.
- `Salida obtenida` es literal, copiada de su terminal. **Se compara con lo que salga de
  verdad**, así que una salida inventada se detecta.
- Entre 6 y 12 hallazgos. Una fila que no corresponda a un defecto real resta la mitad de lo
  que suma una correcta: el máximo se alcanza con precisión, no con volumen.

---

# Parte C — Interpretación de las mediciones

> Un párrafo por endpoint. Expliquen **los tiempos que ustedes obtuvieron**, no la
> teoría general. Si un resultado los sorprendió, dígan­lo: eso se premia.

## `/ping`

## `/consulta-archivo`

## `/servicio-externo`

## `/calculo-pesado`
