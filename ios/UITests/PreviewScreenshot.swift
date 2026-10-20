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

        // The three tabs, then Settings, which is a sheet from the avatar on Home.
        for (index, name) in ["Status", "Messages"].enumerated() {
            let button = app.tabBars.buttons[name]
            if button.waitForExistence(timeout: 5) {
                button.tap()
                sleep(2)
                shoot("0\(index + 2)-\(name)")
            }
        }
        app.tabBars.buttons["Home"].tap()
        let avatar = app.buttons["Settings"]
        if avatar.waitForExistence(timeout: 5) {
            avatar.tap()
            sleep(2)
            shoot("04-Settings")
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
