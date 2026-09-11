#!/usr/bin/env python3
"""Generate UTF-8 Gate 04 crops and review boards deterministically."""

from pathlib import Path

from PIL import Image


REVISION = Path(__file__).resolve().parent
PREVIOUS_CROPS = REVISION.parent / "rev-008" / "source-crops"
OUTPUT = REVISION / "source-crops"


def crop(source_name: str, output_name: str, box: tuple[int, int, int, int], width: int = 760) -> None:
    with Image.open(PREVIOUS_CROPS / source_name) as image:
        region = image.crop(box)
        height = round(region.height * width / region.width)
        region.resize((width, height), Image.Resampling.LANCZOS).save(OUTPUT / output_name)


def write_svg(name: str, content: str) -> None:
    (REVISION / name).write_text(content, encoding="utf-8")


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    crop("rotate-66.50.png", "visible-flat-lower.png", (165, 430, 650, 855))
    crop("slide-42.00.png", "circular-slide-overlap.png", (70, 0, 595, 455))
    crop("official-fixed-carrier.png", "official-concealed-interface.png", (65, 20, 650, 515))
    crop("rotate-67.25.png", "upper-rotates-over-lower.png", (165, 120, 650, 820))

    text = {
        1: "\u5916\u9732\u4e0b\u5c42\uff1a\u5e72\u51c0\u5e73\u9762\uff0c\u4e0d\u753b\u6ed1\u8f68",
        2: "\u7528\u6237\u6743\u5a01\u7ea0\u6b63\uff1b\u89c6\u9891\u53ea\u7528\u4e8e\u6838\u5bf9\u53ef\u89c1\u8fb9\u754c\u3002\u8f68\u9053\u8bc1\u636e\u5c5e\u4e8e\u5706\u7aef\u91cd\u53e0\u533a\u5185\u90e8\uff0c\u4e0d\u80fd\u5ef6\u4f38\u5230\u5916\u9732\u5e73\u9762\u3002",
        3: "\u2460 \u64cd\u4f5c\u65f6\u53ef\u89c1\u7684\u4e0b\u5c42\u8868\u9762",
        4: "\u7eff\u8272 \u00b7 \u53ef\u89c1\u5e73\u9762\u8fb9\u754c",
        5: "\u8868\u9762\u53ef\u6709 artwork \u4e0e\u8fb9\u7f18\u5f00\u53e3\uff1b\u6ca1\u6709\u5916\u9732\u7eb5\u5411\u8f68\u9053\u3002",
        6: "\u4e0a\u6cbf\u88ab\u4e0a\u4ef6\u906e\u4f4f\uff0c\u865a\u7ebf\u540e\u7684\u8fb9\u754c\u7ee7\u7eed unknown\u3002",
        7: "\u2461 \u6ed1\u5f00\u540e\u51fa\u73b0\u7684\u5706\u7aef\u5185\u90e8\u533a",
        8: "\u84dd\u8272\u865a\u7ebf \u00b7 \u9690\u85cf\u673a\u6784 envelope",
        9: "\u53ea\u9501\u5b9a\u201c\u673a\u5236\u4f4d\u4e8e\u5706\u7aef\u91cd\u53e0\u533a\u201d\uff1b\u4e0d\u628a\u56fe\u4e2d\u5185\u90e8\u7ec6\u8282\u753b\u6210\u5916\u9732\u8868\u9762\u3002",
        10: "\u865a\u7ebf\u4e0d\u4ee3\u8868\u7cbe\u786e\u8f68\u9053\u8def\u5f84\u3001\u6df1\u5ea6\u3001\u6570\u91cf\u6216\u8026\u5408\u3002",
        11: "\u7981\u6b62\uff1a\u4e0b\u4e00\u7248\u767d\u6a21\u4e0d\u5f97\u5728\u53ef\u89c1\u4e0b\u5c42\u5e73\u9762\u5efa\u7acb\u4efb\u4f55\u5916\u9732\u6ed1\u8f68\u4ee3\u7406\u3002",
        12: "\u9690\u85cf\u5706\u5f62\u63a5\u53e3\uff1a\u540c\u4e00\u4e0a\u4ef6\u5728\u8fd9\u91cc\u5e73\u79fb\u5e76\u65cb\u8f6c",
        13: "\u53ea\u786e\u8ba4 enclosure \u7684\u4f4d\u7f6e\u4e0e\u8fd0\u52a8\u5173\u7cfb\uff1b\u5185\u90e8\u8def\u5f84\u3001\u96f6\u4ef6\u548c\u8026\u5408\u5168\u90e8\u4fdd\u6301 unknown\u3002",
        14: "\u2460 \u540c\u6b3e\u62c6\u5f00\u56fe\uff1a\u5706\u7aef\u5185\u90e8\u8bc1\u636e",
        15: "\u84dd\u8272\u865a\u7ebf \u00b7 \u5706\u5f62\u91cd\u53e0\uff0f\u5c01\u95ed\u533a",
        16: "\u540c\u6b3e\u62c6\u5f00\u56fe\u53ef\u8bc1\u660e\u4e2d\u5fc3\u63a5\u53e3\u4e0e\u5185\u90e8\u63a5\u89e6\u4ef6\u4f4d\u4e8e\u5706\u7aef\u3002",
        17: "\u8fd9\u4e9b\u96f6\u4ef6\u5728\u6b63\u5e38\u5916\u89c2\u4e2d\u88ab\u4e0a\u4e0b\u4ef6\u5c01\u95ed\uff0c\u4e0d\u4f5c\u4e3a\u53ef\u89c1\u767d\u6a21\u51e0\u4f55\u3002",
        18: "\u9ec4\u8272 \u00b7 \u4ec5\u4e3a\u4e2d\u592e\u65cb\u8f6c\u8f74\u5fc3\u5019\u9009\u8303\u56f4",
        19: "\u2461 \u7528\u6237\u89c6\u9891\uff1a\u4e0a\u4ef6\u76f8\u5bf9\u4e0b\u5c42\u8f6c\u52a8",
        20: "\u6a59\u8272\u4e0a\u4ef6\u901a\u8fc7\u9690\u85cf\u63a5\u53e3\u8fd0\u52a8\uff1b\u4e0b\u5c42\u5916\u9732\u9762\u4ecd\u4fdd\u6301\u5e72\u51c0\u3002",
        21: "\u4e0b\u4e00\u7248 Gate 05 \u65b0\u589e\u95e8\u7981\uff1a",
        22: "\u80f6\u56ca\u5916\u8f6e\u5ed3\u5fc5\u987b\u7528\u9ad8\u5206\u8fa8\u7387\u66f2\u7ebf\uff0f\u5706\u89d2 profile \u751f\u6210\uff0c\u5e76\u5728\u771f\u5b9e\u6e32\u67d3\u4e2d\u65e0\u952f\u9f7f\u3001\u65e0\u5206\u9762\u3001\u5706\u5ea6\u8fde\u7eed\u3002",
        23: "\u672a\u6279\u51c6\u524d\u4e0d\u5f97\u91cd\u5efa\u767d\u6a21\uff1b\u4e0d\u5f97\u628a\u865a\u7ebf envelope \u7ec6\u5316\u6210\u9690\u85cf\u8f68\u9053\u3001\u5b54\u3001\u7403\u7c27\u3001\u7d27\u56fa\u4ef6\u6216\u8026\u5408\u3002",
    }

    common_style = """
      .title{font:800 36px -apple-system,"PingFang SC",sans-serif;fill:#f5f7f8}.sub{font:500 18px -apple-system,"PingFang SC",sans-serif;fill:#aab2b8}
      .panel{fill:#0a0d10;stroke:#303840;stroke-width:2}.head{font:800 21px -apple-system,"PingFang SC",sans-serif;fill:#f5f7f8}
      .note{font:550 16px -apple-system,"PingFang SC",sans-serif;fill:#c5ccd1}.badge{font:800 16px -apple-system,"PingFang SC",sans-serif;fill:#f5f7f8}
      .hidden{fill:#62d9ff18;stroke:#62d9ff;stroke-width:7;stroke-dasharray:14 12}.internal{fill:#62d9ff}.unknown{fill:none;stroke:#a6afb6;stroke-width:5;stroke-dasharray:10 9}
    """
    flat_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="940" viewBox="0 0 1400 940">
  <defs><style>{common_style}.flat{{fill:none;stroke:#55e39b;stroke-width:8;stroke-linecap:round;stroke-linejoin:round}}.yes{{fill:#55e39b}}.no{{fill:#ff8278}}</style></defs>
  <rect width="1400" height="940" fill="#080a0c"/>
  <text x="38" y="54" class="title">{text[1]}</text><text x="38" y="86" class="sub">{text[2]}</text>
  <g transform="translate(28 120)"><rect width="654" height="750" rx="16" class="panel"/><text x="22" y="38" class="head">{text[3]}</text>
    <svg x="22" y="58" width="610" height="535" viewBox="0 0 760 666"><image href="source-crops/visible-flat-lower.png" width="760" height="666"/><path class="flat" d="M205 123 Q354 70 615 126 Q710 157 735 260 L705 485 Q648 584 490 624 Q281 626 154 506 Q123 456 146 392 L178 225 Q183 159 205 123 Z"/><path class="unknown" d="M205 123 Q393 158 615 126"/></svg>
    <rect x="22" y="612" width="610" height="112" rx="12" fill="#0d1512" stroke="#55e39b" stroke-width="2"/><text x="42" y="648" class="badge yes">{text[4]}</text><text x="42" y="681" class="note">{text[5]}</text><text x="42" y="708" class="note">{text[6]}</text>
  </g>
  <g transform="translate(706 120)"><rect width="666" height="750" rx="16" class="panel"/><text x="22" y="38" class="head">{text[7]}</text>
    <svg x="22" y="58" width="622" height="538" viewBox="0 0 760 659"><image href="source-crops/circular-slide-overlap.png" width="760" height="659"/><ellipse class="hidden" cx="391" cy="296" rx="264" ry="270"/><path class="unknown" d="M125 340 Q390 590 658 337"/></svg>
    <rect x="22" y="612" width="622" height="112" rx="12" fill="#0b1419" stroke="#62d9ff" stroke-width="2"/><text x="42" y="648" class="badge internal">{text[8]}</text><text x="42" y="681" class="note">{text[9]}</text><text x="42" y="708" class="note">{text[10]}</text>
  </g>
  <rect x="28" y="890" width="1344" height="34" rx="8" fill="#15100f"/><text x="48" y="913" class="badge no">{text[11]}</text>
</svg>"""
    write_svg("flat-lower-plane.svg", flat_svg)

    interface_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="980" viewBox="0 0 1400 980">
  <defs><marker id="arrow" markerWidth="11" markerHeight="11" refX="9" refY="5.5" orient="auto"><path d="M0 0L11 5.5L0 11Z" fill="#ffb454"/></marker><style>{common_style}.pivot{{fill:none;stroke:#ffe06c;stroke-width:7}}.moving{{fill:none;stroke:#ffb454;stroke-width:8;stroke-linejoin:round}}.arrow{{fill:none;stroke:#ffb454;stroke-width:8;stroke-linecap:round}}.movingText{{fill:#ffb454}}.pivotText{{fill:#ffe06c}}</style></defs>
  <rect width="1400" height="980" fill="#080a0c"/><text x="38" y="54" class="title">{text[12]}</text><text x="38" y="86" class="sub">{text[13]}</text>
  <g transform="translate(28 120)"><rect width="654" height="758" rx="16" class="panel"/><text x="22" y="38" class="head">{text[14]}</text>
    <svg x="22" y="60" width="610" height="516" viewBox="0 0 760 643"><image href="source-crops/official-concealed-interface.png" width="760" height="643"/><ellipse class="hidden" cx="420" cy="286" rx="224" ry="235"/><circle class="pivot" cx="399" cy="309" r="76"/></svg>
    <rect x="22" y="596" width="610" height="136" rx="12" fill="#0b1419" stroke="#62d9ff" stroke-width="2"/><text x="42" y="632" class="badge internal">{text[15]}</text><text x="42" y="665" class="note">{text[16]}</text><text x="42" y="694" class="note">{text[17]}</text><text x="42" y="721" class="badge pivotText">{text[18]}</text>
  </g>
  <g transform="translate(706 120)"><rect width="666" height="758" rx="16" class="panel"/><text x="22" y="38" class="head">{text[19]}</text>
    <svg x="92" y="60" width="480" height="612" viewBox="0 0 760 1097"><image href="source-crops/upper-rotates-over-lower.png" width="760" height="1097"/><path class="moving" d="M142 4 Q375 -48 621 42 L681 430 Q654 540 536 600 L247 583 Q131 523 117 408 Z"/><ellipse class="hidden" cx="385" cy="477" rx="205" ry="118"/><circle class="pivot" cx="385" cy="477" r="58"/></svg>
    <path d="M555 190 Q630 260 560 330" class="arrow" marker-end="url(#arrow)"/><rect x="22" y="690" width="622" height="42" rx="10" fill="#16120c"/><text x="42" y="717" class="badge movingText">{text[20]}</text>
  </g>
  <rect x="28" y="900" width="1344" height="58" rx="10" fill="#111519"/><text x="50" y="925" class="note">{text[21]}</text><text x="246" y="925" class="badge">{text[22]}</text><text x="50" y="949" class="note">{text[23]}</text>
</svg>"""
    write_svg("concealed-circular-interface.svg", interface_svg)


if __name__ == "__main__":
    main()
