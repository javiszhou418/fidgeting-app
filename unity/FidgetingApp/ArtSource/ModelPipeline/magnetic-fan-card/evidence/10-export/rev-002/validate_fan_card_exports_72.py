"""Round-trip validate the 72-segment FBX, GLB, and collision exports."""

from pathlib import Path


HERE = Path(__file__).resolve().parent
LEGACY = HERE.parent / "rev-001/validate_fan_card_exports.py"


def main() -> None:
    source = LEGACY.read_text(encoding="utf-8").replace(
        "50_000",
        "100_000",
    )
    scope = {
        "__file__": str(HERE / "validate_fan_card_exports_72_impl.py"),
        "__name__": "fan_card_export_validator_72_impl",
    }
    exec(compile(source, scope["__file__"], "exec"), scope)
    scope["main"]()


if __name__ == "__main__":
    main()
