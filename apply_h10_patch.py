from pathlib import Path

MAIN = Path("app/src/performance_decision_engine/interfaces/cli/main.py")
DEV_INDEX = Path("app/docs/development/README.md")

IMPORT_LINE = (
    "from performance_decision_engine.interfaces.cli.pipeline "
    "import register_pipeline_command\n"
)
REGISTER_LINE = "register_pipeline_command(app, console)\n"


def patch_main() -> None:
    content = MAIN.read_text(encoding="utf-8")

    if IMPORT_LINE not in content:
        marker = "from performance_decision_engine.infrastructure.repositories.json_execution_repository import (\n"
        position = content.find(marker)
        if position == -1:
            raise RuntimeError("Could not find the expected import block in main.py")
        content = content[:position] + IMPORT_LINE + content[position:]

    if REGISTER_LINE not in content:
        marker = "console = Console()\n"
        content = content.replace(
            marker,
            marker + "\n" + REGISTER_LINE,
            1,
        )

    MAIN.write_text(content, encoding="utf-8")


def patch_development_index() -> None:
    if not DEV_INDEX.exists():
        return
    content = DEV_INDEX.read_text(encoding="utf-8")
    content = content.replace("| H10 | Integration | ⏳ |", "| H10 | Local Integration PoC | ✅ |")
    content = content.replace("| H10 Integration | ⏳ |", "| H10 Local Integration PoC | ✅ |")
    DEV_INDEX.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    patch_main()
    patch_development_index()
    print("H10 patch applied.")
