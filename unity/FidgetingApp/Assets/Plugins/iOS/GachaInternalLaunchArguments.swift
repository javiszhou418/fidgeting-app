import Foundation

/// Returns whether the current process contains either `name value` or
/// `name=value`. This bridge deliberately knows nothing about gacha modes or
/// sequence names; the internal-only C# factory owns that policy and is
/// compiled out of production builds.
@_cdecl("CodexProcessHasLaunchArgumentValue")
public func CodexProcessHasLaunchArgumentValue(
    _ rawName: UnsafePointer<CChar>?,
    _ rawValue: UnsafePointer<CChar>?
) -> Int32 {
    guard let rawName, let rawValue else {
        return 0
    }

    let name = String(cString: rawName)
    let value = String(cString: rawValue)
    guard !name.isEmpty, !value.isEmpty else {
        return 0
    }

    let arguments = ProcessInfo.processInfo.arguments
    let joined = "\(name)=\(value)"
    for index in arguments.indices {
        if arguments[index] == joined {
            return 1
        }

        let next = arguments.index(after: index)
        if arguments[index] == name,
           next < arguments.endIndex,
           arguments[next] == value {
            return 1
        }
    }

    return 0
}
