"""Validate TOML notes and render a portable static site. Python 3.11+, no packages."""
from pathlib import Path
from string import Template
from datetime import date
from html import escape
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import re
import shutil
import tomllib

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist"
CATEGORIES = ("閱讀方法", "研究整理", "寫作練習")


def esc(value):
    return escape(str(value), quote=True)


def text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} 必須為非空文字")


def strings(value, field, minimum=1):
    if not isinstance(value, list) or len(value) < minimum:
        raise ValueError(f"{field} 至少需要 {minimum} 個項目")
    for item in value:
        text(item, field)


def load_notes():
    notes = []
    for path in sorted((ROOT / "content").glob("*.toml")):
        with path.open("rb") as handle:
            note = tomllib.load(handle)
        for key in ("slug", "title", "summary", "category", "date", "kind"):
            text(note.get(key), f"{path.name}: {key}")
        slug = note["slug"]
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) or slug != path.stem:
            raise ValueError(f"{path.name}: slug 必須與英文檔名一致")
        date.fromisoformat(note["date"])
        if note["category"] not in CATEGORIES:
            raise ValueError(f"{slug}: 未知分類")
        if note["kind"] not in ("方法示範", "文獻筆記"):
            raise ValueError(f"{slug}: 未知內容類型")
        if type(note.get("minutes")) is not int or note["minutes"] <= 0:
            raise ValueError(f"{slug}: minutes 必須為正整數")
        strings(note.get("tags"), "tags")
        if len(note["tags"]) > 4:
            raise ValueError(f"{slug}: tags 不可超過四個")
        strings(note.get("checklist"), "checklist", 3)
        sections = note.get("sections")
        if not isinstance(sections, list) or len(sections) < 3:
            raise ValueError(f"{slug}: 至少需要三個段落")
        for section in sections:
            text(section.get("heading"), "heading")
            strings(section.get("paragraphs"), "paragraphs")
            if "bullets" in section:
                strings(section["bullets"], "bullets")
        if note["kind"] == "文獻筆記" and not any(
            "https://" in paragraph for section in sections for paragraph in section["paragraphs"]
        ):
            raise ValueError(f"{slug}: 文獻筆記須記錄可核查來源網址與書目")
        related = note.get("related", [])
        if not isinstance(related, list) or len(related) > 2:
            raise ValueError(f"{slug}: related 最多兩項")
        for item in related:
            text(item.get("slug"), "related.slug")
        notes.append(note)
    if not notes:
        raise ValueError("至少需要一篇筆記")
    slugs = {note["slug"] for note in notes}
    if len(slugs) != len(notes):
        raise ValueError("slug 不可重複")
    for note in notes:
        targets = [item["slug"] for item in note.get("related", [])]
        if len(targets) != len(set(targets)):
            raise ValueError(f'{note["slug"]}: 相關閱讀不可重複')
        if any(target not in slugs or target == note["slug"] for target in targets):
            raise ValueError(f'{note["slug"]}: 相關閱讀連結無效')
    return sorted(notes, key=lambda note: (note["date"], note["slug"]), reverse=True)


def render(name, **values):
    return Template((ROOT / "templates" / name).read_text(encoding="utf-8")).substitute(values)


def card(note, number):
    searchable = " ".join([note["title"], note["summary"], *note["tags"]])
    return f'''<article class="note-card" data-note="{esc(note['category'])}" data-search="{esc(searchable)}">
<div class="card-top"><span class="category">{esc(note['category'])}</span><span>NOTE / {number:02}</span></div>
<h3><a href="notes/{esc(note['slug'])}.html">{esc(note['title'])}</a></h3><p>{esc(note['summary'])}</p>
<div class="card-bottom"><span>{esc(note['kind'])} · {esc(note['date'])}</span><span>{note['minutes']} 分鐘閱讀</span></div></article>'''


class Links(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.ids = set()
        self.h1 = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.h1 += tag == "h1"
        if attrs.get("id"):
            if attrs["id"] in self.ids:
                raise ValueError(f'重複 ID: {attrs["id"]}')
            self.ids.add(attrs["id"])
        for key in ("href", "src"):
            if attrs.get(key):
                self.links.append(attrs[key])


def validate_output():
    parsed = {}
    for path in OUT.rglob("*.html"):
        parser = Links()
        parser.feed(path.read_text(encoding="utf-8"))
        if parser.h1 != 1:
            raise ValueError(f"{path.name}: 必須且只能有一個 h1")
        parsed[path.resolve()] = parser
    for path, parser in parsed.items():
        for link in parser.links:
            url = urlsplit(link)
            if url.scheme or url.netloc:
                continue
            if url.path.startswith("/"):
                raise ValueError(f"不支援 GitHub 子路徑的連結: {link}")
            target = (path.parent / unquote(url.path)).resolve() if url.path else path
            if not target.is_relative_to(OUT.resolve()) or not target.is_file():
                raise ValueError(f"失效內部連結: {path.name} → {link}")
            if url.fragment and target in parsed and unquote(url.fragment) not in parsed[target].ids:
                raise ValueError(f"失效錨點: {path.name} → {link}")
    return len(parsed)


def build():
    notes = load_notes()  # Validate before touching generated output.
    if OUT.is_symlink():
        raise ValueError("dist 不得為符號連結")
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "notes").mkdir(parents=True)
    shutil.copytree(ROOT / "assets", OUT / "assets")
    shutil.copyfile(ROOT / "AGENTS.md", OUT / "AGENTS.md")
    (OUT / ".nojekyll").touch()
    filters = "".join(f'<button type="button" class="filter" data-category="{esc(category)}" aria-pressed="false">{esc(category)}</button>' for category in CATEGORIES)
    home = render("home.html", count=len(notes), filters=filters, cards="".join(card(note, i) for i, note in enumerate(notes, 1)))
    (OUT / "index.html").write_text(render("base.html", root="", title="論文閱讀筆記", description="把讀過的，變成自己的。探索閱讀方法、研究整理與寫作練習，依 AGENTS.md 持續累積的公開筆記網站。", body=home), encoding="utf-8")
    lookup = {note["slug"]: note for note in notes}
    for note in notes:
        sections, toc = [], []
        for i, section in enumerate(note["sections"], 1):
            heading = esc(section["heading"])
            toc.append(f'<a href="#section-{i}">{i:02} / {heading}</a>')
            paragraphs = "".join(f"<p>{esc(item)}</p>" for item in section["paragraphs"])
            bullets = "".join(f"<li>{esc(item)}</li>" for item in section.get("bullets", []))
            sections.append(f'<section id="section-{i}"><h2><span class="section-number">{i:02} /</span>{heading}</h2>{paragraphs}{"<ul>" + bullets + "</ul>" if bullets else ""}</section>')
        related = "".join(f'<a class="related-link" href="{esc(item["slug"])}.html"><small>{esc(lookup[item["slug"]]["category"])}</small>{esc(lookup[item["slug"]]["title"])} ↗</a>' for item in note.get("related", []))
        body = render("note.html", **{key: esc(note[key]) for key in ("category", "kind", "title", "summary", "date", "minutes")}, tags="".join(f"<span>{esc(tag)}</span>" for tag in note["tags"]), toc="".join(toc), sections="".join(sections), checklist="".join(f"<li>{esc(item)}</li>" for item in note["checklist"]), related=related)
        (OUT / "notes" / f'{note["slug"]}.html').write_text(render("base.html", root="../", title=esc(note["title"]), description=esc(note["summary"]), body=body), encoding="utf-8")
    pages = validate_output()
    print(f"建置成功：{len(notes)} 篇筆記，{pages} 個 HTML 頁面，所有內部連結與錨點有效。")


if __name__ == "__main__":
    build()
