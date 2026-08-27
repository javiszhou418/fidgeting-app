"""Compose the smooth-normal Gate 10 review."""

from pathlib import Path


HERE = Path(__file__).resolve().parent
LEGACY = HERE.parent / "rev-001/compose_export_review.py"


def main() -> None:
    scope = {
        "__file__": str(HERE / "compose_export_review_impl.py"),
        "__name__": "fan_card_smooth_export_compose_impl",
    }
    exec(compile(
        LEGACY.read_text(encoding="utf-8"),
        scope["__file__"],
        "exec",
    ), scope)
    scope["main"]()


if __name__ == "__main__":
    main()
