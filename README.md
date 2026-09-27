# ThreadMesh - arquitectura distribuida entre hilos y nodos

Prototipo académico para la Unidad 2 de Arquitectura de Software. ThreadMesh distribuye trabajos entre nodos worker y usa pools de hilos para procesar tareas I/O-bound concurrentemente.

## Arquitectura

- **API Gateway / Proxy:** punto único de entrada (`POST /api/jobs`).
- **Coordinator / Mediator:** desacopla clientes y workers y distribuye las solicitudes.
- **Round Robin Strategy:** selecciona nodos saludables sin acoplar la política al coordinador.
- **Worker Nodes:** ejecutan tareas mediante `ThreadPoolExecutor`.
- **Observer / Event Bus:** publica eventos de despacho, finalización y fallo.

## Patrones aplicados

1. Proxy: gateway frontal y aislamiento de la topología interna.
2. Mediator: coordinación central de nodos.
3. Observer distribuido: eventos de ejecución/fallo.
4. Strategy: política intercambiable de selección de workers.

## Estructura

```text
app/
  gateway/       # Proxy
  coordinator/   # Mediator, Strategy, EventBus
  worker/        # ejecución concurrente
  common/        # modelos y adaptadores
scripts/benchmark.py
tests/
diagrams/
Dockerfile
docker-compose.yml
```

## Ejecución local con Docker

```bash
docker compose up --build
```

Abrir Swagger: `http://localhost:8000/docs`

Ejemplo:

```bash
curl -X POST http://localhost:8000/api/jobs \
  -H 'Content-Type: application/json' \
  -d '{"payload":"procesar-factura-001","duration_ms":80,"job_type":"io"}'
```

## Pruebas

```bash
pip install -r requirements.txt
pytest
python scripts/benchmark.py
```

Las pruebas verifican distribución round-robin, tolerancia al fallo de un worker y publicación de eventos Observer.

## UML

Los archivos fuente se encuentran en `diagrams/`.

## Integrantes

Completar con los nombres y roles reales del equipo antes de la entrega.

## Resultados de referencia del benchmark

Ejecución local con 60 trabajos I/O-bound de 50 ms:

| Nodos | Hilos/nodo | Throughput (trabajos/s) | p95 latencia (ms) | Speedup |
|---:|---:|---:|---:|---:|
| 1 | 2 | 39.81 | 1455.16 | 2.00x |
| 2 | 2 | 78.01 | 752.37 | 3.91x |
| 3 | 4 | 235.70 | 250.47 | 11.82x |

Los valores dependen del hardware y representan una carga sintética controlada, no un SLA productivo.
