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

Clasificado como trivial: no lee nada ni calcula nada, solo devuelve una constante.
Con concurrencia 1 tardó 0.019s en total (p50 0.3ms); con concurrencia 20, 0.024s
(p50 8.7ms). El tiempo total casi no cambia porque no hay ningún trabajo real que
paralelizar — la pequeña subida en la latencia individual es solo el overhead de
manejar 20 hilos a la vez, no del endpoint en sí. Se dejó como `async def`, la
convención estándar en FastAPI para handlers que no bloquean.

## `/consulta-archivo`

Clasificado como IO-bound: lee un archivo del disco con `read_text()`. Este método
es síncrono/bloqueante, así que en teoría declararlo `async def` sin usar una
librería async (como `aiofiles`) es un error — bloquearía el bucle de eventos.
Sin embargo, midiendo con concurrencia 1 (0.020s, p50 0.4ms) y con 20 (0.026s,
p50 8.3ms), el tiempo es prácticamente idéntico al de `/ping`: el archivo es tan
pequeño que el bloqueo no tiene ningún efecto medible. Se decidió dejarlo como
`async def`: la medición demuestra que, para el tamaño de archivo actual, no hay
impacto real en el rendimiento, aunque técnicamente lo más correcto a largo plazo
sería migrar a `aiofiles` si el archivo creciera.

## `/servicio-externo`

Clasificado como IO-bound: simula una llamada a un servicio externo con
`time.sleep(0.3)`. Originalmente estaba declarado `async def`, lo cual es un
defecto grave: `time.sleep()` bloquea todo el proceso, no solo esa petición. Con
concurrencia 1 tardaba 15.4s en total (esperado, 50 peticiones × 0.3s en fila);
pero con concurrencia 20 seguía tardando 15.3s en total, con un p50 de 6107ms —
es decir, las peticiones seguían atendiéndose una por una, sin ningún beneficio
de la concurrencia. Al cambiar el handler a `def` (sin `async`), FastAPI lo corre
automáticamente en un threadpool aparte: con el mismo test, concurrencia 20 bajó
a 0.96s en total, con p50 de 315ms — las 20 peticiones ahora sí se atienden en
paralelo de verdad.

## `/calculo-pesado`

Clasificado como CPU-bound: realiza 3 millones de operaciones matemáticas puras,
sin ninguna espera de E/S. Con `async def` simple, concurrencia 1 tomó 6.765s
(p50 134.6ms) y concurrencia 20 tomó 6.605s (p50 2620.5ms) — el total no mejoró
porque el GIL de Python impide que varios hilos ejecuten cálculo puro en paralelo
de verdad, y bloquear el bucle de eventos además congela todo el servicio mientras
calcula. La solución fue mover el cálculo a un `ProcessPoolExecutor` (procesos
reales, no hilos), usando `run_in_executor`: con esto, concurrencia 20 bajó a
2.325s en total (p50 686.1ms) — casi 3 veces más rápido, limitado ahora solo por
los núcleos de CPU disponibles (4 workers), no por el diseño del código.