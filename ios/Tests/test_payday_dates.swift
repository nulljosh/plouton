// Standalone self-check for the pure date math in PaydayNotificationScheduler.
// Run with: swift ios/Notifications/test_payday_dates.swift
// (Copies the two static functions verbatim since UserNotifications needs a real app target.)
import Foundation

enum Scheduler {
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

    static func reportNudgeFireDate(from now: Date, currentMonthFiled: Bool, calendar: Calendar = .current) -> Date? {
        var components = calendar.dateComponents([.year, .month], from: now)
        components.day = 4
        components.hour = 9
        components.minute = 0
        guard let thisMonth = calendar.date(from: components) else { return nil }
        if !currentMonthFiled && thisMonth > now { return thisMonth }
        return calendar.date(byAdding: .month, value: 1, to: thisMonth)
    }

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

    static func paydayReminderFireDate(paymentDate: Date, from now: Date, calendar: Calendar = .current) -> Date? {
        guard let dayBefore = calendar.date(byAdding: .day, value: -1, to: paymentDate) else { return nil }
        var components = calendar.dateComponents([.year, .month, .day], from: max(dayBefore, now))
        components.hour = 9
        components.minute = 0
        return calendar.date(from: components)
    }
}

var cal = Calendar(identifier: .gregorian)
cal.timeZone = TimeZone(identifier: "America/Vancouver")!

func date(_ y: Int, _ m: Int, _ d: Int, _ h: Int = 0) -> Date {
    cal.date(from: DateComponents(year: y, month: m, day: d, hour: h))!
}

func assertDay(_ got: Date?, _ y: Int, _ m: Int, _ d: Int, _ h: Int, _ label: String) {
    guard let got else { fatalError("FAIL \(label): got nil") }
    let c = cal.dateComponents([.year, .month, .day, .hour], from: got)
    precondition(c.year == y && c.month == m && c.day == d && c.hour == h, "FAIL \(label): got \(c)")
    print("ok  \(label)")
}

// Today is day 1 -> fires today at 9am (the window just opened).
assertDay(Scheduler.nextReportingWindowFireDate(from: date(2026, 9, 1), calendar: cal), 2026, 9, 1, 9, "day 1 -> fires today")

// Mid-window (day 3) -> next occurrence is next month's 1st.
assertDay(Scheduler.nextReportingWindowFireDate(from: date(2026, 9, 3), calendar: cal), 2026, 10, 1, 9, "mid-window -> next month")

// After the window (day 20) -> fires next month's 1st.
assertDay(Scheduler.nextReportingWindowFireDate(from: date(2026, 9, 20), calendar: cal), 2026, 10, 1, 9, "after window -> next month")

// December -> January year rollover.
assertDay(Scheduler.nextReportingWindowFireDate(from: date(2026, 12, 20), calendar: cal), 2027, 1, 1, 9, "december -> january rollover")

// Payday in 5 days -> fires the day before at 9am.
assertDay(Scheduler.paydayReminderFireDate(paymentDate: date(2026, 9, 23), from: date(2026, 9, 18), calendar: cal), 2026, 9, 22, 9, "payday reminder day before")

// Payday is tomorrow -> "day before" is today, still fires today at 9am (not in the past if run before 9am).
assertDay(Scheduler.paydayReminderFireDate(paymentDate: date(2026, 9, 19), from: date(2026, 9, 18, 14), calendar: cal), 2026, 9, 18, 9, "payday reminder clamps to today")

// Day 2, not filed -> nudge on the 4th of this month.
assertDay(Scheduler.reportNudgeFireDate(from: date(2026, 9, 2), currentMonthFiled: false, calendar: cal), 2026, 9, 4, 9, "nudge this month when not filed")

// Day 2, already filed -> skip to next month's 4th.
assertDay(Scheduler.reportNudgeFireDate(from: date(2026, 9, 2), currentMonthFiled: true, calendar: cal), 2026, 10, 4, 9, "filed -> next month")

// Day 4 after 9am -> next month's 4th, never a nudge in the past.
assertDay(Scheduler.reportNudgeFireDate(from: date(2026, 9, 4, 14), currentMonthFiled: false, calendar: cal), 2026, 10, 4, 9, "past the nudge -> next month")

// December -> January rollover.
assertDay(Scheduler.reportNudgeFireDate(from: date(2026, 12, 20), currentMonthFiled: false, calendar: cal), 2027, 1, 4, 9, "nudge december -> january")

// Earnings limit: quiet under 80 percent, "near" from 80, "over" past the limit, nothing with no exemption.
precondition(Scheduler.earningsWarning(earned: 10_000, exemption: 18_000) == nil, "FAIL earnings under 80%")
precondition(Scheduler.earningsWarning(earned: 14_400, exemption: 18_000)?.level == "near", "FAIL earnings at 80%")
precondition(Scheduler.earningsWarning(earned: 18_500, exemption: 18_000)?.level == "over", "FAIL earnings over")
precondition(Scheduler.earningsWarning(earned: 500, exemption: 0) == nil, "FAIL no exemption")
print("ok  earnings warning levels")

print("all payday scheduler checks passed")
