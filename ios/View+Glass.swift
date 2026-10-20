import SwiftUI

// ponytail: one helper, not a glass design system.
// Liquid Glass on 26+; the pre-26 material is the fallback. Floating controls only —
// cards and list fills stay material on purpose.
extension View {
    @ViewBuilder
    func liquidGlass(in shape: some Shape,
                     interactive: Bool = false,
                     fallback: Material = .regularMaterial) -> some View {
        if #available(iOS 26, macOS 26, *) {
            self.glassEffect(interactive ? .regular.interactive() : .regular, in: shape)
        } else {
            self.background(fallback, in: shape)
        }
    }
}

extension View {
    /// The one action style: a 48 point capsule. Liquid Glass on 26+, the bordered styles before.
    @ViewBuilder
    func capsuleAction(prominent: Bool = true) -> some View {
        let base = self.buttonBorderShape(.capsule).controlSize(.large)
        if #available(iOS 26, macOS 26, *) {
            if prominent { base.buttonStyle(.glassProminent) } else { base.buttonStyle(.glass) }
        } else {
            if prominent { base.buttonStyle(.borderedProminent) } else { base.buttonStyle(.bordered) }
        }
    }
}
