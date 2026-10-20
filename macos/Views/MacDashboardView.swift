import SwiftUI

struct MacDashboardView: View {
    @Environment(MacAppState.self) private var appState
    @Environment(\.colorScheme) private var colorScheme

    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                if appState.isOffline {
                    offlineBanner
                } else if appState.isSyncStale {
                    staleSyncBanner
                }

                if appState.isFilingWindowOpen && !appState.isCurrentMonthFiled {
                    filingWindowBanner
                } else if appState.isFilingWindowOpen && appState.isCurrentMonthFiled {
                    reportFiledBanner
                }

                MissedPaymentView(
                    fetch: { try await MacAPIClient.shared.missedPayment() },
                    arrived: { try? await MacAPIClient.shared.markPaid(month: $0) }
                )

                // the whole first screen is the number; Details sits below the fold
                paymentCard
                    .containerRelativeFrame(.vertical) { length, _ in length - 48 }

                DisclosureGroup("Details") {
                    VStack(spacing: 20) {
                        calendarCard
                        if !appState.statusMessages.isEmpty {
                            recentMessagesCard
                        }
                    }
                    .padding(.top, 12)
                }
                .font(.footnote)
                .foregroundStyle(.secondary)
            }
            .padding(.horizontal, 20)
            .padding(.vertical, 24)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .top)
    }

    // MARK: - Payment Card

    // Same hero as the web dashboard: thin tabular digits, a green dollar sign. The amount is set
    // huge and scales down to whatever the window gives it, so it always fills the width.
    private var paymentCard: some View {
        VStack(spacing: 8) {
            Text("NEXT PAYMENT")
                .font(.caption.weight(.medium))
                .foregroundStyle(.secondary)
                .ltrTracking(0.5)

            (Text("$").foregroundStyle(Color.green)
             + Text(appState.paymentAmountText.replacingOccurrences(of: ".00", with: "").replacingOccurrences(of: "$", with: "")))
                .font(.system(size: 600, weight: .thin).monospacedDigit())
                .minimumScaleFactor(0.05)
                .lineLimit(1)
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .contentTransition(.numericText())

            Text(appState.countdownText)
                .font(.title.weight(.light))
                .foregroundStyle(Color.bcLight)

            Text(appState.nextPaymentDateText)
                .font(.subheadline)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity)
    }

    // MARK: - Calendar

    private var calendarCard: some View {
        VStack(alignment: .leading, spacing: 14) {
            MacPaymentCalendarView(paymentDate: appState.parsedNextPaymentDate)
            Divider()
            SupplementsView { try await MacAPIClient.shared.supplements(save: $0) }
        }
        .frame(maxWidth: .infinity)
        .padding(20)
            .background(macCard)
    }

    // MARK: - Recent Messages

    private var recentMessagesCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Image(systemName: "envelope.fill")
                    .foregroundStyle(Color.bcPrimary)
                Text("Recent Messages")
                    .font(.headline)
                Spacer()
                Text("\(appState.statusMessages.count) total")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }

            Divider()

            ForEach(appState.statusMessages.prefix(3)) { message in
                HStack(alignment: .top, spacing: 10) {
                    Circle()
                        .fill(Color.bcLight)
                        .frame(width: 6, height: 6)
                        .padding(.top, 6)
                    VStack(alignment: .leading, spacing: 2) {
                        Text(message.text)
                            .font(.subheadline)
                            .lineLimit(2)
                        if let ts = message.timestamp, let date = MacDateParsing.parse(ts) {
                            Text(date.formatted(date: .abbreviated, time: .shortened))
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
                    }
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(20)
        .background(macCard)
    }

    // MARK: - Shared

    private var filingWindowBanner: some View {
        HStack(spacing: 10) {
            Image(systemName: "exclamationmark.circle.fill")
                .foregroundStyle(Color.orange)
            VStack(alignment: .leading, spacing: 2) {
                Text("Report window open")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(Color.orange)
                Text("Closes the 5th")
                    .font(.caption2)
                    .foregroundStyle(.secondary)
            }
            Spacer()
            Button("Already filed") {
                Task { await appState.markMonthFiled() }
            }
            .font(.caption.weight(.semibold))
            .controlSize(.small)
        }
        .padding(12)
        .background(Color.orange.opacity(0.1), in: RoundedRectangle(cornerRadius: 20, style: .continuous))
        .overlay(RoundedRectangle(cornerRadius: 20, style: .continuous).strokeBorder(Color.orange.opacity(0.3), lineWidth: 1))
    }

    private var reportFiledBanner: some View {
        HStack(spacing: 10) {
            Image(systemName: "checkmark.circle.fill")
                .foregroundStyle(Color.green)
            Text("Report filed this month")
                .font(.caption.weight(.semibold))
                .foregroundStyle(Color.green)
            Spacer()
        }
        .padding(12)
        .background(Color.green.opacity(0.1), in: RoundedRectangle(cornerRadius: 20, style: .continuous))
        .overlay(RoundedRectangle(cornerRadius: 20, style: .continuous).strokeBorder(Color.green.opacity(0.3), lineWidth: 1))
    }

    private var staleSyncBanner: some View {
        HStack {
            Image(systemName: "clock.arrow.circlepath")
                .font(.caption)
            Text(appState.lastSyncDate.map {
                "Not up to date -- last synced \($0.formatted(.relative(presentation: .named)))"
            } ?? "Not up to date -- never synced")
                .font(.caption)
            Spacer()
        }
        .padding(10)
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 20, style: .continuous))
    }

    private var offlineBanner: some View {
        HStack {
            Image(systemName: "wifi.slash")
                .font(.caption)
            Text("Offline -- showing cached data")
                .font(.caption)
            Spacer()
        }
        .padding(10)
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 20, style: .continuous))
    }

    private var macCard: some View {
        RoundedRectangle(cornerRadius: 20, style: .continuous)
            .fill(colorScheme == .dark ? .regularMaterial : .ultraThinMaterial)
            .shadow(color: .black.opacity(colorScheme == .dark ? 0.25 : 0.06), radius: 10, y: 3)
            .overlay(
                RoundedRectangle(cornerRadius: 20, style: .continuous)
                    .strokeBorder(Color.primary.opacity(colorScheme == .dark ? 0.12 : 0.05), lineWidth: 1)
            )
    }
}
