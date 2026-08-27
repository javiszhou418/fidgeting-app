import AppKit
import CoreText
import Foundation

guard CommandLine.arguments.count == 4 || CommandLine.arguments.count == 5 else {
    fputs("usage: render_oxanium_overlay.swift INPUT.png FONT.ttf OUTPUT.png [v5|v6|v7]\n", stderr)
    exit(2)
}

let inputURL = URL(fileURLWithPath: CommandLine.arguments[1])
let fontURL = URL(fileURLWithPath: CommandLine.arguments[2])
let outputURL = URL(fileURLWithPath: CommandLine.arguments[3])
let layout = CommandLine.arguments.count == 5 ? CommandLine.arguments[4] : "v5"

guard layout == "v5" || layout == "v6" || layout == "v7" else {
    fputs("unknown layout: \(layout)\n", stderr)
    exit(2)
}

var registrationError: Unmanaged<CFError>?
if !CTFontManagerRegisterFontsForURL(fontURL as CFURL, .process, &registrationError),
   let error = registrationError?.takeRetainedValue() {
    fputs("font registration failed: \(error)\n", stderr)
    exit(3)
}

func productFont(size: CGFloat, weight: NSFont.Weight) -> NSFont {
    let descriptor = NSFontDescriptor(fontAttributes: [
        .family: "Oxanium",
        .traits: [NSFontDescriptor.TraitKey.weight: weight]
    ])
    guard let font = NSFont(descriptor: descriptor, size: size) else {
        fputs("could not create Oxanium font\n", stderr)
        exit(4)
    }
    return font
}

guard let image = NSImage(contentsOf: inputURL) else {
    fputs("could not read input image\n", stderr)
    exit(5)
}

let canvasHeight = image.size.height
let microFont = productFont(size: 14, weight: .medium)
let tierFont = productFont(size: layout == "v7" ? 20 : 28, weight: .semibold)
let microColor = layout == "v7"
    ? NSColor(calibratedWhite: 0.13, alpha: 0.92)
    : NSColor(white: 0.78, alpha: 1)
let neutralTierColor = NSColor(white: 0.84, alpha: 1)
let v7TierColors = [
    [
        NSColor(calibratedWhite: 0.72, alpha: 1),
        NSColor(calibratedRed: 0.49, green: 0.65, blue: 0.73, alpha: 1),
        NSColor(calibratedRed: 0.72, green: 0.43, blue: 0.31, alpha: 1)
    ],
    [
        NSColor(calibratedRed: 0.76, green: 0.62, blue: 0.39, alpha: 1),
        NSColor(calibratedRed: 0.60, green: 0.46, blue: 0.74, alpha: 1),
        NSColor(calibratedRed: 0.69, green: 0.62, blue: 0.78, alpha: 1)
    ]
]

func drawTopAligned(
    _ text: String,
    x: CGFloat,
    topY: CGFloat,
    font: NSFont,
    color: NSColor
) {
    let attributes: [NSAttributedString.Key: Any] = [
        .font: font,
        .foregroundColor: color
    ]
    let string = NSAttributedString(string: text, attributes: attributes)
    string.draw(at: NSPoint(x: x, y: canvasHeight - topY - font.ascender))
}

let columnX: [CGFloat]
let microRows: [(first: CGFloat, second: CGFloat)]
let tierTopY: [CGFloat]

if layout == "v6" {
    columnX = [184, 621, 1075]
    microRows = [(116, 138), (593, 613)]
    tierTopY = [451, 922]
} else if layout == "v7" {
    columnX = [209, 649, 1091]
    microRows = [(141, 163), (619, 641)]
    tierTopY = [408, 892]
} else {
    columnX = [187, 625, 1081]
    microRows = [(119, 141), (575, 597)]
    tierTopY = [429, 913]
}
let tierLabels = [
    ["STANDARD", "REFINED", "SIGNATURE"],
    ["CHASE", "GRAIL", "1 OF 1"]
]

image.lockFocus()
for row in 0..<2 {
    for column in 0..<3 {
        drawTopAligned(
            "FIDGET ARCHIVE",
            x: columnX[column],
            topY: microRows[row].first,
            font: microFont,
            color: microColor)
        drawTopAligned(
            "SERIES 01",
            x: columnX[column],
            topY: microRows[row].second,
            font: microFont,
            color: microColor)
        drawTopAligned(
            tierLabels[row][column],
            x: columnX[column],
            topY: tierTopY[row],
            font: tierFont,
            color: layout == "v7" ? v7TierColors[row][column] : neutralTierColor)
    }
}
image.unlockFocus()

guard let tiff = image.tiffRepresentation,
      let bitmap = NSBitmapImageRep(data: tiff),
      let png = bitmap.representation(using: .png, properties: [:]) else {
    fputs("could not encode output image\n", stderr)
    exit(6)
}

try png.write(to: outputURL, options: .atomic)
