# August PoC improvements

This extension strengthens the existing H7-H10 flow without replacing it.

## Added commands

| Command | Purpose | Main artifact |
|---|---|---|
| `pde data-quality` | Reports empty columns, duplicates, missing values and class distribution | `dataset_quality.json` |
| `pde evaluate-model` | Compares all features against an assertion-free ablation over repeated splits | `model_comparison.json` |
| `pde predict` | Predicts one real execution and compares H8 with the H6 rule engine | `prediction.json` |
| `pde plan-quadrant` | Converts `maintain/review` into a controlled action for the current quadrant | `quadrant_action.json` |

Training now excludes completely empty feature columns and records their names in
`excluded_empty_feature_columns`. This avoids silently dropping an unnamed column inside
scikit-learn.

## One-command Windows execution

Run from `app` with the virtual environment activated:

```powershell
.\scripts\run_august_poc.ps1 `
    -Dataset ".\examples\output\historical_dataset.csv" `
    -Performance "<execution>\performance.yaml" `
    -Parameters "<resources>\parametricConfigurationValues.yaml" `
    -Results "<execution>\global_stats.json" `
    -Assertions "<execution>\assertions.json" `
    -CurrentQuadrant 5
```

`-Assertions` is optional. The script stops immediately if a required input is missing.

## Interpretation

The two evaluation variants answer different questions:

- `all_features`: fidelity of H8 when approximating the H6 labels.
- `without_assertions`: evidence of whether the model still finds signal without variables
  that directly summarize assertion outcomes.

The majority-class accuracy is included as a minimum reference baseline. With the current
small dataset, metric means and variability must be presented as PoC evidence rather than
production performance.

`plan-quadrant` intentionally keeps the current quadrant when the recommendation is
`review`. It requests human validation instead of inventing whether the next quadrant must
increase or decrease. A future automatic transition requires expert-approved transition
rules and historical labels for the target quadrant.
