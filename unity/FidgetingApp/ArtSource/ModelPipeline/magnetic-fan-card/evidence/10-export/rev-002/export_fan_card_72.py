"""Run the approved export pipeline for 72-segment visible geometry."""

from pathlib import Path


HERE = Path(__file__).resolve().parent
LEGACY = HERE.parent / "rev-001/export_fan_card.py"


def main() -> None:
    source = LEGACY.read_text(encoding="utf-8")
    source = source.replace(
        '"08-lighting/rev-002/"',
        '"08-lighting/rev-003/"',
    ).replace(
        '"fan-card-exact-lighting.blend"',
        '"fan-card-72-segment-lighting.blend"',
    ).replace(
        "50_000",
        "100_000",
    )
    scope = {
        "__file__": str(HERE / "export_fan_card_72_impl.py"),
        "__name__": "fan_card_export_72_impl",
    }
    exec(compile(source, scope["__file__"], "exec"), scope)
    scope["main"]()


if __name__ == "__main__":
    main()
