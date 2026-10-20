import SwiftUI

struct MacContentView: View {
    @Environment(MacAppState.self) private var appState

    var body: some View {
        Group {
            if appState.isAuthenticated {
                AuthenticatedShell()
            } else {
                MacLoginView()
            }
        }
    }
}

private struct AuthenticatedShell: View {
    @Environment(MacAppState.self) private var appState
    @State private var showSettings = false

    var body: some View {
        @Bindable var state = appState

        // A Mac app gets a sidebar, not a phone tab bar. On macOS 26 the sidebar is Liquid Glass for free.
        NavigationSplitView {
            List(MacAppState.AppSection.allCases, selection: Binding(
                get: { appState.selectedSection },
                set: { if let section = $0 { appState.selectedSection = section } }
            )) { section in
                Label(LocalizedStringKey(section.rawValue), systemImage: section.icon)
                    .tag(section)
            }
            .navigationSplitViewColumnWidth(min: 180, ideal: 200, max: 240)
        } detail: {
            detailView
                .frame(maxWidth: .infinity, maxHeight: .infinity)
        }
        .navigationTitle(appState.selectedSection.rawValue)
        .sheet(isPresented: $showSettings) {
            MacSettingsView()
                .frame(minWidth: 420, minHeight: 360)
        }
        .toolbar {
            ToolbarItem(placement: .automatic) {
                Button { showSettings = true } label: {
                    Image(systemName: "gearshape")
                }
                .help("Settings")
            }
            ToolbarItem(placement: .automatic) {
                Button {
                    Task { await appState.refresh() }
                } label: {
                    Image(systemName: "arrow.clockwise")
                }
                .disabled(appState.isLoading)
                .help("Refresh dashboard")
            }
        }
        .overlay(alignment: .top) {
            if let error = appState.errorMessage {
                ErrorBanner(message: error) {
                    appState.errorMessage = nil
                }
                .padding(.top, 8)
            }
        }
    }

    @ViewBuilder
    private var detailView: some View {
        switch appState.selectedSection {
        case .dashboard:
            MacDashboardView()
        case .benefits:
            MacBenefitsView()
        case .messages:
            MacMessagesView()
        }
    }
}

private struct ErrorBanner: View {
    let message: String
    let onDismiss: () -> Void

    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: "exclamationmark.triangle.fill")
                .foregroundStyle(.red)
            Text(message)
                .font(.caption)
                .lineLimit(2)
            Spacer(minLength: 8)
            Button("Dismiss", action: onDismiss)
                .font(.caption.weight(.semibold))
        }
        .padding(.horizontal, 14)
        .padding(.vertical, 10)
        .liquidGlass(in: Capsule(), fallback: .ultraThinMaterial)
        .padding(.horizontal)
        .shadow(radius: 8, y: 2)
    }
}
