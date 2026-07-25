from performance_decision_engine.interfaces.cli.experiments import (
    register_experiment_commands,
)
from performance_decision_engine.interfaces.cli.main import app, console
from performance_decision_engine.interfaces.cli.pipeline import register_pipeline_command

register_pipeline_command(app, console)
register_experiment_commands(app, console)
