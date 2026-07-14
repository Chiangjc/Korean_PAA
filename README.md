# TOPIK 韓語單字學習 App

TOPIK（韓國語能力測驗）單字閃卡學習系統。詳細專案規劃見 [CLAUDE.md](./CLAUDE.md)。

## 檔案說明

| 檔案 | 說明 |
| --- | --- |
| `토픽 어휘 목록_공개 목록.xlsx` | 官方 TOPIK 詞彙表原始檔，資料來源，唯讀。 |
| `토픽_어휘_목록.json` | 從 xlsx 轉出的詞彙資料。`vocabulary` 陣列每筆包含：<br>- `level`：等級（초급 初級 / 중급 中級）<br>- `word`：韓語單字（可能帶同形異義詞編號，如 가격03）<br>- `guide`：길잡이말，例句搭配詞，幫助理解詞義<br>- `pos`：詞性<br>- `word_zh` / `guide_zh`：繁體中文翻譯（跑過 `translate_vocab.py` 後才會有）<br>這份 JSON 是字卡網站的資料來源。 |
| `translate_vocab.py` | 翻譯腳本。目前用 Google Translate 免費 API，批次翻譯 `word`（去掉編號的字根）與 `guide` 的不重複字串，結果先存進 `translate_cache.json`，再回填到 `토픽_어휘_목록.json` 每筆項目的 `word_zh`/`guide_zh`。執行時有 tqdm 進度條可監控進度。 |
| `translate_cache.json` | 翻譯快取（原文 -> 譯文），避免重複呼叫翻譯 API。可刪除重建，但刪除後需重新翻譯全部詞彙。 |
| `site_template.html` | 字卡網站原始碼（HTML/CSS/JS 單一檔案）。含 `__VOCAB_DATA__` 佔位符，實際單字資料由 `build_site.py` 注入。**要改網站功能/樣式請改這個檔案**，不要直接改 `index.html`。 |
| `build_site.py` | 把 `토픽_어휘_목록.json` 的資料壓縮成精簡陣列，注入 `site_template.html` 的佔位符，產生最終的 `index.html`。每次改了單字資料或 `site_template.html` 都要重新執行。 |
| `index.html` | 建置產生的成品，實際發布的字卡網站，內嵌全部單字資料，可獨立開啟或發布成 Artifact。**這是產生出來的檔案，不要手動編輯**，改完 `site_template.html` 後重跑 `build_site.py` 覆蓋它。 |

## 執行翻譯

```bash
python translate_vocab.py
```

需要先安裝 `tqdm`（`pip install tqdm`）。翻譯結果會直接寫回 `토픽_어휘_목록.json` 與 `translate_cache.json`。

## 建置字卡網站

```bash
python build_site.py
```

會讀取 `토픽_어휘_목록.json` + `site_template.html`，產生 `index.html`。改完 `site_template.html`（UI/功能）或重新翻譯過資料後，都要重跑這個指令。

## 啟動網站

`index.html` 是完全獨立的靜態檔案（單字資料都內嵌在裡面），不需要架設後端，有三種開法：

1. **直接雙擊開啟**：在檔案總管找到 `index.html`，雙擊或拖進瀏覽器就能用。最簡單，適合平常自己讀書用。
2. **本機開一個簡易伺服器**（想用手機連同一個 Wi-Fi 測試響應式版面時比較方便）：
   ```bash
   python -m http.server 8000
   ```
   然後瀏覽器開 `http://localhost:8000/index.html`；手機要連同一台電腦的話用 `http://<電腦區網IP>:8000/index.html`。
3. **用 Claude Code 的 Artifact 連結**：請 Claude 執行 `Artifact` 工具發布 `index.html`，會得到一個網址，手機/電腦都能直接開，不用把檔案傳來傳去。改完 `site_template.html` 或重跑 `build_site.py` 之後要重新發布一次才會更新連結內容。

### 字卡網站功能

- 閃卡模式：正面顯示韓語單字（含詞性標籤、同形異義詞編號以上標數字保留），點擊卡片翻面看繁體中文翻譯 + 길잡이말 例句搭配詞（韓文）。
- 標記「已學會 / 還在學」，狀態存在瀏覽器的 `localStorage`（每個瀏覽器/裝置各自獨立，不會跨裝置同步），並可依此篩選卡片。
- 可依等級（初級/中級）與學習狀態篩選，也可切換隨機排序。
- 可切換練習方向（韓 → 中 / 中 → 韓），從中文猜韓文單字，方便反向練習。
- 響應式版面，手機/電腦皆可使用；支援鍵盤操作（← / → 換單字、空白鍵 / ↑ 翻面、↓ / L 標記或取消已學會、R 切換練習方向），畫面上也有提示文字。

## 已知限制

- Google Translate 對同形異義詞、文法詞綴常有誤譯（例如 `-간` 被翻成 `-肝`），未來預算允許時計畫換成 Anthropic API 搭配 `길잡이말` 上下文重新翻譯，細節見 CLAUDE.md 的技術備註 TODO。
