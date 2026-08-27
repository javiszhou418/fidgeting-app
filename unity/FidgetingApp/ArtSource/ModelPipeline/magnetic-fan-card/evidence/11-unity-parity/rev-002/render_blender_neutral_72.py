"""Render the 72-segment FBX with the fixed parity camera."""

from pathlib import Path


HERE = Path(__file__).resolve().parent
LEGACY = HERE.parent / "rev-001/render_blender_neutral.py"


def main() -> None:
    source = LEGACY.read_text(encoding="utf-8").replace(
        '"10-export/rev-001/"',
        '"10-export/rev-002/"',
    )
    scope = {
        "__file__": str(HERE / "render_blender_neutral_72_impl.py"),
        "__name__": "fan_card_blender_parity_72_impl",
    }
    exec(compile(source, scope["__file__"], "exec"), scope)
    scope["main"]()


if __name__ == "__main__":
    main()
