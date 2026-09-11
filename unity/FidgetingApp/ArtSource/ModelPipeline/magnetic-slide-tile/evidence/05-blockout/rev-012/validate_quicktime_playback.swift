import AVFoundation
import CoreVideo
import Foundation

guard CommandLine.arguments.count == 2 else {
    FileHandle.standardError.write(Data("usage: validate_quicktime_playback.swift <video>\n".utf8))
    exit(2)
}

let asset = AVURLAsset(url: URL(fileURLWithPath: CommandLine.arguments[1]))
Task {
    do {
        let playable = try await asset.load(.isPlayable)
        let duration = try await asset.load(.duration)
        guard playable,
              let track = try await asset.loadTracks(withMediaType: .video).first else {
            throw NSError(domain: "QuickTimeValidation", code: 1)
        }
        async let size = track.load(.naturalSize)
        async let frameRate = track.load(.nominalFrameRate)
        let reader = try AVAssetReader(asset: asset)
        let output = AVAssetReaderTrackOutput(
            track: track,
            outputSettings: [
                kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA,
            ])
        reader.add(output)
        guard reader.startReading() else {
            throw reader.error ?? NSError(domain: "QuickTimeValidation", code: 2)
        }
        var samples = 0
        while output.copyNextSampleBuffer() != nil {
            samples += 1
        }
        guard reader.status == .completed else {
            throw reader.error ?? NSError(domain: "QuickTimeValidation", code: 3)
        }
        let naturalSize = try await size
        let nominalFrameRate = try await frameRate
        let payload: [String: Any] = [
            "isPlayable": playable,
            "durationSeconds": CMTimeGetSeconds(duration),
            "width": Int(naturalSize.width),
            "height": Int(naturalSize.height),
            "frameRate": Double(nominalFrameRate),
            "videoSampleCount": samples,
            "readerStatus": "completed",
        ]
        let data = try JSONSerialization.data(withJSONObject: payload, options: [.prettyPrinted, .sortedKeys])
        print(String(decoding: data, as: UTF8.self))
        exit(0)
    } catch {
        FileHandle.standardError.write(Data("QuickTime validation failed: \(error)\n".utf8))
        exit(1)
    }
}
RunLoop.main.run()
