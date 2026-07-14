# TOPIK 韓語單字學習 App

## 專案目標

做一個網頁版的 TOPIK（韓國語能力測驗）單字學習系統，用**閃卡（flashcard）**方式背單字，介面用**繁體中文**，手機和電腦瀏覽器都要能正常使用（響應式設計，不用另外開發手機 App）。

## 資料來源

- 檔案：`토픽_어휘_목록_공開_목록.xlsx`（官方 TOPIK 詞彙表）
- 每個單字有 4 個欄位：
  - `수준`：等級（初級/中級）
  - `어휘`：韓語單字（含同形異義詞編號，例如 가격03）
  - `길잡이말`：例句搭配詞（幫助理解詞義的短語）
  - `품사`：詞性（名詞、動詞、形容詞、副詞…）
- 目前**沒有繁體中文翻譯**，也沒有羅馬拼音，這是最大的缺口。


## 功能規劃

- **閃卡模式**：正面顯示韓語單字（+ 詞性），點擊/點按翻面顯示繁體中文意思與例句搭配詞
- 標記「已學會 / 還在學」，方便複習還不熟的單字
- 可依等級篩選（初級 / 中級）
- 響應式版面，手機和電腦都要好用
- 例句搭配詞（길잡이말）是否要顯示在卡片上，或只當作翻譯的上下文提示

## 檔案結構

- `토픽 어휘 목록_공개 목록.xlsx`：官方 TOPIK 詞彙表原始檔（資料來源，唯讀，不要修改）。
- `토픽_어휘_목록.json`：從 xlsx 轉出的詞彙資料，`vocabulary` 陣列每筆包含 `level`（초급/중급）、`word`（韓語單字，可能帶同形異義詞編號如 가격03）、`guide`（길잡이말例句搭配詞）、`pos`（詞性）。跑過 `translate_vocab.py` 後，每筆會再多出 `word_zh`、`guide_zh`（繁體中文翻譯）欄位。這份 JSON 是字卡網站的資料來源。
- `translate_vocab.py`：翻譯腳本。用 Google Translate 免費 API，把 `word`（去掉編號的字根）與 `guide` 的不重複字串批次翻譯，結果先寫入 `translate_cache.json`，再回填到 `토픽_어휘_목록.json` 每筆 vocabulary 項目的 `word_zh`/`guide_zh`。有 tqdm 進度條可監控翻譯進度。目前翻譯品質有限（同形異義詞/文法詞綴常誤譯），未來預算允許時要換成 Anthropic API（見下方技術備註的 TODO）。
- `translate_cache.json`：翻譯結果快取（原文 -> 譯文的 key-value），避免重複呼叫翻譯 API。可刪除重建，但刪除後要重新翻譯全部詞彙。
- `site_template.html`：字卡網站原始碼（單一 HTML，含內嵌 CSS/JS，無外部依賴）。用 `__VOCAB_DATA__` 佔位符標記單字資料要注入的位置。**修改網站功能/樣式都改這個檔案**。
- `build_site.py`：讀 `토픽_어휘_목록.json`（精簡成 `[level, word, guide, pos, word_zh]` 陣列，用 `json.dumps` 內嵌）+ `site_template.html`，輸出 `index.html`。改了資料或 template 後要重跑。
- `index.html`：建置產物，實際發布用的字卡網站（透過 Artifact 工具發布）。**不要手動編輯**，會被 `build_site.py` 覆蓋。

### 字卡網站架構（維持未來擴充彈性）

- 資料層：`DATA` 是解析後的單字陣列（level/word/guide/pos/zh）。同形異義詞編號（如 가격03 的 03）保留在 `word` 欄位裡，前端用 `parseWord()` 拆成字根 + 上標數字顯示，不會被去除或合併。
- 狀態層：單一 `state` 物件（等級篩選、狀態篩選、隨機排序開關、已學會集合、目前牌組與索引），改狀態一律經過小函式（`computeDeck`/`goTo`/`toggleFlip`/`toggleLearned`）再呼叫 `render()`，方便之後加新篩選條件或功能（例如詞性篩選、測驗模式）。
- 儲存層：`Storage` 物件封裝 `localStorage` 讀寫，之後要加同步/匯出功能（例如跨裝置同步）可以在這一層擴充。
- 樣式用 CSS 變數（design tokens）定義淺色/深色主題，新增元件請透過變數，不要寫死顏色。

## 技術備註

- 前端：單一 HTML/React artifact
- 儲存：`localStorage`（key-value）。原本規劃用 `window.storage`（僅 Claude Artifact 環境才有），但網站要發布到 GitHub Pages，`window.storage` 在那邊永遠不存在，已簡化成只用 `localStorage`。注意這是每個瀏覽器/裝置各自獨立儲存，不會跨裝置同步。
- 翻譯：Anthropic API `/v1/messages`，model 固定用 `claude-sonnet-4-6`，批次呼叫並做 JSON 結構化輸出
  - **TODO（暫緩）**：`translate_vocab.py` 目前仍用 Google Translate 免費 API 產生翻譯，品質不佳（例如同形異義詞/文法詞綴常誤譯，如「-간」被翻成「-肝」）。之後有預算時要換成上述 Anthropic API 方案，並利用 `길잡이말`（例句搭配詞）當上下文以提升翻譯準確度。
