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

    /// The sign-in screen opens the federal-only finder with no account.
    func testFederalFinderWithoutAccount() throws {
        let app = XCUIApplication()
        app.launch()
        let link = app.buttons["Federal benefits, no account needed"]
        XCTAssertTrue(link.waitForExistence(timeout: 10))
        link.tap()
        XCTAssertTrue(app.staticTexts["Find what you are missing"].waitForExistence(timeout: 15))
        attach("10-Federal-intro")
        app.buttons["Start"].tap()
        sleep(1)
        attach("11-Federal-question")
    }

    /// fastlane's snapshot for the App Store run, plus a kept attachment so a plain xcodebuild run has the images too.
    private func shoot(_ name: String) {
        snapshot(name)
        attach(name)
    }

    private func attach(_ name: String) {
        let shot = XCTAttachment(screenshot: XCUIScreen.main.screenshot())
        shot.name = name
        shot.lifetime = .keepAlways
        add(shot)
    }
}
