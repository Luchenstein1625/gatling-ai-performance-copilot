# Arquitectura

## Capas

### Dominio
Representa endpoint, ejecución, Tripleta, cuadrante, métricas y recomendación.

### Ingesta
Lee archivos externos sin decidir.

### Adaptación
Convierte datos externos a objetos de dominio.

### Recomendación
Aplica baseline, reglas y, posteriormente, modelos.

### Explicabilidad
Construye evidencia y una explicación verificable.

### Interfaces
CLI y API.

## Dependencias permitidas

```text
interfaces -> application modules -> domain
parsers/adapters -> domain
recommendation -> domain
storage -> domain
```

El dominio no debe importar FastAPI, Typer, Gatling ni detalles de persistencia.
