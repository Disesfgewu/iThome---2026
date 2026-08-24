/**
 * Mock API Service Layer for UniMock AI
 * Simulates backend response latency and returns structured Pydantic data schemas.
 */

export const mockInitialSessionData = {
  sessionId: "sess_20260824_cs01",
  targetMajor: "資訊工程學系",
  interviewerPersona: "strict", // "strict" | "socratic"
  questionCount: 3,
  currentQuestionIndex: 0,
  isRecording: false,
  extractedProfile: {
    fileName: "陳小明_資工自傳與專案.pdf",
    targetMajor: "資訊工程學系",
    background: "市立高中數理資優班學生，性向偏好資訊與軟體工程，自學 Python 3 年",
    leadershipExperiences: [
      "高二擔任資訊研究社社長，帶領 30 位社友舉辦校際 Hackathon",
      "高一擔任班級副班長，協助班導師處理班務與活動企劃"
    ],
    certificates: [
      "APCS 大學程式設計先修檢定：觀念 4 級分 / 實作 3 級分",
      "TOEIC 多益英語測驗：850 分 (聽讀)"
    ],
    highlights: [
      { category: "專案實作", title: "Edge AI 智慧排程系統", description: "使用 FastAPI 與輕量化模型優化產線瓶頸" },
      { category: "競賽得獎", title: "全國高中軟體設計競賽佳作", description: "於決賽中團隊協作開發演算法解題" }
    ],
    detectedBlindspots: [
      "自傳中提及模型延遲降低 50%，但未列出具體 Benchmark 基準與硬體環境",
      "高中自主學習計畫中，API 安全認證機制描述略顯簡略"
    ]
  },
  questions: [
    {
      index: 1,
      phase: "破冰自述與動機",
      text: "你好！歡迎來到資訊工程學系模擬面試。請用兩分鐘時間簡述：你在 Edge AI 專案中遇到的最大技術瓶頸是什麼？你是如何解決的？",
      hint: "建議採用 STAR 原則：說明背景情境 -> 遭遇的量化瓶頸 (如 Memory OOM) -> 採用的技術解法 (如 INT8 輕量化) -> 最終對比數據。"
    },
    {
      index: 2,
      phase: "專案實作深度追問",
      text: "你在自傳中提及使用了 OpenCV 與 Python 進行即時影像處理解析。當面對高併發或記憶體不足時，你如何避免競爭條件 (Race Condition) 與系統卡頓？",
      hint: "可以從 Multi-threading / Async 佇列、緩衝區機制與底層記憶體釋放的角度切入回答。"
    },
    {
      index: 3,
      phase: "臨場情境與反思",
      text: "如果團隊成員對於你的技術架構提案提出強烈質疑且進度落後，作為社長或專案負責人，你會如何溝通與排解？",
      hint: "展現同理心、數據說服力（Benchmark 對比）與團隊溝通機制。"
    }
  ],
  dialogueHistory: [],
  evaluationReport: {
    scores: {
      logic_structure: 8,
      major_relevance: 9,
      communication_clarity: 8,
      adaptability: 7
    },
    overall_feedback: "該學生在本次模擬面試中展現了札實的資工專業基礎與自主學習熱忱。在技術問題回答上條理分明，若能在遭遇臨場追問時保持冷靜並量化成果數據，表現將更完美。",
    strengths: [
      "具備完整專案開發經驗，技術動機強烈",
      "對目標申請學系的研究領域（Edge Computing & AI）目標明確"
    ],
    improvements: [
      "面對質疑追問時語速稍微過快，建議加入適度停頓",
      "建議多補充 STAR 原則中的量化績效數據（如 FPS 提升 % 數）"
    ],
    question_diagnoses: [
      {
        turn_index: 1,
        question: "請描述一次你在 Edge AI 專案中解決困難技術問題的經驗？",
        original_answer: "我在專案中發現模型部署在邊緣端時記憶體不足，後來我把模型做了一些量化，然後跑起來就變順了。",
        weakness_analysis: "回答過於籠統，缺乏量化數據與具體的技術選型對比（如使用了幾位元量化、推論延遲降低多少毫秒）。",
        improved_sample: "在 Jetson 邊緣端部署時，主要瓶頸在於推論時 VRAM 溢出（OOM）。我透過 INT8 量化技術，將權重記憶體佔用從 4.2GB 壓縮至 1.8GB，在維持 94% 準確率的前提下，推論 FPS 從 12 提升至 38。"
      }
    ]
  }
};

export const mockHistorySessions = [
  {
    sessionId: "sess_20260824_cs01",
    date: "2026-08-24 14:30",
    targetMajor: "資訊工程學系 (CS)",
    roleCategory: "大學個人申請二階模擬",
    duration: "25m 12s",
    score: 84,
    status: "COMPLETED"
  },
  {
    sessionId: "sess_20260820_mba02",
    date: "2026-08-20 09:15",
    targetMajor: "企業管理學系 (MBA)",
    roleCategory: "行為面試演練",
    duration: "32m 05s",
    score: 76,
    status: "COMPLETED"
  },
  {
    sessionId: "sess_20260815_ds03",
    date: "2026-08-15 16:45",
    targetMajor: "資料科學學系 (DS)",
    roleCategory: "技術考核模擬",
    duration: "58m 20s",
    score: 62,
    status: "COMPLETED"
  }
];

export async function uploadResumeApi(file, targetMajor) {
  await new Promise((r) => setTimeout(r, 1200)); // Simulate scanning delay
  return {
    ...mockInitialSessionData.extractedProfile,
    fileName: file ? file.name : "上傳自傳檔案.pdf",
    targetMajor: targetMajor || "資訊工程學系"
  };
}

export async function startInterviewApi(sessionId, targetMajor, persona, questionCount) {
  await new Promise((r) => setTimeout(r, 600));
  return {
    sessionId,
    firstQuestion: mockInitialSessionData.questions[0].text,
    phase: mockInitialSessionData.questions[0].phase
  };
}

export async function respondInterviewApi(sessionId, currentIdx, answer) {
  await new Promise((r) => setTimeout(r, 800));
  const nextIdx = currentIdx + 1;
  const isFinished = nextIdx >= mockInitialSessionData.questions.length;
  return {
    sessionId,
    nextQuestion: isFinished ? null : mockInitialSessionData.questions[nextIdx].text,
    isFinished,
    nextIndex: nextIdx
  };
}

export async function getReportApi(sessionId) {
  await new Promise((r) => setTimeout(r, 500));
  return mockInitialSessionData.evaluationReport;
}

export async function getHistoryApi() {
  await new Promise((r) => setTimeout(r, 400));
  return mockHistorySessions;
}
