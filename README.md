# riesgo-api-v0

Servicio de puntuación de siniestros de la Aseguradora Santo Tomás.
Recibe los datos de una póliza y devuelve la probabilidad de que el siniestro
declarado termine en un pago alto.

## Instalación

```bash
pip install -r requirements.txt
```

El modelo entrenado (`modelo.pkl`) viene en el repositorio.

## Puesta en marcha

**Desarrollo** (con recarga automática al guardar cambios):

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Producción** (sin recarga, con múltiples workers):

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

`--reload` no debe usarse en producción: deja el proceso vulnerable a
reinicios en caliente no controlados.

## Endpoints

| Método | Ruta | Qué hace |
|---|---|---|
| POST | `/score` | Puntúa una póliza |
| GET | `/health` | Verifica que el servicio esté disponible |
| GET | `/historial` | Evaluaciones hechas |
| GET | `/siniestros/{id}` | Consulta un siniestro |
| GET | `/exportar` | Exporta el histórico para el equipo de actuaría |
| GET | `/ping` | Comprobación rápida |
| GET | `/consulta-archivo` | Cuenta los registros del archivo de siniestros |
| GET | `/servicio-externo` | Consulta la tarifa de referencia del reasegurador |
| GET | `/calculo-pesado` | Recalcula la reserva agregada |


### Ejemplo

```bash
curl -X POST localhost:8000/score \
  -H "Content-Type: application/json" \
  -d '{"poliza": "POL-2026-0413", "monto": 4200000, "antiguedad": 3, "siniestros_previos": 1}'
```

```json
{"poliza": "POL-2026-0413", "puntaje": 0.61, "alto_riesgo": false}
```

## Notas

- La clave de la API (`API_KEY`, `CLAVE_FIRMA`) se lee desde variables de entorno con `python-dotenv`. Creá un archivo `.env` en la raíz con `API_KEY=...` y `CLAVE_FIRMA=...` antes de arrancar el servicio.
- El histórico se exporta en formato JSON.