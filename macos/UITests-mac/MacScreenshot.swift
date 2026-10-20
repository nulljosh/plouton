import XCTest

@MainActor
final class MacScreenshot: XCTestCase {

    override func setUpWithError() throws {
        continueAfterFailure = false
    }

    func testCaptureMacScreenshot() throws {
        try capture(dark: false)
    }

    /// Every tab in dark mode too, for QA. Same files, a "-dark" suffix.
    func testCaptureMacScreenshotDark() throws {
        try capture(dark: true)
    }

    private func capture(dark: Bool) throws {
        let app = XCUIApplication()
        // An environment flag, not a launch argument: AppKit reads a bare argument
        // as a file to open, and SwiftUI then skips the main window.
        app.launchEnvironment["UITEST_SNAPSHOT"] = "1"
        app.launchEnvironment["UITEST_APPEARANCE"] = dark ? "dark" : "light"
        app.launch()
        app.activate()
        XCTAssertTrue(app.windows.firstMatch.waitForExistence(timeout: 20), "App window never appeared")
        sleep(2)
        let suffix = dark ? "-dark" : ""
        save(app, "1-main" + suffix)
        for (i, page) in ["Status", "Messages", "Settings"].enumerated() {
            let item = app.buttons[page].firstMatch
            guard item.waitForExistence(timeout: 5) else { continue }
            item.click()
            sleep(2)
            save(app, "\(i + 2)-\(page.lowercased())" + suffix)
        }
    }

    private func save(_ app: XCUIApplication, _ name: String) {
        let window = app.windows.allElementsBoundByIndex.first { $0.frame.width > 200 && $0.frame.height > 200 } ?? app.windows.firstMatch
        let screenshot = window.screenshot()
        let shot = XCTAttachment(screenshot: screenshot)
        shot.name = name
        shot.lifetime = .keepAlways
        add(shot)
        let dir = NSTemporaryDirectory() + "talli-mac-screenshots"
        do {
            try FileManager.default.createDirectory(atPath: dir, withIntermediateDirectories: true)
            try screenshot.pngRepresentation.write(to: URL(fileURLWithPath: "\(dir)/\(name).png"))
        } catch {
            XCTFail("Screenshot write failed: \(error)")
        }
    }
}
