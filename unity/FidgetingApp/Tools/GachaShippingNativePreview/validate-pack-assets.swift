import CoreGraphics
import Foundation
import ImageIO

struct PixelBuffer {
    let width: Int
    let height: Int
    let pixels: [UInt8]

    func alpha(at index: Int) -> UInt8 { pixels[index * 4 + 3] }
}

struct AlphaBounds: Codable, Equatable {
    let x: Int
    let y: Int
    let width: Int
    let height: Int
}

struct LayerAudit: Codable {
    let tier: String
    let layer: String
    let file: String
    let width: Int
    let height: Int
    let alphaBounds: AlphaBounds
    let transparentCorners: Bool
    let sha256: String
}

struct DifferenceAudit: Codable {
    let firstTier: String
    let secondTier: String
    let changedVisiblePixelRatio: Double
    let passed: Bool
}

struct SourceAudit: Codable {
    let sixTiersDeclared: Bool
    let bodyFlapNamesDerivedFromTier: Bool
    let comparisonUsesAllCases: Bool
    let comparisonUsesShippingRenderer: Bool
    let sealedAndTearCapturesDeclared: Bool
}

struct PackAssetReport: Codable {
    let schemaVersion: Int
    let generatedAtUtc: String
    let expectedTierCount: Int
    let expectedLayerCount: Int
    let layers: [LayerAudit]
    let materialDifferences: [DifferenceAudit]
    let source: SourceAudit
    let commonBoundsByLayer: [String: AlphaBounds]
    let allPassed: Bool
}

private let tiers = [
    "standard", "refined", "signature", "chase", "grail", "one-of-one"
]
private let layers = ["body", "flap"]
private let requiredDifferenceRatio = 0.015

private func fail(_ message: String) -> Never {
    FileHandle.standardError.write(Data("ERROR: \(message)\n".utf8))
    exit(1)
}

private func loadPixels(_ url: URL) -> PixelBuffer {
    guard let source = CGImageSourceCreateWithURL(url as CFURL, nil),
          let image = CGImageSourceCreateImageAtIndex(source, 0, nil) else {
        fail("Unable to decode \(url.path)")
    }
    let width = image.width
    let height = image.height
    var pixels = [UInt8](repeating: 0, count: width * height * 4)
    let drewImage = pixels.withUnsafeMutableBytes { bytes -> Bool in
        guard let context = CGContext(
            data: bytes.baseAddress,
            width: width,
            height: height,
            bitsPerComponent: 8,
            bytesPerRow: width * 4,
            space: CGColorSpaceCreateDeviceRGB(),
            bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue) else {
            return false
        }
        context.draw(image, in: CGRect(x: 0, y: 0, width: width, height: height))
        return true
    }
    guard drewImage else { fail("Unable to rasterize \(url.path)") }
    return PixelBuffer(width: width, height: height, pixels: pixels)
}

private func alphaBounds(_ buffer: PixelBuffer) -> AlphaBounds {
    var minX = buffer.width
    var minY = buffer.height
    var maxX = -1
    var maxY = -1
    for y in 0..<buffer.height {
        for x in 0..<buffer.width where buffer.alpha(at: y * buffer.width + x) > 0 {
            minX = min(minX, x)
            minY = min(minY, y)
            maxX = max(maxX, x)
            maxY = max(maxY, y)
        }
    }
    guard maxX >= minX, maxY >= minY else { fail("Layer contains no visible pixels") }
    return AlphaBounds(
        x: minX,
        y: minY,
        width: maxX - minX + 1,
        height: maxY - minY + 1)
}

private func cornersAreTransparent(_ buffer: PixelBuffer) -> Bool {
    let indices = [
        0,
        buffer.width - 1,
        (buffer.height - 1) * buffer.width,
        buffer.width * buffer.height - 1
    ]
    return indices.allSatisfy { buffer.alpha(at: $0) == 0 }
}

private func differenceRatio(_ first: PixelBuffer, _ second: PixelBuffer) -> Double {
    guard first.width == second.width, first.height == second.height else { return 0 }
    var visible = 0
    var changed = 0
    for index in 0..<(first.width * first.height) {
        guard first.alpha(at: index) > 0, second.alpha(at: index) > 0 else { continue }
        visible += 1
        let offset = index * 4
        let delta = abs(Int(first.pixels[offset]) - Int(second.pixels[offset]))
            + abs(Int(first.pixels[offset + 1]) - Int(second.pixels[offset + 1]))
            + abs(Int(first.pixels[offset + 2]) - Int(second.pixels[offset + 2]))
        if delta >= 12 { changed += 1 }
    }
    return visible == 0 ? 0 : Double(changed) / Double(visible)
}

private func sha256(_ url: URL) -> String {
    let process = Process()
    process.executableURL = URL(fileURLWithPath: "/usr/bin/shasum")
    process.arguments = ["-a", "256", url.path]
    let pipe = Pipe()
    process.standardOutput = pipe
    process.standardError = Pipe()
    do { try process.run() } catch { fail("Unable to hash \(url.path): \(error)") }
    process.waitUntilExit()
    guard process.terminationStatus == 0,
          let output = String(
            data: pipe.fileHandleForReading.readDataToEndOfFile(),
            encoding: .utf8),
          let hash = output.split(separator: " ").first else {
        fail("Unable to hash \(url.path)")
    }
    return String(hash)
}

guard CommandLine.arguments.count == 3 else {
    fail("Usage: validate-pack-assets.swift <project-root> <report-json>")
}

let projectRoot = URL(fileURLWithPath: CommandLine.arguments[1], isDirectory: true)
let reportURL = URL(fileURLWithPath: CommandLine.arguments[2])
let assetRoot = projectRoot.appendingPathComponent("Assets/Plugins/iOS/GachaPacks")
var audits: [LayerAudit] = []
var buffers: [String: PixelBuffer] = [:]
var commonBounds: [String: AlphaBounds] = [:]
var passed = true

for tier in tiers {
    for layer in layers {
        let file = "gacha-pack-\(tier)-\(layer).png"
        let url = assetRoot.appendingPathComponent(file)
        guard FileManager.default.fileExists(atPath: url.path) else { fail("Missing \(file)") }
        let buffer = loadPixels(url)
        let bounds = alphaBounds(buffer)
        let transparentCorners = cornersAreTransparent(buffer)
        if buffer.width != 384 || buffer.height != 512 || !transparentCorners { passed = false }
        if let expected = commonBounds[layer], bounds != expected { passed = false }
        commonBounds[layer] = commonBounds[layer] ?? bounds
        buffers["\(tier)-\(layer)"] = buffer
        audits.append(LayerAudit(
            tier: tier,
            layer: layer,
            file: file,
            width: buffer.width,
            height: buffer.height,
            alphaBounds: bounds,
            transparentCorners: transparentCorners,
            sha256: sha256(url)))
    }
}

var differences: [DifferenceAudit] = []
for firstIndex in 0..<tiers.count {
    for secondIndex in (firstIndex + 1)..<tiers.count {
        let ratio = differenceRatio(
            buffers["\(tiers[firstIndex])-body"]!,
            buffers["\(tiers[secondIndex])-body"]!)
        let pairPassed = ratio > requiredDifferenceRatio
        passed = passed && pairPassed
        differences.append(DifferenceAudit(
            firstTier: tiers[firstIndex],
            secondTier: tiers[secondIndex],
            changedVisiblePixelRatio: ratio,
            passed: pairPassed))
    }
}

let presentation = try String(contentsOf: projectRoot.appendingPathComponent(
    "Assets/Plugins/iOS/FidgetGachaPackPresentation.swift"), encoding: .utf8)
let storefront = try String(contentsOf: projectRoot.appendingPathComponent(
    "Assets/Plugins/iOS/FidgetGachaStorefront.swift"), encoding: .utf8)
let capture = try String(contentsOf: projectRoot.appendingPathComponent(
    "Tools/GachaShippingNativePreview/capture-pack-v7.sh"), encoding: .utf8)
let sourceAudit = SourceAudit(
    sixTiersDeclared: tiers.allSatisfy {
        presentation.contains($0 == "one-of-one" ? "oneOfOne = \"one-of-one\"" : "case \($0)")
    },
    bodyFlapNamesDerivedFromTier: presentation.contains("gacha-pack-\\(rawValue)-body")
        && presentation.contains("gacha-pack-\\(rawValue)-flap"),
    comparisonUsesAllCases: storefront.contains("ForEach(GachaPackTier.allCases"),
    comparisonUsesShippingRenderer: storefront.contains(
        "GachaPackVisual(tier: tier, tearProgress: normalizedProgress)"),
    sealedAndTearCapturesDeclared: capture.contains("--preview-all-pack-tiers=0")
        && capture.contains("--preview-all-pack-tiers=0.68"))
let sourceMirror = Mirror(reflecting: sourceAudit)
passed = passed && sourceMirror.children.allSatisfy { ($0.value as? Bool) == true }

let formatter = ISO8601DateFormatter()
let report = PackAssetReport(
    schemaVersion: 1,
    generatedAtUtc: formatter.string(from: Date()),
    expectedTierCount: tiers.count,
    expectedLayerCount: tiers.count * layers.count,
    layers: audits,
    materialDifferences: differences,
    source: sourceAudit,
    commonBoundsByLayer: commonBounds,
    allPassed: passed)
let encoder = JSONEncoder()
encoder.outputFormatting = [.prettyPrinted, .sortedKeys, .withoutEscapingSlashes]
try encoder.encode(report).write(to: reportURL, options: .atomic)
print("Pack asset audit: \(passed ? "PASS" : "FAIL")")
print("Layers: \(audits.count)/\(tiers.count * layers.count)")
print("Report: \(reportURL.path)")
if !passed { exit(2) }
