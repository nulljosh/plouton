import AppIntents
import Foundation

// Siri, Spotlight, the Action button and the long-press menu on the app icon all read these.
// Phrases need the app name, so Siri hears "next cheque in Talli".

struct NextChequeIntent: AppIntent {
    static let title: LocalizedStringResource = "Next cheque"
    static let description = IntentDescription("When your next payment lands and how much it is.")

    func perform() async throws -> some IntentResult & ProvidesDialog {
        // Last dashboard the app saved; no network, no sign-in prompt.
        guard let data = UserDefaults.standard.data(forKey: "cached-dashboard-data"),
              let d = try? JSONDecoder().decode(DashboardData.self, from: data),
              let amount = d.paymentAmount, let date = d.nextPaymentDate else {
            return .result(dialog: "Open Talli once so it can fetch your next payment.")
        }
        return .result(dialog: "Your next payment is \(amount) on \(date).")
    }
}

struct MarkPaidIntent: AppIntent {
    static let title: LocalizedStringResource = "Mark as paid"
    static let description = IntentDescription("Mark this month's cheque as received.")

    func perform() async throws -> some IntentResult & ProvidesDialog {
        let c = Calendar.current, now = Date()
        let month = String(format: "%04d-%02d", c.component(.year, from: now), c.component(.month, from: now))
        do {
            _ = try await APIClient.shared.setPaidStatus(paid: true, month: month)
            return .result(dialog: "Marked this month's cheque as paid.")
        } catch {
            return .result(dialog: "Open Talli and sign in first.")
        }
    }
}

struct OpenMessagesIntent: AppIntent {
    static let title: LocalizedStringResource = "Open messages"
    static let description = IntentDescription("Jump straight to your ministry messages.")
    static let openAppWhenRun = true

    func perform() async throws -> some IntentResult {
        UserDefaults.standard.set(2, forKey: "pending-tab")
        return .result()
    }
}

struct TalliShortcuts: AppShortcutsProvider {
    static var appShortcuts: [AppShortcut] {
        AppShortcut(intent: NextChequeIntent(),
                    phrases: ["Next cheque in \(.applicationName)", "When is my next payment in \(.applicationName)"],
                    shortTitle: "Next cheque", systemImageName: "calendar")
        AppShortcut(intent: MarkPaidIntent(),
                    phrases: ["Mark paid in \(.applicationName)", "My cheque landed in \(.applicationName)"],
                    shortTitle: "Mark as paid", systemImageName: "checkmark.circle")
        AppShortcut(intent: OpenMessagesIntent(),
                    phrases: ["Open messages in \(.applicationName)", "Check my letters in \(.applicationName)"],
                    shortTitle: "Messages", systemImageName: "message")
    }
}
