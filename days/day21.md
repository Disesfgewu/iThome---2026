# 【Day 21】前後端完整串接：FastAPI × React 即時對話引擎實戰

第四階段正式開工！今天我們將前 20 天精心建立的 **FastAPI 後端**與 **React 前端 UI** 進行完整的 HTTP RESTful API 串接，實現 PDF 履歷上傳、RAG 問題生成與即時問答的全鏈路對接。

---

## 1. 串接架構設計

```
React Frontend (Vite, port 5173)
         │
         │  fetch() / JSON / FormData
         ▼
FastAPI Backend (Uvicorn, port 8000)
    ├── POST /api/resume/upload-pdf   ← PDF 解析 + Gemma-4 多模態分析
    ├── POST /api/interview/setup     ← RAG 出題 + Session 建立
    └── POST /api/interview/answer   ← 語意評估 + 動態追問生成
```

---

## 2. 前端 API 呼叫模組 (`frontend/src/api/realApi.js`)

```javascript
const API_BASE_URL = 'http://localhost:8000/api';

// 1. 上傳 PDF 備審
export async function uploadResumeApi(file, targetSchool, targetGroup, targetMajor) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('target_school', targetSchool);
  formData.append('target_major', targetMajor);
  const res = await fetch(`${API_BASE_URL}/resume/upload-pdf`, {
    method: 'POST', body: formData
  });
  const data = await res.json();
  return { fileName: file.name, background: data.candidate_profile?.autobiography || '' };
}

// 2. 啟動面試（RAG 出第一題）
export async function startInterviewApi(sessionId, targetSchool, targetGroup, targetMajor) {
  const res = await fetch(`${API_BASE_URL}/interview/setup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ target_school: targetSchool, target_major: targetMajor })
  });
  const data = await res.json();
  return { sessionId: data.session_id, firstQuestion: data.first_question };
}

// 3. 提交回答（追問生成）
export async function respondInterviewApi(sessionId, currentIdx, answer) {
  const res = await fetch(`${API_BASE_URL}/interview/answer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, user_answer: answer })
  });
  const data = await res.json();
  return { nextQuestion: data.is_finished ? null : data.next_question, isFinished: data.is_finished };
}
```

---

## 3. 跨域 CORS 配置確認

後端 `app/main.py` 允許前端源跨域呼叫：

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

### 4.1 問題診斷：Chain-of-Thought 思考鏈洩漏

Gemma-4-31B 在 thinking mode 下會輸出完整的推理過程（markdown bullet list `*   Role: ...`），然後才輸出真正的問題。這導致前端顯示出英文亂碼的「推理腳本」而非中文面試題。

**根本原因**：
1. `prompt_manager.py` — 當 template kwargs 有缺失 key 時，直接 fallback 到含 markdown heading 的 raw template
2. `response_generation.md` — 存在未填充的 `{user_answer}` placeholder 觸發 KeyError
3. LLM 無 user_input trigger — 系統提示 only，LLM 自由推理

### 4.2 修正措施

**`gemma_llm.py` — 新增 `_strip_thinking_blocks()`**：

```python
def _strip_thinking_blocks(self, text: str) -> str:
    """
    Strategy 1: 嘗試去除 <think>...</think> XML tags
    Strategy 2: 逐行從尾部掃描，返回最後一個非 bullet / 非英文 metadata 的中文句子
    Strategy 3: 段落掃描 fallback
    """
```

**`prompt_manager.py` — 修正 template 填充**：

```python
# 自動偵測所有 {placeholder}，缺失的填 ''，不再 fallback 到 raw template
placeholders = re.findall(r'\{(\w+)\}', clean_template)
fill_kwargs = {p: kwargs.get(p, '') for p in placeholders}
return clean_template.format(**fill_kwargs)
```

**`rag_service.py` — 加入明確的 trigger user_input**：

```python
generated_question = await gemma_client.invoke_with_system_prompt(
    prompt_name="question_generation",
    user_input="請根據以上面試情境與學生背景，直接輸出一道繁體中文面試問題，不要任何說明文字。",
    ...
)
```

---

## 5. End-to-End 串接驗證結果

透過 Python 測試腳本對 FastAPI 進行真實 API 呼叫，驗證完整對話流程：

### 測試腳本 API 呼叫序列
1. `POST /api/interview/setup` — 建立面試 Session + RAG 出題
2. `POST /api/interview/answer` — 提交回答 + 動態追問

### 實測輸出

**Session 建立**：
- `session_id`: `sess_2d5e5ecf09`
- `stage`: `INTRO`
- `rag_seed_questions_count`: 0（向量庫匹配結果）

**第一題（Gemma-4-31B 動態生成）**：
> 你在開發機器學習圖形辨識專案時，選擇了特定的模型架構，請問你是基於什麼考量？此外，如果在實際應用中發現辨識準確率不如預期，你會從哪些維度（例如資料集、超參數或模型結構）去進行分析與優化？

**學生作答**：
> 教授好，我在高中時期開發了一個基於 OpenCV 的邊緣偵測系統，利用 Canny 演算法將圖像前處理速度提升 3 倍，並成功應用於校內機器人競賽的視覺辨識模組，最終獲得全國第一名。

**動態追問（PORTFOLIO_DEEP_DIVE 階段）**：
> 拿到全國第一名的成績確實非常出色，看得出你在實作層面有很強的執行力。不過，你剛才提到的 Canny 演算法主要屬於影像前處理階段，我想進一步了解，在經過前處理之後，你後續使用了什麼樣的模型架構來進行最終的「辨識」？此外，針對該模型，你當時是如何調整參數或優化結構，以確保在競賽環境中能達到理想的準確率？

✅ **狀態機正確推進**：`INTRO → PORTFOLIO_DEEP_DIVE`  
✅ **繁體中文輸出正確**  
✅ **Socratic 追問具深度**  
✅ **Turn Count: 2**（正確計數）

---

## 6. 修改檔案清單

| 檔案 | 修改內容 |
|---|---|
| `frontend/src/api/realApi.js` | 新增完整的 upload / setup / answer / report API 串接 |
| `app/services/gemma_llm.py` | 新增 `_strip_thinking_blocks()` 過濾 Chain-of-Thought |
| `app/services/prompt_manager.py` | 修正 template 填充 + 去除 markdown heading |
| `app/services/rag_service.py` | 新增明確的 user_input trigger |
| `app/routers/interview.py` | 追問 user_prompt 加入輸出格式指令 |
| `docs/system_prompts/question_generation.md` | 加入繁體中文輸出指令 |
| `docs/system_prompts/response_generation.md` | 移除 `{user_answer}` placeholder，加入中文指令 |

---

## 結語與明天預告

今天我們完成了最關鍵的前後端整合里程碑：

- ✅ React Frontend ↔ FastAPI Backend 完整 HTTP 通道建立
- ✅ Gemma-4-31B 中文問答品質修正（Chain-of-Thought 過濾）
- ✅ 完整面試對話流程 E2E 驗證通過
- ✅ 狀態機 INTRO → PORTFOLIO_DEEP_DIVE 正確推進

明天 **【Day 22】**，我們將實作 SSE (Server-Sent Events) 打字機串流，讓 AI 面試官的回應能即時逐字顯示，大幅提升面試的真實感與沉浸感！
