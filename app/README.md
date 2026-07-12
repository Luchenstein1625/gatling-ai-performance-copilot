# Performance Decision Engine

Motor desacoplado para apoyar decisiones de configuración en pruebas de rendimiento.

El caso de estudio inicial utiliza archivos YAML y resultados Gatling, pero el núcleo del sistema no depende de una herramienta específica. Nuevas fuentes como JMeter, k6 o LoadRunner pueden incorporarse mediante adaptadores sin modificar el dominio.

## Arquitectura

```text
app/
├── src/performance_decision_engine/
│   ├── domain/
│   │   ├── entities/
│   │   └── services/
│   ├── application/
│   │   ├── ports/
│   │   └── use_cases/
│   ├── infrastructure/
│   │   ├── parsers/
│   │   └── repositories/
│   └── interfaces/
│       ├── cli/
│       └── api/
├── tests/
├── examples/
├── docs/
├── scripts/
└── pyproject.toml
```

## Responsabilidades

### `domain/`

Contiene el conocimiento del negocio:

- Tripleta;
- cuadrante;
- configuración de endpoint;
- métricas de ejecución;
- recomendación;
- reglas puras.

No importa FastAPI, Typer, YAML, Gatling ni persistencia.

### `application/`

Contiene los casos de uso:

- normalizar una ejecución;
- resolver un cuadrante;
- generar una recomendación baseline.

También define puertos para desacoplar el dominio de archivos y repositorios.

### `infrastructure/`

Implementa detalles externos:

- parser de `performance.yaml`;
- parser de `parametricConfigurationValues.yaml`;
- parser de resultados Gatling;
- repositorio JSON.

### `interfaces/`

Expone la aplicación:

- CLI;
- API HTTP.

## Requisitos

- Python 3.11 o 3.12

## Instalación en PowerShell

Desde la carpeta `app`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## Verificación

Ejecutar cada comando por separado:

```powershell
pde doctor
pde --version
pytest
```

## Ejecutar ejemplo incluido

```powershell
pde normalize `
  --performance examples/input/performance.yaml `
  --parameters examples/input/parametricConfigurationValues.yaml `
  --results examples/input/global_stats.json `
  --output examples/output/execution_summary.json
```

## Resolver un cuadrante

```powershell
pde quadrant --criticality high --complexity medium
```

Resultado esperado:

```text
Quadrant: 6
```

## Ejecutar API

```powershell
uvicorn performance_decision_engine.interfaces.api.main:app --reload
```

Endpoints:

- `GET /health`
- `GET /version`
- `GET /quadrants/{criticality}/{complexity}`

## Calidad

```powershell
ruff check .
black --check .
mypy src
pytest --cov=performance_decision_engine
```

## Flujo funcional inicial

```text
performance.yaml
        +
parametricConfigurationValues.yaml
        +
resultado global
        |
        v
parsers de infraestructura
        |
        v
caso de uso de normalización
        |
        v
entidades del dominio
        |
        v
JSON normalizado
```

## Estado

Esta base incluye:

- arquitectura limpia;
- paquete Python instalable;
- CLI funcional;
- API mínima;
- dominio desacoplado;
- parser YAML;
- parser de parámetros;
- parser de métricas globales;
- normalización;
- baseline simple;
- persistencia JSON;
- pruebas;
- ejemplos.

No declara como implementado ningún modelo de Machine Learning.


# Ejecución

## Crear entorno virtual

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## Instalar dependencias

```powershell
pip install -e ".[dev]"
```

## Verificar instalación

```powershell
pde doctor
```

---

# Ejecutar pruebas

```powershell
pytest
```

---

# Ejecutar parser de parámetros

```powershell
pytest tests/test_parameter_values.py -v
```

---

# Ejecutar normalización

```powershell
pde normalize ...
```

---

# Ejecutar API

```powershell
uvicorn performance_decision_engine.interfaces.api.main:app --reload
```