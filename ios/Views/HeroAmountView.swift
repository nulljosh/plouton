import CoreText
import SwiftUI
#if canImport(UIKit)
import UIKit
private typealias PlatformFont = UIFont
#else
import AppKit
private typealias PlatformFont = NSFont
#endif

/// The Home amount in Talli Display (fonts/TalliDisplay-Semibold.ttf, made by scripts/gen_font.py), shared by
/// iPhone and Mac. Same rule as the web hero: the figures are up to `maxHeight` tall at their own proportions; when
/// `width` is too narrow for that they stretch taller, never more than 1.5x. The $ is half size, green, raised to
/// the top of the figures, the way prices are set. It breathes slowly unless Reduce Motion is on.
struct HeroAmountView: View {
    let digits: String
    let width: CGFloat
    let maxHeight: CGFloat
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    static let fontName = "TalliDisplay-Semibold"
    // Font units per 1000: top of the figures, foot of the comma, the $ top, cap stretch limit, gap after the $.
    private static let top: CGFloat = 712, box: CGFloat = 805, dollarTop: CGFloat = 788
    private static let maxStretch: CGFloat = 1.5, dollarScale: CGFloat = 0.5, gap: CGFloat = 36
    /// Room on each side so the figures never run to the screen edge (points, same 24 as the web).
    static let inset: CGFloat = 24

    /// Registers the bundled font once per process; no Info.plist entry needed.
    private static let registered: Bool = {
        guard let url = Bundle.main.url(forResource: fontName, withExtension: "ttf") else { return false }
        return CTFontManagerRegisterFontsForURL(url as CFURL, .process, nil)
    }()

    /// Width of `text` in font units at 1000 points.
    private static func units(_ text: String, size: CGFloat = 1000) -> CGFloat {
        _ = registered
        let font = PlatformFont(name: fontName, size: size) ?? PlatformFont.systemFont(ofSize: size, weight: .semibold)
        return (text as NSString).size(withAttributes: [.font: font]).width
    }

    /// Point size and vertical stretch for this box.
    static func layout(digits: String, width: CGFloat, maxHeight: CGFloat) -> (size: CGFloat, stretch: CGFloat) {
        let natural = units("$", size: 1000 * dollarScale) + gap + units(digits)
        let byHeight = maxHeight / box * 1000
        let byWidth = max(0, width - 2 * inset) / natural * 1000
        if byHeight <= byWidth { return (byHeight, 1) }
        return (byWidth, min(byHeight / byWidth, maxStretch))
    }

    var body: some View {
        let (size, stretch) = Self.layout(digits: digits, width: width, maxHeight: maxHeight)
        let u = size / 1000
        HStack(alignment: .firstTextBaseline, spacing: Self.gap * u) {
            Text("$")
                .font(.custom(Self.fontName, fixedSize: size * Self.dollarScale))
                .foregroundStyle(Color.green)
                .baselineOffset((Self.top - Self.dollarTop * Self.dollarScale) * u)
            Text(digits)
                .font(.custom(Self.fontName, fixedSize: size))
                .contentTransition(.numericText())
        }
        .fixedSize()
        // The text box starts at the font's ascent (1000 units); lift it so the figures' tops meet the frame's top.
        .offset(y: -(1000 - Self.top) * u)
        .scaleEffect(x: 1, y: stretch, anchor: .top)
        .frame(height: Self.box * u * stretch, alignment: .top)
        .phaseAnimator(reduceMotion ? [false] : [false, true]) { view, inhale in
            view.scaleEffect(inhale ? 1.025 : 1).opacity(inhale ? 0.88 : 1)
        } animation: { _ in .easeInOut(duration: 3) }
        .frame(maxWidth: .infinity)
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("$" + digits)
    }
}
