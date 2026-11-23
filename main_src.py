# main_src.py — "THE WORLD IN ONE DAY": Monday 23 November 2026.
# A hand-built newspaper front page, drawn pixel by pixel with the Python
# standard library only. No network, no clock, no randomness: the same
# input always draws the same bytes.
#
# The renderer is a tiny rasterizer: an embedded 5x7 bitmap font, a small
# set of shape primitives, the day's news data, and a minimal PNG encoder.
# Every line below was written in this session, from scratch.

import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
PAPER   = (246, 241, 227)   # newsprint cream
INK     = (20, 20, 20)      # near-black ink
RED     = (166, 27, 27)     # headline red
BLUE    = (30, 79, 156)     # deep blue
TEAL    = (14, 122, 107)    # teal
GOLD    = (192, 138, 0)     # gold
GREY    = (229, 223, 206)   # light rule grey
DARK    = (22, 50, 79)      # dark navy
OCEAN   = (169, 198, 222)   # map ocean
LAND    = (217, 201, 143)   # map land
LAND2   = (198, 178, 110)   # map land shade
WHITE   = (255, 255, 255)
SKY     = (183, 214, 235)   # illustration sky
GREEN   = (46, 125, 50)
ORANGE  = (214, 106, 0)

# ------------------------------------------------------- embedded 5x7 font
# Each glyph is 7 rows of 5 cells; '#' is ink, '.' is empty. Uppercase,
# lowercase, digits and common punctuation, all drawn by hand here.
FONT = {
'A': ("..#..", ".#.#.", "#...#", "#####", "#...#", "#...#", "#...#"),
'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
'I': (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
'N': ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
'a': (".....", ".....", ".###.", "....#", ".####", "#...#", ".###."),
'b': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
'c': (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
'd': ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
'e': (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
'f': ("..##.", ".#...", "#....", "####.", "#....", "#....", "#...."),
'g': (".....", ".###.", "#...#", "#...#", ".####", "....#", ".###."),
'h': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
'i': ("..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."),
'j': ("...#.", ".....", "..##.", "...#.", "...#.", "#..#.", ".##.."),
'k': ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
'l': (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
'm': (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
'n': (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
'o': (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
'p': (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
'q': (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
'r': (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
's': (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
't': ("..#..", "..#..", ".###.", "..#..", "..#..", "..#..", "..#.."),
'u': (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"),
'v': (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
'w': (".....", ".....", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
'x': (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
'y': (".....", "#...#", "#...#", "#...#", ".####", "....#", ".###."),
'z': (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
'0': (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
'1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
'2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
'3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
'4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
'5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
'6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
'7': ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
'8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
'9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
'.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
'!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
'?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
'-': (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
'(': ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
')': ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
'/': ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
'%': ("##..#", "##.#.", "...#.", "..#..", ".#.##", "#..##", "....."),
'&': (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
'+': (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
'=': (".....", ".....", ".###.", ".....", ".###.", ".....", "....."),
'$': ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
'#': (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
'*': (".....", ".#.#.", ".###.", "#####", ".###.", ".#.#.", "....."),
'@': (".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###."),
'"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
"'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
}

def char_width(scale):
    return 5 * scale

def text_width(text, scale):
    # 1 scale unit of space between glyphs, none after the last one.
    if not text:
        return 0
    return len(text) * (5 * scale + scale) - scale

def wrap_text(text, scale, max_w):
    """Greedy word wrap. Returns a list of lines, each fitting max_w."""
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines

# ------------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = color

    def rect(self, x, y, w, h, color, t=1):
        self.fill_rect(x, y, w, t, color)
        self.fill_rect(x, y + h - t, w, t, color)
        self.fill_rect(x, y, t, h, color)
        self.fill_rect(x + w - t, y, t, h, color)

    def hline(self, x, y, w, color, t=1):
        self.fill_rect(x, y, w, t, color)

    def vline(self, x, y, h, color, t=1):
        self.fill_rect(x, y, t, h, color)

    def line(self, x0, y0, x1, y1, color, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.fill_rect(x - t // 2, y - t // 2, t, t, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                    self.set(xx, yy, color)

    def ring(self, cx, cy, r, color, t=2):
        for yy in range(cy - r - 1, cy + r + 2):
            for xx in range(cx - r - 1, cx + r + 2):
                d2 = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
                if (r - t) * (r - t) <= d2 <= r * r:
                    self.set(xx, yy, color)

    def poly(self, pts, color):
        """Scanline fill of a simple polygon (list of (x, y))."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            nodes = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xi = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
                    nodes.append(xi)
            nodes.sort()
            for k in range(0, len(nodes) - 1, 2):
                for x in range(int(nodes[k]), int(nodes[k + 1]) + 1):
                    self.set(x, y, color)

    def tri(self, a, b, c, color):
        self.poly([a, b, c], color)

    # ------------------------------------------------------------ text
    def glyph(self, x, y, ch, scale, color):
        rows = FONT.get(ch)
        if rows is None:
            rows = FONT["?"]
        for r, row in enumerate(rows):
            for c, cell in enumerate(row):
                if cell == "#":
                    self.fill_rect(x + c * scale, y + r * scale,
                                   scale, scale, color)

    def text(self, x, y, s, scale, color):
        cx = x
        for ch in s:
            self.glyph(cx, y, ch, scale, color)
            cx += 6 * scale
        return cx

    def text_center(self, x, y, w, s, scale, color):
        tw = text_width(s, scale)
        self.text(x + (w - tw) // 2, y, s, scale, color)

    def wrapped(self, x, y, s, scale, color, max_w, line_h,
                max_lines=None):
        """Draw wrapped text; returns (lines_drawn, overflowed)."""
        lines = wrap_text(s, scale, max_w)
        overflowed = False
        if max_lines is not None and len(lines) > max_lines:
            overflowed = True
            lines = lines[:max_lines]
        for i, ln in enumerate(lines):
            if text_width(ln, scale) > max_w:
                overflowed = True
            self.text(x, y + i * line_h, ln, scale, color)
        return len(lines), overflowed

# ------------------------------------------------------------ PNG encoder
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out

def encode_png(w, h, rgb):
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)  # filter: none
        raw += rgb[y * stride:(y + 1) * stride]
    idat = zlib.compress(bytes(raw), 9)
    return sig + _chunk(b"IHDR", ihdr) + _chunk(b"IDAT", idat) + \
        _chunk(b"IEND", b"")

# ---------------------------------------------------------------- news data
# 35 stories, every one dated Monday 23 November 2026 (happened, or first
# reported, on that day). Sources are the outlets that reported them.
# Order: 1-3 leads, 4-13 grid, 14-35 "also on" list.
# Regions: NA North America, LA Latin America, EU Europe, ME Middle East,
# AF Africa, AP Asia-Pacific, SP Sport.

LEADS = [
    dict(n=1, region="ME", kicker="LEAD 1 - MIDDLE EAST",
         head="TANKERS ABLAZE IN THE STRAIT OF HORMUZ",
         deck="Two tankers are struck in the world's busiest oil chokepoint; "
              "Iran says a vessel hit a mine.",
         src="UKMTO / Reuters, 23 Nov"),
    dict(n=2, region="EU", kicker="LEAD 2 - CLIMATE",
         head="COP31 CLIMATE TALKS COLLAPSE WITH NO DEAL",
         deck="Two weeks of talks in Antalya end with no deal on fossil fuels "
              "or climate finance.",
         src="Reuters / Al Jazeera, 23 Nov"),
    dict(n=3, region="NA", kicker="LEAD 3 - AMERICA",
         head="DEMOCRATS WIN BIGGEST HOUSE MAJORITY",
         deck="Flipping a North Carolina seat, Democrats seal their largest "
              "House majority in 34 years.",
         src="AP / The Guardian, 23 Nov"),
]

GRID = [
    dict(n=4, region="EU", icon="rubble",
         head="14 MISSING AFTER KYIV FLAT HIT",
         deck="Drone hits a Kyiv block; 14 missing as rescuers dig the rubble.",
         src="BBC, 23 Nov", lon=30.5, lat=50.4),
    dict(n=5, region="ME", icon="van",
         head="AID VAN STRUCK IN GAZA: 3 DEAD",
         deck="An Israeli strike kills three food-aid workers in Gaza City; "
              "Hamas calls for urgent talks.",
         src="Al Jazeera, 23 Nov", lon=34.5, lat=31.5),
    dict(n=6, region="LA", icon="cuffs",
         head="'CHAPO ISIDRO' CAPTURED IN SINALOA",
         deck="Mexican forces seize FBI-wanted cartel boss 'Chapo Isidro' in "
              "Sinaloa.",
         src="AFP, 23 Nov", lon=-107.9, lat=25.0),
    dict(n=7, region="AP", icon="chartdown",
         head="KOSPI SLIDES 3% ON AI-BUBBLE FEAR",
         deck="Seoul's market tumbles as AI-bubble fears mount; Korea readies "
              "a stabilisation fund.",
         src="Al Jazeera, 23 Nov", lon=127.0, lat=37.5),
    dict(n=8, region="NA", icon="chartdown",
         head="NASDAQ'S WORST WEEK SINCE 2020",
         deck="Nasdaq fell 10% in a week, its worst since 2020; futures bounce "
              "Monday.",
         src="Reuters / IBD, 23 Nov", lon=-74.0, lat=40.7),
    dict(n=9, region="SP", icon="trophy",
         head="ALCARAZ WINS FIRST ATP FINALS",
         deck="Carlos Alcaraz beats Alexander Zverev 6-2, 7-6 in Turin for his "
              "first season-ending title.",
         src="ATP / Daily Star, 23 Nov", lon=7.7, lat=45.1),
    dict(n=10, region="SP", icon="ball",
         head="LIVERPOOL THRASH MAN UTD 4-0",
         deck="Ten-man Man Utd routed 4-0 at Anfield; teenager Rio Ngumoha "
              "stars.",
         src="BBC Sport, 23 Nov", lon=-2.96, lat=53.4),
    dict(n=11, region="SP", icon="car",
         head="VERSTAPPEN WINS LAS VEGAS GP",
         deck="Verstappen wins a dramatic Las Vegas GP; Norris, Piastri on the "
              "podium.",
         src="F1, 23 Nov", lon=-115.1, lat=36.2),
    dict(n=12, region="SP", icon="golf",
         head="THITIKUL'S THIRD TITLE IN A ROW",
         deck="Jeeno Thitikul wins her third straight LPGA title at the "
              "season-ending finale.",
         src="LPGA, 23 Nov", lon=-81.8, lat=26.1),
    dict(n=13, region="AF", icon="virus",
         head="WHO: FIGHTING THREATENS EBOLA FIGHT",
         deck="Fighting near an Ebola hospital in DR Congo puts patients at "
              "grave risk.",
         src="WHO / Al Jazeera, 23 Nov", lon=23.0, lat=-3.0),
]

ALSO = [
    (14, "Kerch Bridge hit 3 times in 4 days; Putin rules out ceasefire talks"),
    (15, "Suspected drone blast hits Russian ship at Benghazi port, Libya"),
    (16, "Russian cargo ship Sparta 2 still burning off Finland after attack"),
    (17, "Poland reports Russian airspace breach; 3 missiles hit on Friday"),
    (18, "Iran strike wounds two in Bahrain; Saudi Arabia condemns attacks"),
    (19, "Saudi-led coalition intercepts Houthi missile over western region"),
    (20, "RSF drone strikes kill civilians in Sudan's capital Khartoum"),
    (21, "24 civilians killed in fresh violence in South Sudan, AFP reports"),
    (22, "Boat sinks on way to funeral in Nigeria; at least 24 dead"),
    (23, "35 Fulanis killed in revenge attacks in Nigeria, officials say"),
    (24, "Toll rises after Serang candy factory fire; dozens still missing"),
    (25, "Flood evacuee numbers fall across Selangor and Perak, Malaysia"),
    (26, "Thousands march in Lisbon as living costs fuel anger"),
    (27, "Myanmar's army-backed govt calls ASEAN decision 'unfair'"),
    (28, "FIFA to confirm UK as host of the 2035 Women's World Cup"),
    (29, "Nine shot at a concert in central California; one critical"),
    (30, "Youth Congress protests Meta over blocked accounts in India"),
    (31, "Nations agree to keep talking on lethal AI weapons at UN"),
    (32, "South Korea education minister quits over AI exam-cheating scandal"),
    (33, "UK to build Ukrainian long-range drones in Britain under new deal"),
    (34, "Brazil ex-leader Bolsonaro 'stable' in intensive care"),
    (35, "North Korea's Kim: country seeks security, not supremacy"),
]

REGIONS = [
    ("N. AMERICA", 3, BLUE),
    ("LATIN AMERICA", 2, TEAL),
    ("EUROPE", 9, DARK),
    ("MIDDLE EAST", 4, RED),
    ("AFRICA", 6, ORANGE),
    ("ASIA-PACIFIC", 7, GOLD),
    ("SPORT", 4, GREEN),
]

NUMBERS = [
    ("2", "TANKERS STRUCK", "IN HORMUZ"),
    ("10%", "NASDAQ'S WEEKLY", "FALL SINCE 2020"),
    ("14", "MISSING AFTER", "KYIV FLAT HIT"),
    ("24", "CIVILIANS KILLED", "IN SOUTH SUDAN"),
    ("3%", "KOSPI SLIDE ON", "AI-BUBBLE FEARS"),
    ("1992", "BIGGEST DEM HOUSE", "MAJORITY SINCE"),
]

SOURCES_LINE = ("SOURCES: REUTERS - BBC - AL JAZEERA - AFP - AP - THE GUARDIAN - "
                "THE HINDU - INVESTOR'S BUSINESS DAILY - ATP - LPGA - F1 - WHO")

# ------------------------------------------------------- lead illustrations
def draw_tanker(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, SKY)
    cv.fill_rect(x, y + h - 26, w, 26, (64, 110, 150))
    for i in range(5):
        cv.hline(x + 8 + i * 14, y + h - 18 + (i % 2) * 5, 60, WHITE, 2)
    # hull of tanker one
    cv.fill_rect(x + 18, y + h - 52, 130, 24, (40, 40, 44))
    cv.fill_rect(x + 18, y + h - 58, 130, 6, RED)
    cv.fill_rect(x + 108, y + h - 84, 26, 26, (220, 220, 220))
    cv.fill_rect(x + 116, y + h - 96, 10, 12, INK)
    # tanker two, smaller, behind
    cv.fill_rect(x + 168, y + h - 46, 110, 18, (70, 70, 78))
    cv.fill_rect(x + 168, y + h - 51, 110, 5, GOLD)
    cv.fill_rect(x + 240, y + h - 70, 20, 19, (220, 220, 220))
    # explosion flames over tanker one
    cv.tri((x + 60, y + h - 58), (x + 78, y + 22), (x + 96, y + h - 58),
           ORANGE)
    cv.tri((x + 78, y + h - 58), (x + 96, y + 8), (x + 114, y + h - 58),
           (230, 180, 20))
    cv.tri((x + 96, y + h - 58), (x + 112, y + 30), (x + 128, y + h - 58),
           RED)
    # smoke
    cv.circle(x + 88, y + 14, 10, (90, 90, 90))
    cv.circle(x + 104, y + 8, 12, (120, 120, 120))
    cv.circle(x + 122, y + 16, 9, (90, 90, 90))
    cv.text(x + 10, y + 6, "STRAIT OF HORMUZ", 1, INK)

def draw_cop(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, (222, 232, 222))
    # sun
    cv.circle(x + w - 34, y + 26, 16, (230, 180, 20))
    # globe with a crack
    cx, cy, r = x + 88, y + h - 46, 38
    cv.circle(cx, cy, r, BLUE)
    cv.circle(cx, cy, r - 6, (120, 180, 220))
    cv.line(cx - r + 6, cy, cx + r - 6, cy, WHITE, 2)
    cv.line(cx, cy - r + 6, cx, cy + r - 6, WHITE, 2)
    cv.ring(cx, cy, r, INK, 2)
    # red crack across the globe
    cv.line(cx - 26, cy - 30, cx - 8, cy - 6, RED, 3)
    cv.line(cx - 8, cy - 6, cx + 6, cy + 8, RED, 3)
    cv.line(cx + 6, cy + 8, cx + 24, cy + 30, RED, 3)
    # broken handshake: two hands that do not meet
    # torn deal paper: two halves with a zigzag tear between them
    px0, py0 = x + 196, y + h - 62
    cv.fill_rect(px0, py0, 40, 40, WHITE)
    cv.rect(px0, py0, 40, 40, INK, 1)
    cv.fill_rect(px0 + 56, py0, 40, 40, WHITE)
    cv.rect(px0 + 56, py0, 40, 40, INK, 1)
    cv.line(px0 + 40, py0, px0 + 48, py0 + 13, RED, 2)
    cv.line(px0 + 48, py0 + 13, px0 + 40, py0 + 26, RED, 2)
    cv.line(px0 + 40, py0 + 26, px0 + 48, py0 + 40, RED, 2)
    cv.hline(px0 + 6, py0 + 10, 28, INK, 1)
    cv.hline(px0 + 6, py0 + 20, 28, INK, 1)
    cv.hline(px0 + 62, py0 + 10, 28, INK, 1)
    cv.hline(px0 + 62, py0 + 20, 28, INK, 1)
    cv.text(x + 10, y + 6, "ANTALYA, TURKIYE", 1, INK)
    cv.text(x + 196, y + h - 26, "NO DEAL", 2, RED)

def draw_capitol(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, SKY)
    # ground
    cv.fill_rect(x, y + h - 22, w, 22, GREEN)
    cx = x + w // 2
    # dome: white disc with an ink ring, lower half erased back to sky so
    # only the upper semicircle shows, sitting on the building
    cv.circle(cx, y + h - 62, 34, WHITE)
    cv.ring(cx, y + h - 62, 34, INK, 2)
    cv.fill_rect(cx - 34, y + h - 62, 68, 34, SKY)
    cv.fill_rect(cx - 3, y + h - 104, 6, 12, INK)
    cv.circle(cx, y + h - 106, 4, RED)
    # capitol building: base + columns, drawn over the dome's base
    bx = x + w // 2 - 90
    cv.fill_rect(bx, y + h - 62, 180, 40, WHITE)
    cv.rect(bx, y + h - 62, 180, 40, INK, 2)
    for i in range(6):
        cv.fill_rect(bx + 12 + i * 28, y + h - 58, 10, 32, INK)
    # ballot box in front
    cv.fill_rect(x + 18, y + h - 44, 34, 22, BLUE)
    cv.fill_rect(x + 14, y + h - 50, 42, 8, DARK)
    cv.fill_rect(x + 30, y + h - 56, 10, 8, WHITE)
    cv.text(x + 10, y + 6, "WASHINGTON", 1, INK)
    cv.text(x + w - 108, y + h - 20, "SINCE 1992", 1, WHITE)

LEAD_ART = {1: draw_tanker, 2: draw_cop, 3: draw_capitol}

# ------------------------------------------------------------- pictograms
def icon_rubble(cv, x, y, s):
    cv.fill_rect(x, y + s - 14, s, 14, GREY)
    cv.tri((x + 4, y + s - 14), (x + 16, y + 4), (x + 28, y + s - 14),
           (120, 120, 120))
    cv.fill_rect(x + 6, y + s - 8, 12, 6, INK)
    cv.fill_rect(x + 22, y + s - 6, 10, 4, RED)
    cv.line(x + 2, y + 2, x + s - 2, y + 10, RED, 2)

def icon_van(cv, x, y, s):
    cv.fill_rect(x + 2, y + 8, s - 8, 16, WHITE)
    cv.rect(x + 2, y + 8, s - 8, 16, INK, 2)
    cv.fill_rect(x + s - 12, y + 14, 8, 10, BLUE)
    cv.circle(x + 10, y + s - 8, 5, INK)
    cv.circle(x + s - 10, y + s - 8, 5, INK)
    cv.text(x + 6, y + 12, "AID", 1, RED)

def icon_cuffs(cv, x, y, s):
    cv.ring(x + 10, y + s // 2, 8, INK, 3)
    cv.ring(x + s - 10, y + s // 2, 8, INK, 3)
    cv.line(x + 10, y + s // 2 - 8, x + s - 10, y + s // 2 + 8, INK, 3)

def icon_chartdown(cv, x, y, s):
    cv.vline(x + 4, y + 4, s - 8, INK, 2)
    cv.hline(x + 4, y + s - 4, s - 8, INK, 2)
    cv.line(x + 6, y + 8, x + 14, y + 14, RED, 3)
    cv.line(x + 14, y + 14, x + 22, y + 12, RED, 3)
    cv.line(x + 22, y + 12, x + s - 4, y + s - 8, RED, 3)
    cv.tri((x + s - 8, y + s - 12), (x + s - 2, y + s - 12),
           (x + s - 5, y + s - 4), RED)

def icon_trophy(cv, x, y, s):
    cv.fill_rect(x + 10, y + 6, s - 20, 14, GOLD)
    cv.fill_rect(x + 6, y + 8, 6, 8, GOLD)
    cv.fill_rect(x + s - 12, y + 8, 6, 8, GOLD)
    cv.fill_rect(x + s // 2 - 2, y + 20, 4, 8, GOLD)
    cv.fill_rect(x + 10, y + 28, s - 20, 4, GOLD)
    cv.text(x + 13, y + 9, "1", 1, INK)

def icon_ball(cv, x, y, s):
    cx, cy, r = x + s // 2, y + s // 2, s // 2 - 3
    cv.circle(cx, cy, r, WHITE)
    cv.ring(cx, cy, r, INK, 2)
    cv.circle(cx, cy, 5, INK)
    for dx, dy in ((-10, -8), (10, -8), (0, 12)):
        cv.line(cx, cy, cx + dx, cy + dy, INK, 2)

def icon_car(cv, x, y, s):
    cv.fill_rect(x + 4, y + 12, s - 8, 10, RED)
    cv.fill_rect(x + 10, y + 6, s - 20, 8, RED)
    cv.fill_rect(x + 14, y + 8, 8, 5, SKY)
    cv.circle(x + 12, y + s - 8, 5, INK)
    cv.circle(x + s - 12, y + s - 8, 5, INK)
    cv.line(x + 2, y + s - 4, x + s - 2, y + s - 4, INK, 2)

def icon_golf(cv, x, y, s):
    cv.circle(x + 10, y + s - 8, 4, WHITE)
    cv.ring(x + 10, y + s - 8, 4, INK, 1)
    cv.vline(x + s - 12, y + 4, s - 12, INK, 2)
    cv.tri((x + s - 12, y + 4), (x + s - 12, y + 14), (x + 8, y + 9), RED)
    cv.hline(x + 4, y + s - 4, s - 8, GREEN, 3)

def icon_virus(cv, x, y, s):
    cx, cy = x + s // 2, y + s // 2
    for dx, dy in ((-12, 0), (12, 0), (0, -12), (0, 12),
                   (-9, -9), (9, -9), (-9, 9), (9, 9)):
        cv.line(cx, cy, cx + dx, cy + dy, TEAL, 2)
    cv.circle(cx, cy, 9, TEAL)
    cv.circle(cx - 3, cy - 3, 2, WHITE)
    cv.circle(cx + 3, cy + 2, 2, WHITE)

ICONS = {
    "rubble": icon_rubble, "van": icon_van, "cuffs": icon_cuffs,
    "chartdown": icon_chartdown, "trophy": icon_trophy, "ball": icon_ball,
    "car": icon_car, "golf": icon_golf, "virus": icon_virus,
}

# ------------------------------------------------------------------ layout
def draw_masthead(cv, overflow):
    cv.hline(16, 10, 992, INK, 3)
    cv.text_center(16, 18, 992, "THE WORLD IN ONE DAY", 5, INK)
    cv.text_center(16, 62, 992, "MONDAY 23 NOVEMBER 2026", 3, RED)
    cv.hline(16, 90, 992, RED, 2)
    cv.text_center(16, 96, 992,
                   "35 STORIES FROM ONE DAY - EVERY STORY DATED 23 NOVEMBER 2026",
                   1, INK)

def draw_numbers(cv, overflow):
    y, h = 112, 54
    bw = 162
    for i, (num, l1, l2) in enumerate(NUMBERS):
        x = 16 + i * (bw + 6)
        cv.fill_rect(x, y, bw, h, GREY)
        cv.rect(x, y, bw, h, INK, 1)
        cv.text_center(x, y + 5, bw, num, 3, RED)
        cv.text_center(x, y + 30, bw, l1, 1, INK)
        cv.text_center(x, y + 40, bw, l2, 1, INK)

def draw_regions(cv, overflow):
    y, h = 172, 34
    seg = 992 // 7
    for i, (name, count, color) in enumerate(REGIONS):
        x = 16 + i * seg
        w = seg - 4 if i < 6 else 992 - 6 * seg - 4
        cv.fill_rect(x, y, w, h, color)
        cv.text_center(x, y + 4, w, name, 1, WHITE)
        cv.text_center(x, y + 16, w, str(count) + " STORIES", 1, WHITE)

def draw_leads(cv, overflow):
    y0 = 214
    col_w = 316
    for i, lead in enumerate(LEADS):
        x = 16 + i * (col_w + 20)
        cv.text(x, y0, lead["kicker"], 1, RED)
        cv.rect(x, y0 + 12, col_w, 108, INK, 2)
        LEAD_ART[lead["n"]](cv, x + 2, y0 + 14, col_w - 4, 104)
        _, ov = cv.wrapped(x, y0 + 130, lead["head"], 3, INK, col_w,
                           24, max_lines=3)
        overflow.append(("lead-head-%d" % lead["n"], ov))
        _, ov = cv.wrapped(x, y0 + 206, lead["deck"], 2, INK, col_w,
                           17, max_lines=4)
        overflow.append(("lead-deck-%d" % lead["n"], ov))
        cv.text(x, y0 + 276, lead["src"], 1, (90, 90, 90))

def draw_grid(cv, overflow):
    y0 = 504
    cell_w, cell_h = 192, 88
    for i, g in enumerate(GRID):
        col = i % 5
        row = i // 5
        x = 16 + col * (cell_w + 8)
        y = y0 + row * (cell_h + 8)
        cv.fill_rect(x, y, cell_w, cell_h, WHITE)
        cv.rect(x, y, cell_w, cell_h, INK, 1)
        ICONS[g["icon"]](cv, x + 6, y + 4, 32)
        cv.text(x + 44, y + 6, str(g["n"]) + ".", 2, RED)
        _, ov = cv.wrapped(x + 6, y + 40, g["head"], 1, INK, cell_w - 12,
                           9, max_lines=2)
        overflow.append(("grid-head-%d" % g["n"], ov))
        _, ov = cv.wrapped(x + 6, y + 60, g["deck"], 1, (60, 60, 60),
                           cell_w - 12, 9, max_lines=3)
        overflow.append(("grid-deck-%d" % g["n"], ov))

# ------------------------------------------------------------- world map
# Very simplified continent outlines, lon/lat pairs, drawn by hand.
NORTH_AMERICA = [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80),
                 (-85, 70), (-75, 62), (-65, 60), (-55, 47), (-70, 42),
                 (-75, 35), (-80, 26), (-90, 21), (-97, 16), (-105, 20),
                 (-115, 28), (-125, 40), (-150, 60)]
SOUTH_AMERICA = [(-80, 10), (-75, 5), (-60, 5), (-50, 0), (-40, -5),
                 (-35, -10), (-40, -20), (-48, -28), (-58, -35),
                 (-65, -45), (-70, -52), (-73, -40), (-75, -20),
                 (-80, -5)]
EUROPE = [(-10, 36), (-5, 44), (0, 50), (5, 58), (10, 60), (18, 56),
          (25, 60), (30, 70), (40, 68), (45, 60), (40, 50), (30, 45),
          (20, 40), (12, 38), (3, 37), (-9, 37)]
AFRICA = [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (30, 31),
          (35, 28), (43, 12), (51, 10), (48, 0), (40, -10), (35, -20),
          (30, -30), (20, -35), (15, -27), (12, -18), (8, -2), (9, 4),
          (-8, 5)]
ASIA = [(40, 68), (60, 70), (80, 73), (100, 77), (120, 73), (140, 72),
        (160, 70), (178, 66), (170, 60), (160, 55), (150, 45),
        (140, 40), (130, 35), (127, 40), (122, 32), (115, 25),
        (108, 18), (105, 10), (100, 8), (95, 15), (90, 22), (85, 20),
        (80, 10), (75, 8), (70, 20), (60, 25), (55, 27), (50, 30),
        (48, 30), (43, 35), (40, 40), (40, 50)]
AUSTRALIA = [(113, -22), (114, -30), (120, -34), (130, -32), (140, -38),
             (150, -37), (153, -27), (146, -19), (142, -11), (135, -12),
             (130, -13), (122, -14)]
CONTINENTS = [NORTH_AMERICA, SOUTH_AMERICA, EUROPE, AFRICA, ASIA,
              AUSTRALIA]

# Map markers for the 13 lead + grid stories: (story no, lon, lat).
MARKERS = [
    (1, 57, 26), (2, 30, 36), (3, -77, 39),
    (4, 30.5, 50.4), (5, 34.5, 31.5), (6, -107.9, 25.0),
    (7, 127.0, 37.5), (8, -74.0, 40.7), (9, 7.7, 45.1),
    (10, -2.96, 53.4), (11, -115.1, 36.2), (12, -81.8, 26.1),
    (13, 23.0, -3.0),
]
# Small nudges (dx, dy in px) so close markers do not sit on each other.
NUDGES = {2: (-8, -6), 5: (10, 8), 1: (8, -8), 4: (0, -8),
          6: (-12, 12), 11: (10, -10), 12: (0, 10)}

def lonlat_to_xy(lon, lat, mx, my, mw, mh):
    px = mx + (lon + 170.0) / 360.0 * mw
    py = my + (80.0 - lat) / 140.0 * mh
    return int(px), int(py)

def draw_map(cv, overflow):
    mx, my, mw, mh = 16, 714, 620, 112
    cv.text(16, 694, "WHERE IT HAPPENED - 13 PLACES", 2, INK)
    cv.fill_rect(mx, my, mw, mh, OCEAN)
    cv.rect(mx, my, mw, mh, INK, 2)
    for cont in CONTINENTS:
        pts = [lonlat_to_xy(lon, lat, mx, my, mw, mh) for lon, lat in cont]
        cv.poly(pts, LAND)
        for i in range(len(pts)):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % len(pts)]
            cv.line(x0, y0, x1, y1, (120, 100, 50), 1)
    for n, lon, lat in MARKERS:
        px, py = lonlat_to_xy(lon, lat, mx, my, mw, mh)
        dx, dy = NUDGES.get(n, (0, 0))
        px += dx
        py += dy
        cv.circle(px, py, 9, RED)
        cv.ring(px, py, 9, WHITE, 1)
        label = str(n)
        tw = text_width(label, 1)
        cv.text(px - tw // 2, py - 4, label, 1, WHITE)

def draw_datecheck(cv, overflow):
    x, y, w, h = 652, 694, 356, 132
    cv.fill_rect(x, y, w, h, (255, 248, 220))
    cv.rect(x, y, w, h, RED, 2)
    cv.text(x + 10, y + 8, "DATE CHECK", 2, RED)
    cv.hline(x + 10, y + 26, w - 20, RED, 1)
    cv.text(x + 10, y + 32, "LEFT OUT - IT WAS 22 NOV NEWS:", 1, INK)
    _, ov = cv.wrapped(x + 10, y + 44,
                       "BepiColombo entered orbit around Mercury on Sun 22 Nov "
                       "(ESA). A day old, so it is not in today's 35.",
                       1, INK, w - 20, 9, max_lines=3)
    overflow.append(("datecheck-leftout", ov))
    cv.text(x + 10, y + 76, "NOT YET - AFTER 23 NOV:", 1, INK)
    _, ov = cv.wrapped(x + 10, y + 88,
                       "Spain votes in a snap election on Sun 29 Nov. Polls, "
                       "not results, so no winner is shown here.",
                       1, INK, w - 20, 9, max_lines=3)
    overflow.append(("datecheck-notyet", ov))
    cv.text(x + 10, y + 118, "EVERY STORY ABOVE IS 23 NOV 2026.", 1, RED)

def draw_also(cv, overflow):
    y0 = 836
    cv.text(16, y0, "ALSO ON 23 NOVEMBER", 2, INK)
    cv.hline(16, y0 + 18, 992, INK, 2)
    col_w = 484
    for i, (n, line) in enumerate(ALSO):
        col = i // 11
        row = i % 11
        x = 16 + col * (col_w + 24)
        y = y0 + 26 + row * 11
        cv.text(x, y, str(n) + ".", 1, RED)
        _, ov = cv.wrapped(x + 26, y, line, 1, INK, col_w - 26, 9,
                           max_lines=1)
        overflow.append(("also-%d" % n, ov))

def draw_footer(cv, overflow):
    y = 1000
    cv.hline(16, y - 6, 992, INK, 1)
    cv.text_center(16, y, 992, SOURCES_LINE, 1, (90, 90, 90))
    cv.text_center(16, y + 10, 992,
                   "DRAWN BY HAND IN PYTHON - NO PHOTOS - ALL 35 STORIES DATED "
                   "23 NOVEMBER 2026", 1, (90, 90, 90))

def render():
    """Draw the whole front page. Returns (png_bytes, overflow_list)."""
    cv = Canvas(W, H, PAPER)
    overflow = []
    draw_masthead(cv, overflow)
    draw_numbers(cv, overflow)
    draw_regions(cv, overflow)
    draw_leads(cv, overflow)
    draw_grid(cv, overflow)
    draw_map(cv, overflow)
    draw_datecheck(cv, overflow)
    draw_also(cv, overflow)
    draw_footer(cv, overflow)
    return encode_png(W, H, cv.px), overflow

def count_stories():
    return len(LEADS) + len(GRID) + len(ALSO)
