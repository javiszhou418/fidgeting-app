"""Compare 72-segment Blender and Unity neutral captures."""

from pathlib import Path


HERE = Path(__file__).resolve().parent
LEGACY = HERE.parent / "rev-001/build_unity_parity_report.py"


def main() -> None:
    source = LEGACY.read_text(encoding="utf-8").replace(
        "34284",
        "70548",
    )
    scope = {
        "__file__": str(HERE / "build_unity_parity_report_72_impl.py"),
        "__name__": "fan_card_unity_parity_72_impl",
    }
    exec(compile(source, scope["__file__"], "exec"), scope)
    scope["main"]()


if __name__ == "__main__":
    main()
