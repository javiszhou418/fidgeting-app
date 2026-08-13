import AppKit
import Foundation

private enum RenderError: Error, CustomStringConvertible {
    case usage
    case unreadable(URL)
    case bitmap
    case png

    var description: String {
        switch self {
        case .usage:
            return "usage: render_svg.swift OUTPUT_DIRECTORY INPUT.svg [INPUT.svg ...]"
        case .unreadable(let url):
            return "unable to read SVG: \(url.path)"
        case .bitmap:
            return "unable to allocate RGBA bitmap"
        case .png:
            return "unable to encode PNG"
        }
    }
}

private func render(svg source: URL, to destination: URL) throws {
    guard let image = NSImage(contentsOf: source) else {
        throw RenderError.unreadable(source)
    }
    guard let bitmap = NSBitmapImageRep(
        bitmapDataPlanes: nil,
        pixelsWide: 1024,
        pixelsHigh: 1024,
        bitsPerSample: 8,
        samplesPerPixel: 4,
        hasAlpha: true,
        isPlanar: false,
        colorSpaceName: NSColorSpaceName.deviceRGB,
        bytesPerRow: 0,
        bitsPerPixel: 0) else {
        throw RenderError.bitmap
    }

    NSGraphicsContext.saveGraphicsState()
    defer { NSGraphicsContext.restoreGraphicsState() }
    guard let graphics = NSGraphicsContext(bitmapImageRep: bitmap) else {
        throw RenderError.bitmap
    }
    graphics.imageInterpolation = NSImageInterpolation.high
    NSGraphicsContext.current = graphics
    graphics.cgContext.clear(CGRect(x: 0, y: 0, width: 1024, height: 1024))
    image.draw(
        in: NSRect(x: 0, y: 0, width: 1024, height: 1024),
        from: .zero,
        operation: .sourceOver,
        fraction: 1,
        respectFlipped: true,
        hints: [.interpolation: NSImageInterpolation.high])
    graphics.flushGraphics()

    guard let data = bitmap.representation(
        using: NSBitmapImageRep.FileType.png,
        properties: [:]) else {
        throw RenderError.png
    }
    try data.write(to: destination, options: Data.WritingOptions.atomic)
}

do {
    let arguments = Array(CommandLine.arguments.dropFirst())
    guard arguments.count >= 2 else { throw RenderError.usage }
    let outputDirectory = URL(fileURLWithPath: arguments[0], isDirectory: true)
    try FileManager.default.createDirectory(
        at: outputDirectory,
        withIntermediateDirectories: true)

    for sourcePath in arguments.dropFirst() {
        let source = URL(fileURLWithPath: sourcePath)
        let destination = outputDirectory
            .appendingPathComponent(source.deletingPathExtension().lastPathComponent)
            .appendingPathExtension("png")
        try render(svg: source, to: destination)
        print(destination.path)
    }
} catch {
    FileHandle.standardError.write(Data("render_svg_error=\(error)\n".utf8))
    exit(1)
}
