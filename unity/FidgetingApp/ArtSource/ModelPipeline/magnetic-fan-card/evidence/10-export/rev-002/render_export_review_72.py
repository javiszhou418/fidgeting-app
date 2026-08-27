"""Render neutral reviews for the 72-segment exports."""

from pathlib import Path


HERE = Path(__file__).resolve().parent
LEGACY = HERE.parent / "rev-001/render_export_review.py"


def main() -> None:
    scope = {
        "__file__": str(HERE / "render_export_review_72_impl.py"),
        "__name__": "fan_card_export_review_72_impl",
    }
    exec(compile(
        LEGACY.read_text(encoding="utf-8"),
        scope["__file__"],
        "exec",
    ), scope)
    scope["main"]()


if __name__ == "__main__":
    main()
