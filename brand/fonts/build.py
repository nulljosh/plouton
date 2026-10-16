"""Talli Sans: a monoline, proportionally spaced typeface built from stroke skeletons.

Every glyph is a set of centre-lines on a 1000-unit em. Strokes are 80 units with
round caps, the same terminals as the tally marks in the icon. Advance widths are
computed per glyph from its drawn width plus side bearings chosen by shape
(straight stem, round, diagonal), so spacing is proportional, not monospaced.

Run: uv run --with fonttools --with shapely python build.py
"""
import math
from shapely.geometry import LineString
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

STROKE = 80
H = STROKE / 2

def L(*pts):
    return [list(pts)]

def A(cx, cy, rx, ry, a0, a1, n=28):
    return [[(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
              cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]]

def P(*parts):
    out = []
    for p in parts:
        out += p
    return out

def rot180(paths, cx=200, cy=350):
    return [[(2 * cx - x, 2 * cy - y) for x, y in p] for p in paths]

dot = lambda x, y: L((x, y), (x, y + 0.1))

G = {}
# ---- capitals (skeleton cap height 660, base 40) ----
G['A'] = P(L((0,40),(220,660),(440,40)), L((75,230),(365,230)))
G['B'] = P(L((0,40),(0,660),(210,660)), A(210,505,155,155,90,-90), L((210,350),(0,350)),
           L((0,350),(230,350)), A(230,195,155,155,90,-90), L((230,40),(0,40)))
G['C'] = A(250,350,250,310,45,315)
G['D'] = P(L((0,40),(0,660),(170,660)), A(170,350,260,310,90,-90), L((170,40),(0,40)))
G['E'] = P(L((330,660),(0,660),(0,40),(330,40)), L((0,350),(270,350)))
G['F'] = P(L((330,660),(0,660),(0,40)), L((0,350),(270,350)))
G['G'] = P(A(250,350,250,310,45,360), L((500,350),(290,350)))
G['H'] = P(L((0,40),(0,660)), L((400,40),(400,660)), L((0,350),(400,350)))
G['I'] = L((0,40),(0,660))
G['J'] = P(L((300,660),(300,200)), A(150,200,150,160,0,-180))
G['K'] = P(L((0,40),(0,660)), L((360,660),(0,260)), L((120,380),(380,40)))
G['L'] = L((0,660),(0,40),(310,40))
G['M'] = L((0,40),(0,660),(240,250),(480,660),(480,40))
G['N'] = L((0,40),(0,660),(400,40),(400,660))
G['O'] = A(260,350,260,310,0,360)
G['P'] = P(L((0,40),(0,660),(210,660)), A(210,495,165,165,90,-90), L((210,330),(0,330)))
G['Q'] = P(A(260,350,260,310,0,360), L((340,150),(490,20)))
G['R'] = P(G['P'], L((190,330),(380,40)))
G['S'] = P(A(230,505,200,155,30,270), A(230,195,200,155,90,-150))
G['T'] = P(L((0,660),(440,660)), L((220,660),(220,40)))
G['U'] = P(L((0,660),(0,200)), A(200,200,200,160,180,360), L((400,200),(400,660)))
G['V'] = L((0,660),(220,40),(440,660))
G['W'] = L((0,660),(150,40),(300,500),(450,40),(600,660))
G['X'] = P(L((0,660),(420,40)), L((420,660),(0,40)))
G['Y'] = P(L((0,660),(220,340),(440,660)), L((220,340),(220,40)))
G['Z'] = L((0,660),(400,660),(0,40),(400,40))
# ---- lowercase (x-height skeleton 460) ----
bowl = A(190,250,190,210,0,360)
G['a'] = P(bowl, L((380,460),(380,40)))
G['b'] = P(L((0,660),(0,40)), bowl)
G['c'] = A(190,250,190,210,40,320)
G['d'] = P(bowl, L((380,660),(380,40)))
G['e'] = P(L((0,250),(400,250)), A(200,250,200,210,0,315))
G['f'] = P(L((130,40),(130,545)), A(260,545,130,115,180,70), L((20,460),(260,460)))
G['g'] = P(bowl, L((380,460),(380,-20)), A(190,-20,190,140,0,-160))
G['h'] = P(L((0,660),(0,40)), A(190,300,190,160,180,0), L((380,300),(380,40)))
G['i'] = P(L((0,40),(0,460)), dot(0,630))
G['j'] = P(L((190,460),(190,-20)), A(0,-20,190,140,0,-160), dot(190,630))
G['k'] = P(L((0,660),(0,40)), L((330,460),(0,200)), L((100,300),(350,40)))
G['l'] = L((0,660),(0,40))
G['m'] = P(L((0,460),(0,40)), A(150,310,150,150,180,0), L((300,310),(300,40)),
           A(450,310,150,150,180,0), L((600,310),(600,40)))
G['n'] = P(L((0,460),(0,40)), A(190,300,190,160,180,0), L((380,300),(380,40)))
G['o'] = A(200,250,200,210,0,360)
G['p'] = P(L((0,460),(0,-160)), bowl)
G['q'] = P(bowl, L((380,460),(380,-160)))
G['r'] = P(L((0,460),(0,40)), A(200,300,200,160,180,60))
G['s'] = P(A(180,360,160,100,30,270), A(180,150,160,110,90,-150))
G['t'] = P(L((130,640),(130,160)), A(260,160,130,120,180,270), L((20,460),(280,460)))
G['u'] = P(L((0,460),(0,200)), A(190,200,190,160,180,360), L((380,460),(380,40)))
G['v'] = L((0,460),(210,40),(420,460))
G['w'] = L((0,460),(130,40),(280,400),(430,40),(560,460))
G['x'] = P(L((0,460),(380,40)), L((380,460),(0,40)))
G['y'] = P(L((0,460),(210,40),(420,460)), L((210,40),(90,-160)))
G['z'] = L((0,460),(360,460),(0,40),(360,40))
# ---- figures ----
G['0'] = A(200,350,200,310,0,360)
G['1'] = L((40,520),(200,660),(200,40))
G['2'] = P(A(200,490,200,170,160,-40), L((353,381),(0,40),(400,40)))
G['3'] = P(A(190,505,180,155,150,-90), A(190,195,200,155,90,-150))
G['4'] = L((330,40),(330,660),(0,200),(420,200))
G['5'] = P(L((380,660),(40,660),(25,365),(115,364)), A(200,210,200,170,115,-150))
G['6'] = P(A(200,215,200,175,0,360), L((0,215),(0,420)), A(230,420,230,240,180,50))
G['7'] = L((0,660),(400,660),(130,40))
G['8'] = P(A(200,505,170,155,0,360), A(200,195,200,155,0,360))
G['9'] = rot180(G['6'])
# ---- punctuation and finance marks ----
G['.'] = dot(0,40)
G[','] = L((10,30),(-30,-120))
G[':'] = P(dot(0,40), dot(0,430))
G[';'] = P(L((10,30),(-30,-120)), dot(0,430))
G['-'] = L((0,300),(240,300))
G['+'] = P(L((0,300),(300,300)), L((150,150),(150,450)))
G['='] = P(L((0,240),(300,240)), L((0,380),(300,380)))
G['_'] = L((0,-60),(440,-60))
G['/'] = L((0,-20),(300,700))
G['('] = A(260,300,200,460,115,245)
G[')'] = A(-60,300,200,460,65,-65)
G['!'] = P(L((0,660),(0,220)), dot(0,40))
G['?'] = P(A(200,495,190,165,160,-70), L((265,340),(200,260),(200,200)), dot(200,40))
G["'"] = L((0,660),(0,520))
G['"'] = P(L((0,660),(0,520)), L((140,660),(140,520)))
G['%'] = P(A(80,560,80,100,0,360), A(330,140,80,100,0,360), L((0,40),(410,660)))
G['$'] = P(G['S'], L((230,760),(230,-60)))
G['#'] = P(L((120,40),(200,660)), L((300,40),(380,660)), L((30,230),(440,230)), L((60,470),(470,470)))
G['&'] = P(L((420,40),(60,470)), A(130,520,110,140,-30,330), L((140,380),(60,300)),
           A(180,200,150,160,150,320))
G['@'] = P(A(300,260,300,300,0,320), A(300,260,110,150,0,360), L((410,260),(410,330)))

SPACE_ADV = 260
STRAIGHT = set("BDEFHIKLMNPRbhiklmnpqruEFT!:;.,|")
STRAIGHT_R = set("HIJMNUadhilmnqu!:;.,|")
DIAG = set("AVWXYTvwxykz7/")

def outline(name):
    strokes = [LineString(p).buffer(H, cap_style=1, join_style=1, resolution=12) for p in G[name]]
    shape = unary_union(strokes)
    return shape

def sidebearings(ch, shape):
    l = 70 if ch in STRAIGHT else 45
    r = 70 if ch in STRAIGHT_R else 45
    if ch in DIAG:
        l = r = 22
    if ch in "T":
        l = r = 18
    if ch in ".,:;!'\"":
        l = r = 70
    return l, r

def to_glyph(shape, dx):
    pen = TTGlyphPen(None)
    polys = [shape] if shape.geom_type == 'Polygon' else list(shape.geoms)
    for poly in polys:
        poly = orient(poly, sign=-1.0)  # exterior clockwise, holes counter-clockwise
        for ring in [poly.exterior] + list(poly.interiors):
            pts = [(round(x + dx), round(y)) for x, y in ring.coords[:-1]]
            pen.moveTo(pts[0])
            for p in pts[1:]:
                pen.lineTo(p)
            pen.closePath()
    return pen.glyph()

names = {' ': 'space', '.': 'period', ',': 'comma', ':': 'colon', ';': 'semicolon', '-': 'hyphen',
         '+': 'plus', '=': 'equal', '_': 'underscore', '/': 'slash', '(': 'parenleft', ')': 'parenright',
         '!': 'exclam', '?': 'question', "'": 'quotesingle', '"': 'quotedbl', '%': 'percent',
         '$': 'dollar', '#': 'numbersign', '&': 'ampersand', '@': 'at',
         **{str(i): n for i, n in enumerate("zero one two three four five six seven eight nine".split())}}
gname = lambda ch: names.get(ch, ch)

glyphs = {'.notdef': TTGlyphPen(None).glyph()}
metrics = {'.notdef': (500, 0)}
cmap = {}
order = ['.notdef', 'space']
glyphs['space'] = TTGlyphPen(None).glyph(); metrics['space'] = (SPACE_ADV, 0); cmap[32] = 'space'
widths = {}
for ch in G:
    sh = outline(ch)
    minx, miny, maxx, maxy = sh.bounds
    l, r = sidebearings(ch, sh)
    dx = l - minx
    adv = round((maxx - minx) + l + r)
    gn = gname(ch)
    glyphs[gn] = to_glyph(sh, dx)
    metrics[gn] = (adv, l)
    cmap[ord(ch)] = gn
    order.append(gn)
    widths[ch] = adv

fb = FontBuilder(1000, isTTF=True)
fb.setupGlyphOrder(order)
fb.setupCharacterMap(cmap)
fb.setupGlyf(glyphs)
fb.setupHorizontalMetrics(metrics)
fb.setupHorizontalHeader(ascent=800, descent=-250)
fb.setupNameTable({'familyName': 'Talli Sans', 'styleName': 'Regular',
                   'uniqueFontIdentifier': 'TalliSans-Regular', 'fullName': 'Talli Sans Regular',
                   'psName': 'TalliSans-Regular', 'version': 'Version 1.000',
                   'copyright': 'Copyright 2026 Joshua Trommel. MIT.'})
fb.setupOS2(sTypoAscender=800, sTypoDescender=-250, usWinAscent=900, usWinDescent=300,
            sCapHeight=700, sxHeight=500, achVendID='TALI', fsType=0)
fb.setupPost()
fb.save('TalliSans-Regular.ttf')
fb.font.flavor = 'woff'
fb.font.save('TalliSans-Regular.woff')
print('glyphs', len(order), 'widths sample', {k: widths[k] for k in 'iamWO1'})
