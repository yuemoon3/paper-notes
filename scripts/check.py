"""Check public outputs, source consistency and GitHub Pages portability."""
from build import ROOT, OUT, load_notes, validate_output


def main():
    notes = load_notes()
    pages = validate_output()
    if pages != len(notes) + 1:
        raise ValueError("輸出頁數與內容不一致；請重新建置")
    for note in notes:
        page = OUT / "notes" / f'{note["slug"]}.html'
        if not page.is_file():
            raise ValueError(f"缺少筆記頁: {note['slug']}")
    for file in ("AGENTS.md", "assets/style.css", "assets/app.js"):
        if (ROOT / file).read_bytes() != (OUT / file).read_bytes():
            raise ValueError(f"來源與輸出不同步: {file}")
    for path in OUT.rglob("*.html"):
        source = path.read_text(encoding="utf-8")
        for required in ('lang="zh-Hant"', 'name="viewport"', 'id="main"'):
            if required not in source:
                raise ValueError(f"{path.name}: 缺少 {required}")
    print(f"檢查通過：{len(notes)} 篇有效內容、{pages} 個頁面、資源同步、內部連結及子路徑相容。")


if __name__ == "__main__":
    main()
