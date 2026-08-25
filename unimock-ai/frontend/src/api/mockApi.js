/**
 * Mock API Service Layer for UniMock AI
 * Simulates backend response latency and returns structured Pydantic data schemas.
 */

export const mockInitialSessionData = {
  sessionId: "sess_20260824_cs01",
  targetSchool: "國立臺灣大學",
  targetGroup: "資訊電機學群",
  targetMajor: "資訊工程學系",
  interviewerPersona: "strict", // "strict" | "socratic"
  questionCount: 3,
  currentQuestionIndex: 0,
  isRecording: false,
  extractedProfile: {
    fileName: "陳小明_資工自傳與專案.pdf",
    targetSchool: "國立臺灣大學",
    targetGroup: "資訊電機學群",
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
      phase: "破冰自述與專業動機",
      text: "你好！歡迎來到國立臺灣大學資訊工程學系模擬面試。面對頂尖學術標準，請用兩分鐘簡述：你在 Edge AI 專案中遇到的最大技術瓶頸與底層架構抉擇是什麼？",
      hint: "頂尖名校著重底層原理與數據對比！建議採用 STAR 原則：背景情境 -> 核心瓶頸 (如 Memory OOM) -> 技術選型對比 (如 INT8 量化 vs 剪枝) -> 量化驗證結果。"
    },
    {
      index: 2,
      phase: "高難度專業技術與申論深度追問",
      text: "你在專案中使用了 OpenCV 與 Python 進行即時影像解析。在頂尖學術研究中，當面對高併發與多執行緒競爭條件 (Race Condition) 時，你會如何設計無鎖定 (Lock-free) 佇列與記憶體管理機制？",
      hint: "可從 Multi-threading / Async 併發模型、記憶體釋放與 Cache Coherence 切入申論。"
    },
    {
      index: 3,
      phase: "開放式申論與團隊架構決策",
      text: "假設你在推動全新的分散式 Agent 系統架構時，資深同儕與指導老師對你的技術提案提出強烈質疑。作為專案主導者，你如何透過 Benchmark 數據與科學實驗設計來驗證並說服團隊？",
      hint: "展現頂尖學術素養：實驗對照組設計、同理心溝通與 Benchmark 數據說服力。"
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
    overall_feedback: "該學生在本次模擬面試中展現了札實的資工專業基礎與自主學習熱忱。面對頂尖名校等級的高難度技術追問時答題條理分明，若能再補充更多量化 Benchmark 對比，表現將更完美。",
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

export const mockDepartmentGroups = [
  "資訊電機學群",
  "醫藥衛生學群",
  "數理化學學群",
  "工程學群",
  "管理學群",
  "財經學群",
  "外語學群",
  "人文社會學群",
  "生物資源學群",
  "建築與設計學群"
];

export function checkSchoolTier(schoolName) {
  const topTierKeywords = ['臺灣大學', '台大', '成功大學', '成大', '清華大學', '清大', '陽明交通大學', '交大', '政治大學', '政大', '臺灣科技大學', '臺科大', '中央大學', '中興大學', '中正大學', '中山大學'];
  const isTopTier = topTierKeywords.some(k => (schoolName || '').includes(k));
  return {
    isTopTier,
    tierLabel: isTopTier ? '頂尖前段名校模式' : '一般大學模式',
    difficultyDesc: isTopTier
      ? '🔥 已啟動高難度專業技術與申論題型（要求底層架構、演算法原理與 Benchmark 數據分析）'
      : '📘 已啟動標準模擬面試題型（著重個人動機、專案亮點與團隊溝通）'
  };
}

export const mockHistorySessions = [
  {
    sessionId: "sess_20260824_cs01",
    date: "2026-08-24 14:30",
    targetSchool: "國立臺灣大學",
    targetGroup: "資訊電機學群",
    targetMajor: "資訊工程學系",
    roleCategory: "頂尖名校二階模擬",
    duration: "25m 12s",
    score: 84,
    status: "COMPLETED"
  },
  {
    sessionId: "sess_20260820_mba02",
    date: "2026-08-20 09:15",
    targetSchool: "國立成功大學",
    targetGroup: "管理學群",
    targetMajor: "企業管理學系",
    roleCategory: "行為面試演練",
    duration: "32m 05s",
    score: 76,
    status: "COMPLETED"
  },
  {
    sessionId: "sess_20260815_ds03",
    date: "2026-08-15 16:45",
    targetSchool: "國立清華大學",
    targetGroup: "數理化學學群",
    targetMajor: "資料科學學系",
    roleCategory: "技術考核模擬",
    duration: "58m 20s",
    score: 62,
    status: "COMPLETED"
  }
];

export async function uploadResumeApi(file, targetSchool, targetGroup, targetMajor) {
  await new Promise((r) => setTimeout(r, 1200)); // Simulate scanning delay
  return {
    ...mockInitialSessionData.extractedProfile,
    fileName: file ? file.name : "上傳自傳檔案.pdf",
    targetSchool: targetSchool || "國立臺灣大學",
    targetGroup: targetGroup || "資訊電機學群",
    targetMajor: targetMajor || "資訊工程學系"
  };
}

export async function startInterviewApi(sessionId, targetSchool, targetGroup, targetMajor, persona, questionCount) {
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
