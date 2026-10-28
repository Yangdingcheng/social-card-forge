import sys, os, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cardforge import SIZES, THEMES, cards_from_md, render

def test_all_sizes_render():
    from PIL import Image
    card = {"title": "测试标题要足够长来触发自动缩小和断行逻辑继续加长", "points": ["要点一", "要点二"], "tag": "测试", "highlight": "1080", "brand": "@t"}
    with tempfile.TemporaryDirectory() as td:
        for s in SIZES:
            p = render(card, s, "news", os.path.join(td, f"{s}.png"))
            with Image.open(p) as im: assert im.size == SIZES[s], (s, im.size)

def test_themes_render():
    with tempfile.TemporaryDirectory() as td:
        for t in THEMES:
            render({"title": "主题", "points": []}, "xhs", t, os.path.join(td, f"{t}.png"))

def test_md_parse(tmp=""):
    import tempfile
    md = "# 标题一\n要点A\n要点B\n\n---\n# 标题二\n要点C\n"
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(md); path = f.name
    cards = cards_from_md(path)
    assert len(cards) == 2 and cards[0]["points"] == ["要点A", "要点B"] and cards[1]["title"] == "标题二"

if __name__ == "__main__":
    test_all_sizes_render(); test_themes_render(); test_md_parse(); print("ok")
