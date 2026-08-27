import Foundation
import RiveRuntime
import SwiftUI

@main
struct RiveAssetInspectorApp: App {
    var body: some Scene {
        WindowGroup {
            Color.black
                .ignoresSafeArea()
                .task {
                    await Self.inspect()
                }
        }
    }

    @MainActor
    private static func inspect() async {
        do {
            guard let assetURL = Bundle.main.url(
                forResource: "gacha-single-draw-jumbotron",
                withExtension: "riv") else { throw InspectorError.missingAsset }
            let data = try Data(contentsOf: assetURL)
            RiveLog.logger = RiveLog.system(levels: .all)

            let worker = try await Worker()
            let file = try await File(source: .data(data), worker: worker)
            let artboardNames = try await file.getArtboardNames()
            print("asset=\(assetURL.path)")
            print("bytes=\(data.count)")
            print("artboards=\(artboardNames)")

            for artboardName in artboardNames {
                let artboard = try await file.createArtboard(artboardName)
                let stateMachines = try await artboard.getStateMachineNames()
                print("artboard[\(artboardName)].stateMachines=\(stateMachines)")
                do {
                    let info = try await file.getDefaultViewModelInfo(for: artboard)
                    print(
                        "artboard[\(artboardName)].defaultViewModel="
                        + "\(info.viewModelName)/\(info.instanceName)")
                } catch {
                    print("artboard[\(artboardName)].defaultViewModel.error=\(error)")
                }
            }

            let viewModelNames = try await file.getViewModelNames()
            print("viewModels=\(viewModelNames)")
            for viewModelName in viewModelNames {
                let instances = try await file.getInstanceNames(of: viewModelName)
                let properties = try await file.getProperties(of: viewModelName)
                print("viewModel[\(viewModelName)].instances=\(instances)")
                for property in properties {
                    print(
                        "viewModel[\(viewModelName)].property="
                        + "\(property.name):\(property.type)")
                }
            }
        } catch {
            print("inspector.error=\(error)")
        }
    }

    private enum InspectorError: Error {
        case missingAsset
    }
}
