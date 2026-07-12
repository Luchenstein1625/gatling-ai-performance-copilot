# Performance Decision Engine

Motor desacoplado para apoyar decisiones de configuración en pruebas de rendimiento.

El caso de estudio inicial utiliza Gatling, `performance.yaml` y `parametricConfigurationValues.yaml`, pero la arquitectura está diseñada para incorporar otras herramientas mediante parsers y adaptadores.

## Objetivo del MVP

1. Leer configuraciones existentes.
2. Resolver parámetros semánticos.
3. Leer resultados de una ejecución.
4. Normalizar la información.
5. Aplicar un baseline.
6. Generar una recomendación explicable.
7. Registrar validación humana.

## Estructura

```text
app/
├── src/performance_decision_engine/
│   ├── api/
│   ├── cli/
│   ├── config/
│   ├── core/
│   ├── domain/
│   ├── parsers/
│   ├── adapters/
│   ├── recommendation/
│   ├── explainability/
│   ├── evaluation/
│   └── storage/
├── tests/
├── examples/
├── docs/
├── scripts/
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── Makefile
├── Makefile.ps1
└── CONTRIBUTING.md
```

## Responsabilidad de cada carpeta

| Carpeta | Responsabilidad |
|---|---|
| `domain/` | Entidades y reglas del negocio, independientes de herramientas |
| `parsers/` | Lectura de YAML, JSON y resultados externos |
| `adapters/` | Conversión desde formatos externos hacia el dominio |
| `recommendation/` | Baseline, reglas y modelos de recomendación |
| `explainability/` | Evidencia y explicaciones |
| `evaluation/` | Métricas y comparación con baseline |
| `storage/` | Persistencia JSON, CSV y futura base de datos |
| `api/` | Interfaz HTTP con FastAPI |
| `cli/` | Interfaz de línea de comandos |
| `core/` | Logging, excepciones y utilidades comunes |
| `config/` | Configuración y variables de entorno |

## Requisitos

- Python 3.11 o 3.12
- PowerShell, Bash o terminal equivalente

## Instalación en Windows PowerShell

Desde la carpeta `app`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## Instalación en Linux/macOS

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## Comprobar instalación

```bash
pde --version
pde doctor
```

También se puede ejecutar como módulo:

```bash
python -m performance_decision_engine --version
python -m performance_decision_engine doctor
```

## Ejecutar ejemplo de normalización

```bash
pde normalize \
  --performance examples/input/performance.yaml \
  --parameters examples/input/parametricConfigurationValues.yaml \
  --gatling examples/input/global_stats.json \
  --output examples/output/execution_summary.json
```

En PowerShell:

```powershell
pde normalize `
  --performance examples/input/performance.yaml `
  --parameters examples/input/parametricConfigurationValues.yaml `
  --gatling examples/input/global_stats.json `
  --output examples/output/execution_summary.json
```

## Ejecutar pruebas

```bash
pytest
```

Con cobertura:

```bash
pytest --cov=performance_decision_engine --cov-report=term-missing
```

## Calidad de código

```bash
ruff check .
black --check .
mypy src
```

Para corregir formato:

```bash
black .
ruff check . --fix
```

## Ejecutar API

```bash
uvicorn performance_decision_engine.api.main:app --reload
```

Endpoints iniciales:

- `GET /health`
- `GET /version`

## Estado actual

Esta plantilla incluye:

- paquete Python instalable;
- CLI funcional;
- comando `doctor`;
- comando `normalize`;
- parser de `performance.yaml`;
- parser de parámetros;
- parser global Gatling;
- modelos Pydantic;
- almacenamiento JSON;
- baseline de matriz;
- API mínima;
- pruebas unitarias;
- archivos de ejemplo;
- documentación técnica.

Todavía no incluye:

- recomendador entrenado;
- clasificación automática validada;
- migración completa de `performance-lib`;
- integración productiva;
- despliegue corporativo.

## Principio de diseño

La herramienta de pruebas es una dependencia externa. La lógica del dominio y de recomendación no debe depender directamente de Gatling.
