"""Collect Gate 12 evidence for the 72-segment clean Banner revision."""

from pathlib import Path


HERE = Path(__file__).resolve().parent
LEGACY = HERE.parent / "rev-001/collect_shipping_evidence.py"


def main() -> None:
    source = LEGACY.read_text(encoding="utf-8")
    source = source.replace(
        "FanCardAcceptanceTests-Gate12.xml",
        "FanCardAcceptanceTests-Gate12-72.xml",
    ).replace(
        "GachaStorefrontIntegrationTests-Gate12.xml",
        "GachaStorefrontIntegrationTests-Gate12-72.xml",
    ).replace(
        '"09-environment/rev-005"',
        '"09-environment/rev-007"',
    )
    scope = {
        "__file__": str(HERE / "collect_shipping_evidence_72_impl.py"),
        "__name__": "fan_card_shipping_collector_72_impl",
    }
    exec(compile(source, scope["__file__"], "exec"), scope)
    scope["main"]()


if __name__ == "__main__":
    main()
