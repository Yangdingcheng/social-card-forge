#!/usr/bin/env python3
"""
Social Card Forge — turn one piece of content into platform-ready cards, locally.

One input -> Xiaohongshu (3:4) + WeChat cover (2.35:1) + WeChat square (1:1)
          + Bilibili (16:9) + vertical video cover (9:16), in one run.
No uploads, no watermark, no AI image generation, no API key. Original implementation.

Usage:
  python3 cardforge.py --title "3 个让你早下班的习惯" --points "先列清单;一次只做一件事;睡前复盘" --tag "效率"
  python3 cardforge.py --input examples/cards.example.json --size all
  python3 cardforge.py --md examples/post.md --theme paper
"""
import argparse, hashlib, json, os, re, sys

SIZES = {  # name: (width, height) — platform specs
    "xhs": (1080, 1440),          # Xiaohongshu 3:4
    "wechat": (1080, 460),        # WeChat cover 2.35:1
    "wechat-square": (1080, 1080),
    "bili": (1920, 1080),         # Bilibili / video 16:9
    "vertical": (1080, 1920),     # short-video cover 9:16
}
THEMES = {
    "news":  {"bg": (17, 17, 17),    "fg": (255, 255, 255), "accent": (208, 0, 0),   "hl": (255, 200, 0), "sub": (170, 170, 170)},
    "paper": {"bg": (250, 246, 238), "fg": (34, 34, 34),    "accent": (190, 40, 40), "hl": (190, 40, 40),  "sub": (120, 115, 105)},
    "bold":  {"bg": (255, 205, 0),   "fg": (15, 15, 15),    "accent": (15, 15, 15),  "hl": (208, 0, 0),    "sub": (80, 70, 0)},
    "ocean": {"bg": (10, 35, 66),    "fg": (240, 248, 255), "accent": (0, 180, 220), "hl": (0, 220, 200),  "sub": (150, 180, 205)},
}
FONT_CANDIDATES_BOLD = [
    "C:\\Windows\\Fonts\\msyhbd.ttc", "/System/Library/Fonts/PingFang.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
]
FONT_CANDIDATES = [
    "C:\\Windows\\Fonts\\msyh.ttc", "/System/Library/Fonts/PingFang.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]

def _font(size, bold=False):
    from PIL import ImageFont
    for p in (FONT_CANDIDATES_BOLD if bold else FONT_CANDIDATES):
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except Exception: continue
    return ImageFont.load_default()

def wrap(draw, text, font, max_w):
    lines, cur = [], ""
    for ch in text:
        if ch == "\n":
            lines.append(cur); cur = ""; continue
        if draw.textlength(cur + ch, font=font) <= max_w: cur += ch
        else: lines.append(cur); cur = ch
    if cur: lines.append(cur)
    return lines or [""]

def fit_title(draw, title, max_w, start, max_lines=3):
    size = start
    while size >= 28:
        f = _font(size, bold=True)
        lines = wrap(draw, title, f, max_w)
        if len(lines) <= max_lines: return f, lines
        size -= 6
    f = _font(28, bold=True)
    return f, wrap(draw, title, f, max_w)[:max_lines]

def render(card, size_name, theme_name, out_path, page=None):
    from PIL import Image, ImageDraw
    W, H = SIZES[size_name]; t = THEMES[theme_name]
    img = Image.new("RGB", (W, H), t["bg"]); d = ImageDraw.Draw(img)
    margin = int(W * 0.075)
    wide = size_name == "bili"          # landscape: points on the right
    short = H < 700                     # wechat wide cover: title-focused
    # accent bar
    d.rectangle([0, 0, W, max(10, H // 90)], fill=t["accent"])
    y = int(H * 0.09)
    if card.get("tag"):
        f = _font(max(26, W // 34))
        label = f" {card['tag']} "
        tw = d.textlength(label, font=f)
        d.rounded_rectangle([margin, y, margin + tw + 12, y + max(44, W // 22)], radius=10, fill=t["accent"])
        d.text((margin + 6, y + 6), label, fill=(255, 255, 255), font=f)
        y += int(H * 0.075)
    title_w = int(W * 0.52) if wide else W - 2 * margin
    tf, tlines = fit_title(d, card["title"], title_w, start=int(W * (0.085 if not short else 0.11)), max_lines=3 if not short else 2)
    lh = int(tf.size * 1.28)
    for ln in tlines:
        d.text((margin, y), ln, fill=t["fg"], font=tf); y += lh
    y += int(H * 0.02)
    points = card.get("points", [])
    if points and not short:
        pf = _font(max(28, W // 30))
        plh = int(pf.size * 1.5)
        px = int(W * 0.56) if wide else margin
        py = int(H * 0.12) if wide else y
        pw = W - px - margin if wide else W - 2 * margin
        for i, p in enumerate(points, 1):
            num = f"{i:02d}"
            d.text((px, py), num, fill=t["hl"], font=_font(max(28, W // 30), bold=True))
            for ln in wrap(d, p, pf, pw - int(W * 0.075)):
                d.text((px + int(W * 0.075), py), ln, fill=t["fg"], font=pf); py += plh
            py += int(plh * 0.35)
            if py > H - int(H * 0.14): break
    if card.get("highlight"):
        d.text((margin, H - int(H * 0.13)), card["highlight"], fill=t["hl"], font=_font(max(30, W // 26), bold=True))
    footer = card.get("brand", "")
    if page: footer = (footer + "  ·  " if footer else "") + page
    if footer:
        d.text((margin, H - int(H * 0.065)), footer, fill=t["sub"], font=_font(max(24, W // 40)))
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    img.save(out_path)
    return out_path

def slug(text):
    return hashlib.md5(text.encode()).hexdigest()[:8]

def cards_from_md(path):
    raw = open(path, encoding="utf-8").read()
    cards = []
    for block in re.split(r"\n---\n", raw):
        lines = [ln.strip() for ln in block.strip().splitlines() if ln.strip()]
        if not lines: continue
        title = re.sub(r"^#\s*", "", lines[0])
        points = [re.sub(r"^[-*]\s*", "", ln) for ln in lines[1:]]
        cards.append({"title": title, "points": points})
    return cards

def main():
    ap = argparse.ArgumentParser(description="Social Card Forge")
    ap.add_argument("--title"); ap.add_argument("--points", help="用 ; 分隔")
    ap.add_argument("--tag", default=""); ap.add_argument("--highlight", default="")
    ap.add_argument("--brand", default="")
    ap.add_argument("--input", help="cards.json: [{title, points[], tag, highlight, brand}]")
    ap.add_argument("--md", help="Markdown: # 标题 + 要点行，--- 分页成多张卡")
    ap.add_argument("--size", default="xhs", choices=list(SIZES) + ["all"])
    ap.add_argument("--theme", default="news", choices=list(THEMES))
    ap.add_argument("--out", default="out")
    a = ap.parse_args()
    if a.input: cards = json.load(open(a.input, encoding="utf-8"))
    elif a.md: cards = cards_from_md(a.md)
    elif a.title: cards = [{"title": a.title, "points": a.points.split(";") if a.points else [],
                            "tag": a.tag, "highlight": a.highlight, "brand": a.brand}]
    else: ap.error("give --title, --input or --md")
    sizes = list(SIZES) if a.size == "all" else [a.size]
    n = 0
    for ci, card in enumerate(cards, 1):
        card.setdefault("brand", a.brand)
        for s in sizes:
            out = os.path.join(a.out, f"{ci:02d}-{slug(card['title'])}-{s}-{a.theme}.png")
            render(card, s, a.theme, out, page=f"{ci}/{len(cards)}" if len(cards) > 1 else None)
            print("wrote", out); n += 1
    print(f"Done: {n} card(s) from {len(cards)} card(s), theme={a.theme}")

if __name__ == "__main__":
    try: import PIL  # noqa
    except ImportError: sys.exit("Need Pillow: pip install pillow")
    main()
