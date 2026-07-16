import html
import json
from pathlib import Path

from performance_decision_engine.domain.entities.execution import NormalizedExecution
from performance_decision_engine.domain.entities.recommendation import Recommendation


class HtmlReportGenerator:
    """Generate one dependency-free, self-contained H10 HTML report."""

    def generate(
        self,
        execution: NormalizedExecution,
        recommendation: Recommendation,
        output_path: Path,
        *,
        training_status: dict[str, object] | None = None,
        model_explanation: dict[str, object] | None = None,
    ) -> None:
        metrics = execution.global_metrics
        assertions = metrics.assertions

        trace = recommendation.evidence.get("decision_trace", [])
        if not isinstance(trace, list):
            trace = []

        rows = [
            ("Total requests", metrics.total_requests),
            ("Successful requests", metrics.successful_requests),
            ("Failed requests", metrics.failed_requests),
            ("Error rate", f"{metrics.error_rate_percent:.2f}%"),
            (
                "Mean response time",
                self._milliseconds(metrics.mean_response_time_ms),
            ),
            (
                "P95 response time",
                self._milliseconds(metrics.p95_response_time_ms),
            ),
            (
                "P99 response time",
                self._milliseconds(metrics.p99_response_time_ms),
            ),
            (
                "Requests per second",
                (
                    f"{metrics.requests_per_second:.2f}"
                    if metrics.requests_per_second is not None
                    else "N/A"
                ),
            ),
            (
                "Assertions",
                (
                    f"{assertions.successful}/{assertions.total} passed"
                    if assertions is not None
                    else "Not provided"
                ),
            ),
        ]

        endpoint_rows = [
            (
                endpoint.name,
                endpoint.enabled,
                endpoint.triplet.concurrency_value,
                endpoint.triplet.iterations_value,
                endpoint.triplet.response_time_ms,
            )
            for endpoint in execution.configuration.endpoints
        ]

        training_status_json = html.escape(
            json.dumps(
                training_status or {"status": "not_requested"},
                indent=2,
                ensure_ascii=False,
            )
        )

        model_explanation_json = html.escape(
            json.dumps(
                model_explanation or {"status": "not_available"},
                indent=2,
                ensure_ascii=False,
            )
        )

        decision_trace_json = html.escape(
            json.dumps(
                trace,
                indent=2,
                ensure_ascii=False,
            )
        )

        recommendation_action = html.escape(recommendation.action.upper())
        recommendation_explanation = html.escape(recommendation.explanation)

        triggered_rule = html.escape(str(recommendation.evidence.get("triggered_rule") or "None"))

        metrics_cards = "".join(self._metric_card(label, value) for label, value in rows)

        endpoints_table_rows = "".join(self._endpoint_row(*row) for row in endpoint_rows)

        warnings_html = self._warnings(execution.warnings)

        document = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta
    name="viewport"
    content="width=device-width, initial-scale=1"
>
<title>Performance Decision Engine - H10 Report</title>
<style>
:root {{
    color-scheme: light;
    font-family: Inter, Arial, sans-serif;
}}

body {{
    margin: 0;
    background: #f4f6f8;
    color: #17202a;
}}

main {{
    max-width: 1100px;
    margin: 0 auto;
    padding: 32px 20px 64px;
}}

header {{
    background: #152238;
    color: white;
    padding: 28px;
    border-radius: 14px;
}}

h1,
h2 {{
    margin-top: 0;
}}

.grid {{
    display: grid;
    grid-template-columns: repeat(
        auto-fit,
        minmax(220px, 1fr)
    );
    gap: 14px;
}}

.card {{
    background: white;
    border-radius: 12px;
    padding: 18px;
    margin-top: 18px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
}}

.metric {{
    font-size: 1.35rem;
    font-weight: 700;
}}

.label {{
    color: #607080;
    font-size: 0.88rem;
}}

.status {{
    display: inline-block;
    padding: 8px 12px;
    border-radius: 999px;
    background: {self._status_background(recommendation.action)};
    color: {self._status_foreground(recommendation.action)};
    font-weight: 700;
}}

table {{
    width: 100%;
    border-collapse: collapse;
}}

th,
td {{
    text-align: left;
    padding: 10px;
    border-bottom: 1px solid #e8ebef;
}}

pre {{
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    background: #f7f8fa;
    padding: 14px;
    border-radius: 8px;
}}

.warning {{
    color: #8a4b00;
}}

footer {{
    color: #64748b;
    margin-top: 24px;
    font-size: 0.85rem;
}}
</style>
</head>

<body>
<main>
<header>
<h1>Performance Decision Engine</h1>
<p>H10 Local Proof of Concept — End-to-End Analysis Report</p>
<span class="status">{recommendation_action}</span>
</header>

<section class="card">
<h2>Executive summary</h2>
<p>{recommendation_explanation}</p>
<p>
<strong>Triggered rule:</strong>
{triggered_rule}
</p>
</section>

<section class="grid">
{metrics_cards}
</section>

<section class="card">
<h2>Configured endpoints</h2>
<table>
<thead>
<tr>
<th>Name</th>
<th>Enabled</th>
<th>Concurrency</th>
<th>Iterations</th>
<th>Response target</th>
</tr>
</thead>
<tbody>
{endpoints_table_rows}
</tbody>
</table>
</section>

<section class="card">
<h2>Decision trace</h2>
<pre>{decision_trace_json}</pre>
</section>

<section class="card">
<h2>Warnings</h2>
{warnings_html}
</section>

<section class="card">
<h2>Machine Learning stage</h2>
<pre>{training_status_json}</pre>
</section>

<section class="card">
<h2>Model explanation</h2>
<pre>{model_explanation_json}</pre>
</section>

<footer>
Generated locally by H10.
This PoC does not connect to bank platforms
or production services.
</footer>
</main>
</body>
</html>
"""

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path.write_text(
            document,
            encoding="utf-8",
        )

    @staticmethod
    def _milliseconds(value: int | None) -> str:
        if value is None:
            return "N/A"

        return f"{value} ms"

    @staticmethod
    def _metric_card(
        label: str,
        value: object,
    ) -> str:
        escaped_label = html.escape(label)
        escaped_value = html.escape(str(value))

        return (
            '<article class="card">'
            f'<div class="label">{escaped_label}</div>'
            f'<div class="metric">{escaped_value}</div>'
            "</article>"
        )

    @staticmethod
    def _endpoint_row(
        name: str,
        enabled: bool,
        concurrency: int | None,
        iterations: int | None,
        response_time: int | None,
    ) -> str:
        target = f"{response_time} ms" if response_time is not None else "N/A"

        concurrency_value = concurrency if concurrency is not None else "N/A"

        iterations_value = iterations if iterations is not None else "N/A"

        return (
            "<tr>"
            f"<td>{html.escape(name)}</td>"
            f"<td>{'Yes' if enabled else 'No'}</td>"
            f"<td>{concurrency_value}</td>"
            f"<td>{iterations_value}</td>"
            f"<td>{target}</td>"
            "</tr>"
        )

    @staticmethod
    def _warnings(warnings: list[str]) -> str:
        if not warnings:
            return "<p>No warnings.</p>"

        items = "".join(
            ('<li class="warning">' f"{html.escape(warning)}" "</li>") for warning in warnings
        )

        return f"<ul>{items}</ul>"

    @staticmethod
    def _status_background(action: str) -> str:
        if action == "maintain":
            return "#dff6e5"

        return "#fff0d9"

    @staticmethod
    def _status_foreground(action: str) -> str:
        if action == "maintain":
            return "#166534"

        return "#9a3412"
