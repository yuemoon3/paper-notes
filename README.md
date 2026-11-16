# Paper Notes｜論文閱讀筆記

以 **AGENTS.md** 定義開發方式、以結構化內容持續新增頁面的課堂小專案。不是只交一頁網站：AI 先讀規則，再依同一格式新增內容，建置器自動更新首頁、文章及相關閱讀。

- 網站：https://yuemoon3.github.io/paper-notes/ （部署成功後可瀏覽）
- 原始碼：https://github.com/yuemoon3/paper-notes
- AI 協作規則：[AGENTS.md](AGENTS.md)

## 功能與設計

繁體中文、米白紙張與深綠筆記風格；響應式首頁、3 篇方法示範筆記、文章目錄、行動清單與相關閱讀。支援標題／摘要／標籤搜尋，以及三種主題篩選。關閉 JavaScript 仍可閱讀所有內容。無登入、資料庫、分析追蹤或外部字型。

**內容聲明：** 三篇皆為原創方法示範，不是已驗證的論文摘要或實證研究，不含工作資料夾中的私人研究文件。

## 本機執行

需求為 Python 3.11 或以上，不需安裝套件。

```sh
python3 scripts/build.py
python3 scripts/check.py
python3 -m http.server 8000 --directory dist
```

開啟 http://localhost:8000 。也可直接開啟產生的 dist/index.html；所有內容為預先產生的 HTML，不依賴 fetch。

## 專案結構

```text
AGENTS.md              AI 必讀：目的、風格、內容格式、誠信、流程
content/*.toml         每篇一檔的筆記資料
templates/*.html       首頁、文章、共用頁首與頁尾
assets/                CSS 與漸進增強的搜尋功能
scripts/build.py       內容驗證與靜態頁面產生
scripts/check.py       產物、連結與可攜性檢查
.github/workflows/     自動建置及發布 GitHub Pages
dist/                  產生結果，不納入 Git
```

## 如何新增第 4 篇筆記

1. 請 AI 先讀 AGENTS.md。複製 content/reading-workflow.toml 為 content/your-topic.toml。
2. 修改 slug 與所有內容；檔名與 slug 相同。分類限「閱讀方法」「研究整理」「寫作練習」。日期格式為 YYYY-MM-DD。
3. 填寫標題、摘要、閱讀分鐘、1–4 個標籤、至少 3 個 sections、至少 3 個 checklist 項目與最多 2 個 related。
4. 執行建置和檢查；首頁清單、計數、獨立文章頁自動產生。不需手動改 HTML。
5. 檢查手機與桌機閱讀體驗，提交原始碼並推送 main。

可貼給 AI：

> 請先閱讀 AGENTS.md，參照 content/reading-workflow.toml，新增一篇關於「如何做閱讀紀錄」的「方法示範」筆記。沿用既有版型、加入相關閱讀，執行建置與檢查，並回報結果。

## GitHub Pages

將本資料夾內容放在儲存庫根目錄；main 是發布分支。在 GitHub 的 **Settings → Pages → Source** 選擇 **GitHub Actions**。推送後，在 Actions 確認 Build and deploy Paper Notes 成功。workflow 會建置、驗證並發布 dist/，支援 /paper-notes/ 子路徑。

若尚未連上 GitHub，可先建立空白公開儲存庫，於本資料夾執行：

```sh
git init -b main
git add .
git commit -m "建立 Paper Notes 與 AI 協作規則"
git remote add origin https://github.com/你的帳號/paper-notes.git
git push -u origin main
```

請勿從上層「論文」資料夾執行 git add，以免納入私人檔案。

## 作業對照

| 作業要求 | 對應成果 |
| --- | --- |
| 自訂小專案 | 論文閱讀方法與寫作練習筆記網站 |
| 規則文件 | AGENTS.md 的九項協作規範 |
| 依規則製作網頁 | 共用版型 + TOML 內容 + 自動建置 |
| 可繼續新增內容 | 新增一份 TOML 即產生一篇文章 |
| GitHub 與可瀏覽網頁 | 完整原始碼、Pages workflow 與公開網站 |
