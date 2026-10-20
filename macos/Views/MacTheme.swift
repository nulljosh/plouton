import SwiftUI

// One accent, the same Talli blue the web uses (#5B9BD5). bcLight is kept as a name only.
extension Color {
    static let bcPrimary = Color(red: 91/255, green: 155/255, blue: 213/255)
    static let bcLight = bcPrimary
}

// MARK: - Shared Card Modifiers

private let macCardShape = RoundedRectangle(cornerRadius: 20, style: .continuous)

// Glass card: one radius (20), padding on the 4 point scale, a hairline edge, no drop shadow.
struct MacGlassCard: ViewModifier {
    @Environment(\.colorScheme) private var colorScheme
    var padding: CGFloat = 16

    func body(content: Content) -> some View {
        content
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(padding)
            .background(macCardShape.fill(colorScheme == .dark ? .regularMaterial : .ultraThinMaterial))
            .overlay(
                macCardShape.strokeBorder(
                    Color.primary.opacity(colorScheme == .dark ? 0.12 : 0.05),
                    lineWidth: 1
                )
            )
    }
}

extension View {
    func macGlassCard(padding: CGFloat = 16) -> some View { modifier(MacGlassCard(padding: padding)) }
}
