# ThreadMesh Distributed

ThreadMesh es un prototipo académico de arquitectura distribuida que simula la comunicación entre nodos y el procesamiento concurrente mediante hilos. El proyecto modela una topología de trabajo donde un gateway recibe solicitudes, un coordinador distribuye tareas usando una estrategia round robin y varios workers ejecutan trabajos en paralelo con `ThreadPoolExecutor`.

## Descripción

La solución representa un caso de estudio en Arquitectura de Software centrado en la coordinación de servicios distribuidos en memoria local. El sistema no pretende reemplazar un broker de mensajería real, sino demostrar de forma clara cómo se pueden aplicar patrones de diseño para separar responsabilidades, mejorar la tolerancia a fallos y mantener una estructura distribuida simple y evaluable.

## Objetivo académico

Este proyecto está relacionado con los siguientes objetivos de aprendizaje:

- arquitectura distribuida;
- comunicación entre nodos;
- gestión de hilos;
- escalabilidad;
- robustez;
- mantenibilidad;
- patrones de diseño.

ThreadMesh sirve como prototipo para analizar cómo una entrada central, una coordinación mediada y varios workers operando en paralelo pueden soportar cargas concurrentes en un entorno de laboratorio.

## Arquitectura

El sistema está compuesto por los siguientes elementos principales:

- API Gateway como Proxy: actúa como punto único de entrada para clientes externos y encapsula la lógica de acceso a los nodos internos.
- Coordinator como Mediator: centraliza la coordinación de trabajos y evita que los clientes interactúen directamente con cada worker.
- Round Robin como Strategy: selecciona el siguiente worker saludable en orden circular para balancear la carga de forma determinista.
- Event Bus como Observer: publica eventos de despacho, finalización y fallo para desacoplar la lógica de negocio de la observabilidad.
- Worker Nodes: ejecutan tareas con simulación de trabajo I/O-bound usando hilos.
- ThreadPoolExecutor: proporciona concurrencia dentro de cada worker para procesar varios trabajos en paralelo.

## Patrones utilizados

| Patrón | Implementación | Propósito |
| --- | --- | --- |
| Proxy | API Gateway | Punto de entrada y desacoplamiento |
| Mediator | Coordinator | Coordinar comunicación entre nodos |
| Strategy | Round Robin | Selección intercambiable de workers |
| Observer | Event Bus | Propagación desacoplada de eventos |

## Tecnologías

El prototipo utiliza únicamente tecnologías reales presentes en el proyecto:

- Python
- FastAPI
- HTTPX
- Pydantic
- ThreadPoolExecutor
- Pytest
- Docker
- Docker Compose
- PlantUML

## Estructura del proyecto

```text
threadmesh-distributed/
├── app/
│   ├── common/        # modelos compartidos y adaptadores locales
│   ├── coordinator/   # mediator, strategy y event bus
│   ├── gateway/       # proxy de entrada REST
│   └── worker/        # nodos de procesamiento con hilos
├── diagrams/          # fuentes PlantUML
├── docs/              # evidencia de benchmark y documentación adicional
├── scripts/           # scripts de evaluación de desempeño
├── tests/             # pruebas de patrones y resiliencia
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml
├── .gitignore
├── README.md
├── benchmark_results.json
└── LICENSE            # opcional, si se agrega en el repositorio final
```

## Requisitos previos

Se recomienda:

- Python 3.9+
- pip
- Docker y Docker Compose (para ejecución en contenedores)
- Git

## Instalación

```bash
git clone https://github.com/NaySalazar/threadmesh-distributed.git
cd threadmesh-distributed
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

## Ejecución con Docker

```bash
docker compose up --build
```

La API del gateway queda disponible en:

- Swagger/OpenAPI: http://localhost:8000/docs
- Healthcheck: http://localhost:8000/health

## Ejecución local

La ejecución local requiere levantar primero los workers, luego el coordinator y finalmente el gateway.

```bash
WORKER_ID=worker-a THREADS=4 uvicorn app.worker.main:app --host 0.0.0.0 --port 8001
WORKER_ID=worker-b THREADS=4 uvicorn app.worker.main:app --host 0.0.0.0 --port 8002
WORKER_ID=worker-c THREADS=4 uvicorn app.worker.main:app --host 0.0.0.0 --port 8003

WORKER_ENDPOINTS=http://localhost:8001,http://localhost:8002,http://localhost:8003 \
uvicorn app.coordinator.main:app --host 0.0.0.0 --port 8000

COORDINATOR_URL=http://localhost:8000 \
uvicorn app.gateway.main:app --host 0.0.0.0 --port 8004
```

## Uso de la API

El proyecto expone una API REST con FastAPI. La ruta principal de negocio se encuentra en el gateway:

- GET /health — estado del gateway
- POST /api/jobs — envío de un trabajo para ser distribuido

El coordinator también expone:

- GET /health — estado del coordinador
- POST /jobs — despacho directo a workers

Los workers expone:

- GET /health — healthcheck del worker
- POST /process — procesamiento de una tarea individual

## Ejemplo de solicitud

```bash
curl -X POST http://localhost:8000/api/jobs \
  -H 'Content-Type: application/json' \
  -d '{
    "payload": "procesar-factura-001",
    "duration_ms": 80,
    "job_type": "io"
  }'
```

La respuesta devuelve un `job_id`, `worker_id`, `status`, `elapsed_ms` y `result`.

## Pruebas

Para ejecutar el conjunto de pruebas del prototipo:

```bash
python3 -m pytest -q
```

Las pruebas validan:

- distribución round robin entre workers;
- bypass de workers fallidos;
- emisión de eventos con el patrón Observer.

## Benchmark / evaluación de desempeño

El script de benchmark disponible en `scripts/benchmark.py` permite simular cargas I/O-bound para comparar la mejora por escalabilidad horizontal.

```bash
python3 scripts/benchmark.py
```

Los resultados también se encuentran en `benchmark_results.json` y `docs/benchmark_results.json`.

### Resultado de referencia

| Nodos | Hilos/nodo | Throughput (trabajos/s) | p95 latencia (ms) | Speedup |
| --- | ---: | ---: | ---: | ---: |
| 1 | 2 | 39.81 | 1455.16 | 2.00x |
| 2 | 2 | 78.01 | 752.37 | 3.91x |
| 3 | 4 | 235.70 | 250.47 | 11.82x |

> Estas métricas corresponden a pruebas de laboratorio y no representan un SLA de producción.

## Diagramas UML

La carpeta `diagrams/` contiene los artefactos fuente de PlantUML para la representación de la arquitectura:

- `01_componentes.puml` — diagrama de componentes
- `02_secuencia.puml` — diagrama de secuencia
- `03_despliegue.puml` — diagrama de despliegue

Estos artefactos son la evidencia documental del prototipo y se pueden renderizar con una herramienta PlantUML compatible.

## Robustez y escalabilidad

ThreadMesh incorpora principios básicos de robustez y escalabilidad para un prototipo académico:

- concurrencia por hilos en cada worker;
- múltiples worker nodes para repartir trabajo;
- recuperación ante fallo mediante reintento contra nodos saludables;
- escalabilidad horizontal mediante aumento de nodos y workers;
- límites claros de diseño que evitan asumir comportamiento de producción completo.

## Limitaciones

Este prototipo es deliberadamente simple y presenta las siguientes limitaciones honestas:

- coordinador central como único punto de decisión;
- comunicación sincrónica entre gateway, coordinador y workers;
- event bus en memoria, sin persistencia ni distribución;
- estrategia Round Robin simple, sin algoritmos avanzados de balanceo;
- no incluye mecanismos de backpressure ni control de saturación real.

## Mejoras futuras

Como trabajo posterior, pueden incorporarse evoluciones razonables como:

- RabbitMQ o Kafka para mensajería asíncrona;
- backpressure y cola de tareas;
- health checks más elaborados;
- observabilidad con métricas y logs estructurados;
- replicación del coordinador para mayor disponibilidad;
- orquestación con Kubernetes o Docker Swarm.

Estas mejoras son propuestas de evolución futuras, no funcionalidades actuales del proyecto.

## Integrantes

Sección editable para registrar al equipo:

- [Nombre integrante 1] — Rol
- [Nombre integrante 2] — Rol
- [Nombre integrante 3] — Rol

## Contexto académico

- Curso: Arquitectura de Software
- Unidad 2
- Actividad: Tejiendo redes: Arquitectura de software entre hilos y nodos

## Evidencia de implementación

El repositorio incluye la evidencia necesaria para evaluar la implementación del prototipo:

- código fuente del servicio distribuido;
- patrones de diseño implementados en código;
- pruebas automatizadas de resiliencia y evento;
- diagrama UML fuente;
- benchmark y resultados reproducibles;
- configuración de contenedores para ejecución.

## Notas finales

ThreadMesh se presenta como un prototipo didáctico, orientado a demostrar la relación entre arquitectura distribuida, manejo de concurrencia y patrones de diseño en un entorno controlado.
