# Application

## CLI

### Entrenar modelo

```bash
pde train-model --dataset dataset.csv --model model.joblib --report report.json
```

### Explicar modelo

```bash
pde explain-model --model model.joblib --output model_explanation.json
```

El comando genera una explicación global del árbol de decisión sin modificar el artefacto entrenado.

## Artefactos

- model.joblib
- report.json
- model_explanation.json
