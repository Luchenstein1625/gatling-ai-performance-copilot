from performance_decision_engine.interfaces.cli.main import app, console
from performance_decision_engine.interfaces.cli.pipeline import register_pipeline_command

register_pipeline_command(app, console)
