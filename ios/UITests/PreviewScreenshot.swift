import XCTest

@MainActor
final class PreviewScreenshot: XCTestCase {

    override func setUpWithError() throws {
        continueAfterFailure = false
    }

    func testCaptureAppStoreScreenshots() throws {
        let app = XCUIApplication()
        setupSnapshot(app)
        app.launchArguments.append("UITEST_SNAPSHOT")
        app.launch()

        sleep(3)
        let gotIt = app.buttons["Got it"]
        if gotIt.waitForExistence(timeout: 3) {
            gotIt.tap()
            sleep(1)
        }
        shoot("01-Home")

        // The other three tabs: Status, Messages, Settings.
        for (index, name) in ["Status", "Messages", "Settings"].enumerated() {
            let button = app.tabBars.buttons[name]
            if button.waitForExistence(timeout: 5) {
                button.tap()
                sleep(2)
                shoot("0\(index + 2)-\(name)")
            }
        }
    }

    /// fastlane's snapshot for the App Store run, plus a kept attachment so a plain xcodebuild run has the images too.
    private func shoot(_ name: String) {
        snapshot(name)
        let shot = XCTAttachment(screenshot: XCUIScreen.main.screenshot())
        shot.name = name
        shot.lifetime = .keepAlways
        add(shot)
    }
}
