"""Render camera-distance depth for the smooth-normal light scene."""

from pathlib import Path


HERE = Path(__file__).resolve().parent
LEGACY = HERE.parent / "rev-003/render_depth_pass.py"


def main() -> None:
    source = LEGACY.read_text(encoding="utf-8").replace(
        '"fan-card-72-segment-lighting.blend"',
        '"fan-card-smooth-normal-lighting.blend"',
    )
    scope = {
        "__file__": str(HERE / "render_depth_pass_impl.py"),
        "__name__": "fan_card_smooth_depth_impl",
    }
    exec(compile(source, scope["__file__"], "exec"), scope)
    scope["main"]()


if __name__ == "__main__":
    main()
