# UniMock AI：30 天使用 Antigravity 與 Google AI Studio 打造智慧教育 Agent

### 階段一：專案啟航、環境搭建與 Stitch 前端原型（Day 1 – Day 5）

* **Day 1｜專案啟航：升學面試痛點與 UniMock AI 核心架構定義**
*產出：專案背景、教育賽道痛點分析、系統模組架構圖*
* **Day 2｜雙劍合璧：Antigravity 工作區設定與 Google AI Studio API 串接測試**
*產出：Antigravity 環境就緒、cURL 成功調用模型列表與 Gemma-4-31B-it 通訊驗證*
* **Day 3｜AI 賦能前端：使用 Google Stitch 快速生成模擬面試艙原型**
*產出：Stitch 提示詞設計、生成包含視訊區、問答區與評分面板的第一版 UI*
* **Day 4｜介面打磨：調整 Stitch 前端畫面與互動元件優化**
*產出：匯出高保真前端專案、調整狀態切換（待機、面試中、評分生成）*
* **Day 5｜介面打磨：調整 UI 畫面與互動元件體驗優化**
*產出：響應式 UI 調整、動態動畫與元件細節修飾、流暢互動體驗*

---

### 階段二：資料前處理、RAG 向量庫與核心 Client 封裝（Day 6 – Day 10）

* **Day 6｜面試知識庫建置：歷年面試題庫清理與向量 Embedding 實戰**
*產出：各學系題庫前處理 Pipeline、本地向量資料庫（Vector Store）建構完成*
* **Day 7｜大腦就緒：LangChain 環境配置與 Gemma 模型客製化串接**
*產出：LangChain 自訂 ChatModel 封裝、Gemma ChatML 提示樣板測試*
* **Day 8｜知識檢索：打造後端 RAG 檢索器與向量資料庫 API 服務**
*產出：向量相似度檢索 API、科系面試題與評分標準檢索端點*
* **Day 9｜模組化大腦：LLM 後端 Client 與對話上下文管理模組封裝**
*產出：強健的 Gemma API Client（含錯誤重試、Token 計數與流式支援）*
* **Day 10｜多模態備審前處理：PDF 文件閱讀工具 + Gemma 備審解析 AI**
*產出：PDF 提取器、學生經歷亮點與自傳邏輯疑點萃取 Agent*

---

### 階段三：後端 Agent 核心開工與狀態機流轉（Day 11 – Day 20）

* **Day 11｜面試官 Persona 引擎：資工、商管、醫學跨科系角色設定**
*產出：科系教授 Prompt 庫、口氣與提問維度注入模組*
* **Day 12｜面試狀態機（State Machine）：四階段對話流轉機制實作**
*產出：自我介紹 ➔ 備審深挖 ➔ 情境應變 ➔ 學生反問狀態控制器*
* **Day 13｜動態追問邏輯（Dynamic Follow-up）：蘇格拉底式深入提問 Agent**
*產出：針對學生模糊回答進行「Why / How」二階追問的 Prompt 邏輯*
* **Day 14｜LangChain Memory 實戰：多輪對話記憶與上下文滑動視窗**
*產出：維持對話脈絡且不超出 Token 上限的 Memory 管理機制*
* **Day 15｜面試評測大腦（Rubric Evaluator）：STAR 原則與評分維度設計**
*產出：多維度評分 Prompt、結構化 JSON 輸出驗證器*
* **Day 16｜回答修飾生成器：原回答弱點診斷與優化範例對照**
*產出：逐題診斷與修改建議生成 Pipeline*
* **Day 17｜雷達圖數據與綜合診斷書生成引擎**
*產出：整合分數、優缺點分析與評語的完整 JSON 報告生成器*
* **Day 18｜安全防護網：Guardrails 個資過濾與防 Prompt Injection 實作**
*產出：輸入安全性過濾中介軟體（Middleware）*
* **Day 19｜後端 API 端點大整合：串接 Session、對話鏈與評分管線**
*產出：完整的 FastAPI 路由（`/upload`, `/start`, `/chat`, `/report`）*
* **Day 20｜後端整合驗收：自動化測試與端到端對話邏輯驗證**
*產出：Pytest 單元測試腳本、後端 Pipeline 完整通過驗證日誌*

---

### 階段四：前後端串接、多模態互動與功能深化（Day 21 – Day 28）

* **Day 21｜前後端接軌：FastAPI 與 Stitch 生成前端的 API 串接實戰**
*產出：完成 PDF 上傳、即時文字對話的前後端連通*
* **Day 22｜極速響應：實作 SSE (Server-Sent Events) 流式文字串流傳輸**
*產出：面試官回答即時打字機效果、降低使用者等待延遲*
* **Day 23｜開口說話：前端整合 Web Speech API 語音輸入（STT）**
*產出：學生即時口語答題、語音轉文字送出功能*
* **Day 24｜擬真面試官：整合 TTS 語音朗讀與音波動畫反饋**
*產出：AI 面試官語音發問、擬真對話波形視覺效果*
* **Day 25｜報告視覺化：前端動態雷達圖與評分報告渲染**
*產出：結合 Chart.js / ECharts 渲染多維度面試成績單*
* **Day 26｜報告本地匯出：一鍵下載 Markdown / PDF 診斷書**
*產出：面試紀錄與雷達圖本地匯出功能實作*
* **Day 27｜防呆與例外處理：網路中斷、麥克風異常與模型重試機制**
*產出：優雅降級（Graceful Degradation）與前端錯誤提示元件*
* **Day 28｜全端效能調優：Token 成本精算與系統延遲最佳化**
*產出：系統端到端延遲壓制在 1.5 秒內的調優紀錄*

---

### 階段五：驗收測試與專案結案（Day 29 – Day 30）

* **Day 29｜真實場景端到端驗收：高中生備審模擬實測與 Demo 影片展示**
*產出：真實案例測試報告、系統操作 Demo 影片錄製*
* **Day 30｜完賽總結：30 天架構復盤、開源釋出與智慧教育未來展望**
*產出：GitHub 開源 Repo 釋出、架構演進覆盤、鐵人賽完賽心得*