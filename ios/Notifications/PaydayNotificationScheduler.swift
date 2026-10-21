import Foundation
import UserNotifications

// ponytail: local notifications only, no APNs/device tokens/server/background mode. Both
// triggers are calendar dates (reporting window is always days 1-5, payday is a known future
// date from the scrape), so UNCalendarNotificationTrigger covers it with zero backend work.
// See roadmap.md "Stashed 2026-08-10" for why a push backend was rejected.
enum PaydayNotificationScheduler {
    static let paydayId = "talli.payday"
    static let reportingWindowId = "talli.reporting-window"
    static let reportNudgeId = "talli.report-nudge"
    static let earningsId = "talli.earnings-limit"

    /// The next day-1-of-month at 9am. Only fires for *this* month if today is day 1
    /// (window just opened); any other day of the month means the next occurrence is
    /// next month's day 1, whether the window is open (days 2-5) or closed (6+).
    static func nextReportingWindowFireDate(from now: Date, calendar: Calendar = .current) -> Date? {
        let day = calendar.component(.day, from: now)
        let targetMonth = day == 1 ? now : calendar.date(byAdding: .month, value: 1, to: now)
        guard let targetMonth else { return nil }
        var components = calendar.dateComponents([.year, .month], from: targetMonth)
        components.day = 1
        components.hour = 9
        components.minute = 0
        return calendar.date(from: components)
    }

    /// 9am on the 4th, the nudge for a report not yet marked filed: this month's 4th if it
    /// is still ahead and this month is open, otherwise next month's (refreshed on each sync).
    static func reportNudgeFireDate(from now: Date, currentMonthFiled: Bool, calendar: Calendar = .current) -> Date? {
        var components = calendar.dateComponents([.year, .month], from: now)
        components.day = 4
        components.hour = 9
        components.minute = 0
        guard let thisMonth = calendar.date(from: components) else { return nil }
        if !currentMonthFiled && thisMonth > now { return thisMonth }
        return calendar.date(byAdding: .month, value: 1, to: thisMonth)
    }

    /// The warning for this year's work earnings, or nil: "near" once 80 percent of the
    /// exemption is used, "over" past it. Each level fires once a year.
    static func earningsWarning(earned: Double, exemption: Double) -> (level: String, title: String, body: String)? {
        guard exemption > 0 else { return nil }
        let money = { (n: Double) in n.formatted(.currency(code: "CAD").precision(.fractionLength(0))) }
        if earned > exemption {
            return ("over", "Over your earnings limit", "You are \(money(earned - exemption)) over this year's \(money(exemption)) exemption. Assistance drops by the amount over.")
        }
        if earned >= exemption * 0.8 {
            return ("near", "Close to your earnings limit", "\(money(exemption - earned)) left of this year's \(money(exemption)) exemption.")
        }
        return nil
    }

    /// 9am the day before `paymentDate`, or 9am today if that has already passed.
    static func paydayReminderFireDate(paymentDate: Date, from now: Date, calendar: Calendar = .current) -> Date? {
        guard let dayBefore = calendar.date(byAdding: .day, value: -1, to: paymentDate) else { return nil }
        var components = calendar.dateComponents([.year, .month, .day], from: max(dayBefore, now))
        components.hour = 9
        components.minute = 0
        return calendar.date(from: components)
    }

    static func requestAuthorizationIfNeeded() async {
        let center = UNUserNotificationCenter.current()
        // Categories must be registered every launch, not just on first prompt.
        setupNotificationCategories(center)
        let settings = await center.notificationSettings()
        guard settings.authorizationStatus == .notDetermined else { return }
        _ = try? await center.requestAuthorization(options: [.alert, .sound, .badge])
    }

    private static func setupNotificationCategories(_ center: UNUserNotificationCenter) {
        let fileReportAction = UNNotificationAction(identifier: "FILE_REPORT", title: "File report", options: [.authenticationRequired])
        let reportCategory = UNNotificationCategory(identifier: "REPORT_WINDOW", actions: [fileReportAction], intentIdentifiers: [])
        center.setNotificationCategories([reportCategory])
    }

    /// Reschedules the reminders. Safe to call after every dashboard refresh -- replacing
    /// a pending request with the same identifier is a no-op if the date hasn't moved.
    static func reschedule(nextPaymentDate: Date?, currentMonthFiled: Bool = false, earnings: (year: Int, earned: Double, exemption: Double)? = nil, now: Date = Date()) async {
        let center = UNUserNotificationCenter.current()
        let settings = await center.notificationSettings()
        guard settings.authorizationStatus == .authorized else { return }

        // Unset means on: bool(forKey:) would read a missing key as false.
        let defaults = UserDefaults.standard
        let paydayEnabled = defaults.object(forKey: "notifications_payday_enabled") as? Bool ?? true
        let reportingWindowEnabled = defaults.object(forKey: "notifications_reporting_window_enabled") as? Bool ?? true

        center.removePendingNotificationRequests(withIdentifiers: [paydayId, reportingWindowId, reportNudgeId])

        if reportingWindowEnabled, let fireDate = nextReportingWindowFireDate(from: now) {
            schedule(
                id: reportingWindowId,
                title: "Reporting window is open",
                body: "You can file your monthly report now through the 5th.",
                fireDate: fireDate,
                category: "REPORT_WINDOW",
                center: center
            )
        }

        if reportingWindowEnabled, let fireDate = reportNudgeFireDate(from: now, currentMonthFiled: currentMonthFiled) {
            schedule(
                id: reportNudgeId,
                title: "Monthly report not filed yet",
                body: "The reporting window closes on the 5th.",
                fireDate: fireDate,
                category: "REPORT_WINDOW",
                center: center
            )
        }

        // Fires a minute after the sync that crosses a level; the flag keeps it to once a year.
        let earningsEnabled = defaults.object(forKey: "notifications_earnings_enabled") as? Bool ?? true
        if earningsEnabled, let e = earnings, let w = earningsWarning(earned: e.earned, exemption: e.exemption) {
            let key = "talli.earnings-warned.\(e.year).\(w.level)"
            if !defaults.bool(forKey: key) {
                defaults.set(true, forKey: key)
                schedule(id: earningsId, title: w.title, body: w.body, fireDate: now.addingTimeInterval(60), center: center)
            }
        }

        if paydayEnabled, let paymentDate = nextPaymentDate, let fireDate = paydayReminderFireDate(paymentDate: paymentDate, from: now) {
            schedule(
                id: paydayId,
                title: "Payment coming tomorrow",
                body: "Your next payment is expected tomorrow.",
                fireDate: fireDate,
                center: center
            )
        }
    }

    private static func schedule(id: String, title: String, body: String, fireDate: Date, category: String? = nil, center: UNUserNotificationCenter) {
        let content = UNMutableNotificationContent()
        content.title = title
        content.body = body
        content.sound = .default
        if let category {
            content.categoryIdentifier = category
        }

        let components = Calendar.current.dateComponents([.year, .month, .day, .hour, .minute], from: fireDate)
        let trigger = UNCalendarNotificationTrigger(dateMatching: components, repeats: false)
        let request = UNNotificationRequest(identifier: id, content: content, trigger: trigger)
        center.add(request)
    }
}
