# 【Day 21】前後端完整串接：FastAPI × React 即時對話引擎實戰

第四階段正式開工！今天我們將前 20 天精心建立的 **FastAPI 後端**與 **React 前端 UI** 進行完整的 HTTP RESTful API 串接，實現 PDF 履歷上傳、RAG 問題生成與即時問答的全鏈路連動，並透過 Agent-Eye 實機啟動測試與截圖記錄。

---

## 1. 串接架構設計

```
React Frontend (Vite, port 5173)
         │
         │  fetch() / JSON / FormData
         ▼
FastAPI Backend (Uvicorn, port 8000)
    ├── POST /api/resume/upload-pdf   ← PDF 解析 + 多模態特徵提取
    ├── POST /api/interview/setup     ← 向量檢索出題 (RAG) + Session 初始化
    ├── POST /api/interview/answer   ← Socratic 追問生成 + STAR 狀態機推進
    └── POST /api/reports/generate   ← 四維度戰略評估診斷書產出
```

---

## 2. 前端 API 呼叫模組 (`frontend/src/api/realApi.js`)

```javascript
const API_BASE_URL = 'http://localhost:8000/api';

// 1. 上傳 PDF 備審履歷
export async function uploadResumeApi(file, targetSchool, targetGroup, targetMajor) {
  const formData = new FormData();
  if (file) formData.append('file', file);
  formData.append('target_school', targetSchool || '');
  formData.append('target_major', targetMajor || '');

  const res = await fetch(`${API_BASE_URL}/resume/upload-pdf`, {
    method: 'POST',
    body: formData
  });
  const data = await res.json();
  return {
    fileName: file ? file.name : '',
    targetSchool,
    targetGroup,
    targetMajor,
    background: data.candidate_profile?.autobiography || '',
    rawProfile: data.candidate_profile
  };
}

// 2. 啟動面試（RAG 出第一題）
export async function startInterviewApi(sessionId, targetSchool, targetGroup, targetMajor, persona, questionCount, extractedProfile) {
  const payload = {
    target_school: targetSchool || '',
    target_major: targetMajor || '',
    interview_mode: persona === 'strict' ? '頂大嚴謹模式' : '標準二階面試',
    candidate_profile: extractedProfile?.rawProfile || {
      applicant_name: '',
      high_school: '',
      autobiography: extractedProfile?.background || ''
    }
  };

  const res = await fetch(`${API_BASE_URL}/interview/setup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  const data = await res.json();
  return {
    sessionId: data.session_id,
    firstQuestion: data.first_question,
    phase: '破冰自述與專業動機'
  };
}

// 3. 提交回答（Socratic 追問生成）
export async function respondInterviewApi(sessionId, currentIdx, answer) {
  const payload = {
    session_id: sessionId,
    user_answer: answer
  };

  const res = await fetch(`${API_BASE_URL}/interview/answer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  const data = await res.json();
  return {
    sessionId: data.session_id,
    nextQuestion: data.is_finished ? null : data.next_question,
    isFinished: data.is_finished,
    nextIndex: currentIdx + 1
  };
}
```

---

## 3. 跨域 CORS 配置確認

確保後端 `app/main.py` 允許前端源進行跨域呼叫：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 4. Gemma-4-31B 輸出品質修正

### 4.1 問題診斷：Chain-of-Thought (思考鏈) 洩漏
Gemma-4-31B 在推理過程中，會輸出 markdown bullet list（`* Role: ...`、`* Draft: ...`）等思維鏈內容。這導致前端 UI 偶爾會收到未過濾的思考片段。

### 4.2 修正方案
1. **`gemma_llm.py`**：新增 `_strip_thinking_blocks()`，從尾部解析出最後一句完整的繁體中文問句，徹底去除所有推導清單與 XML tags。
2. **`prompt_manager.py`**：自動安全填補 template 中的 `{placeholder}`，並濾除 markdown `#` 標題行，避免 prompt 結構損壞。
3. **`InterviewPage.jsx`**：改進打字機效果渲染，採用 `currentQ.text.slice(0, i)` 切片計數，防止 React StrictMode 下字元重複堆疊。

---

## 5. 實機操作連動截圖紀錄

### 步驟 1：面試參數與志願設定（乾淨空狀態）
進入 `http://localhost:5173/`，左側設定目標學校「國立臺灣大學」與學系「資訊工程學系」，右側履歷備審檔案呈現乾淨初始狀態：

![面試參數設定頁面](images/day21/day21_setup_page.png)

---

### 步驟 2：上傳 PDF 備審檔案與多模態解析
上傳 PDF 備審履歷（如 `sample_resume.pdf`），系統自動調用 `/api/resume/upload-pdf` 完成多模態結構化分析：

![PDF 備審履歷上傳解析完成](images/day21/day21_pdf_uploaded.png)

![履歷亮點與潛在盲區分析](images/day21/day21_pdf_highlights.png)

---

### 步驟 3：點擊「🚀 啟動模擬面試艙」
滑動至頁面底端，點擊啟動按鈕，前端將結構化履歷與志願參數發送至 `/api/interview/setup`：

![啟動模擬面試艙按鈕](images/day21/day21_launch_button.png)

---

### 步驟 4：AI 考官動態第一題生成（破冰自述與專業動機）
後端向量資料庫與 Gemma-4-31B 生成針對資訊工程學系的專屬中文面試考題：

![AI 考官動態第一題](images/day21/day21_first_question.png)

> **AI 教授發問內容**：  
> 「在目前生成式人工智慧（Generative AI）快速普及的趨勢下，許多人認為傳統的程式設計能力將不再重要，你對這個觀點有什麼看法？此外，如果你進入台大資工系就讀，你認為哪些底層的計算機科學基礎（例如：演算法、作業系統或計算理論）在 AI 時代反而會變得更加關鍵？請說明你的理由。」

---

### 步驟 5：考生輸入作答內容
在回答區域填入考生的 STAR 結構化作答（以邊緣運算與 OpenCV 專案為例）：

![考生作答輸入](images/day21/day21_answer_entered.png)

> **考生作答**：  
> 「教授您好，我在高中時期主導開發了基於 OpenCV 的智慧邊緣影像辨識系統，成功將推論延遲降低至 45ms，並應用於校內自走車避障專案獲得全國資訊競賽佳作。」

---

### 步驟 6：提交作答與 Socratic 深度追問
點擊「確認送出回答」，後端 `/api/interview/answer` 接收回答，狀態機推進至 `PORTFOLIO_DEEP_DIVE`（專案經歷與架構設計），Gemma-4-31B 針對考生作答中的技術細節展開精準追問：

![AI 考官 Socratic 深度追問](images/day21/day21_followup_question.png)

> **AI 教授深度追問**：  
> 「能在高中階段就主導開發影像辨識系統，並將推論延遲優化至 45 毫秒且獲得全國競賽肯定，這顯示你在實作與效能調校上有不錯的經驗。我想請你深入說明，當時你是透過什麼具體的方法來降低延遲的？是在影像預處理、模型輕量化，還是針對邊緣運算硬體做了特定的優化？請詳細分享你的思考過程與執行步驟。」

---

## 6. 修改與新增檔案清單

| 檔案 | 類型 | 說明 |
|---|---|---|
| `frontend/src/api/realApi.js` | 新增 | 前後端真實 HTTP RESTful API Client |
| `frontend/src/pages/SetupPage.jsx` | 修改 | 連接真實 PDF 上傳與啟動面試 API |
| `frontend/src/pages/InterviewPage.jsx` | 修改 | 即時回答送出、動態問題堆疊與打字機修正 |
| `frontend/src/pages/ReportPage.jsx` | 修改 | 評測診斷報告空值保護與安全渲染 |
| `app/services/gemma_llm.py` | 修改 | 新增 `_strip_thinking_blocks()` 去除思考鏈 |
| `app/services/prompt_manager.py` | 修改 | 修復 template 填充與 markdown heading 過濾 |
| `app/services/rag_service.py` | 修改 | 新增繁體中文 user_input trigger 指令 |
| `days/images/day21/*.png` | 新增 | Agent-Eye 實機操作之 7 張高清測試截圖 |

---

## 結語與明天預告

今天我們成功實現了 **UniMock AI 前後端全鏈路即時連動**：
- ✅ PDF 備審檔案上傳與多模態特徵提取
- ✅ FastAPI 與 React 雙向 RESTful API 溝通
- ✅ Gemma-4-31B 繁體中文高精準度 Socratic 追問
- ✅ 完整連動流程透過 Agent-Eye 截圖存證記錄

明天 **【Day 22】**，我們將實作 **SSE (Server-Sent Events) 打字機串流**，讓 AI 面試官的回覆能夠即時逐字流暢輸出，進一步提升模擬面試的臨場感與互動體驗！
