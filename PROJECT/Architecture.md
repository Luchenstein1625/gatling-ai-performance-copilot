# Arquitectura Preliminar

```text
Endpoint + YAML + criticidad/complejidad
                |
                v
        Ingesta y validación
                |
                v
          Motor de matriz
                |
                v
      Configuración resuelta
                |
                v
             Gatling
                |
                v
        Parser de resultados
                |
                v
      Historial normalizado
                |
                v
    Baseline + recomendador
                |
                v
 Explicación + validación humana
                |
                v
         Registro de feedback
```

## Componentes
1. parser de configuración;
2. resolver de parámetros;
3. motor de cuadrantes;
4. parser Gatling;
5. base histórica;
6. baseline;
7. recomendador;
8. explicador;
9. human-in-the-loop.
