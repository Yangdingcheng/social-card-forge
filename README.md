# Social Card Forge

**一份内容，一次生成所有平台的卡片尺寸：小红书 3:4 + 公众号封面 2.35:1 + 公众号次图 1:1 + B站 16:9 + 竖版 9:16。本地运行，不上传、无水印、不用 AI 生图。**

**One input → every platform size in one run. Local, private, no watermark, no image-generation cost.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)

## 为什么又做一个卡片工具？/ Why another card tool

市面上的图卡工具多数是网页版：内容要贴到别人网站上、一个尺寸一个尺寸地导、换个平台就要重排。这个工具反着来：

- **一次出全尺寸**：同一份内容，`--size all` 一次生成 5 个平台尺寸，不用重排 5 遍
- **全本地**：内容不出你的电脑，没有账号、没有上传、没有水印
- **批量**：一个 JSON / 一篇 Markdown（`---` 分页）就是一整套图文，页码自动编号
- **命令行**：能进脚本、进流水线、被 AI Agent 调用，而不是只能手点网页

## 快速开始 / Quick start

```bash
git clone https://github.com/Yangdingcheng/social-card-forge.git
cd social-card-forge
pip install -r requirements.txt

# 单张卡
python3 cardforge.py --title "3 个让你早下班的习惯" \
  --points "先列清单;一次只做一件事;睡前复盘 5 分钟" --tag "效率" --brand "@我的账号"

# 一份内容，全部平台尺寸
python3 cardforge.py --input examples/cards.example.json --size all

# 一篇 Markdown 变一套小红书图文（--- 分页）
python3 cardforge.py --md examples/post.md --theme paper
```

## 尺寸 / Sizes

| 参数 | 尺寸 | 用途 |
|---|---|---|
| `xhs` | 1080×1440 | 小红书封面 / 图文 |
| `wechat` | 1080×460 | 公众号首图（2.35:1） |
| `wechat-square` | 1080×1080 | 公众号次图 / 朋友圈 |
| `bili` | 1920×1080 | B站 / 视频封面（16:9） |
| `vertical` | 1080×1920 | 抖音 / 视频号封面（9:16） |
| `all` | 以上全部 | 一次生成 |

## 主题 / Themes

`news` 新闻黑红 · `paper` 纸感米白 · `bold` 黄黑撞色 · `ocean` 深蓝科技

标题字号自动适配：太长自动缩小、自动断行，关键数字用 `--highlight` 单独一行高亮。

## 输入格式

JSON（一张卡一个对象）：

```json
[{"title": "标题", "points": ["要点1", "要点2"], "tag": "分类", "highlight": "51.8%", "brand": "@账号"}]
```

Markdown：`#` 一级标题是卡片标题，其余行是要点，`---` 分隔多张卡。

## Roadmap

- [ ] 背景图模式：照片打底 + 暗色遮罩 + 大字标题
- [ ] 更多主题（投稿制，欢迎 PR 一张主题截图 + 参数）
- [ ] 字体与字距微调、emoji 标签
- [ ] 与 WeChat Creator Kit 打通：文章生成后自动配全套卡片

## License

MIT
