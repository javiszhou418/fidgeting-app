import AppKit
import Foundation

guard CommandLine.arguments.count == 3 else {
    fputs("usage: export_pack_layers.swift CONTACT_SHEET.png OUTPUT_DIRECTORY\n", stderr)
    exit(2)
}

let inputURL = URL(fileURLWithPath: CommandLine.arguments[1])
let outputDirectory = URL(fileURLWithPath: CommandLine.arguments[2], isDirectory: true)

guard let source = NSImage(contentsOf: inputURL) else {
    fputs("could not read contact sheet\n", stderr)
    exit(3)
}

try FileManager.default.createDirectory(
    at: outputDirectory,
    withIntermediateDirectories: true)

struct PackCrop {
    let id: String
    let x: CGFloat
    let topY: CGFloat
}

let crops = [
    PackCrop(id: "standard", x: 145, topY: 52),
    PackCrop(id: "refined", x: 586, topY: 52),
    PackCrop(id: "signature", x: 1028, topY: 52),
    PackCrop(id: "chase", x: 145, topY: 535),
    PackCrop(id: "grail", x: 586, topY: 535),
    PackCrop(id: "one-of-one", x: 1028, topY: 535)
]

let canvasWidth: CGFloat = 384
let canvasHeight: CGFloat = 512
let cropWidth: CGFloat = 348
let cropHeight: CGFloat = 428
let destinationLeft: CGFloat = 18
let destinationTop: CGFloat = 42

enum PackLayer: String, CaseIterable {
    case body
    case flap
}

func point(_ x: CGFloat, _ topY: CGFloat) -> NSPoint {
    NSPoint(
        x: destinationLeft + x,
        y: canvasHeight - destinationTop - topY)
}

func silhouettePath() -> NSBezierPath {
    let path = NSBezierPath()
    path.move(to: point(6, 3))
    path.line(to: point(342, 3))
    path.line(to: point(342, 43))
    path.curve(
        to: point(336, 66),
        controlPoint1: point(342, 51),
        controlPoint2: point(337, 59))
    path.curve(
        to: point(336, 381),
        controlPoint1: point(343, 132),
        controlPoint2: point(343, 342))
    path.line(to: point(342, 425))
    path.line(to: point(6, 425))
    path.line(to: point(12, 381))
    path.curve(
        to: point(12, 66),
        controlPoint1: point(5, 342),
        controlPoint2: point(5, 132))
    path.curve(
        to: point(6, 43),
        controlPoint1: point(11, 59),
        controlPoint2: point(6, 51))
    path.close()
    return path
}

func layerClipRect(_ layer: PackLayer) -> NSRect {
    let top: CGFloat = layer == .flap ? 0 : 50
    let height: CGFloat = layer == .flap ? 60 : cropHeight - top
    return NSRect(
        x: 0,
        y: canvasHeight - destinationTop - top - height,
        width: canvasWidth,
        height: height)
}

func render(_ crop: PackCrop, layer: PackLayer) throws {
    guard let bitmap = NSBitmapImageRep(
        bitmapDataPlanes: nil,
        pixelsWide: Int(canvasWidth),
        pixelsHigh: Int(canvasHeight),
        bitsPerSample: 8,
        samplesPerPixel: 4,
        hasAlpha: true,
        isPlanar: false,
        colorSpaceName: .deviceRGB,
        bytesPerRow: 0,
        bitsPerPixel: 0),
          let graphicsContext = NSGraphicsContext(bitmapImageRep: bitmap) else {
        throw NSError(
            domain: "GachaPackLayerExport",
            code: 1,
            userInfo: [NSLocalizedDescriptionKey: "could not create bitmap context"])
    }

    NSGraphicsContext.saveGraphicsState()
    NSGraphicsContext.current = graphicsContext
    defer { NSGraphicsContext.restoreGraphicsState() }

    NSColor.clear.setFill()
    NSRect(x: 0, y: 0, width: canvasWidth, height: canvasHeight).fill()
    NSGraphicsContext.current?.imageInterpolation = .high

    NSGraphicsContext.saveGraphicsState()
    silhouettePath().addClip()
    NSBezierPath(rect: layerClipRect(layer)).addClip()

    let sourceRect = NSRect(
        x: crop.x,
        y: source.size.height - crop.topY - cropHeight,
        width: cropWidth,
        height: cropHeight)
    let destinationRect = NSRect(
        x: destinationLeft,
        y: canvasHeight - destinationTop - cropHeight,
        width: cropWidth,
        height: cropHeight)
    source.draw(
        in: destinationRect,
        from: sourceRect,
        operation: .copy,
        fraction: 1,
        respectFlipped: true,
        hints: [.interpolation: NSImageInterpolation.high.rawValue])
    NSGraphicsContext.restoreGraphicsState()

    guard let png = bitmap.representation(using: .png, properties: [:]) else {
        throw NSError(
            domain: "GachaPackLayerExport",
            code: 1,
            userInfo: [NSLocalizedDescriptionKey: "could not encode PNG"])
    }

    let outputURL = outputDirectory.appendingPathComponent(
        "gacha-pack-\(crop.id)-\(layer.rawValue).png")
    try png.write(to: outputURL, options: .atomic)
}

for crop in crops {
    for layer in PackLayer.allCases {
        try render(crop, layer: layer)
    }
}
